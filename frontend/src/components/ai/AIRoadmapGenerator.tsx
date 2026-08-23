import React, { useState, useEffect } from 'react';
import { Roadmap, RoadmapItem, StudentSkill } from '../../types';
import { AICoreOrb } from './AICoreOrb';
import {
  Sparkles,
  Check,
  Award,
  Compass,
  CheckCircle2,
} from 'lucide-react';

interface AIRoadmapGeneratorProps {
  roadmap: Roadmap | null;
  skills: StudentSkill[];
  generating: boolean;
  onCompleteItem: (itemId: string) => void;
  completingItemId: string | null;
  onGenerateNew: () => void;
}

export const AIRoadmapGenerator: React.FC<AIRoadmapGeneratorProps> = ({
  roadmap,
  skills,
  generating,
  onCompleteItem,
  completingItemId,
  onGenerateNew,
}) => {
  const [revealedNodesCount, setRevealedNodesCount] = useState<number>(0);
  const [synthesisStage, setSynthesisStage] = useState<number>(0);

  const synthesisStages = [
    'Analyzing evaluated weaknesses and draft gap deductions...',
    'Traversing statutory curriculum concepts & learning standards...',
    'Calibrating personalized 5-phase milestone trajectory...',
    'Synthesizing practice targets & mastery certifications...',
  ];

  // Progressive generation loading animation
  useEffect(() => {
    if (generating) {
      setRevealedNodesCount(0);
      setSynthesisStage(0);
      const stageInterval = setInterval(() => {
        setSynthesisStage((prev) => (prev < synthesisStages.length - 1 ? prev + 1 : prev));
      }, 800);
      return () => clearInterval(stageInterval);
    }
  }, [generating]);

  // Progressive reveal of actual roadmap items when response arrives
  useEffect(() => {
    if (roadmap && !generating) {
      const items = roadmap.roadmap_items || [];
      setRevealedNodesCount(0);
      let count = 0;
      const revealInterval = setInterval(() => {
        count += 1;
        setRevealedNodesCount(count);
        if (count >= items.length) {
          clearInterval(revealInterval);
        }
      }, 200);
      return () => clearInterval(revealInterval);
    }
  }, [roadmap, generating]);

  const items = roadmap?.roadmap_items || [];
  const completedCount = items.filter((i) => i.is_completed).length;
  const progressPercent = items.length > 0 ? (completedCount / items.length) * 100 : 0;

  return (
    <div className="space-y-8 animate-fade-in font-sans">
      {/* If Generating: 3D AI Core Universe Generation State */}
      {generating ? (
        <div className="glass-panel-glow p-8 sm:p-12 rounded-[2.5rem] border border-primary-500/40 text-center space-y-6 shadow-2xl relative overflow-hidden">
          <div className="absolute -top-32 -left-32 w-80 h-80 bg-primary-600/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-32 -right-32 w-80 h-80 bg-accent-amber/20 rounded-full blur-3xl pointer-events-none" />

          <AICoreOrb size="lg" stageText={synthesisStages[synthesisStage]} />

          <div className="max-w-md mx-auto space-y-3 pt-2">
            <h3 className="text-xl font-bold text-white tracking-tight">
              Synthesizing 5-Phase Personalized Curriculum
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              DraftForge AI is dynamically organizing your drafting trajectory based on verified evaluation findings.
            </p>
          </div>
        </div>
      ) : roadmap ? (
        /* Roadmap View with 3D Progressive Nodes */
        <div className="space-y-6">
          {/* Header Card with Progress Gauge */}
          <div className="glass-panel-glow p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6 relative overflow-hidden">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 uppercase tracking-wider font-mono">
                    Personalized 5-Phase Track
                  </span>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                    Active Curriculum
                  </span>
                </div>
                <h2 className="text-2xl font-extrabold text-white tracking-tight">
                  {roadmap.title}
                </h2>
                <p className="text-xs text-slate-400">
                  Calibrated to elevate your weakest statutory clauses and jurat structures to commercial mastery.
                </p>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <span className="text-xs text-slate-400 font-medium block">Curriculum Completion</span>
                  <span className="text-2xl font-extrabold text-accent-cyan font-mono">
                    {Math.round(progressPercent)}%
                  </span>
                </div>

                <button
                  onClick={onGenerateNew}
                  className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-bold rounded-xl border border-slate-800 hover:border-slate-700 transition-all flex items-center gap-2"
                >
                  <Sparkles className="w-3.5 h-3.5 text-primary-400" />
                  <span>Resynthesize</span>
                </button>
              </div>
            </div>

            {/* Overall Progress Bar */}
            <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-primary-500 via-indigo-500 to-accent-cyan rounded-full transition-all duration-700 shadow-glow"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          {/* 5-Phase Progressive Materialized Nodes Timeline */}
          <div className="space-y-4 relative">
            {/* SVG Connecting Track Line */}
            <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-gradient-to-b from-primary-500 via-indigo-500 to-accent-cyan hidden sm:block opacity-40" />

            {items.map((item: RoadmapItem, idx: number) => {
              const isRevealed = idx < revealedNodesCount;
              const isCompleted = item.is_completed;
              const isCompleting = completingItemId === item.id;

              return (
                <div
                  key={item.id}
                  className={`transition-all duration-500 transform ${
                    isRevealed
                      ? 'opacity-100 translate-y-0'
                      : 'opacity-0 translate-y-4 pointer-events-none'
                  }`}
                >
                  <div
                    className={`relative p-5 sm:p-6 rounded-3xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                      isCompleted
                        ? 'bg-emerald-950/20 border-emerald-500/40 shadow-md shadow-emerald-500/5'
                        : 'glass-panel border-slate-800 hover:border-primary-500/40'
                    }`}
                  >
                    {/* Left Phase Badge & Description */}
                    <div className="flex items-start gap-4">
                      {/* Node Icon Avatar */}
                      <div
                        className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-sm shrink-0 shadow-lg ${
                          isCompleted
                            ? 'bg-emerald-500 text-white shadow-emerald-500/25'
                            : 'bg-slate-900 border border-slate-800 text-primary-400'
                        }`}
                      >
                        {isCompleted ? (
                          <Check className="w-6 h-6 stroke-[3]" />
                        ) : (
                          <span className="font-mono text-sm font-extrabold">{item.phase_number}</span>
                        )}
                      </div>

                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                            Phase {item.phase_number}
                          </span>
                          {isCompleted && (
                            <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider font-mono">
                              ✓ Completed
                            </span>
                          )}
                        </div>

                        <h3 className="font-extrabold text-base text-white tracking-tight">
                          {item.title}
                        </h3>

                        {item.description && (
                          <p className="text-xs text-slate-300 leading-relaxed max-w-2xl font-sans">
                            {item.description}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Right Check-off Action Button */}
                    <div className="flex items-center gap-3 self-end sm:self-center shrink-0">
                      {!isCompleted ? (
                        <button
                          onClick={() => onCompleteItem(item.id)}
                          disabled={isCompleting}
                          className="px-4 py-2 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-primary-500/20 transition-all disabled:opacity-50 flex items-center gap-1.5"
                        >
                          {isCompleting ? (
                            <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <CheckCircle2 className="w-4 h-4" />
                          )}
                          <span>Mark Phase Complete</span>
                        </button>
                      ) : (
                        <div className="text-[11px] font-mono text-emerald-400 font-semibold px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-1.5">
                          <Award className="w-3.5 h-3.5" />
                          <span>Milestone Achieved</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Bottom Skill Mastery Matrix Ribbon */}
          {skills.length > 0 && (
            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
              <div className="flex items-center gap-2">
                <Compass className="w-4 h-4 text-accent-cyan" />
                <h3 className="font-bold text-sm text-white">Target Skill Matrices</h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {skills.slice(0, 6).map((sk) => (
                  <div
                    key={sk.id}
                    className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/80 flex items-center justify-between"
                  >
                    <div>
                      <h4 className="font-bold text-xs text-white truncate max-w-[170px]">
                        {sk.skill?.name || 'Legal Drafting'}
                      </h4>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {sk.skill?.category || 'General'}
                      </span>
                    </div>

                    <span className="font-mono text-xs font-bold text-emerald-400">
                      {Math.round(sk.proficiency_score)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Empty Roadmap State */
        <div className="glass-panel p-12 rounded-3xl border border-slate-800 text-center space-y-5 max-w-md mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-primary-600/10 border border-primary-500/30 flex items-center justify-center mx-auto text-primary-400 shadow-xl shadow-primary-500/10">
            <Compass className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">No Active Learning Roadmap</h3>
            <p className="text-xs text-slate-400">
              Synthesize a tailored 5-phase statutory drafting trajectory based on your latest draft evaluations.
            </p>
          </div>
          <button
            onClick={onGenerateNew}
            className="w-full py-3 bg-gradient-to-r from-primary-600 to-indigo-600 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary-500/25 flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>Generate 5-Phase Roadmap</span>
          </button>
        </div>
      )}
    </div>
  );
};
