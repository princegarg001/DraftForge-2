import React, { useState } from 'react';
import {
  Network,
  Database,
} from 'lucide-react';

export const Hero3DVisual: React.FC = () => {
  const [activeHighlight, setActiveHighlight] = useState<number | null>(null);

  return (
    <div className="relative w-full max-w-2xl mx-auto perspective-1200 select-none">
      {/* Ambient Radial Background Glows */}
      <div className="absolute -inset-4 bg-gradient-to-tr from-primary-600/20 via-accent-cyan/15 to-indigo-600/20 rounded-[3rem] blur-3xl -z-10 animate-pulse-glow" />
      <div className="absolute -top-12 -right-12 w-64 h-64 bg-accent-cyan/15 rounded-full blur-3xl -z-10 pointer-events-none" />

      {/* Main 3D Floating Canvas Container */}
      <div className="hero-3d-card relative glass-panel-glow rounded-3xl border border-slate-700/80 p-5 sm:p-7 shadow-2xl backdrop-blur-2xl transition-all duration-700">
        {/* Top Window Chrome */}
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800/80">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-rose-500/80" />
            <span className="w-3 h-3 rounded-full bg-amber-500/80" />
            <span className="w-3 h-3 rounded-full bg-emerald-500/80" />
            <span className="text-[11px] font-mono text-slate-400 ml-2">
              DraftForge_Studio / Affidavit_Draft_v2.legal
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-primary-500/20 text-primary-300 border border-primary-500/30">
              Live RAG Evaluation
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          </div>
        </div>

        {/* Legal Document Editor Simulation */}
        <div className="relative rounded-2xl bg-slate-950/90 border border-slate-800/80 p-5 font-mono text-xs text-slate-300 leading-relaxed overflow-hidden">
          {/* Sweeping Laser Scan Line */}
          <div className="laser-scan-line animate-scan" />

          {/* Heading */}
          <div className="text-center font-bold text-slate-100 mb-3 tracking-wider text-[13px] border-b border-slate-800/60 pb-2">
            BEFORE THE COMPETENT BAR COUNCIL AUTHORITY, NEW DELHI
            <p className="text-[10px] text-primary-400 font-normal mt-0.5">
              IN THE MATTER OF: STATUTORY ENROLLMENT UNDER ADVOCATES ACT, 1961
            </p>
          </div>

          {/* Clauses with Live AI Annotations */}
          <div className="space-y-2.5 text-[11px] sm:text-xs">
            <p
              onMouseEnter={() => setActiveHighlight(1)}
              onMouseLeave={() => setActiveHighlight(null)}
              className={`p-1.5 rounded-lg transition-all cursor-pointer ${
                activeHighlight === 1
                  ? 'bg-emerald-500/20 text-emerald-200 border-l-2 border-emerald-400'
                  : 'text-slate-300 hover:bg-slate-900'
              }`}
            >
              <strong className="text-primary-300">1. IDENTIFICATION & AGE:</strong> I, Ramesh Kumar, Son of Shri Suresh Kumar, aged about 24 years, resident of Sector 14, Gurugram, Haryana, do hereby solemnly affirm on oath as under:
            </p>

            <p
              onMouseEnter={() => setActiveHighlight(2)}
              onMouseLeave={() => setActiveHighlight(null)}
              className={`p-1.5 rounded-lg transition-all cursor-pointer ${
                activeHighlight === 2
                  ? 'bg-emerald-500/20 text-emerald-200 border-l-2 border-emerald-400'
                  : 'text-slate-300 hover:bg-slate-900'
              }`}
            >
              <strong className="text-primary-300">2. LEGAL CHARACTER:</strong> That I have graduated with LL.B (Honours) from an institution recognized by the Bar Council of India, and no criminal proceedings or moral turpitude charges are pending against me in any court of law.
            </p>

            <p
              onMouseEnter={() => setActiveHighlight(3)}
              onMouseLeave={() => setActiveHighlight(null)}
              className={`p-1.5 rounded-lg transition-all cursor-pointer ${
                activeHighlight === 3
                  ? 'bg-amber-500/20 text-amber-200 border-l-2 border-amber-400'
                  : 'text-slate-300 hover:bg-slate-900'
              }`}
            >
              <strong className="text-amber-400">3. FULL-TIME ENGAGEMENT:</strong> That I am not engaged in any commercial trade, full-time business, or salaried profession contrary to the Bar Council of India Rules.
            </p>

            <div
              onMouseEnter={() => setActiveHighlight(4)}
              onMouseLeave={() => setActiveHighlight(null)}
              className={`p-2.5 rounded-xl transition-all cursor-pointer border ${
                activeHighlight === 4
                  ? 'bg-primary-950/40 border-primary-500/50 text-white'
                  : 'bg-slate-900/60 border-slate-800/80 text-slate-300'
              }`}
            >
              <div className="flex items-center justify-between font-bold text-primary-300 mb-1">
                <span>VERIFICATION JURAT:</span>
                <span className="text-[9px] font-mono text-emerald-400 uppercase">
                  ✓ Verified under Oath
                </span>
              </div>
              <p className="text-[10px] text-slate-400 leading-normal">
                "Verified at New Delhi on this 23rd day of August, 2026, that the contents of paragraphs 1 to 3 are true to my personal knowledge and belief. Nothing material has been concealed."
              </p>
            </div>
          </div>
        </div>

        {/* Floating Holographic Badge 1: Deterministic Score Card (Top Right) */}
        <div className="absolute -top-6 -right-4 sm:-right-8 p-3.5 rounded-2xl glass-panel-glow border border-emerald-500/40 shadow-xl animate-float">
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#1e293b"
                  strokeWidth="3.5"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="3.5"
                  strokeDasharray="87, 100"
                  strokeLinecap="round"
                />
              </svg>
              <span className="absolute font-mono font-extrabold text-xs text-white">87%</span>
            </div>
            <div>
              <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400 block">
                Deterministic Rubric
              </span>
              <span className="font-bold text-xs text-emerald-400">Statutory Compliant</span>
            </div>
          </div>
        </div>

        {/* Floating Holographic Badge 2: FastEmbed Qdrant Match (Bottom Left) */}
        <div className="absolute -bottom-6 -left-3 sm:-left-8 p-3.5 rounded-2xl glass-panel-glow border border-indigo-500/40 shadow-xl animate-float-reverse">
          <div className="flex items-center gap-2.5 text-xs">
            <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[9px] font-mono text-slate-400 block">
                FastEmbed 384-dim Match
              </span>
              <span className="font-bold text-white text-[11px]">
                96.4% Ground Truth Precedent
              </span>
            </div>
          </div>
        </div>

        {/* Floating Holographic Badge 3: Neo4j Graph RAG Risk Alert (Bottom Right) */}
        <div className="absolute -bottom-6 right-2 sm:right-6 p-3 rounded-2xl glass-panel-glow border border-accent-cyan/40 shadow-xl animate-float-slow">
          <div className="flex items-center gap-2 text-xs">
            <div className="w-7 h-7 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-accent-cyan">
              <Network className="w-3.5 h-3.5" />
            </div>
            <div className="text-left font-mono">
              <span className="text-[9px] text-slate-400 block">Neo4j Aura Graph</span>
              <span className="font-bold text-accent-cyan text-[10px]">
                Prerequisites Verified
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
