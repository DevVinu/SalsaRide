'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { Header } from '../components/Header';
import { JunctionCanvas } from '../components/JunctionCanvas';
import { ControlPanel, PRESETS } from '../components/ControlPanel';
import { AnalyticsPanel } from '../components/AnalyticsPanel';
import { CorridorMonitor } from '../components/CorridorMonitor';
import { UserNavHUD } from '../components/UserNavHUD';
import {
  Direction,
  LaneData,
  SignalPhase,
  ControllerMode,
  SimulationStats,
  Vehicle,
  JunctionNode,
  TrackedUser,
  CorridorStatus,
} from '../types/traffic';
import {
  createInitialLanes,
  calculateAdaptiveGreenDuration,
  computeStats,
  FIXED_GREEN_TIME,
  YELLOW_TIME,
  ALL_RED_TIME,
} from '../lib/trafficEngine';
import {
  SAMPLE_JUNCTIONS,
  generateInitialUsers,
  analyzeCorridors,
  calculateHaversineDistanceMeters,
  getCorridorDirection,
} from '../lib/geoEngine';
import { Map, Layers, Navigation, Sliders, MapPin, Zap } from 'lucide-react';

// Dynamic import for Leaflet map component to prevent SSR window reference error
const JunctionMap = dynamic(
  () => import('../components/JunctionMap').then((mod) => mod.JunctionMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[480px] bg-zinc-950 rounded-2xl border-2 border-zinc-800 flex items-center justify-center text-zinc-400 font-mono text-xs">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-indigo-500 animate-ping" />
          <span>Loading Geospatial OpenStreetMap Layer...</span>
        </div>
      </div>
    ),
  }
);

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'MAP' | 'CANVAS'>('MAP');

  // Junction state
  const [selectedJunction, setSelectedJunction] = useState<JunctionNode>(SAMPLE_JUNCTIONS[0]);
  const [trackedUsers, setTrackedUsers] = useState<TrackedUser[]>(() =>
    generateInitialUsers(SAMPLE_JUNCTIONS[0])
  );
  const [selectedUser, setSelectedUser] = useState<TrackedUser | null>(null);
  const [isLocating, setIsLocating] = useState<boolean>(false);

  // Simulation controls
  const [isRunning, setIsRunning] = useState<boolean>(true);
  const [simSpeed, setSimSpeed] = useState<number>(1);
  const [mode, setMode] = useState<ControllerMode>('ADAPTIVE');
  const [simTime, setSimTime] = useState<number>(0);

  // Signal & Canvas state
  const [lanes, setLanes] = useState<Record<Direction, LaneData>>(createInitialLanes());
  const [phase, setPhase] = useState<SignalPhase>('NORTH_SOUTH_GREEN');
  const [phaseTimeRemaining, setPhaseTimeRemaining] = useState<number>(24);
  const [currentAllocatedGreen, setCurrentAllocatedGreen] = useState<number>(24);
  const [dischargingDirection, setDischargingDirection] = useState<Direction | null>('NORTH');

  const [stats, setStats] = useState<SimulationStats>({
    totalServed: 0,
    totalWaitTime: 0,
    avgWaitTime: 0,
    maxWaitTime: 0,
    fixedBaselineAvgWait: 0,
    delayReductionPercent: 0,
    fuelSavedLiters: 0,
    co2SavedKg: 0,
  });

  const dischargeAccumulatorRef = useRef<{ NS: number; EW: number }>({ NS: 0, EW: 0 });

  // Corridor analysis derived from active GPS users
  const { corridors, overcrowdedCorridor, recommendedPhase, updatedUsers } =
    analyzeCorridors(selectedJunction, trackedUsers, phase);

  // Switch Junction
  const handleSelectJunction = (junction: JunctionNode) => {
    setSelectedJunction(junction);
    const newUsers = generateInitialUsers(junction);
    setTrackedUsers(newUsers);
    setSelectedUser(null);
  };

  // Add commuter on map click
  const handleAddUserAtCoords = (lat: number, lng: number) => {
    const dist = calculateHaversineDistanceMeters({ lat, lng }, selectedJunction);
    const dir = getCorridorDirection({ lat, lng }, selectedJunction);
    const newId = `USR-${(trackedUsers.length + 1).toString().padStart(3, '0')}`;

    const newUser: TrackedUser = {
      id: newId,
      name: `Commuter #${trackedUsers.length + 1}`,
      lat,
      lng,
      distanceMeters: dist,
      corridor: dir,
      speedKmh: dist < 120 ? 8 : 32,
      lastPingTime: Date.now(),
      advice: {
        title: 'New Commuter Ping',
        message: 'Calculating shortest jam-solving route',
        severity: 'info',
        action: 'PROCEED',
        etaSeconds: Math.round(dist / 6),
      },
    };

    setTrackedUsers((prev) => [...prev, newUser]);
    setSelectedUser(newUser);
  };

  // Browser Geolocation integration
  const handleTrackBrowserLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }

    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setIsLocating(false);
        const userLat = pos.coords.latitude;
        const userLng = pos.coords.longitude;

        // Create a custom junction around user's current city or place user near current junction
        handleAddUserAtCoords(userLat, userLng);
      },
      () => {
        setIsLocating(false);
        // Fallback: spawn a simulated user on the congested corridor
        handleAddUserAtCoords(
          selectedJunction.lat + 0.0018,
          selectedJunction.lng
        );
      },
      { timeout: 8000 }
    );
  };

  // Reset helper
  const handleReset = () => {
    setLanes(createInitialLanes());
    setTrackedUsers(generateInitialUsers(selectedJunction));
    setSelectedUser(null);
    setPhase('NORTH_SOUTH_GREEN');
    setPhaseTimeRemaining(mode === 'ADAPTIVE' ? 24 : FIXED_GREEN_TIME);
    setCurrentAllocatedGreen(mode === 'ADAPTIVE' ? 24 : FIXED_GREEN_TIME);
    setSimTime(0);
    setStats({
      totalServed: 0,
      totalWaitTime: 0,
      avgWaitTime: 0,
      maxWaitTime: 0,
      fixedBaselineAvgWait: 0,
      delayReductionPercent: 0,
      fuelSavedLiters: 0,
      co2SavedKg: 0,
    });
  };

  const handleUpdateArrivalRate = (dir: Direction, rate: number) => {
    setLanes((prev) => ({
      ...prev,
      [dir]: { ...prev[dir], arrivalRatePerMin: rate },
    }));
  };

  const handleInjectEmergency = (dir: Direction) => {
    const emergencyCar: Vehicle = {
      id: `SOS-${Math.floor(Math.random() * 900 + 100)}`,
      direction: dir,
      enteredAt: simTime,
      isEmergency: true,
    };
    setLanes((prev) => ({
      ...prev,
      [dir]: {
        ...prev[dir],
        queue: [emergencyCar, ...prev[dir].queue],
        hasEmergency: true,
      },
    }));
  };

  const handleApplyPreset = (presetId: string) => {
    const preset = PRESETS.find((p) => p.id === presetId);
    if (!preset) return;
    setLanes((prev) => {
      const updated = { ...prev };
      (Object.keys(preset.rates) as Direction[]).forEach((dir) => {
        updated[dir] = { ...updated[dir], arrivalRatePerMin: preset.rates[dir] };
      });
      return updated;
    });
  };

  // Main simulation tick loop
  useEffect(() => {
    if (!isRunning) return;

    const intervalMs = 150;
    const intervalTimer = setInterval(() => {
      const dt = (intervalMs / 1000) * simSpeed;

      setSimTime((prevTime) => {
        const nextSimTime = prevTime + dt;

        // 1. Influx & Discharge for schematic lanes
        setLanes((prevLanes) => {
          const nextLanes = { ...prevLanes };

          (Object.keys(nextLanes) as Direction[]).forEach((dir) => {
            const lane = nextLanes[dir];
            const arrivalProb = (lane.arrivalRatePerMin / 60) * dt;
            if (Math.random() < arrivalProb) {
              const newVehicle: Vehicle = {
                id: `C${Math.floor(Math.random() * 9000 + 1000)}`,
                direction: dir,
                enteredAt: nextSimTime,
              };
              lane.queue = [...lane.queue, newVehicle];
            }
          });

          const isNSGreen = phase === 'NORTH_SOUTH_GREEN';
          const isEWGreen = phase === 'EAST_WEST_GREEN';

          if (isNSGreen) {
            dischargeAccumulatorRef.current.NS += dt;
            if (dischargeAccumulatorRef.current.NS >= 1.2) {
              dischargeAccumulatorRef.current.NS = 0;
              if (nextLanes.NORTH.queue.length > 0) {
                const [departed, ...remaining] = nextLanes.NORTH.queue;
                nextLanes.NORTH.queue = remaining;
                nextLanes.NORTH.totalServed += 1;
                nextLanes.NORTH.totalWaitTime += nextSimTime - departed.enteredAt;
                setDischargingDirection('NORTH');
              }
              if (nextLanes.SOUTH.queue.length > 0) {
                const [departed, ...remaining] = nextLanes.SOUTH.queue;
                nextLanes.SOUTH.queue = remaining;
                nextLanes.SOUTH.totalServed += 1;
                nextLanes.SOUTH.totalWaitTime += nextSimTime - departed.enteredAt;
              }
            }
          } else if (isEWGreen) {
            dischargeAccumulatorRef.current.EW += dt;
            if (dischargeAccumulatorRef.current.EW >= 1.2) {
              dischargeAccumulatorRef.current.EW = 0;
              if (nextLanes.EAST.queue.length > 0) {
                const [departed, ...remaining] = nextLanes.EAST.queue;
                nextLanes.EAST.queue = remaining;
                nextLanes.EAST.totalServed += 1;
                nextLanes.EAST.totalWaitTime += nextSimTime - departed.enteredAt;
                setDischargingDirection('EAST');
              }
              if (nextLanes.WEST.queue.length > 0) {
                const [departed, ...remaining] = nextLanes.WEST.queue;
                nextLanes.WEST.queue = remaining;
                nextLanes.WEST.totalServed += 1;
                nextLanes.WEST.totalWaitTime += nextSimTime - departed.enteredAt;
              }
            }
          }

          setStats(computeStats(nextLanes, nextSimTime, mode));
          return nextLanes;
        });

        // 2. Advance simulated GPS tracked commuters towards the junction
        setTrackedUsers((prevUsers) => {
          return prevUsers.map((u) => {
            // Speed in meters per second
            const speedMps = (u.speedKmh * 1000) / 3600;
            const dist = calculateHaversineDistanceMeters(u, selectedJunction);

            // If at green light, discharge user through junction and reset to outer distance
            const isGreenForUser =
              (u.corridor === 'NORTH' || u.corridor === 'SOUTH')
                ? phase === 'NORTH_SOUTH_GREEN'
                : phase === 'EAST_WEST_GREEN';

            if (dist <= 30) {
              if (isGreenForUser) {
                // Passed through! Respawn at outer edge of corridor
                const angle = u.corridor === 'NORTH' ? 0 : u.corridor === 'EAST' ? 90 : u.corridor === 'SOUTH' ? 180 : 270;
                const rad = (angle * Math.PI) / 180;
                const newDist = selectedJunction.geofenceRadiusMeters * (0.75 + Math.random() * 0.2);
                const dLat = (Math.cos(rad) * newDist) / 111000;
                const dLng = (Math.sin(rad) * newDist) / (111000 * Math.cos((selectedJunction.lat * Math.PI) / 180));

                return {
                  ...u,
                  lat: selectedJunction.lat + dLat,
                  lng: selectedJunction.lng + dLng,
                  distanceMeters: Math.round(newDist),
                  speedKmh: Math.round(25 + Math.random() * 15),
                };
              } else {
                // Stopped at red signal
                return { ...u, speedKmh: 0 };
              }
            } else {
              // Moving inward towards junction
              const stepFraction = Math.min(0.04, (speedMps * dt) / Math.max(50, dist));
              const newLat = u.lat + (selectedJunction.lat - u.lat) * stepFraction;
              const newLng = u.lng + (selectedJunction.lng - u.lng) * stepFraction;
              const newDist = calculateHaversineDistanceMeters({ lat: newLat, lng: newLng }, selectedJunction);

              return {
                ...u,
                lat: newLat,
                lng: newLng,
                distanceMeters: newDist,
              };
            }
          });
        });

        // 3. Phase Controller State Machine
        setPhaseTimeRemaining((prevRemaining) => {
          const nextRemaining = prevRemaining - dt;

          if (nextRemaining <= 0) {
            switch (phase) {
              case 'NORTH_SOUTH_GREEN':
                setPhase('NORTH_SOUTH_YELLOW');
                return YELLOW_TIME;

              case 'NORTH_SOUTH_YELLOW':
                setPhase('ALL_RED_TRANSITION_1');
                return ALL_RED_TIME;

              case 'ALL_RED_TRANSITION_1': {
                setPhase('EAST_WEST_GREEN');
                const ewUsers = corridors.EAST.activeUsersCount + corridors.WEST.activeUsersCount;
                const nsUsers = corridors.NORTH.activeUsersCount + corridors.SOUTH.activeUsersCount;
                const duration = mode === 'ADAPTIVE'
                  ? calculateAdaptiveGreenDuration(ewUsers, nsUsers, false, false)
                  : FIXED_GREEN_TIME;
                setCurrentAllocatedGreen(duration);
                return duration;
              }

              case 'EAST_WEST_GREEN':
                setPhase('EAST_WEST_YELLOW');
                return YELLOW_TIME;

              case 'EAST_WEST_YELLOW':
                setPhase('ALL_RED_TRANSITION_2');
                return ALL_RED_TIME;

              case 'ALL_RED_TRANSITION_2': {
                setPhase('NORTH_SOUTH_GREEN');
                const nsUsers = corridors.NORTH.activeUsersCount + corridors.SOUTH.activeUsersCount;
                const ewUsers = corridors.EAST.activeUsersCount + corridors.WEST.activeUsersCount;
                const duration = mode === 'ADAPTIVE'
                  ? calculateAdaptiveGreenDuration(nsUsers, ewUsers, false, false)
                  : FIXED_GREEN_TIME;
                setCurrentAllocatedGreen(duration);
                return duration;
              }
            }
          }

          return nextRemaining;
        });

        return nextSimTime;
      });
    }, intervalMs);

    return () => clearInterval(intervalTimer);
  }, [isRunning, simSpeed, mode, phase, corridors, selectedJunction]);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col gap-6">
        {/* JUNCTION SELECTOR & VIEW MODE TABS */}
        <div className="flex flex-wrap items-center justify-between gap-4 bg-zinc-900/60 border border-zinc-800 rounded-2xl p-3 sm:p-4">
          {/* Junction Selector Dropdown */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
                Active Junction Corridor
              </div>
              <select
                value={selectedJunction.id}
                onChange={(e) => {
                  const junc = SAMPLE_JUNCTIONS.find((j) => j.id === e.target.value);
                  if (junc) handleSelectJunction(junc);
                }}
                className="bg-zinc-800 border border-zinc-700 text-xs font-bold text-white rounded-lg px-2.5 py-1 mt-0.5 outline-none cursor-pointer hover:border-indigo-500 transition-colors"
              >
                {SAMPLE_JUNCTIONS.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.name} ({j.address.split(',')[1]?.trim() || j.address})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* View Mode Toggle: Interactive Map vs Schematic Canvas */}
          <div className="flex items-center bg-zinc-950 p-1 rounded-xl border border-zinc-800">
            <button
              onClick={() => setActiveTab('MAP')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'MAP'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <Map className="w-3.5 h-3.5" />
              <span>Geospatial Map View</span>
            </button>
            <button
              onClick={() => setActiveTab('CANVAS')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'CANVAS'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>2D Intersection View</span>
            </button>
          </div>
        </div>

        {/* MAIN DISPLAY: MAP OR CANVAS + HUD */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Main Visualizer Column */}
          <div className="lg:col-span-7 flex flex-col gap-4">
            {activeTab === 'MAP' ? (
              <JunctionMap
                junction={selectedJunction}
                users={updatedUsers}
                corridors={corridors}
                selectedUser={selectedUser}
                onSelectUser={setSelectedUser}
                onAddUserAtCoords={handleAddUserAtCoords}
                currentPhase={phase}
              />
            ) : (
              <JunctionCanvas
                phase={phase}
                phaseTimeRemaining={phaseTimeRemaining}
                currentAllocatedGreen={currentAllocatedGreen}
                lanes={lanes}
                mode={mode}
                simTime={simTime}
                dischargingDirection={dischargingDirection}
              />
            )}

            {/* Overcrowding Monitor & Jam-Solving Mechanism */}
            <CorridorMonitor
              corridors={corridors}
              overcrowdedCorridor={overcrowdedCorridor}
              recommendedPhase={recommendedPhase}
              currentPhase={phase}
              phaseRemaining={phaseTimeRemaining}
            />

            {/* Performance Telemetry */}
            <AnalyticsPanel
              stats={stats}
              mode={mode}
              currentPhase={phase}
              phaseRemaining={phaseTimeRemaining}
              currentAllocatedGreen={currentAllocatedGreen}
            />
          </div>

          {/* Right Column: Driver HUD + Controls */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            {/* Driver In-Car Heads-Up Display */}
            <UserNavHUD
              user={selectedUser}
              phase={phase}
              phaseTimeRemaining={phaseTimeRemaining}
              onClearSelection={() => setSelectedUser(null)}
              onTrackBrowserLocation={handleTrackBrowserLocation}
              isLocating={isLocating}
            />

            {/* Simulation & Traffic Controls */}
            <ControlPanel
              isRunning={isRunning}
              onTogglePlay={() => setIsRunning(!isRunning)}
              onReset={handleReset}
              simSpeed={simSpeed}
              onSetSpeed={setSimSpeed}
              mode={mode}
              onToggleMode={() => setMode(mode === 'ADAPTIVE' ? 'FIXED' : 'ADAPTIVE')}
              lanes={lanes}
              onUpdateArrivalRate={handleUpdateArrivalRate}
              onInjectEmergency={handleInjectEmergency}
              onApplyPreset={handleApplyPreset}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
