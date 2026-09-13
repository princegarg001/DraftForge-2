import React, { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { InvitationPreview } from '../types';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { useToast } from '../components/common/Toast';
import { Scale, Lock, User, Eye, EyeOff, ArrowRight, AlertCircle, GraduationCap } from 'lucide-react';

const MIN_PASSWORD_LENGTH = 12;

/** Mirrors the server-side policy so the rule is visible before submitting. */
const passwordIssues = (password: string): string[] => {
  const issues: string[] = [];
  if (password.length < MIN_PASSWORD_LENGTH) {
    issues.push(`At least ${MIN_PASSWORD_LENGTH} characters`);
  }
  const classes = [
    /[a-z]/.test(password),
    /[A-Z]/.test(password),
    /\d/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ].filter(Boolean).length;
  if (classes < 3) {
    issues.push('Three of: lowercase, uppercase, digits, symbols');
  }
  return issues;
};

export const AcceptInvitePage: React.FC = () => {
  const { loginWithResponse } = useAuth();
  const { showToast } = useToast();

  const [token] = useState<string>(() => new URLSearchParams(window.location.search).get('token') ?? '');
  const [preview, setPreview] = useState<InvitationPreview | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);

  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const loadPreview = useCallback(async () => {
    if (!token) {
      setLoadError('This link is missing its invitation code.');
      setChecking(false);
      return;
    }
    try {
      const { data } = await api.previewInvitation(token);
      setPreview(data);
      if (data.full_name) setFullName(data.full_name);
    } catch (err: any) {
      setLoadError(
        err.response?.data?.detail ??
          'This invitation link is no longer valid. Ask your instructor to resend it.'
      );
    } finally {
      setChecking(false);
    }
  }, [token]);

  useEffect(() => {
    void loadPreview();
  }, [loadPreview]);

  const issues = passwordIssues(password);
  const mismatch = confirmPassword.length > 0 && password !== confirmPassword;
  const canSubmit = !submitting && issues.length === 0 && !mismatch && confirmPassword.length > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    setSubmitting(true);
    try {
      const { data } = await api.acceptInvitation({
        token,
        password,
        full_name: fullName || undefined,
      });
      loginWithResponse(data);
      showToast(`Welcome to ${preview?.class_name ?? 'DraftForge'}.`, 'success');
      // Drop the token from the address bar so it does not linger in history
      // or get copied out of a shared screenshot.
      window.history.replaceState({}, '', '/');
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail ?? 'Could not complete sign-up. Please try again.');
      showToast('Could not complete sign-up', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const shell = (children: React.ReactNode) => (
    <div className="min-h-screen w-full flex items-center justify-center p-4 sm:p-6 bg-background relative overflow-hidden font-sans">
      <div className="absolute w-[500px] h-[500px] bg-primary-600/10 rounded-full blur-3xl -top-32 -left-32 pointer-events-none" />
      <div className="absolute w-[500px] h-[500px] bg-accent-cyan/10 rounded-full blur-3xl -bottom-32 -right-32 pointer-events-none" />
      <div className="w-full max-w-md glass-panel-glow p-8 rounded-3xl border border-slate-800 shadow-2xl relative z-10 space-y-6 animate-scale-in">
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-primary-600 via-indigo-600 to-accent-cyan p-0.5 mx-auto shadow-xl shadow-primary-500/25">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
              <Scale className="w-7 h-7 text-primary-400" />
            </div>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Draft<span className="text-primary-400">Forge</span>
          </h1>
        </div>
        {children}
      </div>
    </div>
  );

  if (checking) {
    return shell(
      <div className="flex flex-col items-center gap-3 py-6">
        <LoadingSpinner size="md" />
        <p className="text-xs text-slate-400">Checking your invitation…</p>
      </div>
    );
  }

  if (loadError || !preview) {
    return shell(
      <div className="space-y-5">
        <div className="flex gap-3 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <p className="text-xs text-rose-200 leading-relaxed">{loadError}</p>
        </div>
        <button
          onClick={() => {
            window.location.href = '/';
          }}
          className="w-full py-3 bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs rounded-xl transition-colors"
        >
          Go to Sign In
        </button>
      </div>
    );
  }

  const inputClass =
    'w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus-ring';

  return shell(
    <div className="space-y-6">
      <div className="p-4 rounded-xl bg-primary-600/10 border border-primary-500/30 space-y-1.5">
        <div className="flex items-center gap-2">
          <GraduationCap className="w-4 h-4 text-primary-400 shrink-0" />
          <span className="text-xs font-bold text-white">{preview.class_name}</span>
        </div>
        <p className="text-[11px] text-slate-300 leading-relaxed">
          {preview.teacher_name ? `${preview.teacher_name} invited you` : 'You have been invited'}
          {preview.institution ? ` at ${preview.institution}` : ''}. Set a password to join.
        </p>
      </div>

      {/* Read-only: the address is fixed by the invitation. Letting it be
          edited would allow a token to be redeemed against another address. */}
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
        <input
          type="email"
          value={preview.email}
          readOnly
          disabled
          className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-400 cursor-not-allowed"
        />
      </div>

      {submitError && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 font-medium text-center">
          {submitError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Full Name</label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Aditya Verma"
              autoComplete="name"
              className={inputClass}
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Choose a Password</label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type={showPassword ? 'text' : 'password'}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              autoComplete="new-password"
              className={`${inputClass} pr-10`}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {password.length > 0 && issues.length > 0 && (
            <ul className="mt-2 space-y-0.5">
              {issues.map((issue) => (
                <li key={issue} className="text-[11px] text-amber-400/90">
                  • {issue}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Confirm Password</label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type={showPassword ? 'text' : 'password'}
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••••••"
              autoComplete="new-password"
              className={inputClass}
            />
          </div>
          {mismatch && <p className="mt-2 text-[11px] text-rose-400">Passwords do not match.</p>}
        </div>

        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full py-3 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2"
        >
          {submitting ? <LoadingSpinner size="sm" /> : <ArrowRight className="w-4 h-4" />}
          <span>Join {preview.class_name}</span>
        </button>
      </form>
    </div>
  );
};
