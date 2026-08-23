import React from 'react';
import {
  FileText,
  Sparkles,
  ShieldAlert,
  Cpu,
  Database,
  GraduationCap,
} from 'lucide-react';

interface AICoreOrbProps {
  stageText?: string;
  size?: 'sm' | 'md' | 'lg';
  activeNodes?: Array<'DOCUMENT' | 'CLAUSES' | 'KNOWLEDGE' | 'RISKS' | 'SKILLS'>;
}

export const AICoreOrb: React.FC<AICoreOrbProps> = ({
  stageText = 'AI Core Processing...',
  size = 'md',
  activeNodes = ['DOCUMENT', 'CLAUSES', 'KNOWLEDGE', 'RISKS', 'SKILLS'],
}) => {
  const isLg = size === 'lg';
  const isSm = size === 'sm';

  const containerSize = isLg ? 'w-72 h-72' : isSm ? 'w-44 h-44' : 'w-56 h-56';
  const coreSize = isLg ? 'w-24 h-24' : isSm ? 'w-14 h-14' : 'w-18 h-18';

  return (
    <div className="relative flex flex-col items-center justify-center select-none">
      {/* Outer 3D Node Orbit System */}
      <div className={`relative ${containerSize} flex items-center justify-center perspective-1000`}>
        {/* Rotating Outer Gyroscope Ring 1 */}
        <div className="absolute inset-0 rounded-full border border-primary-500/30 animate-spin [animation-duration:12s]" />

        {/* Rotating Outer Gyroscope Ring 2 (Reversed & Tilted) */}
        <div className="absolute inset-2 rounded-full border border-accent-cyan/25 animate-spin [animation-duration:16s] [animation-direction:reverse] transform rotate-45" />

        {/* Pulsing Energy Aura Wave */}
        <div className="absolute inset-6 rounded-full bg-gradient-to-tr from-primary-600/20 via-indigo-600/30 to-accent-cyan/20 blur-xl animate-pulse-glow" />

        {/* Central 3D Glowing Nucleus */}
        <div className={`relative ${coreSize} rounded-full bg-gradient-to-tr from-primary-600 via-indigo-500 to-accent-cyan p-0.5 shadow-2xl shadow-primary-500/50 flex items-center justify-center z-10 animate-float`}>
          <div className="w-full h-full rounded-full bg-slate-950/90 flex flex-col items-center justify-center p-2 text-center backdrop-blur-md">
            <Cpu className="w-6 h-6 text-accent-cyan animate-pulse" />
            {!isSm && (
              <span className="text-[9px] font-mono font-bold text-primary-300 uppercase tracking-widest mt-1">
                AI CORE
              </span>
            )}
          </div>
        </div>

        {/* Orbiting Satellite Node: DOCUMENT (Top Left) */}
        {activeNodes.includes('DOCUMENT') && (
          <div className="absolute top-2 left-2 p-2 rounded-xl glass-panel-glow border border-primary-500/40 text-primary-300 shadow-lg animate-float-slow flex items-center gap-1.5 z-20">
            <FileText className="w-3.5 h-3.5" />
            <span className="text-[9px] font-mono font-bold hidden sm:inline">DOCUMENT</span>
          </div>
        )}

        {/* Orbiting Satellite Node: CLAUSES (Top Right) */}
        {activeNodes.includes('CLAUSES') && (
          <div className="absolute top-2 right-2 p-2 rounded-xl glass-panel-glow border border-accent-cyan/40 text-accent-cyan shadow-lg animate-float-reverse flex items-center gap-1.5 z-20">
            <Sparkles className="w-3.5 h-3.5" />
            <span className="text-[9px] font-mono font-bold hidden sm:inline">CLAUSES</span>
          </div>
        )}

        {/* Orbiting Satellite Node: KNOWLEDGE (Bottom Left) */}
        {activeNodes.includes('KNOWLEDGE') && (
          <div className="absolute bottom-2 left-2 p-2 rounded-xl glass-panel-glow border border-indigo-500/40 text-indigo-300 shadow-lg animate-float flex items-center gap-1.5 z-20">
            <Database className="w-3.5 h-3.5" />
            <span className="text-[9px] font-mono font-bold hidden sm:inline">KNOWLEDGE</span>
          </div>
        )}

        {/* Orbiting Satellite Node: RISKS (Bottom Right) */}
        {activeNodes.includes('RISKS') && (
          <div className="absolute bottom-2 right-2 p-2 rounded-xl glass-panel-glow border border-rose-500/40 text-rose-300 shadow-lg animate-float-slow flex items-center gap-1.5 z-20">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span className="text-[9px] font-mono font-bold hidden sm:inline">RISKS</span>
          </div>
        )}

        {/* Orbiting Satellite Node: SKILLS (Center Bottom) */}
        {activeNodes.includes('SKILLS') && (
          <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 p-1.5 px-2.5 rounded-xl glass-panel-glow border border-emerald-500/40 text-emerald-300 shadow-lg animate-pulse flex items-center gap-1.5 z-20">
            <GraduationCap className="w-3.5 h-3.5" />
            <span className="text-[9px] font-mono font-bold">SKILLS</span>
          </div>
        )}

        {/* SVG Connecting Energy Beams */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-40">
          <line x1="20%" y1="20%" x2="50%" y2="50%" stroke="#818cf8" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="80%" y1="20%" x2="50%" y2="50%" stroke="#06b6d4" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="20%" y1="80%" x2="50%" y2="50%" stroke="#6366f1" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="80%" y1="80%" x2="50%" y2="50%" stroke="#f43f5e" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="50%" y1="90%" x2="50%" y2="50%" stroke="#10b981" strokeWidth="1.5" strokeDasharray="3 3" />
        </svg>
      </div>

      {/* Status Stage Text Ticker */}
      {stageText && (
        <div className="mt-4 px-4 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs font-mono text-slate-300 flex items-center gap-2 shadow-lg">
          <span className="w-2 h-2 rounded-full bg-accent-cyan animate-ping" />
          <span>{stageText}</span>
        </div>
      )}
    </div>
  );
};
