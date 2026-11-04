'use client';

import React from 'react';
import { Direction, CorridorStatus, SignalPhase } from '../types/traffic';
import { AlertTriangle, CheckCircle2, TrendingUp, Navigation, ArrowRight, Zap, RefreshCw } from 'lucide-react';

interface CorridorMonitorProps {
  corridors: Record<Direction, CorridorStatus>;
  overcrowdedCorridor: Direction | null;
  recommendedPhase: SignalPhase;
  currentPhase: SignalPhase;
  phaseRemaining: number;
}

export const CorridorMonitor: React.FC<CorridorMonitorProps> = ({
  corridors,
  overcrowdedCorridor,
  recommendedPhase,
  currentPhase,
  phaseRemaining,
}) => {
  const directions: Direction[] = ['NORTH', 'SOUTH', 'EAST', 'WEST'];

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 shadow-xl flex flex-col gap-5">
      {/* HEADER & OVERCROWDING SUMMARY */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Navigation className="w-4 h-4 text-indigo-400" />
            <span>Corridor Overcrowding & Jam-Solving Engine</span>
          </h3>
          <p className="text-xs text-zinc-400 mt-0.5">
            Geofenced user density within 500m of junction
          </p>
        </div>

        {overcrowdedCorridor ? (
          <div className="flex items-center gap-2 bg-red-950/80 border border-red-500/50 text-red-300 px-3 py-1.5 rounded-xl text-xs font-bold animate-pulse">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span>Overcrowding Alert: {overcrowdedCorridor} Corridor</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 px-3 py-1.5 rounded-xl text-xs font-semibold">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>All Corridors Balanced</span>
          </div>
        )}
      </div>

      {/* 4 APPROACH CORRIDORS STATUS CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {directions.map((dir) => {
          const corridor = corridors[dir];
          const isOvercrowded = corridor.congestionLevel === 'OVERCROWDED';
          const isModerate = corridor.congestionLevel === 'MODERATE';

          let badgeColor = 'bg-emerald-950 text-emerald-400 border-emerald-500/30';
          if (isOvercrowded) badgeColor = 'bg-red-950 text-red-400 border-red-500/40';
          else if (isModerate) badgeColor = 'bg-amber-950 text-amber-400 border-amber-500/30';

          return (
            <div
              key={dir}
              className={`p-3.5 rounded-xl border transition-all ${
                isOvercrowded
                  ? 'bg-red-950/20 border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.1)]'
                  : 'bg-zinc-800/40 border-zinc-800'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-xs text-zinc-200">{corridor.name}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeColor}`}>
                  {corridor.congestionLevel}
                </span>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-3 gap-2 text-center my-2.5">
                <div className="bg-zinc-900/80 p-1.5 rounded-lg border border-zinc-800">
                  <div className="text-[10px] text-zinc-400">Active Users</div>
                  <div className="text-sm font-mono font-bold text-white mt-0.5">
                    {corridor.activeUsersCount}
                  </div>
                </div>

                <div className="bg-zinc-900/80 p-1.5 rounded-lg border border-zinc-800">
                  <div className="text-[10px] text-zinc-400">&lt; 150m Queue</div>
                  <div className="text-sm font-mono font-bold text-indigo-300 mt-0.5">
                    {corridor.usersInInnerZone}
                  </div>
                </div>

                <div className="bg-zinc-900/80 p-1.5 rounded-lg border border-zinc-800">
                  <div className="text-[10px] text-zinc-400">Avg Speed</div>
                  <div className="text-sm font-mono font-bold text-zinc-200 mt-0.5">
                    {corridor.avgSpeedKmh} <span className="text-[9px] font-normal text-zinc-500">km/h</span>
                  </div>
                </div>
              </div>

              {/* Saturation Progress Bar */}
              <div className="w-full bg-zinc-700/60 h-1.5 rounded-full overflow-hidden mt-1">
                <div
                  className={`h-full transition-all duration-500 ${
                    isOvercrowded ? 'bg-red-500' : isModerate ? 'bg-amber-400' : 'bg-emerald-500'
                  }`}
                  style={{ width: `${corridor.saturationPercentage}%` }}
                />
              </div>

              {/* Jam-solving action per corridor */}
              <div className="mt-2 text-[11px] text-zinc-400 flex items-center justify-between">
                <span>Clearance Target: <strong className="text-zinc-200 font-mono">{corridor.optimalClearingTimeSeconds}s</strong></span>
                {corridor.rerouteAdvised && (
                  <span className="text-red-300 font-semibold text-[10px] flex items-center gap-0.5">
                    <span>Detour Active</span>
                    <ArrowRight className="w-2.5 h-2.5" />
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* SHORTEST JAM-SOLVING MECHANISM BANNER */}
      <div className="bg-gradient-to-r from-indigo-950/60 via-zinc-900 to-indigo-950/40 border border-indigo-500/30 rounded-xl p-4 flex flex-col gap-2">
        <div className="flex items-center gap-2 text-indigo-300 text-xs font-bold uppercase tracking-wider">
          <Zap className="w-4 h-4 text-indigo-400" />
          <span>Active Shortest Jam-Solving Mechanism</span>
        </div>
        <div className="text-xs text-zinc-200 leading-relaxed">
          {overcrowdedCorridor ? (
            <span>
              The algorithm identified severe congestion on the{' '}
              <strong className="text-red-400">{overcrowdedCorridor} Corridor</strong>. Dual-action mitigation engaged:
              <br />
              <strong className="text-white">1. Signal Level:</strong> Dynamic extension granting up to{' '}
              <strong className="text-emerald-400">{corridors[overcrowdedCorridor].optimalClearingTimeSeconds}s green</strong>{' '}
              to flush out the inner queue.
              <br />
              <strong className="text-white">2. Driver Guidance:</strong> Inbound users in the 200m–500m zone receive{' '}
              <strong className="text-amber-300">early bypass reroute signals</strong> to divert traffic onto parallel radials before they enter the bottleneck.
            </span>
          ) : (
            <span>
              All corridors are operating within safe density thresholds. Signals are dynamically cycling based on balanced vehicle counts to minimize deceleration stops.
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

