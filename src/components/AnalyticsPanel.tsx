'use client';

import React from 'react';
import { SimulationStats, ControllerMode, SignalPhase } from '../types/traffic';
import { TrendingDown, Clock, CheckCircle2, Leaf, Zap, BarChart3 } from 'lucide-react';

interface AnalyticsPanelProps {
  stats: SimulationStats;
  mode: ControllerMode;
  currentPhase: SignalPhase;
  phaseRemaining: number;
  currentAllocatedGreen: number;
}

export const AnalyticsPanel: React.FC<AnalyticsPanelProps> = ({
  stats,
  mode,
  currentPhase,
  phaseRemaining,
  currentAllocatedGreen,
}) => {
  const isAdaptive = mode === 'ADAPTIVE';

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 shadow-xl flex flex-col gap-5">
      {/* HEADER */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-bold text-zinc-100 uppercase tracking-wider">
            Real-Time Congestion Telemetry
          </h3>
        </div>
        <div className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-300 border border-zinc-700">
          Phase Cycle: <span className="font-bold text-white">{Math.ceil(phaseRemaining)}s left</span> / {currentAllocatedGreen}s
        </div>
      </div>

      {/* PRIMARY METRICS GRID */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Metric 1: Congestion Reduction */}
        <div className="bg-gradient-to-br from-emerald-950/40 to-zinc-900 border border-emerald-500/30 rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-[11px] font-medium uppercase tracking-wider">Delay Reduced</span>
            <TrendingDown className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2">
            <div className="text-2xl font-mono font-extrabold text-emerald-400">
              {isAdaptive ? `-${stats.delayReductionPercent}%` : '0%'}
            </div>
            <div className="text-[10px] text-zinc-400 mt-0.5">
              vs Fixed-Time Baseline
            </div>
          </div>
        </div>

        {/* Metric 2: Average Wait Time */}
        <div className="bg-zinc-800/40 border border-zinc-800 rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-[11px] font-medium uppercase tracking-wider">Avg Wait Time</span>
            <Clock className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2">
            <div className="text-2xl font-mono font-extrabold text-white">
              {stats.avgWaitTime}s
            </div>
            <div className="text-[10px] text-zinc-400 mt-0.5">
              Baseline: <span className="text-zinc-300 font-mono">{stats.fixedBaselineAvgWait}s</span>
            </div>
          </div>
        </div>

        {/* Metric 3: Total Vehicles Cleared */}
        <div className="bg-zinc-800/40 border border-zinc-800 rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-[11px] font-medium uppercase tracking-wider">Cars Cleared</span>
            <CheckCircle2 className="w-4 h-4 text-teal-400" />
          </div>
          <div className="mt-2">
            <div className="text-2xl font-mono font-extrabold text-teal-400">
              {stats.totalServed}
            </div>
            <div className="text-[10px] text-zinc-400 mt-0.5">
              Max queue wait: {stats.maxWaitTime}s
            </div>
          </div>
        </div>

        {/* Metric 4: Environmental Savings */}
        <div className="bg-gradient-to-br from-lime-950/30 to-zinc-900 border border-lime-500/20 rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-[11px] font-medium uppercase tracking-wider">Idle Emissions</span>
            <Leaf className="w-4 h-4 text-lime-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-mono font-extrabold text-lime-400">
              {stats.co2SavedKg} kg
            </div>
            <div className="text-[10px] text-zinc-400 mt-0.5">
              {stats.fuelSavedLiters} L fuel saved
            </div>
          </div>
        </div>
      </div>

      {/* COMPARATIVE EXPLAINER BANNER */}
      <div className="bg-zinc-950/70 rounded-xl p-3.5 border border-zinc-800/80 flex items-start gap-3 text-xs">
        <Zap className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-zinc-300 leading-relaxed">
          {isAdaptive ? (
            <span>
              <strong className="text-emerald-400 font-semibold">SalsaRide Adaptive Algorithm Active:</strong>{' '}
              Continuously balances green time based on real-time vehicle density ratios. When an active corridor queue drains early, green is automatically terminated to grant immediate right-of-way to waiting opposing traffic, eliminating empty-intersection delay.
            </span>
          ) : (
            <span>
              <strong className="text-amber-400 font-semibold">Traditional Fixed-Timer Baseline:</strong>{' '}
              Running constant 24-second fixed cycles. Notice how empty lanes hold green signals while congested corridors accumulate queue delays and idling emissions.
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

