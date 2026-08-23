import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Submission, Assignment } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import {
  FileCheck,
  ShieldAlert,
  FileText,
  Save,
} from 'lucide-react';

export const SubmissionsAuditor: React.FC<{ assignmentId?: string }> = ({
  assignmentId: initialAssignmentId,
}) => {
  const { showToast } = useToast();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<string>(initialAssignmentId || '');
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [selectedSub, setSelectedSub] = useState<Submission | null>(null);
  const [overrideScore, setOverrideScore] = useState<number>(0);
  const [overrideReason, setOverrideReason] = useState('');
  const [teacherNotes, setTeacherNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [savingOverride, setSavingOverride] = useState(false);

  useEffect(() => {
    api
      .getTeacherAssignments()
      .then((res) => {
        setAssignments(res.data || []);
        if (!selectedAssignmentId && res.data?.length > 0) {
          setSelectedAssignmentId(res.data[0].id);
        }
      })
      .catch(() => showToast('Failed to load assignments', 'error'));
  }, []);

  useEffect(() => {
    if (selectedAssignmentId) {
      setLoading(true);
      api
        .getAssignmentSubmissions(selectedAssignmentId)
        .then((res) => {
          setSubmissions(res.data || []);
          if (res.data?.length > 0) {
            const first = res.data[0];
            setSelectedSub(first);
            setOverrideScore(first.final_score ?? first.evaluation?.overall_score ?? 0);
            setTeacherNotes(first.teacher_notes || '');
          } else {
            setSelectedSub(null);
          }
        })
        .catch(() => showToast('Failed to fetch assignment submissions', 'error'))
        .finally(() => setLoading(false));
    }
  }, [selectedAssignmentId]);

  const handleSelectSubmission = (sub: Submission) => {
    setSelectedSub(sub);
    setOverrideScore(sub.final_score ?? sub.evaluation?.overall_score ?? 0);
    setTeacherNotes(sub.teacher_notes || '');
    setOverrideReason('');
  };

  const handleOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSub) return;
    if (!overrideReason.trim()) {
      showToast('Please provide a rationale / audit note for the score override.', 'error');
      return;
    }

    setSavingOverride(true);
    try {
      const res = await api.overrideScore(selectedSub.id, {
        overridden_score: Number(overrideScore),
        override_reason: overrideReason,
        teacher_notes: teacherNotes.trim() || undefined,
      });
      setSelectedSub(res.data);
      setSubmissions((prev) =>
        prev.map((s) => (s.id === res.data.id ? res.data : s))
      );
      showToast('Faculty score override persisted with audit trail!', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to persist override', 'error');
    } finally {
      setSavingOverride(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header & Assignment Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl glass-panel-glow border border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-white tracking-tight">Submissions Auditor</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              Grading & Score Overrides
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Review student draft submissions, verify automated RAG evaluations, and submit score overrides.
          </p>
        </div>

        {/* Assignment Switcher */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-400">Assignment:</span>
          <select
            value={selectedAssignmentId}
            onChange={(e) => setSelectedAssignmentId(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus-ring min-w-[220px]"
          >
            {assignments.map((a) => (
              <option key={a.id} value={a.id}>
                {a.title} ({a.submissions_count || 0} subs)
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left 4 Cols: Submissions List */}
        <div className="col-span-12 lg:col-span-4 glass-panel p-5 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-400">
              Student Submissions ({submissions.length})
            </h3>
          </div>

          {loading ? (
            <div className="py-16 flex justify-center">
              <LoadingSpinner size="md" />
            </div>
          ) : submissions.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500 space-y-2">
              <FileText className="w-8 h-8 text-slate-700 mx-auto" />
              <p>No student submissions received yet for this assignment.</p>
            </div>
          ) : (
            <div className="space-y-2.5 max-h-[650px] overflow-y-auto pr-1">
              {submissions.map((s) => {
                const isSelected = selectedSub?.id === s.id;
                const score = s.final_score ?? s.evaluation?.overall_score ?? 0;

                return (
                  <div
                    key={s.id}
                    onClick={() => handleSelectSubmission(s)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all space-y-2 ${
                      isSelected
                        ? 'bg-primary-600/15 border-primary-500/50 text-white shadow-md'
                        : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-200">
                          {s.student_name ? s.student_name[0].toUpperCase() : 'S'}
                        </div>
                        <span className="font-bold text-xs text-white truncate max-w-[140px]">
                          {s.student_name || s.student_email || 'Student Submission'}
                        </span>
                      </div>

                      <span className="font-mono text-xs font-extrabold text-emerald-400">
                        {score} pts
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-500">
                      <span className="uppercase">{s.status}</span>
                      <span>{new Date(s.submitted_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right 8 Cols: Audit & Score Override Card */}
        <div className="col-span-12 lg:col-span-8 glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
          {selectedSub ? (
            <>
              {/* Submission Meta Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-indigo-500 to-primary-700 flex items-center justify-center text-white font-bold text-sm">
                    {selectedSub.student_name ? selectedSub.student_name[0].toUpperCase() : 'U'}
                  </div>
                  <div>
                    <h3 className="font-bold text-base text-white">
                      {selectedSub.student_name || selectedSub.student_email}
                    </h3>
                    <p className="text-xs text-slate-400 font-mono">
                      Submitted on {new Date(selectedSub.submitted_at).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                      Effective Score
                    </span>
                    <span className="text-2xl font-extrabold text-emerald-400 font-mono">
                      {selectedSub.final_score ?? selectedSub.evaluation?.overall_score ?? 0} pts
                    </span>
                  </div>
                </div>
              </div>

              {/* Automated Evaluation Summary If Present */}
              {selectedSub.evaluation && (
                <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-xs uppercase tracking-wider text-slate-300">
                      Automated RAG Evaluation Breakdown
                    </h4>
                    <span className="text-[10px] font-mono text-slate-400">
                      Rubric {selectedSub.evaluation.rubric_version}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 text-xs">
                      <span className="text-slate-400 text-[10px] block">Structure:</span>
                      <strong className="text-white text-sm">
                        {selectedSub.evaluation.structure_score} pts
                      </strong>
                    </div>
                    <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 text-xs">
                      <span className="text-slate-400 text-[10px] block">Clause Coverage:</span>
                      <strong className="text-white text-sm">
                        {selectedSub.evaluation.clause_score} pts
                      </strong>
                    </div>
                    <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 text-xs">
                      <span className="text-slate-400 text-[10px] block">Formatting / Jurats:</span>
                      <strong className="text-white text-sm">
                        {selectedSub.evaluation.formatting_score} pts
                      </strong>
                    </div>
                  </div>
                </div>
              )}

              {/* Faculty Score Override Form */}
              <form
                onSubmit={handleOverride}
                className="p-5 sm:p-6 rounded-2xl bg-amber-950/15 border border-amber-500/30 space-y-4"
              >
                <div className="flex items-center gap-2 text-amber-300 font-bold text-xs uppercase tracking-wider">
                  <ShieldAlert className="w-4 h-4" />
                  <span>Audited Score Override & Feedback</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      New Total Score
                    </label>
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={overrideScore}
                      onChange={(e) => setOverrideScore(Number(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus-ring font-mono font-bold"
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Audit Rationale / Reason
                    </label>
                    <input
                      type="text"
                      value={overrideReason}
                      onChange={(e) => setOverrideReason(e.target.value)}
                      placeholder="e.g. Approved creative dispute resolution clause structure"
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus-ring"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Qualitative Feedback for Student (Optional)
                  </label>
                  <textarea
                    value={teacherNotes}
                    onChange={(e) => setTeacherNotes(e.target.value)}
                    placeholder="Provide constructive drafting guidance..."
                    rows={3}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus-ring resize-none"
                  />
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={savingOverride || !overrideReason.trim()}
                    className="px-5 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-amber-500/20 transition-all disabled:opacity-50 flex items-center gap-2"
                  >
                    {savingOverride ? <LoadingSpinner size="sm" /> : <Save className="w-3.5 h-3.5" />}
                    <span>Persist Score Override</span>
                  </button>
                </div>
              </form>
            </>
          ) : (
            <div className="p-16 text-center text-xs text-slate-500 space-y-2">
              <FileCheck className="w-10 h-10 text-slate-700 mx-auto" />
              <p>Select a submission from the left to inspect and audit evaluation scores.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};