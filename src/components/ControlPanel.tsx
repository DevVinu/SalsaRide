'use client';

import React from 'react';
import { Direction, LaneData, ControllerMode, PresetScenario } from '../types/traffic';
import { Play, Pause, RotateCcw, Zap, Sliders, AlertTriangle, FastForward } from 'lucide-react';

interface ControlPanelProps {
  isRunning: boolean;
  onTogglePlay: () => void;
  onReset: () => void;
  simSpeed: number;
  onSetSpeed: (speed: number) => void;
  mode: ControllerMode;
  onToggleMode: () => void;
  lanes: Record<Direction, LaneData>;
  onUpdateArrivalRate: (dir: Direction, rate: number) => void;
  onInjectEmergency: (dir: Direction) => void;
  onApplyPreset: (presetId: string) => void;
}

export const PRESETS: PresetScenario[] = [
  {
    id: 'morning_rush',
    name: 'Morning Commute Rush',
    description: 'Heavy North/South inbound corridors (35 cars/min) vs light cross-traffic.',
    rates: { NORTH: 36, SOUTH: 32, EAST: 8, WEST: 10 },
  },
  {
    id: 'evening_rush',
    name: 'Evening Commute Rush',
    description: 'Heavy East/West artery evacuation (35 cars/min) vs moderate North/South.',
    rates: { NORTH: 12, SOUTH: 10, EAST: 34, WEST: 38 },
  },
  {
    id: 'heavy_bottleneck',
    name: 'One-Sided Severe Jam',
    description: 'Massive single-direction spike (North 48 cars/min) testing dynamic early-clearance.',
    rates: { NORTH: 48, SOUTH: 14, EAST: 6, WEST: 6 },
  },
  {
    id: 'balanced',
    name: 'Balanced Off-Peak Flow',
    description: 'Uniform light to moderate traffic on all approaches (15 cars/min).',
    rates: { NORTH: 16, SOUTH: 15, EAST: 14, WEST: 15 },
  },
];

export const ControlPanel: React.FC<ControlPanelProps> = ({
  isRunning,
  onTogglePlay,
  onReset,
  simSpeed,
  onSetSpeed,
  mode,
  onToggleMode,
  lanes,
  onUpdateArrivalRate,
  onInjectEmergency,
  onApplyPreset,
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 shadow-xl flex flex-col gap-6">
      {/* TOP CONTROLS & MODE TOGGLE */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-800 pb-4">
        {/* Play/Pause/Reset */}
        <div className="flex items-center gap-2">
          <button
            onClick={onTogglePlay}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold text-sm transition-all shadow-md ${
              isRunning
                ? 'bg-amber-600 hover:bg-amber-500 text-white shadow-amber-900/30'
                : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/30'
            }`}
          >
            {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isRunning ? 'Pause Sim' : 'Start Sim'}</span>
          </button>

          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-medium text-sm transition-colors"
            title="Reset Simulation"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset</span>
          </button>

          {/* Speed Multiplier */}
          <div className="flex items-center bg-zinc-800/80 rounded-xl p-1 border border-zinc-700/60 ml-2">
            {[1, 2, 4].map((spd) => (
              <button
                key={spd}
                onClick={() => onSetSpeed(spd)}
                className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold transition-all ${
                  simSpeed === spd
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                {spd}x
              </button>
            ))}
          </div>
        </div>

        {/* Algorithm Mode Switcher */}
        <div className="flex items-center gap-3">
          <div className="text-xs text-zinc-400 font-medium hidden sm:block">Controller Mode:</div>
          <button
            onClick={onToggleMode}
            className={`relative flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-xs tracking-wider transition-all border ${
              mode === 'ADAPTIVE'
                ? 'bg-gradient-to-r from-emerald-900/60 to-teal-900/40 border-emerald-500/80 text-emerald-300 shadow-[0_0_15px_rgba(16,185,129,0.2)]'
                : 'bg-zinc-800/90 border-zinc-700 text-zinc-300'
            }`}
          >
            <Zap className={`w-3.5 h-3.5 ${mode === 'ADAPTIVE' ? 'text-emerald-400 animate-pulse' : 'text-zinc-400'}`} />
            <span>{mode === 'ADAPTIVE' ? '⚡ SALSA ADAPTIVE AI' : '⏱ FIXED-TIMER (TRADITIONAL)'}</span>
          </button>
        </div>
      </div>

      {/* COMMUTE RUSH PRESETS */}
      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2.5 flex items-center gap-1.5">
          <Sliders className="w-3.5 h-3.5 text-indigo-400" />
          <span>Commute Traffic Scenarios</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => onApplyPreset(preset.id)}
              className="text-left p-2.5 rounded-xl bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700/50 hover:border-indigo-500/50 transition-all group"
            >
              <div className="text-xs font-bold text-zinc-200 group-hover:text-indigo-300">
                {preset.name}
              </div>
              <div className="text-[11px] text-zinc-400 line-clamp-1 mt-0.5">
                {preset.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* APPROACH INFLUX SLIDERS */}
      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-3 flex items-center justify-between">
          <span>Approach Inflow Rates (Cars / Minute)</span>
          <span className="text-[11px] text-zinc-500 font-normal">Adjust live sliders</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {(Object.keys(lanes) as Direction[]).map((dir) => {
            const lane = lanes[dir];
            return (
              <div
                key={dir}
                className="bg-zinc-800/40 border border-zinc-800 rounded-xl p-3 flex flex-col gap-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-zinc-300">{lane.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-indigo-400">
                      {lane.arrivalRatePerMin} cars/min
                    </span>
                    <button
                      onClick={() => onInjectEmergency(dir)}
                      className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-950/80 hover:bg-red-800 text-red-300 border border-red-700/60 transition-colors flex items-center gap-0.5"
                      title="Inject Emergency Vehicle"
                    >
                      <AlertTriangle className="w-2.5 h-2.5" />
                      <span>SOS</span>
                    </button>
                  </div>
                </div>

                <input
                  type="range"
                  min="2"
                  max="50"
                  step="2"
                  value={lane.arrivalRatePerMin}
                  onChange={(e) => onUpdateArrivalRate(dir, Number(e.target.value))}
                  className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-zinc-700 rounded-lg"
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

