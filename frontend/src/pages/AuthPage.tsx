import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { UserRole } from '../types';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { useToast } from '../components/common/Toast';
import {
  Scale,
  Lock,
  Mail,
  User,
  GraduationCap,
  ArrowRight,
  Eye,
  EyeOff,
  ChevronLeft,
} from 'lucide-react';

interface AuthPageProps {
  onBackToLanding?: () => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onBackToLanding }) => {
  const { login } = useAuth();
  const { showToast } = useToast();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<UserRole>('STUDENT');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        const res = await api.login({ email, password });
        login(res.data.access_token, {
          id: res.data.user_id,
          email: res.data.email,
          role: res.data.role,
          full_name: res.data.full_name,
        });
        showToast(`Welcome back, ${res.data.full_name || 'Legal Scholar'}!`, 'success');
      } else {
        const res = await api.register({
          email,
          password,
          full_name: fullName,
          role,
        });
        login(res.data.access_token, {
          id: res.data.user_id,
          email: res.data.email,
          role: res.data.role,
          full_name: res.data.full_name,
        });
        showToast('Account registered successfully!', 'success');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.');
      showToast('Authentication failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (demoRole: 'student' | 'teacher') => {
    if (demoRole === 'student') {
      setEmail('student@draftforge.ai');
      setPassword('Password123!');
      setFullName('Aditya Verma');
      setRole('STUDENT');
    } else {
      setEmail('teacher@draftforge.ai');
      setPassword('Password123!');
      setFullName('Prof. Vikram Seth');
      setRole('TEACHER');
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 sm:p-6 bg-background relative overflow-hidden font-sans">
      {/* Background Decorative Glows */}
      <div className="absolute w-[500px] h-[500px] bg-primary-600/10 rounded-full blur-3xl -top-32 -left-32 pointer-events-none" />
      <div className="absolute w-[500px] h-[500px] bg-accent-cyan/10 rounded-full blur-3xl -bottom-32 -right-32 pointer-events-none" />

      <div className="w-full max-w-md glass-panel-glow p-8 rounded-3xl border border-slate-800 shadow-2xl relative z-10 space-y-6 animate-scale-in">
        {/* Back to Landing Page Link */}
        {onBackToLanding && (
          <button
            onClick={onBackToLanding}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Back to Home</span>
          </button>
        )}

        {/* Brand Header */}
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
            Evidence-Grounded Legal Drafting Education & Evaluation
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex p-1 bg-slate-900 rounded-2xl border border-slate-800">
          <button
            type="button"
            onClick={() => {
              setIsLogin(true);
              setError(null);
            }}
            className={`flex-1 py-2 rounded-xl text-xs font-bold transition-all ${
              isLogin ? 'bg-primary-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setIsLogin(false);
              setError(null);
            }}
            className={`flex-1 py-2 rounded-xl text-xs font-bold transition-all ${
              !isLogin ? 'bg-primary-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 font-medium text-center animate-fade-in">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Full Legal Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Adv. Rohit Deshmukh"
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus-ring"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@institution.edu"
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus-ring"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-10 py-2.5 text-xs text-white placeholder-slate-500 focus-ring"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Portal Role Selection
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setRole('STUDENT')}
                  className={`p-3 rounded-xl border text-xs font-semibold text-left transition-all flex items-center gap-2.5 ${
                    role === 'STUDENT'
                      ? 'bg-primary-600/20 text-white border-primary-500 shadow-md shadow-primary-500/10'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  <User className="w-4 h-4 text-primary-400 shrink-0" />
                  <div>
                    <span className="block text-xs font-bold text-white">Student</span>
                    <span className="text-[10px] text-slate-400">Draft & Learn</span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setRole('TEACHER')}
                  className={`p-3 rounded-xl border text-xs font-semibold text-left transition-all flex items-center gap-2.5 ${
                    role === 'TEACHER'
                      ? 'bg-primary-600/20 text-white border-primary-500 shadow-md shadow-primary-500/10'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  <GraduationCap className="w-4 h-4 text-accent-cyan shrink-0" />
                  <div>
                    <span className="block text-xs font-bold text-white">Faculty</span>
                    <span className="text-[10px] text-slate-400">Grade & Ingest</span>
                  </div>
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary-500/25 transition-all disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
          >
            {loading ? <LoadingSpinner size="sm" /> : <ArrowRight className="w-4 h-4" />}
            <span>{isLogin ? 'Sign In to Portal' : 'Register & Enter'}</span>
          </button>
        </form>

        {/* Demo Fast Autofill */}
        <div className="pt-3 border-t border-slate-800 text-center space-y-2">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold block">
            Demo Sandbox Autofill:
          </span>
          <div className="flex justify-center gap-2">
            <button
              type="button"
              onClick={() => handleQuickFill('student')}
              className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 text-[11px] font-semibold rounded-lg border border-slate-800 transition-colors"
            >
              Demo Student
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('teacher')}
              className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 text-[11px] font-semibold rounded-lg border border-slate-800 transition-colors"
            >
              Demo Faculty
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};