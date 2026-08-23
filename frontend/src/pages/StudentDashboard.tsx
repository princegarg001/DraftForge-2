import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { StudentProgress } from '../types';
import { DraftWorkspace } from '../components/student/DraftWorkspace';
import { StudentAssignmentsView } from '../components/student/StudentAssignmentsView';
import { EvaluationCard } from '../components/student/EvaluationCard';
import { LoopholeViewer } from '../components/student/LoopholeViewer';
import { TutorChat } from '../components/student/TutorChat';
import { RoadmapView } from '../components/student/RoadmapView';
import { QuizRunner } from '../components/student/QuizRunner';
import { SkillAnalyticsView } from '../components/student/SkillAnalyticsView';
import { ReferenceCorpusView } from '../components/student/ReferenceCorpusView';
import {
  FileEdit,
  GraduationCap,
  MessageSquare,
  FolderArchive,
  Sparkles,
} from 'lucide-react';

interface StudentDashboardProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({
  activeTab,
  setActiveTab,
}) => {
  const { user } = useAuth();
  const [selectedEvaluationId, setSelectedEvaluationId] = useState<string>('');
  const [learningSubtab, setLearningSubtab] = useState<'roadmap' | 'tutor'>('roadmap');

  // Real Metric States loaded from backend
  const [progress, setProgress] = useState<StudentProgress | null>(null);
  const [draftsCount, setDraftsCount] = useState<number>(0);
  const [skillsCount, setSkillsCount] = useState<number>(0);
  const [assignmentsCount, setAssignmentsCount] = useState<number>(0);

  useEffect(() => {
    const fetchQuickMetrics = async () => {
      try {
        const [progRes, draftRes, skillRes, assignRes] = await Promise.allSettled([
          api.getProgress(),
          api.getDrafts(),
          api.getSkills(),
          api.getAssignments(),
        ]);

        if (progRes.status === 'fulfilled') setProgress(progRes.value.data);
        if (draftRes.status === 'fulfilled') setDraftsCount(draftRes.value.data?.length || 0);
        if (skillRes.status === 'fulfilled') setSkillsCount(skillRes.value.data?.length || 0);
        if (assignRes.status === 'fulfilled') setAssignmentsCount(assignRes.value.data?.length || 0);
      } catch {
        // graceful fallback to zero metrics
      }
    };
    fetchQuickMetrics();
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const handleSelectEvaluation = (id: string) => {
    setSelectedEvaluationId(id);
    setActiveTab('evaluations');
  };

  const handleNavigateToLoopholes = (id: string) => {
    setSelectedEvaluationId(id);
    setActiveTab('loopholes');
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6 animate-fade-in font-sans">
      {/* ========================================================================= */}
      {/* 1. STUDENT EXECUTIVE HERO BANNER */}
      {/* ========================================================================= */}
      <div className="relative glass-panel-glow p-6 sm:p-8 rounded-3xl border border-slate-800 shadow-2xl overflow-hidden">
        {/* Background Ambient Glows */}
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-primary-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-16 -bottom-16 w-64 h-64 bg-accent-cyan/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          {/* Left Title & Status */}
          <div className="space-y-2">
            <div className="flex items-center gap-2.5">
              <span className="px-3 py-1 rounded-full text-[10px] font-bold bg-primary-500/10 text-primary-300 border border-primary-500/20 uppercase tracking-wider font-mono">
                Legal Drafting Studio
              </span>
              <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>Qdrant & Neo4j Active</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {getGreeting()},{' '}
              <span className="gradient-text-primary">
                {user?.full_name || 'Legal Scholar'}
              </span>
            </h1>

            <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
              Continue crafting evidence-grounded legal drafts. Review automated 100-point rubric evaluations, explore graph loopholes, and elevate your statutory drafting proficiency.
            </p>

            {/* Quick Action Navigation Chips */}
            <div className="flex flex-wrap items-center gap-2 pt-2">
              <button
                onClick={() => setActiveTab('workspace')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'workspace'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <FileEdit className="w-3.5 h-3.5 text-primary-400" />
                <span>Open Workspace</span>
              </button>

              <button
                onClick={() => setActiveTab('assignments')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'assignments'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <FolderArchive className="w-3.5 h-3.5 text-accent-cyan" />
                <span>Coursework ({assignmentsCount})</span>
              </button>

              <button
                onClick={() => {
                  setLearningSubtab('roadmap');
                  setActiveTab('learning');
                }}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'learning'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <GraduationCap className="w-3.5 h-3.5 text-accent-amber" />
                <span>5-Phase Roadmap</span>
              </button>

              <button
                onClick={() => setActiveTab('quizzes')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'quizzes'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                <span>Quizzes</span>
              </button>
            </div>
          </div>

          {/* Right Real Metrics Ribbon */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950/70 p-4 rounded-2xl border border-slate-800/80 shadow-inner">
            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-center space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono block">
                Total Drafts
              </span>
              <span className="text-xl font-extrabold text-white font-mono">{draftsCount}</span>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-center space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono block">
                Evaluations
              </span>
              <span className="text-xl font-extrabold text-primary-400 font-mono">
                {progress?.total_evaluations ?? 0}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-center space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono block">
                Average Score
              </span>
              <span className="text-xl font-extrabold text-emerald-400 font-mono">
                {progress ? Math.round(progress.average_score) : 0}
                <span className="text-[10px] font-normal text-slate-400">/100</span>
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-center space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono block">
                Skills Active
              </span>
              <span className="text-xl font-extrabold text-accent-cyan font-mono">
                {skillsCount}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 2. ACTIVE TAB RENDERER */}
      {/* ========================================================================= */}
      <div className="space-y-6">
        {/* Tab: Legal Drafting Workspace */}
        {activeTab === 'workspace' && (
          <DraftWorkspace
            onSelectEvaluation={handleSelectEvaluation}
            onNavigateToLoopholes={handleNavigateToLoopholes}
          />
        )}

        {/* Tab: Class Assignments */}
        {activeTab === 'assignments' && (
          <StudentAssignmentsView
            onSelectEvaluation={handleSelectEvaluation}
            onNavigateToWorkspace={() => setActiveTab('workspace')}
          />
        )}

        {/* Tab: Evaluation & Evidence */}
        {activeTab === 'evaluations' && (
          <EvaluationCard
            evaluationId={selectedEvaluationId}
            onNavigateToLoopholes={handleNavigateToLoopholes}
            onNavigateToWorkspace={() => setActiveTab('workspace')}
          />
        )}

        {/* Tab: Neo4j GraphRAG Loopholes */}
        {activeTab === 'loopholes' && (
          <LoopholeViewer
            evaluationId={selectedEvaluationId}
            onNavigateToWorkspace={() => setActiveTab('workspace')}
          />
        )}

        {/* Tab: AI Roadmap & Socratic Tutor */}
        {activeTab === 'learning' && (
          <div className="space-y-6">
            {/* Subtab Bar */}
            <div className="flex items-center gap-2 p-1 bg-slate-900/90 rounded-2xl border border-slate-800 w-fit">
              <button
                onClick={() => setLearningSubtab('roadmap')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  learningSubtab === 'roadmap'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <GraduationCap className="w-3.5 h-3.5" />
                <span>5-Phase Learning Roadmap</span>
              </button>
              <button
                onClick={() => setLearningSubtab('tutor')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  learningSubtab === 'tutor'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Socratic AI Tutor Chat</span>
              </button>
            </div>

            {learningSubtab === 'roadmap' ? <RoadmapView /> : <TutorChat />}
          </div>
        )}

        {/* Tab: Interactive Quizzes */}
        {activeTab === 'quizzes' && <QuizRunner />}

        {/* Tab: Skills & Leaderboard */}
        {activeTab === 'progress' && <SkillAnalyticsView />}

        {/* Tab: Legal Reference Corpus */}
        {activeTab === 'reference_corpus' && <ReferenceCorpusView />}
      </div>
    </div>
  );
};