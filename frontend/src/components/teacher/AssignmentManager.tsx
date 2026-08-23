import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Assignment, DocumentType } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import {
  FileCheck,
  Plus,
  Users,
  Search,
  BookOpen,
  Clock,
} from 'lucide-react';

export const AssignmentManager: React.FC<{ onSelectAssignment: (id: string) => void }> = ({
  onSelectAssignment,
}) => {
  const { showToast } = useToast();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [instructions, setInstructions] = useState('');
  const [docType, setDocType] = useState<DocumentType>('EMPLOYMENT_AGREEMENT');
  const [deadline, setDeadline] = useState('');
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchAssignments = async () => {
    setLoading(true);
    try {
      const res = await api.getTeacherAssignments();
      setAssignments(res.data || []);
    } catch (err: any) {
      showToast('Failed to load assignments', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssignments();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !instructions.trim()) {
      showToast('Please provide an assignment title and drafting instructions.', 'error');
      return;
    }
    setCreating(true);
    try {
      await api.createAssignment({
        title,
        description: description.trim() || undefined,
        document_type: docType,
        instructions,
        deadline: deadline ? new Date(deadline).toISOString() : undefined,
      });
      showToast(`Assignment "${title}" published successfully!`, 'success');
      setTitle('');
      setDescription('');
      setInstructions('');
      setDeadline('');
      await fetchAssignments();
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to create assignment', 'error');
    } finally {
      setCreating(false);
    }
  };

  const filtered = assignments.filter((a) =>
    a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    a.instructions.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl glass-panel-glow border border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-white tracking-tight">Assignment Management</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 font-mono">
              Faculty Studio
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Publish drafting briefs, enforce statutory constraints, and track student submissions in real-time.
          </p>
        </div>

        <div className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-2xl text-xs font-mono text-slate-300">
          Active Assignments: <span className="text-accent-cyan font-bold">{assignments.length}</span>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Create Assignment Form (Left 5 Cols) */}
        <div className="col-span-12 lg:col-span-5 glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
            <Plus className="w-4 h-4 text-primary-400" />
            <h3 className="font-bold text-sm text-white">Create New Assignment</h3>
          </div>

          <form onSubmit={handleCreate} className="space-y-3.5">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Assignment Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Executive Employment Agreement Drafting"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus-ring"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Short Description (Optional)
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. Focus on restrictive covenants and termination notice"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus-ring"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Target Legal Document Category
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value as DocumentType)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus-ring"
              >
                <option value="AFFIDAVIT_OF_CHARACTER">Affidavit of Character (India)</option>
                <option value="EMPLOYMENT_AGREEMENT">Employment Agreement (India)</option>
                <option value="RENT_AGREEMENT">Residential Rent Deed (India)</option>
                <option value="LEGAL_NOTICE">Statutory Legal Notice</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Instructions & Rubric Constraints
              </label>
              <textarea
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                rows={4}
                placeholder="Specify mandatory party clauses, consideration terms, notice periods, and statutory references..."
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus-ring resize-none font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Submission Deadline
              </label>
              <input
                type="datetime-local"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus-ring"
              />
            </div>

            <button
              type="submit"
              disabled={creating || !title.trim() || !instructions.trim()}
              className="w-full py-2.5 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary-500/25 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {creating ? <LoadingSpinner size="sm" /> : <FileCheck className="w-4 h-4" />}
              <span>Publish Assignment</span>
            </button>
          </form>
        </div>

        {/* Existing Assignments (Right 7 Cols) */}
        <div className="col-span-12 lg:col-span-7 glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800">
            <h3 className="font-bold text-sm text-white">Active Classroom Assignments</h3>
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search..."
                className="bg-slate-900 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 focus-ring"
              />
            </div>
          </div>

          {loading ? (
            <div className="py-16 flex justify-center">
              <LoadingSpinner size="lg" label="Loading faculty assignments..." />
            </div>
          ) : filtered.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 space-y-2">
              <BookOpen className="w-10 h-10 text-slate-700 mx-auto" />
              <p>No assignments published yet. Create one on the left.</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
              {filtered.map((a) => (
                <div
                  key={a.id}
                  onClick={() => onSelectAssignment(a.id)}
                  className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-accent-cyan/50 cursor-pointer transition-all space-y-3 group"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-900 text-primary-400 border border-primary-500/20">
                        {a.document_type.replace(/_/g, ' ')}
                      </span>
                      <h4 className="font-bold text-sm text-white mt-1.5 group-hover:text-accent-cyan transition-colors">
                        {a.title}
                      </h4>
                    </div>

                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
                      {a.status}
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                    {a.instructions}
                  </p>

                  <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
                    <div className="flex items-center gap-1.5 text-accent-cyan font-semibold">
                      <Users className="w-3.5 h-3.5" />
                      <span>{a.submissions_count || 0} Submissions</span>
                    </div>

                    <div className="flex items-center gap-1 text-[11px] text-slate-500">
                      <Clock className="w-3 h-3 text-accent-amber" />
                      <span>
                        {a.deadline ? new Date(a.deadline).toLocaleDateString() : 'No Deadline'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};