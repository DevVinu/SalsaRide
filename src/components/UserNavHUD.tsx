'use client';

import React from 'react';
import { TrackedUser, SignalPhase, TrafficSignal } from '../types/traffic';
import { getSignalState } from '../lib/trafficEngine';
import { Navigation, AlertCircle, CheckCircle, ArrowRight, Compass, ShieldAlert, Sparkles, MapPin } from 'lucide-react';

interface UserNavHUDProps {
  user: TrackedUser | null;
  phase: SignalPhase;
  phaseTimeRemaining: number;
  onClearSelection: () => void;
  onTrackBrowserLocation: () => void;
  isLocating: boolean;
}

export const UserNavHUD: React.FC<UserNavHUDProps> = ({
  user,
  phase,
  phaseTimeRemaining,
  onClearSelection,
  onTrackBrowserLocation,
  isLocating,
}) => {
  const signals = getSignalState(phase);

  if (!user) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 shadow-xl flex flex-col items-center justify-center text-center gap-3">
        <div className="w-12 h-12 rounded-2xl bg-zinc-800 flex items-center justify-center text-zinc-400">
          <Navigation className="w-6 h-6 text-indigo-400" />
        </div>
        <div>
          <h4 className="text-sm font-bold text-white">Driver In-Car HUD & Signal Advisory</h4>
          <p className="text-xs text-zinc-400 mt-1 max-w-sm">
            Click on any commuter marker on the interactive map to inspect their real-time signal guidance and shortest jam-solving recommendations.
          </p>
        </div>
        <button
          onClick={onTrackBrowserLocation}
          disabled={isLocating}
          className="mt-1 flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-all shadow-md"
        >
          <MapPin className="w-3.5 h-3.5" />
          <span>{isLocating ? 'Locating Device...' : 'Simulate / Track My Location'}</span>
        </button>
      </div>
    );
  }

  // Determine signal for this user's corridor
  const isNS = user.corridor === 'NORTH' || user.corridor === 'SOUTH';
  const userSignal: TrafficSignal = isNS ? signals.NS : signals.EW;

  const isGreen = userSignal === 'GREEN';
  const isYellow = userSignal === 'YELLOW';
  const isRed = userSignal === 'RED';

  const advice = user.advice;
  const isReroute = advice.action === 'REROUTE';
  const isPriority = advice.action === 'PREPARE_GREEN';

  return (
    <div className="bg-gradient-to-b from-zinc-900 via-zinc-900 to-zinc-950 border-2 border-indigo-500/40 rounded-2xl p-5 shadow-2xl flex flex-col gap-4">
      {/* HUD HEADER */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-indigo-600/30 border border-indigo-400/40 flex items-center justify-center text-indigo-300 font-mono font-bold text-xs">
            {user.id.replace('USR-', '#')}
          </div>
          <div>
            <div className="text-xs font-bold text-white flex items-center gap-1.5">
              <span>{user.name}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                {user.corridor} CORRIDOR
              </span>
            </div>
            <div className="text-[10px] text-zinc-400">
              {user.distanceMeters}m to junction • Speed: {user.speedKmh} km/h
            </div>
          </div>
        </div>

        <button
          onClick={onClearSelection}
          className="text-xs text-zinc-400 hover:text-white px-2 py-1 rounded bg-zinc-800 hover:bg-zinc-700 transition-colors"
        >
          Close HUD
        </button>
      </div>

      {/* SIGNAL HEAD & STATUS DISPLAY */}
      <div className="flex items-center justify-between bg-zinc-950/80 border border-zinc-800 rounded-xl p-3">
        <div className="flex items-center gap-3">
          {/* Signal Indicator Light */}
          <div className="flex gap-1 bg-black p-1.5 rounded-lg border border-zinc-800">
            <div
              className={`w-4 h-4 rounded-full ${
                isRed ? 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.9)]' : 'bg-red-950/40'
              }`}
            />
            <div
              className={`w-4 h-4 rounded-full ${
                isYellow ? 'bg-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.9)] animate-pulse' : 'bg-amber-950/40'
              }`}
            />
            <div
              className={`w-4 h-4 rounded-full ${
                isGreen ? 'bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.9)]' : 'bg-emerald-950/40'
              }`}
            />
          </div>

          <div>
            <div className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
              Approaching Signal
            </div>
            <div className="text-sm font-extrabold text-white">
              {isGreen ? 'GREEN - PROCEED' : isYellow ? 'AMBER - CLEARING' : 'RED - STOP'}
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="text-[10px] text-zinc-400">Phase Cycle</div>
          <div className="font-mono text-base font-bold text-indigo-400">
            {Math.ceil(phaseTimeRemaining)}s
          </div>
        </div>
      </div>

      {/* SHORTEST JAM-SOLVING INSTRUCTION CARD */}
      <div
        className={`p-4 rounded-xl border flex flex-col gap-2 ${
          isReroute
            ? 'bg-red-950/30 border-red-500/50 shadow-[0_0_20px_rgba(239,68,68,0.15)]'
            : isPriority
            ? 'bg-emerald-950/30 border-emerald-500/50 shadow-[0_0_20px_rgba(16,185,129,0.15)]'
            : 'bg-zinc-800/40 border-zinc-700/60'
        }`}
      >
        <div className="flex items-center justify-between">
          <span
            className={`text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
              isReroute ? 'text-red-400' : isPriority ? 'text-emerald-400' : 'text-zinc-300'
            }`}
          >
            {isReroute ? <AlertCircle className="w-4 h-4 text-red-400" /> : <Sparkles className="w-4 h-4 text-emerald-400" />}
            <span>{advice.title}</span>
          </span>

          <span
            className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full uppercase ${
              isReroute
                ? 'bg-red-900/60 text-red-200 border border-red-500/60 animate-bounce'
                : 'bg-emerald-900/60 text-emerald-200 border border-emerald-500/60'
            }`}
          >
            {advice.action}
          </span>
        </div>

        <p className="text-xs text-zinc-300 leading-relaxed">
          {advice.message}
        </p>

        {advice.alternateRouteBenefit && (
          <div className="mt-1 p-2 rounded-lg bg-zinc-900 border border-amber-500/40 flex items-center justify-between text-xs">
            <span className="text-amber-300 font-semibold flex items-center gap-1">
              <span>💡 {advice.alternateRouteBenefit}</span>
            </span>
            <button className="px-2 py-1 rounded bg-amber-500 hover:bg-amber-400 text-black font-bold text-[10px] transition-colors flex items-center gap-1">
              <span>Accept Detour</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

