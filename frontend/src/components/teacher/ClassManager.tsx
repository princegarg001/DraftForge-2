import React, { useCallback, useEffect, useState } from 'react';
import { api } from '../../services/api';
import { ClassRoom, Enrollment, BulkInviteResponse } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import {
  Users,
  Plus,
  Mail,
  RefreshCw,
  Trash2,
  Copy,
  Check,
  School,
  UserPlus,
  X,
} from 'lucide-react';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Parse a pasted roster.
 *
 * Accepts one entry per line, either a bare address or "Name <email>" /
 * "Name, email" — the shapes that come out of a spreadsheet column or a copied
 * mailing list, which is how rosters actually arrive.
 */
export const parseRoster = (raw: string): { email: string; full_name?: string }[] => {
  const seen = new Set<string>();
  const parsed: { email: string; full_name?: string }[] = [];

  for (const line of raw.split(/[\n\r]+/)) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    let name: string | undefined;
    let email: string | undefined;

    const angled = trimmed.match(/^(.*?)<([^>]+)>$/);
    if (angled) {
      name = angled[1].trim().replace(/["',]+$/, '').trim() || undefined;
      email = angled[2].trim();
    } else {
      const parts = trimmed.split(/[,;\t]/).map((p) => p.trim()).filter(Boolean);
      const emailPart = parts.find((p) => EMAIL_PATTERN.test(p));
      if (emailPart) {
        email = emailPart;
        name = parts.filter((p) => p !== emailPart).join(' ').trim() || undefined;
      } else if (EMAIL_PATTERN.test(trimmed)) {
        email = trimmed;
      }
    }

    if (!email) continue;
    const normalized = email.toLowerCase();
    if (!EMAIL_PATTERN.test(normalized) || seen.has(normalized)) continue;

    seen.add(normalized);
    parsed.push({ email: normalized, full_name: name });
  }

  return parsed;
};

export const ClassManager: React.FC = () => {
  const { showToast } = useToast();

  const [classes, setClasses] = useState<ClassRoom[]>([]);
  const [selected, setSelected] = useState<ClassRoom | null>(null);
  const [roster, setRoster] = useState<Enrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [rosterLoading, setRosterLoading] = useState(false);

  const [showCreate, setShowCreate] = useState(false);
  const [newClass, setNewClass] = useState({ name: '', institution: '', academic_term: '' });
  const [creating, setCreating] = useState(false);

  const [showInvite, setShowInvite] = useState(false);
  const [rosterText, setRosterText] = useState('');
  const [inviting, setInviting] = useState(false);
  const [inviteResult, setInviteResult] = useState<BulkInviteResponse | null>(null);

  const [copiedCode, setCopiedCode] = useState(false);

  const loadClasses = useCallback(async () => {
    try {
      const { data } = await api.getMyClasses();
      setClasses(data);
      setSelected((current) => current ?? data[0] ?? null);
    } catch {
      showToast('Could not load your classes', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const loadRoster = useCallback(
    async (classId: string) => {
      setRosterLoading(true);
      try {
        const { data } = await api.getRoster(classId);
        setRoster(data);
      } catch {
        showToast('Could not load the roster', 'error');
      } finally {
        setRosterLoading(false);
      }
    },
    [showToast]
  );

  useEffect(() => {
    void loadClasses();
  }, [loadClasses]);

  useEffect(() => {
    if (selected) void loadRoster(selected.id);
  }, [selected, loadRoster]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const { data } = await api.createClass({
        name: newClass.name,
        institution: newClass.institution || undefined,
        academic_term: newClass.academic_term || undefined,
      });
      setClasses((prev) => [data, ...prev]);
      setSelected(data);
      setShowCreate(false);
      setNewClass({ name: '', institution: '', academic_term: '' });
      showToast(`Created ${data.name}`, 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail ?? 'Could not create the class', 'error');
    } finally {
      setCreating(false);
    }
  };

  const parsedRoster = parseRoster(rosterText);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected || parsedRoster.length === 0) return;
    setInviting(true);
    setInviteResult(null);
    try {
      const { data } = await api.inviteStudents(selected.id, parsedRoster);
      setInviteResult(data);
      showToast(`${data.invited} invitation${data.invited === 1 ? '' : 's'} sent`, 'success');
      setRosterText('');
      await loadRoster(selected.id);
      await loadClasses();
    } catch (err: any) {
      showToast(err.response?.data?.detail ?? 'Could not send invitations', 'error');
    } finally {
      setInviting(false);
    }
  };

  const handleResend = async (email: string) => {
    if (!selected) return;
    try {
      await api.resendInvitation(selected.id, email);
      showToast(`Invitation resent to ${email}`, 'success');
      await loadRoster(selected.id);
    } catch (err: any) {
      showToast(err.response?.data?.detail ?? 'Could not resend', 'error');
    }
  };

  const handleRemove = async (enrollment: Enrollment) => {
    if (!selected) return;
    if (!window.confirm(`Remove ${enrollment.email} from ${selected.name}? Their work is kept.`)) {
      return;
    }
    try {
      await api.removeStudent(selected.id, enrollment.id);
      showToast('Student removed from the class', 'success');
      await loadRoster(selected.id);
      await loadClasses();
    } catch (err: any) {
      showToast(err.response?.data?.detail ?? 'Could not remove the student', 'error');
    }
  };

  const copyJoinCode = async () => {
    if (!selected?.join_code) return;
    try {
      await navigator.clipboard.writeText(selected.join_code);
      setCopiedCode(true);
      window.setTimeout(() => setCopiedCode(false), 2000);
    } catch {
      showToast('Could not copy to clipboard', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <LoadingSpinner size="md" />
      </div>
    );
  }

  const panel = 'bg-slate-900/60 border border-slate-800 rounded-2xl';
  const input =
    'w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus-ring';

  return (
    <div className="p-4 sm:p-6 space-y-5 max-w-6xl mx-auto">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <School className="w-5 h-5 text-primary-400" />
            Classes
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Add students by email; each receives an invitation to set their password.
          </p>
        </div>
        <button
          onClick={() => setShowCreate((v) => !v)}
          className="flex items-center gap-1.5 px-3.5 py-2 bg-primary-600 hover:bg-primary-500 text-white text-xs font-bold rounded-xl transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          New Class
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className={`${panel} p-5 space-y-3 animate-fade-in`}>
          <div className="grid gap-3 sm:grid-cols-3">
            <input
              required
              value={newClass.name}
              onChange={(e) => setNewClass({ ...newClass, name: e.target.value })}
              placeholder="Class name (required)"
              className={input}
            />
            <input
              value={newClass.institution}
              onChange={(e) => setNewClass({ ...newClass, institution: e.target.value })}
              placeholder="Institution"
              className={input}
            />
            <input
              value={newClass.academic_term}
              onChange={(e) => setNewClass({ ...newClass, academic_term: e.target.value })}
              placeholder="Term, e.g. Autumn 2026"
              className={input}
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={creating || !newClass.name.trim()}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition-colors flex items-center gap-2"
            >
              {creating && <LoadingSpinner size="sm" />}
              Create
            </button>
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {classes.length === 0 ? (
        <div className={`${panel} p-10 text-center`}>
          <Users className="w-8 h-8 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-300 font-semibold">No classes yet</p>
          <p className="text-xs text-slate-500 mt-1">
            Create a class, then add your students by email.
          </p>
        </div>
      ) : (
        <div className="grid gap-5 lg:grid-cols-[260px_1fr]">
          <div className="space-y-2">
            {classes.map((cls) => (
              <button
                key={cls.id}
                onClick={() => setSelected(cls)}
                className={`w-full text-left p-3.5 rounded-xl border transition-all ${
                  selected?.id === cls.id
                    ? 'bg-primary-600/15 border-primary-500/50'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <span className="block text-xs font-bold text-white truncate">{cls.name}</span>
                <span className="block text-[11px] text-slate-400 mt-0.5">
                  {cls.student_count} student{cls.student_count === 1 ? '' : 's'}
                  {cls.academic_term ? ` · ${cls.academic_term}` : ''}
                </span>
              </button>
            ))}
          </div>

          {selected && (
            <div className="space-y-4">
              <div className={`${panel} p-5 space-y-4`}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 className="text-sm font-bold text-white">{selected.name}</h3>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      {selected.institution || 'No institution set'}
                      {selected.academic_term ? ` · ${selected.academic_term}` : ''}
                    </p>
                  </div>
                  <button
                    onClick={() => setShowInvite((v) => !v)}
                    className="flex items-center gap-1.5 px-3.5 py-2 bg-primary-600 hover:bg-primary-500 text-white text-xs font-bold rounded-xl transition-colors"
                  >
                    <UserPlus className="w-3.5 h-3.5" />
                    Add Students
                  </button>
                </div>

                {selected.join_code && (
                  <div className="flex items-center gap-2 text-[11px]">
                    <span className="text-slate-500">Join code</span>
                    <code className="px-2 py-1 bg-slate-950 border border-slate-800 rounded-lg text-primary-300 font-mono tracking-wider">
                      {selected.join_code}
                    </code>
                    <button
                      onClick={copyJoinCode}
                      className="text-slate-400 hover:text-white transition-colors"
                      aria-label="Copy join code"
                    >
                      {copiedCode ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                )}
              </div>

              {showInvite && (
                <form onSubmit={handleInvite} className={`${panel} p-5 space-y-3 animate-fade-in`}>
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-slate-300">
                      Paste your roster — one student per line
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowInvite(false)}
                      className="text-slate-500 hover:text-slate-300"
                      aria-label="Close"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <textarea
                    value={rosterText}
                    onChange={(e) => setRosterText(e.target.value)}
                    rows={7}
                    placeholder={
                      'aditya@university.edu\nPriya Nair <priya@university.edu>\nKavya Iyer, kavya@university.edu'
                    }
                    className={`${input} font-mono leading-relaxed resize-y`}
                  />
                  <div className="flex flex-wrap items-center gap-3">
                    <button
                      type="submit"
                      disabled={inviting || parsedRoster.length === 0}
                      className="px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition-colors flex items-center gap-2"
                    >
                      {inviting ? <LoadingSpinner size="sm" /> : <Mail className="w-3.5 h-3.5" />}
                      Send {parsedRoster.length > 0 ? parsedRoster.length : ''} Invitation
                      {parsedRoster.length === 1 ? '' : 's'}
                    </button>
                    <span className="text-[11px] text-slate-500">
                      {parsedRoster.length} valid address{parsedRoster.length === 1 ? '' : 'es'} detected
                    </span>
                  </div>

                  {inviteResult && (
                    <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400 space-y-1">
                      <p>
                        <span className="text-emerald-400 font-semibold">{inviteResult.invited} sent</span>
                        {inviteResult.skipped > 0 && ` · ${inviteResult.skipped} already enrolled`}
                        {inviteResult.failed > 0 && (
                          <span className="text-rose-400"> · {inviteResult.failed} failed</span>
                        )}
                      </p>
                    </div>
                  )}
                </form>
              )}

              <div className={panel}>
                <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-bold text-white">
                    Roster ({roster.length})
                  </span>
                  {rosterLoading && <LoadingSpinner size="sm" />}
                </div>

                {roster.length === 0 && !rosterLoading ? (
                  <p className="px-5 py-8 text-center text-xs text-slate-500">
                    No students yet. Use “Add Students” to invite them.
                  </p>
                ) : (
                  <ul className="divide-y divide-slate-800">
                    {roster.map((entry) => (
                      <li
                        key={entry.id}
                        className="px-5 py-3 flex flex-wrap items-center justify-between gap-2"
                      >
                        <div className="min-w-0">
                          <span className="block text-xs text-white truncate">
                            {entry.full_name || entry.email}
                          </span>
                          {entry.full_name && (
                            <span className="block text-[11px] text-slate-500 truncate">
                              {entry.email}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2.5">
                          <span
                            className={`px-2 py-0.5 rounded-lg text-[10px] font-bold ${
                              entry.status === 'ACTIVE'
                                ? 'bg-emerald-500/15 text-emerald-300'
                                : 'bg-amber-500/15 text-amber-300'
                            }`}
                          >
                            {entry.status === 'ACTIVE' ? 'Joined' : 'Invited'}
                          </span>
                          {entry.status !== 'ACTIVE' && (
                            <button
                              onClick={() => handleResend(entry.email)}
                              className="text-slate-400 hover:text-primary-300 transition-colors"
                              title="Resend invitation"
                            >
                              <RefreshCw className="w-3.5 h-3.5" />
                            </button>
                          )}
                          <button
                            onClick={() => handleRemove(entry)}
                            className="text-slate-400 hover:text-rose-400 transition-colors"
                            title="Remove from class"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
