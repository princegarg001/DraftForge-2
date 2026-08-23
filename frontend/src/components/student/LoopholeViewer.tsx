import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { LoopholeReport, Draft } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import {
  ShieldAlert,
  ArrowRight,
  AlertOctagon,
  CheckCircle2,
  Sparkles,
  Network,
  BookOpen,
  Share2,
} from 'lucide-react';

interface LoopholeViewerProps {
  evaluationId?: string;
  onNavigateToWorkspace?: () => void;
  onNavigateToTutor?: () => void;
}

export const LoopholeViewer: React.FC<LoopholeViewerProps> = ({
  evaluationId: initialEvalId,
  onNavigateToWorkspace,
}) => {
  const { showToast } = useToast();
  const [report, setReport] = useState<LoopholeReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [severityFilter, setSeverityFilter] = useState<'ALL' | 'HIGH' | 'MEDIUM' | 'LOW'>('ALL');
  const [selectedNodeIndex, setSelectedNodeIndex] = useState<number | null>(null);

  const fetchLoopholes = async (id: string) => {
    setLoading(true);
    try {
      const res = await api.getLoopholes(id);
      setReport(res.data);
      if (res.data.loopholes?.length > 0) {
        setSelectedNodeIndex(0);
      }
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Error fetching graph loopholes', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialEvalId && initialEvalId.trim() !== '') {
      fetchLoopholes(initialEvalId);
    } else {
      setLoading(true);
      api
        .getDrafts()
        .then((res) => {
          setDrafts(res.data || []);
        })
        .catch((err) => {
          console.error(err);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [initialEvalId]);

  const handleEvaluateAndAnalyze = async (draftId: string) => {
    setAnalyzing(true);
    try {
      const evalRes = await api.evaluateDraft(draftId);
      await fetchLoopholes(evalRes.data.id);
      showToast('Neo4j Graph Traversal & Risk Audit Completed!', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Graph analysis failed', 'error');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading || analyzing) {
    return (
      <div className="py-24 flex justify-center">
        <LoadingSpinner size="xl" label="Traversing Neo4j Aura Graph Dependency Topology..." />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="glass-panel p-8 sm:p-12 rounded-3xl border border-slate-800 space-y-6 text-center max-w-xl mx-auto animate-fade-in-up">
        <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mx-auto text-rose-400">
          <Network className="w-8 h-8" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white tracking-tight">
            Select Draft for Neo4j Graph Loophole Analysis
          </h3>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Traverse dependency chains and identify missing prerequisite clauses, statutory risk exposures, and legal loopholes.
          </p>
        </div>

        {drafts.length > 0 ? (
          <div className="space-y-2.5 text-left pt-2">
            {drafts.map((d) => (
              <div
                key={d.id}
                onClick={() => handleEvaluateAndAnalyze(d.id)}
                className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-rose-500/50 cursor-pointer flex items-center justify-between transition-all group"
              >
                <div>
                  <span className="font-bold text-xs text-white group-hover:text-rose-300 transition-colors">
                    {d.title}
                  </span>
                  <span className="block text-[10px] text-slate-400 font-mono mt-0.5">
                    {d.document_type.replace(/_/g, ' ')} • {d.versions?.length || 1} Revisions
                  </span>
                </div>
                <button className="px-3.5 py-1.5 bg-rose-500/10 text-rose-300 group-hover:bg-rose-500/20 border border-rose-500/30 rounded-xl text-xs font-bold transition-all flex items-center gap-1">
                  <span>Audit Graph</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 bg-slate-900/60 rounded-2xl border border-slate-800 text-xs text-slate-400 space-y-3">
            <p>No drafts available for analysis.</p>
            {onNavigateToWorkspace && (
              <button
                onClick={onNavigateToWorkspace}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-xs font-bold rounded-xl shadow transition-all"
              >
                Create a Draft
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  const filteredLoopholes = report.loopholes.filter((lh) => {
    if (severityFilter === 'ALL') return true;
    return lh.severity === severityFilter;
  });

  const activeLoophole = selectedNodeIndex !== null && report.loopholes[selectedNodeIndex]
    ? report.loopholes[selectedNodeIndex]
    : report.loopholes[0];

  return (
    <div className="space-y-6 animate-fade-in font-sans">
      {/* Top Banner */}
      <div className="glass-panel-glow p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 shrink-0">
              <Network className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">
                  Neo4j Graph Reasoning
                </span>
                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20 font-mono">
                  {report.document_type}
                </span>
              </div>
              <h2 className="text-xl font-extrabold text-white tracking-tight mt-0.5">
                GraphRAG Structural Loophole Analysis
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-4 py-2 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-xs font-bold text-rose-300 font-mono">
              {report.high_severity_count} High Severity Risks
            </div>
            <div className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-2xl text-xs font-bold text-slate-200 font-mono">
              {report.total_loopholes} Total Gaps
            </div>
          </div>
        </div>

        {/* Severity Filter Tabs */}
        <div className="flex items-center gap-2 pt-2 border-t border-slate-800/80">
          <span className="text-xs text-slate-400 font-medium mr-2">Filter Severity:</span>
          {(['ALL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1 rounded-xl text-xs font-semibold transition-all ${
                severityFilter === sev
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Interactive 3D Graph Topology Visualizer (Only if loopholes exist) */}
      {report.loopholes.length > 0 && activeLoophole && (
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2">
              <Share2 className="w-4 h-4 text-accent-cyan" />
              <h3 className="font-bold text-sm text-white tracking-tight">
                Interactive Graph Knowledge Topology
              </h3>
            </div>
            <span className="text-[10px] font-mono text-slate-400">
              Traversed from Neo4j Aura Graph Database
            </span>
          </div>

          {/* SVG Knowledge Graph Visualizer */}
          <div className="relative rounded-2xl bg-slate-950 p-6 border border-slate-800/80 overflow-x-auto">
            <div className="min-w-[650px] flex items-center justify-between gap-4 relative py-8">
              {/* SVG Connecting Curves */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
                <path
                  d="M 100 70 C 180 70, 180 70, 260 70"
                  stroke="#6366f1"
                  strokeWidth="2"
                  strokeDasharray="4 4"
                  fill="none"
                  className="animate-pulse"
                />
                <path
                  d="M 370 70 C 440 70, 440 70, 520 70"
                  stroke="#f43f5e"
                  strokeWidth="2"
                  fill="none"
                />
              </svg>

              {/* Node 1: Contract Document Node */}
              <div className="relative z-10 p-4 rounded-2xl bg-slate-900 border border-primary-500/40 text-center shadow-lg w-44">
                <span className="text-[9px] font-mono font-bold text-primary-400 block uppercase">
                  DOCUMENT NODE
                </span>
                <span className="text-xs font-bold text-white block truncate mt-1">
                  {report.document_type.replace(/_/g, ' ')}
                </span>
                <span className="text-[9px] font-mono text-emerald-400 mt-1 block">
                  ● Tested Draft
                </span>
              </div>

              {/* Node 2: Missing Prerequisite Node */}
              <div className="relative z-10 p-4 rounded-2xl bg-rose-950/40 border border-rose-500/60 text-center shadow-xl w-48 animate-pulse-glow">
                <span className="text-[9px] font-mono font-bold text-rose-400 block uppercase">
                  MISSING PREREQUISITE
                </span>
                <span className="text-xs font-extrabold text-white block truncate mt-1">
                  {activeLoophole.prerequisite_clause_name || activeLoophole.related_clause_name || 'Clause Boundary'}
                </span>
                <span className="text-[9px] font-mono text-rose-300 mt-1 block">
                  ⚠ Unmet Dependency
                </span>
              </div>

              {/* Node 3: Risk Exposure & Skill Target Node */}
              <div className="relative z-10 p-4 rounded-2xl bg-slate-900 border border-amber-500/40 text-center shadow-lg w-48">
                <span className="text-[9px] font-mono font-bold text-amber-400 block uppercase">
                  EXPOSED RISK
                </span>
                <span className="text-xs font-bold text-white block truncate mt-1">
                  {activeLoophole.risk_name || 'Unmitigated Liability'}
                </span>
                <span className="text-[9px] font-mono text-indigo-300 mt-1 block truncate">
                  🎯 {activeLoophole.skill_name || 'Remedial Drafting'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loopholes Cards Grid */}
      {filteredLoopholes.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-3xl border border-slate-800 space-y-3">
          <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
          <h3 className="text-base font-bold text-white">No Gaps Detected</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            The draft satisfies all prerequisite structural nodes and unmitigated risk relationships in the knowledge graph.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredLoopholes.map((lh, idx) => {
            const isHigh = lh.severity === 'HIGH';
            const isMedium = lh.severity === 'MEDIUM';
            const isSelected = selectedNodeIndex === idx;

            return (
              <div
                key={idx}
                onClick={() => setSelectedNodeIndex(idx)}
                className={`glass-panel p-6 rounded-3xl border transition-all space-y-4 cursor-pointer ${
                  isSelected
                    ? 'ring-2 ring-primary-500 border-primary-500/50 shadow-2xl'
                    : isHigh
                    ? 'border-rose-500/30 bg-rose-950/10 hover:border-rose-500/50'
                    : isMedium
                    ? 'border-amber-500/30 bg-amber-950/10 hover:border-amber-500/50'
                    : 'border-slate-800 bg-slate-900/40 hover:border-slate-700'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                        isHigh
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      <ShieldAlert className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-sm text-white">{lh.title}</h4>
                      <span className="text-[10px] font-mono text-slate-400">
                        Gap Type: {lh.gap_type}
                      </span>
                    </div>
                  </div>

                  <span
                    className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider font-mono self-start sm:self-auto ${
                      isHigh
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : isMedium
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-slate-800 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {lh.severity} RISK
                  </span>
                </div>

                <p className="text-xs text-slate-200 leading-relaxed bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80">
                  {lh.educational_observation}
                </p>

                {/* Missing Dependency Graph Flow */}
                {lh.prerequisite_clause_name && (
                  <div className="flex flex-wrap items-center gap-2 p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono">
                    <span className="text-rose-400 font-semibold">{lh.related_clause_name}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                    <span className="text-slate-400">Missing Prerequisite Node:</span>
                    <span className="text-emerald-400 font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                      {lh.prerequisite_clause_name}
                    </span>
                  </div>
                )}

                {/* Risk & Skill Meta */}
                <div className="flex flex-wrap items-center gap-3 text-[11px]">
                  {lh.risk_name && (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300">
                      <AlertOctagon className="w-3.5 h-3.5" />
                      <span>Exposes: {lh.risk_name}</span>
                    </div>
                  )}

                  {lh.skill_name && (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-primary-500/10 border border-primary-500/20 text-primary-300">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Skill Target: {lh.skill_name}</span>
                    </div>
                  )}
                </div>

                {/* Actionable Reference Recommendation */}
                <div className="p-4 bg-primary-950/20 rounded-2xl border border-primary-500/20 text-xs space-y-1.5">
                  <div className="flex items-center gap-2 text-primary-300 font-bold text-[11px] uppercase tracking-wider font-mono">
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>Statutory Remediation Advice:</span>
                  </div>
                  <p className="text-slate-200 leading-relaxed font-sans">
                    {lh.reference_recommendation}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};