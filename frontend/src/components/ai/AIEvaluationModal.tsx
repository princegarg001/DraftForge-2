import React, { useState, useEffect } from 'react';
import { Evaluation } from '../../types';
import { AICoreOrb } from './AICoreOrb';
import {
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowRight,
  X,
  FileText,
  Network,
  GraduationCap,
} from 'lucide-react';

interface AIEvaluationModalProps {
  isOpen: boolean;
  onClose: () => void;
  evaluation: Evaluation | null;
  evaluating: boolean;
  draftTitle?: string;
  draftContent?: string;
  onNavigateToLoopholes?: (evalId: string) => void;
  onNavigateToRoadmap?: () => void;
  onViewDetailedEvidence?: () => void;
}

export const AIEvaluationModal: React.FC<AIEvaluationModalProps> = ({
  isOpen,
  onClose,
  evaluation,
  evaluating,
  draftTitle = 'Legal Draft',
  draftContent = '',
  onNavigateToLoopholes,
  onNavigateToRoadmap,
  onViewDetailedEvidence,
}) => {
  const [loadingStage, setLoadingStage] = useState(0);
  const [animatedScore, setAnimatedScore] = useState(0);

  const stages = [
    'Parsing statutory demarcations & recitals...',
    'Generating 384-dimensional FastEmbed vectors...',
    'Matching semantic clauses against Qdrant gold standards...',
    'Traversing Neo4j Aura graph prerequisite dependencies...',
    'Executing mathematical 100-point rubric calculation...',
  ];

  // Cycle through decorative loading stages while evaluating
  useEffect(() => {
    if (evaluating) {
      setAnimatedScore(0);
      setLoadingStage(0);
      const interval = setInterval(() => {
        setLoadingStage((prev) => (prev < stages.length - 1 ? prev + 1 : prev));
      }, 700);
      return () => clearInterval(interval);
    }
  }, [evaluating]);

  // Score count-up reveal animation when real evaluation arrives
  useEffect(() => {
    if (evaluation && !evaluating) {
      const targetScore = evaluation.is_overridden && evaluation.overridden_score !== null
        ? evaluation.overridden_score
        : evaluation.overall_score;

      let current = 0;
      const step = Math.max(1, Math.floor(targetScore / 30));
      const timer = setInterval(() => {
        current += step;
        if (current >= targetScore) {
          setAnimatedScore(targetScore);
          clearInterval(timer);
        } else {
          setAnimatedScore(current);
        }
      }, 25);
      return () => clearInterval(timer);
    }
  }, [evaluation, evaluating]);

  if (!isOpen) return null;

  const effectiveScore = evaluation
    ? evaluation.is_overridden && evaluation.overridden_score !== null
      ? evaluation.overridden_score
      : evaluation.overall_score
    : 0;

  const scoreColor =
    effectiveScore >= 75
      ? 'text-emerald-400'
      : effectiveScore >= 50
      ? 'text-amber-400'
      : 'text-rose-400';

  const strokeColor =
    effectiveScore >= 75
      ? '#10b981'
      : effectiveScore >= 50
      ? '#f59e0b'
      : '#f43f5e';

  const maxScore = evaluation?.max_score || 100;
  const circumference = 2 * Math.PI * 46;
  const strokeDashoffset = circumference - (animatedScore / maxScore) * circumference;

  const passCount = evaluation?.evidence_items?.filter((i) => i.status === 'PASS').length || 0;
  const warningCount = evaluation?.evidence_items?.filter((i) => i.status === 'WARNING' || i.status === 'PARTIAL').length || 0;
  const failCount = evaluation?.evidence_items?.filter((i) => i.status === 'FAIL').length || 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/90 backdrop-blur-2xl animate-fade-in overflow-y-auto">
      {/* Modal Container */}
      <div className="relative w-full max-w-5xl glass-panel-glow p-6 sm:p-10 rounded-[2.5rem] border border-slate-700/80 shadow-2xl space-y-8 my-auto overflow-hidden animate-scale-in">
        {/* Ambient Radial Background Glows */}
        <div className="absolute -top-32 -left-32 w-80 h-80 bg-primary-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -right-32 w-80 h-80 bg-accent-cyan/20 rounded-full blur-3xl pointer-events-none" />

        {/* Top Modal Chrome */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-primary-600 to-accent-cyan p-0.5 shadow-lg shadow-primary-500/25">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-accent-cyan" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-extrabold text-base sm:text-lg text-white tracking-tight">
                  Deterministic AI Evaluation Engine
                </h3>
                <span className="px-2.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-primary-500/10 text-primary-300 border border-primary-500/20">
                  Rubric v1.0
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                {draftTitle} • Grounded in Qdrant & Neo4j
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Evaluating State: 3D AI Core + Document Scanning Laser */}
        {evaluating ? (
          <div className="py-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
            {/* Left 6 Cols: Central 3D AI Core */}
            <div className="lg:col-span-6 flex flex-col items-center justify-center space-y-6">
              <AICoreOrb size="lg" stageText={stages[loadingStage]} />

              {/* Progress Step Nodes */}
              <div className="w-full max-w-sm space-y-2 pt-2">
                {stages.map((stage, idx) => {
                  const isDone = idx < loadingStage;
                  const isCurrent = idx === loadingStage;
                  return (
                    <div
                      key={idx}
                      className={`flex items-center gap-2.5 text-xs font-mono transition-all ${
                        isDone
                          ? 'text-emerald-400'
                          : isCurrent
                          ? 'text-accent-cyan font-bold scale-105'
                          : 'text-slate-600'
                      }`}
                    >
                      <span className={`w-2 h-2 rounded-full ${isDone ? 'bg-emerald-400' : isCurrent ? 'bg-accent-cyan animate-ping' : 'bg-slate-800'}`} />
                      <span className="truncate">{stage}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right 6 Cols: 3D Document with Sweeping Laser Scan Line */}
            <div className="lg:col-span-6">
              <div className="relative rounded-3xl bg-slate-950/95 border border-slate-800 p-6 font-mono text-xs text-slate-300 leading-relaxed overflow-hidden shadow-2xl perspective-1000 hero-3d-card max-h-[360px]">
                {/* Active Laser Scanning Beam */}
                <div className="laser-scan-line animate-scan" />

                <div className="text-center pb-2 mb-3 border-b border-slate-800/80">
                  <span className="text-[10px] font-bold text-primary-400 uppercase tracking-widest block">
                    ACTIVE STATUTORY SCAN
                  </span>
                  <p className="text-xs text-white font-bold truncate">{draftTitle}</p>
                </div>

                <div className="space-y-2 text-[11px] text-slate-400 leading-relaxed max-h-[240px] overflow-hidden opacity-80 select-none">
                  {draftContent ? (
                    <p className="whitespace-pre-wrap">{draftContent.slice(0, 500)}...</p>
                  ) : (
                    <>
                      <p className="text-slate-300">1. IDENTIFICATION & AGE: I, the deponent, solemnly affirm...</p>
                      <p className="text-slate-300">2. OPERATIVE COVENANTS: That all declarations made herein are true...</p>
                      <p className="text-slate-300">3. VERIFICATION JURAT: Verified under the Indian Evidence Act...</p>
                      <p className="text-slate-400">4. DISPUTE RESOLUTION: Subject to competent jurisdiction...</p>
                    </>
                  )}
                </div>

                <div className="mt-4 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span>FastEmbed Tokenizer</span>
                  <span className="text-emerald-400 animate-pulse">Scanning Active</span>
                </div>
              </div>
            </div>
          </div>
        ) : evaluation ? (
          /* Real Evaluation Results: Cinematic Score Reveal */
          <div className="space-y-8 relative z-10 animate-fade-in">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              {/* Left 5 Cols: 3D Animated Score Reveal Gauge */}
              <div className="lg:col-span-5 glass-panel p-8 rounded-3xl border border-slate-800 text-center space-y-4">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block font-mono">
                  Deterministic Score Result
                </span>

                <div className="relative w-40 h-40 mx-auto flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 108 108">
                    <circle cx="54" cy="54" r="46" stroke="#1e293b" strokeWidth="8" fill="transparent" />
                    <circle
                      cx="54"
                      cy="54"
                      r="46"
                      stroke={strokeColor}
                      strokeWidth="8"
                      fill="transparent"
                      strokeDasharray={circumference}
                      strokeDashoffset={strokeDashoffset}
                      strokeLinecap="round"
                      className="transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-4xl font-extrabold font-mono tracking-tight ${scoreColor}`}>
                      {animatedScore}
                    </span>
                    <span className="text-xs text-slate-400 font-bold uppercase">
                      / {maxScore} pts
                    </span>
                  </div>
                </div>

                <div className="pt-2">
                  <span
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono ${
                      effectiveScore >= 75
                        ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                        : effectiveScore >= 50
                        ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                        : 'bg-rose-500/10 text-rose-300 border border-rose-500/30'
                    }`}
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>{effectiveScore >= 75 ? 'Statutory Compliant' : effectiveScore >= 50 ? 'Revision Advised' : 'High Risk Gaps'}</span>
                  </span>
                </div>
              </div>

              {/* Right 7 Cols: 4-Pillar Score Breakdown & Summary */}
              <div className="lg:col-span-7 space-y-4">
                <div className="grid grid-cols-2 gap-3.5">
                  <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <span className="text-[11px] font-semibold text-slate-400">Structure & Demarcation</span>
                    <p className="text-xl font-extrabold text-white font-mono">{evaluation.structure_score} / 25 pts</p>
                    <span className="text-[10px] text-emerald-400 font-mono">Title, recitals & numbering</span>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <span className="text-[11px] font-semibold text-slate-400">Clause Coverage</span>
                    <p className="text-xl font-extrabold text-primary-400 font-mono">{evaluation.clause_score} / 50 pts</p>
                    <span className="text-[10px] text-primary-300 font-mono">Semantic precedent matching</span>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <span className="text-[11px] font-semibold text-slate-400">Formatting & Jurats</span>
                    <p className="text-xl font-extrabold text-accent-cyan font-mono">{evaluation.formatting_score} / 25 pts</p>
                    <span className="text-[10px] text-accent-cyan font-mono">Oath affirmation & stamps</span>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
                    <span className="text-[11px] font-semibold text-slate-400">Contradiction Penalty</span>
                    <p className="text-xl font-extrabold text-rose-400 font-mono">-{evaluation.gap_penalty} pts</p>
                    <span className="text-[10px] text-rose-300 font-mono">Restraints & statutory gaps</span>
                  </div>
                </div>

                {/* Evidence Summary Counters */}
                <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 flex items-center justify-around text-center text-xs font-mono">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Validated Items</span>
                    <span className="text-emerald-400 font-bold text-base flex items-center justify-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> {passCount} PASS
                    </span>
                  </div>
                  <div className="h-8 w-px bg-slate-800" />
                  <div>
                    <span className="text-slate-400 block text-[10px]">Advisory Warnings</span>
                    <span className="text-amber-400 font-bold text-base flex items-center justify-center gap-1">
                      <AlertTriangle className="w-3.5 h-3.5" /> {warningCount} WARN
                    </span>
                  </div>
                  <div className="h-8 w-px bg-slate-800" />
                  <div>
                    <span className="text-slate-400 block text-[10px]">Critical Gaps</span>
                    <span className="text-rose-400 font-bold text-base flex items-center justify-center gap-1">
                      <XCircle className="w-3.5 h-3.5" /> {failCount} FAIL
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Next Action Gateway Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-6 border-t border-slate-800/80">
              <button
                onClick={() => {
                  onClose();
                  if (onViewDetailedEvidence) onViewDetailedEvidence();
                }}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-bold border border-slate-800 transition-all flex items-center justify-center gap-2"
              >
                <FileText className="w-4 h-4 text-primary-400" />
                <span>Inspect Evidence Findings ({evaluation.evidence_items?.length || 0})</span>
              </button>

              <div className="flex items-center gap-3 w-full sm:w-auto">
                {onNavigateToLoopholes && (
                  <button
                    onClick={() => {
                      onClose();
                      onNavigateToLoopholes(evaluation.id);
                    }}
                    className="flex-1 sm:flex-none px-5 py-2.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 text-xs font-bold rounded-xl border border-rose-500/30 transition-all flex items-center justify-center gap-2"
                  >
                    <Network className="w-4 h-4 text-rose-400" />
                    <span>Neo4j Graph Loopholes</span>
                  </button>
                )}

                {onNavigateToRoadmap && (
                  <button
                    onClick={() => {
                      onClose();
                      onNavigateToRoadmap();
                    }}
                    className="flex-1 sm:flex-none px-6 py-2.5 bg-gradient-to-r from-primary-600 via-indigo-600 to-accent-cyan hover:from-primary-500 hover:to-accent-cyan text-white text-xs font-bold rounded-xl shadow-lg shadow-primary-500/25 transition-all flex items-center justify-center gap-2"
                  >
                    <GraduationCap className="w-4 h-4" />
                    <span>Synthesize 5-Phase Roadmap</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
