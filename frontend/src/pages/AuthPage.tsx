import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { useToast } from '../components/common/Toast';
import {
  Scale,
  Lock,
  Mail,
  User,
  KeyRound,
  ArrowRight,
  Eye,
  EyeOff,
  ChevronLeft,
  Info,
} from 'lucide-react';

interface AuthPageProps {
  onBackToLanding?: () => void;
}

type Mode = 'signin' | 'faculty';

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

export const AuthPage: React.FC<AuthPageProps> = ({ onBackToLanding }) => {
  const { loginWithResponse } = useAuth();
  const { showToast } = useToast();

  const [mode, setMode] = useState<Mode>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [registrationCode, setRegistrationCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const issues = mode === 'faculty' ? passwordIssues(password) : [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === 'signin') {
        const res = await api.login({ email, password });
        loginWithResponse(res.data);
        showToast(`Welcome back, ${res.data.full_name || 'Legal Scholar'}.`, 'success');
      } else {
        const res = await api.registerFaculty({
          email,
          password,
          full_name: fullName,
          registration_code: registrationCode,
        });
        loginWithResponse(res.data);
        showToast('Faculty account created.', 'success');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check your details.');
      showToast('Authentication failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    'w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus-ring';

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 sm:p-6 bg-background relative overflow-hidden font-sans">
      <div className="absolute w-[500px] h-[500px] bg-primary-600/10 rounded-full blur-3xl -top-32 -left-32 pointer-events-none" />
      <div className="absolute w-[500px] h-[500px] bg-accent-cyan/10 rounded-full blur-3xl -bottom-32 -right-32 pointer-events-none" />

      <div className="w-full max-w-md glass-panel-glow p-8 rounded-3xl border border-slate-800 shadow-2xl relative z-10 space-y-6 animate-scale-in">
        {onBackToLanding && (
          <button
            onClick={onBackToLanding}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Back to Home</span>
          </button>
        )}

        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-primary-600 via-indigo-600 to-accent-cyan p-0.5 mx-auto shadow-xl shadow-primary-500/25">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
              <Scale className="w-7 h-7 text-primary-400" />
            </div>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Draft<span className="text-primary-400">Forge</span>
          </h1>
          <p className="text-xs text-slate-400">
            Evidence-Grounded Legal Drafting Education &amp; Evaluation
          </p>
        </div>

        <div className="flex p-1 bg-slate-900 rounded-2xl border border-slate-800">
          {(
            [
              ['signin', 'Sign In'],
              ['faculty', 'Faculty Sign-Up'],
            ] as [Mode, string][]
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => {
                setMode(value);
                setError(null);
              }}
              className={`flex-1 py-2 rounded-xl text-xs font-bold transition-all ${
                mode === value ? 'bg-primary-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Students no longer self-register: accounts are created by an
            instructor adding them to a class roster. */}
        {mode === 'signin' && (
          <div className="flex gap-2.5 p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400 leading-relaxed">
            <Info className="w-3.5 h-3.5 text-primary-400 shrink-0 mt-0.5" />
            <span>
              Students join by invitation. If your instructor has added you to a class, check your
              email for a link to set your password.
            </span>
          </div>
        )}

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 font-medium text-center animate-fade-in">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'faculty' && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Prof. Vikram Seth"
                  autoComplete="name"
                  className={inputClass}
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@institution.edu"
                autoComplete="email"
                className={inputClass}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                autoComplete={mode === 'faculty' ? 'new-password' : 'current-password'}
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
            {mode === 'faculty' && password.length > 0 && issues.length > 0 && (
              <ul className="mt-2 space-y-0.5">
                {issues.map((issue) => (
                  <li key={issue} className="text-[11px] text-amber-400/90">
                    • {issue}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {mode === 'faculty' && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Faculty Registration Code
              </label>
              <div className="relative">
                <KeyRound className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="text"
                  required
                  value={registrationCode}
                  onChange={(e) => setRegistrationCode(e.target.value)}
                  placeholder="Issued by your institution"
                  className={inputClass}
                />
              </div>
              <p className="mt-1.5 text-[11px] text-slate-500">
                Instructor accounts require a code from your institution's administrator.
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || (mode === 'faculty' && issues.length > 0)}
            className="w-full py-3 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2"
          >
            {loading ? <LoadingSpinner size="sm" /> : <ArrowRight className="w-4 h-4" />}
            <span>{mode === 'signin' ? 'Sign In to Portal' : 'Create Faculty Account'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
