import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Evaluation, Draft, ExplainEvaluationResponse } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import { AIEvaluationModal } from '../ai/AIEvaluationModal';
import {
  AlertTriangle,
  XCircle,
  CheckCircle2,
  Sparkles,
  BookOpen,
  FileText,
  ShieldAlert,
  ArrowRight,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface EvaluationCardProps {
  evaluationId?: string;
  onNavigateToLoopholes?: (evalId: string) => void;
  onNavigateToTutor?: (draftId?: string) => void;
  onNavigateToWorkspace?: () => void;
}

export const EvaluationCard: React.FC<EvaluationCardProps> = ({
  evaluationId: initialEvalId,
  onNavigateToLoopholes,
  onNavigateToTutor,
  onNavigateToWorkspace,
}) => {
  const { showToast } = useToast();
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [loading, setLoading] = useState(false);
  const [explanationData, setExplanationData] = useState<ExplainEvaluationResponse | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [evaluating, setEvaluating] = useState(false);
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'PASS' | 'PARTIAL' | 'FAIL' | 'WARNING'>('ALL');
  const [expandedFindings, setExpandedFindings] = useState<Record<number, boolean>>({});

  // 3D AI Modal State
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [activeDraftTitle, setActiveDraftTitle] = useState('');
  const [activeDraftContent, setActiveDraftContent] = useState('');

  const fetchEval = async (id: string) => {
    setLoading(true);
    try {
      const res = await api.getEvaluation(id);
      setEvaluation(res.data);
      if (res.data.llm_explanation) {
        setExplanationData({
          evaluation_id: res.data.id,
          explanation: res.data.llm_explanation,
          remedial_suggestions: [],
        });
      } else {
        setExplanationData(null);
      }
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to load evaluation details', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialEvalId && initialEvalId.trim() !== '') {
      fetchEval(initialEvalId);
    } else {
      api
        .getDrafts()
        .then((res) => {
          setDrafts(res.data || []);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }
  }, [initialEvalId]);

  const handleEvaluateDraft = async (draft: Draft) => {
    setActiveDraftTitle(draft.title);
    const versions = draft.versions || [];
    const latestContent = versions.length > 0 ? versions[versions.length - 1].raw_content : '';
    setActiveDraftContent(latestContent);
    setIsAiModalOpen(true);
    setEvaluating(true);

    try {
      const res = await api.evaluateDraft(draft.id);
      setEvaluation(res.data);
      showToast('Deterministic RAG Evaluation Completed!', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Evaluation failed to complete', 'error');
      setIsAiModalOpen(false);
    } finally {
      setEvaluating(false);
    }
  };

  const handleRequestExplanation = async () => {
    if (!evaluation) return;
    setExplaining(true);
    try {
      const res = await api.explainEvaluation(evaluation.id);
      setExplanationData(res.data);
      showToast('AI synthesized pedagogical explanation', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to generate explanation', 'error');
    } finally {
      setExplaining(false);
    }
  };

  const toggleFindingExpand = (index: number) => {
    setExpandedFindings((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <LoadingSpinner size="xl" label="Verifying draft against statutory rubrics & Qdrant..." />
      </div>
    );
  }

  // If no evaluation selected yet, show available drafts selector
  if (!evaluation) {
    return (
      <div className="space-y-6">
        <div className="glass-panel p-8 sm:p-12 rounded-3xl border border-slate-800 space-y-6 text-center max-w-xl mx-auto animate-fade-in-up">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-primary-600 to-indigo-600 flex items-center justify-center mx-auto shadow-xl shadow-primary-500/20">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Select a Draft for Deterministic Evaluation
            </h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Choose an existing draft from your workspace to run rule-based rubric checks, scanning laser sweeps, and evidence findings.
            </p>
          </div>

          {drafts.length > 0 ? (
            <div className="space-y-2.5 text-left pt-2">
              {drafts.map((d) => (
                <div
                  key={d.id}
                  onClick={() => handleEvaluateDraft(d)}
                  className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-primary-500/50 cursor-pointer flex items-center justify-between transition-all group"
                >
                  <div>
                    <span className="font-bold text-xs text-white group-hover:text-primary-300 transition-colors">
                      {d.title}
                    </span>
                    <span className="block text-[10px] text-slate-400 font-mono mt-0.5">
                      {d.document_type.replace(/_/g, ' ')} • {d.versions?.length || 1} Revisions
                    </span>
                  </div>
                  <button className="px-3.5 py-1.5 bg-primary-600 group-hover:bg-primary-500 text-white rounded-xl text-xs font-bold shadow transition-all flex items-center gap-1">
                    <span>Evaluate</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 bg-slate-900/60 rounded-2xl border border-slate-800 text-xs text-slate-400 space-y-3">
              <p>No drafts found in your workspace.</p>
              {onNavigateToWorkspace && (
                <button
                  onClick={onNavigateToWorkspace}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-xs font-bold rounded-xl shadow transition-all"
                >
                  Create Your First Draft
                </button>
              )}
            </div>
          )}
        </div>

        {/* 3D AI Evaluation Modal */}
        <AIEvaluationModal
          isOpen={isAiModalOpen}
          onClose={() => setIsAiModalOpen(false)}
          evaluation={evaluation}
          evaluating={evaluating}
          draftTitle={activeDraftTitle}
          draftContent={activeDraftContent}
          onNavigateToLoopholes={onNavigateToLoopholes}
        />
      </div>
    );
  }

  const effectiveScore = evaluation.is_overridden && evaluation.overridden_score !== null
    ? evaluation.overridden_score
    : evaluation.overall_score;

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

  const circumference = 2 * Math.PI * 42;
  const strokeDashoffset = circumference - (effectiveScore / evaluation.max_score) * circumference;

  const filteredEvidence = (evaluation.evidence_items || []).filter((item) => {
    if (activeFilter === 'ALL') return true;
    return item.status === activeFilter;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header Card with Circular Gauge & Score Breakdown */}
      <div className="glass-panel-glow p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          {/* Circular Score Gauge */}
          <div className="flex items-center gap-6">
            <div className="relative w-28 h-28 flex items-center justify-center shrink-0">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  stroke="#1e293b"
                  strokeWidth="8"
                  fill="transparent"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="42"
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
                <span className={`text-2xl font-extrabold tracking-tight ${scoreColor}`}>
                  {effectiveScore.toFixed(0)}
                </span>
                <span className="text-[10px] font-semibold text-slate-400">
                  / {evaluation.max_score}
                </span>
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
                  Deterministic Audit
                </span>
                {evaluation.is_overridden && (
                  <span className="px-2 py-0.5 rounded-md text-[9px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/20 uppercase tracking-wider font-mono">
                    Faculty Overridden
                  </span>
                )}
              </div>
              <h2 className="text-xl font-extrabold text-white tracking-tight">
                Draft Quality Score
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                Rubric Standard: {evaluation.rubric_version} • Evaluated on{' '}
                {new Date(evaluation.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Quick Action Navigation Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            {onNavigateToLoopholes && (
              <button
                onClick={() => onNavigateToLoopholes(evaluation.id)}
                className="flex items-center gap-2 px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 rounded-xl text-xs font-bold border border-rose-500/20 transition-all shadow-sm"
              >
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                <span>Neo4j Graph Loopholes</span>
              </button>
            )}

            {onNavigateToTutor && (
              <button
                onClick={() => onNavigateToTutor()}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 rounded-xl text-xs font-bold border border-indigo-500/20 transition-all"
              >
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <span>Ask Socratic Tutor</span>
              </button>
            )}
          </div>
        </div>

        {/* 4 Score Breakdown Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-slate-800/80">
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[11px] font-semibold text-slate-400">Structure & Demarcation</span>
            <p className="text-xl font-bold text-white font-mono">{evaluation.structure_score} pts</p>
            <span className="text-[10px] text-slate-500 block">Title, recitals & numbered averments</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[11px] font-semibold text-slate-400">Clause Coverage</span>
            <p className="text-xl font-bold text-white font-mono">{evaluation.clause_score} pts</p>
            <span className="text-[10px] text-slate-500 block">Qdrant vector matched clauses</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[11px] font-semibold text-slate-400">Formatting & Jurats</span>
            <p className="text-xl font-bold text-white font-mono">{evaluation.formatting_score} pts</p>
            <span className="text-[10px] text-slate-500 block">Oaths, verification & stamps</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[11px] font-semibold text-slate-400">Contradiction Penalty</span>
            <p className="text-xl font-bold text-rose-400 font-mono">-{evaluation.gap_penalty} pts</p>
            <span className="text-[10px] text-slate-500 block">Deducted for legal inconsistencies</span>
          </div>
        </div>
      </div>

      {/* AI Pedagogical Explanation Panel */}
      <div className="glass-panel p-6 rounded-3xl border border-primary-500/30 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center text-primary-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white">AI Pedagogical Explanation</h3>
              <p className="text-xs text-slate-400">
                Evidence-grounded rationale explaining statutory strengths and errors
              </p>
            </div>
          </div>

          <button
            onClick={handleRequestExplanation}
            disabled={explaining}
            className="px-4 py-1.5 bg-primary-600 hover:bg-primary-500 text-white rounded-xl text-xs font-bold shadow-md shadow-primary-500/20 transition-all disabled:opacity-50 flex items-center gap-1.5"
          >
            {explaining ? <LoadingSpinner size="sm" /> : <Sparkles className="w-3.5 h-3.5" />}
            <span>{explanationData ? 'Regenerate Narrative' : 'Explain My Score'}</span>
          </button>
        </div>

        {explanationData ? (
          <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-3 animate-fade-in">
            <div className="text-xs text-slate-200 whitespace-pre-wrap leading-relaxed font-sans">
              {explanationData.explanation}
            </div>

            {explanationData.remedial_suggestions?.length > 0 && (
              <div className="pt-2 border-t border-slate-800 space-y-1.5">
                <span className="text-[10px] font-bold text-accent-cyan uppercase tracking-wider font-mono">
                  Remedial Statutory Recommendations:
                </span>
                <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                  {explanationData.remedial_suggestions.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <p className="text-xs text-slate-400 bg-slate-950/50 p-3.5 rounded-xl border border-slate-800/80">
            Click &ldquo;Explain My Score&rdquo; to receive an AI-generated pedagogical breakdown with statutory citations.
          </p>
        )}
      </div>

      {/* Granular Evidence Findings */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">
              Itemized Evidence Findings ({evaluation.evidence_items?.length || 0})
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Audited against gold-standard statutory legal reference corpus
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 p-1 bg-slate-900 rounded-xl border border-slate-800 overflow-x-auto">
            {(['ALL', 'PASS', 'PARTIAL', 'FAIL', 'WARNING'] as const).map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                  activeFilter === filter
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        {/* Findings List */}
        <div className="space-y-3.5">
          {filteredEvidence.length === 0 ? (
            <div className="py-8 text-center text-slate-500 text-xs">
              No evidence findings matching filter "{activeFilter}".
            </div>
          ) : (
            filteredEvidence.map((item, idx) => {
              const isPass = item.status === 'PASS';
              const isPartial = item.status === 'PARTIAL';
              const isFail = item.status === 'FAIL';
              const isWarning = item.status === 'WARNING';
              const isExpanded = !!expandedFindings[idx];

              return (
                <div
                  key={idx}
                  className={`p-4 sm:p-5 rounded-2xl border transition-all ${
                    isPass
                      ? 'bg-emerald-950/20 border-emerald-500/30'
                      : isPartial
                      ? 'bg-amber-950/20 border-amber-500/30'
                      : isWarning
                      ? 'bg-rose-950/30 border-rose-500/40 shadow-sm'
                      : 'bg-rose-950/20 border-rose-500/30'
                  }`}
                >
                  <div
                    onClick={() => toggleFindingExpand(idx)}
                    className="flex items-center justify-between cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      {isPass && <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />}
                      {isPartial && <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />}
                      {(isFail || isWarning) && <XCircle className="w-5 h-5 text-rose-400 shrink-0" />}

                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-700">
                            {item.category}
                          </span>
                          <h4 className="font-bold text-xs sm:text-sm text-white">
                            {item.criterion}
                          </h4>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono font-bold text-white">
                        {item.score} / {item.max_score} pts
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider font-mono ${
                          isPass
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : isPartial
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        }`}
                      >
                        {item.status}
                      </span>
                      <button className="text-slate-400 hover:text-white">
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 mt-2.5 leading-relaxed">{item.explanation}</p>

                  {/* Expanded Evidence Details */}
                  {isExpanded && (
                    <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-3 animate-fade-in">
                      {item.student_evidence && (
                        <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-xs space-y-1">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">
                            Student Draft Excerpt:
                          </span>
                          <p className="font-mono text-[11px] text-slate-200 whitespace-pre-wrap">
                            "{item.student_evidence}"
                          </p>
                        </div>
                      )}

                      {item.reference_evidence && (
                        <div className="p-3.5 bg-primary-950/20 rounded-xl border border-primary-500/20 text-xs space-y-1.5">
                          <div className="flex items-center justify-between text-primary-400 font-semibold text-[11px]">
                            <div className="flex items-center gap-1.5">
                              <BookOpen className="w-3.5 h-3.5" />
                              <span>
                                Gold Standard: {item.source_document || 'Reference Corpus'}
                              </span>
                            </div>
                            <span className="font-mono">Page {item.source_page || 1} • {item.source_section || 'General'}</span>
                          </div>
                          <p className="text-slate-200 font-mono text-[11px] leading-relaxed">
                            "{item.reference_evidence}"
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* 3D AI Evaluation Modal */}
      <AIEvaluationModal
        isOpen={isAiModalOpen}
        onClose={() => setIsAiModalOpen(false)}
        evaluation={evaluation}
        evaluating={evaluating}
        draftTitle={activeDraftTitle}
        draftContent={activeDraftContent}
        onNavigateToLoopholes={onNavigateToLoopholes}
      />
    </div>
  );
};