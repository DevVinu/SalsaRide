'use client';

import React from 'react';
import { Direction, LaneData, SignalPhase, TrafficSignal } from '../types/traffic';
import { getSignalState } from '../lib/trafficEngine';
import { ShieldAlert, Car } from 'lucide-react';

interface JunctionCanvasProps {
  phase: SignalPhase;
  phaseTimeRemaining: number;
  currentAllocatedGreen: number;
  lanes: Record<Direction, LaneData>;
  mode: 'ADAPTIVE' | 'FIXED';
  simTime: number;
  dischargingDirection: Direction | null;
}

export const JunctionCanvas: React.FC<JunctionCanvasProps> = ({
  phase,
  phaseTimeRemaining,
  currentAllocatedGreen,
  lanes,
  mode,
  simTime,
  dischargingDirection,
}) => {
  const signals = getSignalState(phase);

  // Helper to render traffic light head
  const renderTrafficLight = (
    signal: TrafficSignal,
    position: 'top' | 'bottom' | 'left' | 'right',
    label: string
  ) => {
    const isGreen = signal === 'GREEN';
    const isYellow = signal === 'YELLOW';
    const isRed = signal === 'RED';

    return (
      <div className="flex flex-col items-center bg-zinc-900 border-2 border-zinc-700 p-1.5 rounded-lg shadow-xl">
        <span className="text-[10px] font-semibold text-zinc-400 mb-1 tracking-wider uppercase">
          {label}
        </span>
        <div className="flex gap-1.5 bg-black/80 p-1 rounded-md">
          {/* Red light */}
          <div
            className={`w-4 h-4 rounded-full transition-all duration-300 ${
              isRed
                ? 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.9)] ring-2 ring-red-400'
                : 'bg-red-950/40 opacity-40'
            }`}
          />
          {/* Yellow light */}
          <div
            className={`w-4 h-4 rounded-full transition-all duration-300 ${
              isYellow
                ? 'bg-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.9)] ring-2 ring-amber-300 animate-pulse'
                : 'bg-amber-950/40 opacity-40'
            }`}
          />
          {/* Green light */}
          <div
            className={`w-4 h-4 rounded-full transition-all duration-300 ${
              isGreen
                ? 'bg-emerald-500 shadow-[0_0_14px_rgba(16,185,129,0.9)] ring-2 ring-emerald-300'
                : 'bg-emerald-950/40 opacity-40'
            }`}
          />
        </div>
        {/* Countdown display */}
        <div className="mt-1 font-mono text-[11px] font-bold text-zinc-200">
          {(isGreen || isYellow) ? `${Math.ceil(phaseTimeRemaining)}s` : '--'}
        </div>
      </div>
    );
  };

  // Helper to render queue vehicles in lane
  const renderQueueLane = (dir: Direction, orientation: 'vertical' | 'horizontal') => {
    const lane = lanes[dir];
    const isDischarging = dischargingDirection === dir;

    return (
      <div className="flex flex-wrap items-center justify-center gap-1.5 p-1 max-h-full">
        {lane.queue.slice(0, 10).map((veh, idx) => {
          const waitTime = Math.max(0, Math.floor(simTime - veh.enteredAt));
          const isLeadCar = idx === 0;

          return (
            <div
              key={veh.id}
              className={`relative flex items-center justify-center rounded px-1.5 py-0.5 text-[10px] font-mono font-bold shadow-md transition-all duration-300 ${
                veh.isEmergency
                  ? 'bg-red-600 text-white animate-bounce ring-2 ring-red-300'
                  : isLeadCar && isDischarging
                  ? 'bg-emerald-600 text-white translate-y-[-2px] scale-105'
                  : 'bg-indigo-600/90 text-indigo-50 border border-indigo-400/30'
              }`}
              title={`Vehicle ${veh.id} • Waiting: ${waitTime}s`}
            >
              {veh.isEmergency ? (
                <ShieldAlert className="w-3 h-3 mr-0.5 animate-spin" />
              ) : (
                <Car className="w-2.5 h-2.5 mr-0.5 opacity-80" />
              )}
              <span>{waitTime}s</span>
            </div>
          );
        })}
        {lane.queue.length > 10 && (
          <div className="text-[10px] text-amber-300 font-bold bg-amber-950/80 px-1 rounded border border-amber-500/50">
            +{lane.queue.length - 10} more
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="relative w-full max-w-2xl aspect-square mx-auto bg-zinc-950 rounded-2xl border-2 border-zinc-800 shadow-2xl overflow-hidden flex items-center justify-center select-none">
      {/* Background Grid Pattern */}
      <div 
        className="absolute inset-0 opacity-15"
        style={{
          backgroundImage: 'radial-gradient(circle, #3f3f46 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }}
      />

      {/* ROAD SYSTEM */}
      {/* Vertical Road (North - South) */}
      <div className="absolute w-44 h-full bg-zinc-800/90 border-x-4 border-dashed border-zinc-600 flex flex-col justify-between">
        {/* Yellow center line */}
        <div className="absolute left-1/2 -translate-x-1/2 w-1 h-full border-r-2 border-amber-400/80" />
      </div>

      {/* Horizontal Road (East - West) */}
      <div className="absolute h-44 w-full bg-zinc-800/90 border-y-4 border-dashed border-zinc-600 flex justify-between">
        {/* Yellow center line */}
        <div className="absolute top-1/2 -translate-y-1/2 w-full border-b-2 border-amber-400/80" />
      </div>

      {/* INTERSECTION CENTER BOX */}
      <div className="absolute w-44 h-44 bg-zinc-800 flex items-center justify-center border-2 border-zinc-700/60">
        {/* Center Intersection Crossings Pattern */}
        <div className="w-20 h-20 rounded-full border border-dashed border-zinc-600/50 flex flex-col items-center justify-center">
          <div className="text-[10px] font-mono text-zinc-400 font-bold">
            {mode === 'ADAPTIVE' ? '⚡ SMART' : '⏱ FIXED'}
          </div>
          <div className="text-xs font-mono font-extrabold text-white">
            {phase.includes('NORTH_SOUTH') ? 'N-S FLOW' : phase.includes('EAST_WEST') ? 'E-W FLOW' : 'CLEARING'}
          </div>
        </div>
      </div>

      {/* STOP LINES */}
      {/* North Stop Line */}
      <div className="absolute top-[calc(50%-88px)] w-44 h-2 bg-white/90 border-b-2 border-zinc-900" />
      {/* South Stop Line */}
      <div className="absolute bottom-[calc(50%-88px)] w-44 h-2 bg-white/90 border-t-2 border-zinc-900" />
      {/* West Stop Line */}
      <div className="absolute left-[calc(50%-88px)] h-44 w-2 bg-white/90 border-r-2 border-zinc-900" />
      {/* East Stop Line */}
      <div className="absolute right-[calc(50%-88px)] h-44 w-2 bg-white/90 border-l-2 border-zinc-900" />

      {/* APPROACH QUEUE LANES */}
      {/* North Approach (Vehicles heading South) */}
      <div className="absolute top-2 left-1/2 -translate-x-1/2 w-40 flex flex-col items-center">
        <div className="text-[10px] font-bold text-zinc-400 mb-1 flex items-center gap-1">
          <span>NORTH CORRIDOR</span>
          <span className="bg-zinc-800 text-zinc-200 px-1 rounded font-mono">
            Q: {lanes.NORTH.queue.length}
          </span>
        </div>
        {renderQueueLane('NORTH', 'vertical')}
      </div>

      {/* South Approach (Vehicles heading North) */}
      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-40 flex flex-col-reverse items-center">
        <div className="text-[10px] font-bold text-zinc-400 mt-1 flex items-center gap-1">
          <span>SOUTH CORRIDOR</span>
          <span className="bg-zinc-800 text-zinc-200 px-1 rounded font-mono">
            Q: {lanes.SOUTH.queue.length}
          </span>
        </div>
        {renderQueueLane('SOUTH', 'vertical')}
      </div>

      {/* West Approach (Vehicles heading East) */}
      <div className="absolute left-2 top-1/2 -translate-y-1/2 h-36 w-32 flex flex-col justify-center">
        <div className="text-[10px] font-bold text-zinc-400 mb-1 flex items-center gap-1">
          <span>WEST CORRIDOR</span>
          <span className="bg-zinc-800 text-zinc-200 px-1 rounded font-mono">
            Q: {lanes.WEST.queue.length}
          </span>
        </div>
        {renderQueueLane('WEST', 'horizontal')}
      </div>

      {/* East Approach (Vehicles heading West) */}
      <div className="absolute right-2 top-1/2 -translate-y-1/2 h-36 w-32 flex flex-col justify-center items-end text-right">
        <div className="text-[10px] font-bold text-zinc-400 mb-1 flex items-center gap-1">
          <span>EAST CORRIDOR</span>
          <span className="bg-zinc-800 text-zinc-200 px-1 rounded font-mono">
            Q: {lanes.EAST.queue.length}
          </span>
        </div>
        {renderQueueLane('EAST', 'horizontal')}
      </div>

      {/* TRAFFIC LIGHT SIGNALS */}
      {/* North Signal */}
      <div className="absolute top-[calc(50%-135px)] left-[calc(50%+96px)]">
        {renderTrafficLight(signals.NS, 'top', 'North-South')}
      </div>

      {/* South Signal */}
      <div className="absolute bottom-[calc(50%-135px)] right-[calc(50%+96px)]">
        {renderTrafficLight(signals.NS, 'bottom', 'North-South')}
      </div>

      {/* East Signal */}
      <div className="absolute top-[calc(50%+96px)] right-[calc(50%-135px)]">
        {renderTrafficLight(signals.EW, 'right', 'East-West')}
      </div>

      {/* West Signal */}
      <div className="absolute bottom-[calc(50%+96px)] left-[calc(50%-135px)]">
        {renderTrafficLight(signals.EW, 'left', 'East-West')}
      </div>
    </div>
  );
};

