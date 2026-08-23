import React from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  FileEdit,
  ClipboardCheck,
  ShieldAlert,
  GraduationCap,
  HelpCircle,
  TrendingUp,
  FolderArchive,
  BookOpen,
  Users,
  UploadCloud,
  FileCheck,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isCollapsed?: boolean;
  setIsCollapsed?: (collapsed: boolean) => void;
  isMobileMenuOpen?: boolean;
  setIsMobileMenuOpen?: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  isCollapsed = false,
  setIsCollapsed,
  isMobileMenuOpen = false,
  setIsMobileMenuOpen,
}) => {
  const { user } = useAuth();
  const isTeacher = user?.role === 'TEACHER' || user?.role === 'ADMIN';

  const studentNavItems = [
    {
      id: 'workspace',
      label: 'Drafting Workspace',
      icon: FileEdit,
      badge: 'Editor',
      color: 'text-primary-400',
    },
    {
      id: 'assignments',
      label: 'Class Assignments',
      icon: FolderArchive,
      badge: 'Portal',
      color: 'text-accent-cyan',
    },
    {
      id: 'evaluations',
      label: 'Evaluation & Evidence',
      icon: ClipboardCheck,
      badge: '100 pts',
      color: 'text-accent-emerald',
    },
    {
      id: 'loopholes',
      label: 'GraphRAG Loopholes',
      icon: ShieldAlert,
      badge: 'Neo4j',
      color: 'text-accent-rose',
    },
    {
      id: 'learning',
      label: 'AI Roadmap & Tutor',
      icon: GraduationCap,
      badge: 'Socratic',
      color: 'text-indigo-400',
    },
    {
      id: 'quizzes',
      label: 'Interactive Quizzes',
      icon: HelpCircle,
      badge: 'Practice',
      color: 'text-accent-amber',
    },
    {
      id: 'progress',
      label: 'Skills & Leaderboard',
      icon: TrendingUp,
      badge: 'Analytics',
      color: 'text-accent-emerald',
    },
    {
      id: 'reference_corpus',
      label: 'Reference Corpus',
      icon: BookOpen,
      badge: 'RAG',
      color: 'text-slate-400',
    },
  ];

  const teacherNavItems = [
    {
      id: 'teacher_assignments',
      label: 'Manage Assignments',
      icon: FileCheck,
      badge: 'Faculty',
      color: 'text-accent-cyan',
    },
    {
      id: 'teacher_submissions',
      label: 'Submissions Auditor',
      icon: ClipboardCheck,
      badge: 'Grading',
      color: 'text-accent-emerald',
    },
    {
      id: 'teacher_reference',
      label: 'Ingest Reference Corpus',
      icon: UploadCloud,
      badge: 'Qdrant RAG',
      color: 'text-indigo-400',
    },
    {
      id: 'teacher_analytics',
      label: 'Cohort Intelligence',
      icon: Users,
      badge: 'Analytics',
      color: 'text-accent-amber',
    },
  ];

  const navItems = isTeacher ? teacherNavItems : studentNavItems;

  const handleSelectTab = (id: string) => {
    setActiveTab(id);
    if (setIsMobileMenuOpen) setIsMobileMenuOpen(false);
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-30 lg:hidden animate-fade-in"
          onClick={() => setIsMobileMenuOpen && setIsMobileMenuOpen(false)}
        />
      )}

      <aside
        className={`fixed lg:static top-16 bottom-0 left-0 z-30 bg-slate-950/90 backdrop-blur-xl border-r border-slate-800/80 flex flex-col justify-between transition-all duration-300 ${
          isMobileMenuOpen
            ? 'translate-x-0 w-64'
            : ' -translate-x-full lg:translate-x-0 ' + (isCollapsed ? 'w-20' : 'w-64')
        }`}
      >
        {/* Nav Items */}
        <div className="p-3.5 space-y-1.5 overflow-y-auto">
          <div className="px-3 py-2 flex items-center justify-between">
            <span
              className={`text-[10px] font-bold text-slate-500 uppercase tracking-wider ${
                isCollapsed ? 'hidden' : 'block'
              }`}
            >
              {isTeacher ? 'Faculty Portal' : 'Student Studio'}
            </span>
            {setIsCollapsed && (
              <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="hidden lg:flex p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              >
                {isCollapsed ? (
                  <ChevronRight className="w-3.5 h-3.5" />
                ) : (
                  <ChevronLeft className="w-3.5 h-3.5" />
                )}
              </button>
            )}
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleSelectTab(item.id)}
                className={`w-full flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all relative group ${
                  isActive
                    ? 'bg-gradient-to-r from-primary-600/20 to-primary-600/5 text-white border border-primary-500/30 shadow-lg shadow-primary-500/10'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60'
                }`}
                title={isCollapsed ? item.label : undefined}
              >
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-colors ${
                    isActive
                      ? 'bg-primary-500 text-white shadow-md shadow-primary-500/30'
                      : 'bg-slate-900 group-hover:bg-slate-800 ' + item.color
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                {!isCollapsed && (
                  <div className="flex-1 text-left flex items-center justify-between overflow-hidden">
                    <span className="truncate">{item.label}</span>
                    {item.badge && (
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded-md uppercase tracking-wider ${
                          isActive
                            ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                            : 'bg-slate-800/80 text-slate-500 border border-slate-700/40'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </div>
                )}

                {/* Active Indicator Bar */}
                {isActive && (
                  <span className="absolute left-0 top-2 bottom-2 w-1 bg-primary-500 rounded-r-full shadow-glow" />
                )}
              </button>
            );
          })}
        </div>

        {/* Bottom System Pro Card */}
        {!isCollapsed && (
          <div className="p-3.5 m-3 rounded-2xl bg-gradient-to-br from-slate-900 to-indigo-950/40 border border-slate-800/80 shadow-lg">
            <div className="flex items-center gap-2 mb-1.5">
              <Sparkles className="w-4 h-4 text-accent-cyan" />
              <p className="text-xs font-semibold text-white">Hybrid Reasoning</p>
            </div>
            <p className="text-[10px] text-slate-400 leading-relaxed mb-2.5">
              Deterministic rubrics verified against Qdrant RAG and Neo4j Aura graphs.
            </p>
            <div className="flex items-center justify-between text-[9px] font-mono text-slate-400 pt-2 border-t border-slate-800/80">
              <span>FastEmbed (384-dim)</span>
              <span className="text-emerald-400 font-semibold">Ready</span>
            </div>
          </div>
        )}
      </aside>
    </>
  );
};