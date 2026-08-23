import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  Scale,
  LogOut,
  Sparkles,
  Menu,
  X,
  User,
  Shield,
  GraduationCap,
} from 'lucide-react';
import { HealthModal } from './HealthModal';
import { ClassifierModal } from './ClassifierModal';

interface NavbarProps {
  activeTab?: string;
  setActiveTab: (tab: string) => void;
  isMobileMenuOpen?: boolean;
  setIsMobileMenuOpen?: (open: boolean) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  setActiveTab,
  isMobileMenuOpen,
  setIsMobileMenuOpen,
}) => {
  const { user, logout } = useAuth();
  const [isHealthOpen, setIsHealthOpen] = useState(false);
  const [isClassifierOpen, setIsClassifierOpen] = useState(false);

  const getRoleIcon = () => {
    if (user?.role === 'TEACHER') return <GraduationCap className="w-3.5 h-3.5 text-accent-cyan" />;
    if (user?.role === 'ADMIN') return <Shield className="w-3.5 h-3.5 text-accent-amber" />;
    return <User className="w-3.5 h-3.5 text-primary-400" />;
  };

  const getInitials = (name?: string | null) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  };

  return (
    <>
      <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl px-4 sm:px-6 flex items-center justify-between sticky top-0 z-40">
        {/* Brand */}
        <div className="flex items-center gap-3.5">
          {setIsMobileMenuOpen && (
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden p-2 text-slate-400 hover:text-white rounded-xl bg-slate-900 border border-slate-800"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          )}

          <div
            onClick={() => setActiveTab(user?.role === 'TEACHER' ? 'teacher_assignments' : 'workspace')}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary-600 via-indigo-600 to-accent-cyan flex items-center justify-center shadow-lg shadow-primary-500/25 group-hover:scale-105 transition-transform">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold tracking-tight text-white group-hover:text-primary-300 transition-colors">
                  Draft<span className="text-primary-400">Forge</span>
                </span>
                <span className="hidden sm:inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold bg-primary-500/10 text-primary-300 border border-primary-500/20 uppercase tracking-wider">
                  AI Legal Platform
                </span>
              </div>
              <p className="text-[10px] text-slate-400 hidden sm:block font-medium">
                Deterministic Evaluation & Graph Reasoning
              </p>
            </div>
          </div>
        </div>

        {/* Action Controls & User Badge */}
        <div className="flex items-center gap-2.5 sm:gap-3.5">
          {/* Quick Classifier Tool Button */}
          <button
            onClick={() => setIsClassifierOpen(true)}
            className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 text-slate-300 hover:text-white text-xs font-medium border border-slate-800 hover:border-slate-700 transition-all shadow-sm group"
            title="Classify legal text into document type"
          >
            <Sparkles className="w-3.5 h-3.5 text-accent-cyan group-hover:rotate-12 transition-transform" />
            <span>Classify Text</span>
          </button>

          {/* System Health Check Button */}
          <button
            onClick={() => setIsHealthOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-semibold border border-emerald-500/20 transition-all"
            title="Inspect Database, Qdrant & Neo4j Connectivity"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="hidden sm:inline">System Healthy</span>
          </button>

          {/* User Profile Card */}
          <div className="flex items-center gap-3 pl-2 border-l border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-primary-700 flex items-center justify-center text-white text-xs font-bold shadow-md shadow-primary-500/20">
                {getInitials(user?.full_name)}
              </div>
              <div className="hidden lg:block text-left">
                <p className="text-xs font-semibold text-white truncate max-w-[120px]">
                  {user?.full_name || user?.email.split('@')[0]}
                </p>
                <div className="flex items-center gap-1 text-[10px] text-slate-400 font-medium">
                  {getRoleIcon()}
                  <span>{user?.role || 'STUDENT'}</span>
                </div>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={logout}
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-colors border border-transparent hover:border-rose-500/20"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Global Modals */}
      <HealthModal isOpen={isHealthOpen} onClose={() => setIsHealthOpen(false)} />
      <ClassifierModal isOpen={isClassifierOpen} onClose={() => setIsClassifierOpen(false)} />
    </>
  );
};