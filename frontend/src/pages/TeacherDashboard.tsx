import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { CohortAnalytics } from '../types';
import { AssignmentManager } from '../components/teacher/AssignmentManager';
import { SubmissionsAuditor } from '../components/teacher/SubmissionsAuditor';
import { CohortAnalyticsView } from '../components/teacher/CohortAnalyticsView';
import { ReferenceUploader } from '../components/teacher/ReferenceUploader';
import { ClassManager } from '../components/teacher/ClassManager';
import {
  FileCheck,
  ClipboardCheck,
  UploadCloud,
  Users,
  School,
} from 'lucide-react';

interface TeacherDashboardProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const TeacherDashboard: React.FC<TeacherDashboardProps> = ({
  activeTab,
  setActiveTab,
}) => {
  const { user } = useAuth();
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<string>('');
  const [cohort, setCohort] = useState<CohortAnalytics | null>(null);
  const [assignmentsCount, setAssignmentsCount] = useState<number>(0);

  useEffect(() => {
    const fetchTeacherMetrics = async () => {
      try {
        const [cRes, aRes] = await Promise.allSettled([
          api.getCohortAnalytics(),
          api.getTeacherAssignments(),
        ]);
        if (cRes.status === 'fulfilled') setCohort(cRes.value.data);
        if (aRes.status === 'fulfilled') setAssignmentsCount(aRes.value.data?.length || 0);
      } catch {
        // graceful fallback
      }
    };
    fetchTeacherMetrics();
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const handleSelectAssignment = (id: string) => {
    setSelectedAssignmentId(id);
    setActiveTab('teacher_submissions');
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6 animate-fade-in font-sans">
      {/* ========================================================================= */}
      {/* 1. TEACHER EXECUTIVE COMMAND BANNER */}
      {/* ========================================================================= */}
      <div className="relative glass-panel-glow p-6 sm:p-8 rounded-3xl border border-slate-800 shadow-2xl overflow-hidden">
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-accent-cyan/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-16 -bottom-16 w-64 h-64 bg-primary-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          {/* Left Title & Actions */}
          <div className="space-y-2">
            <div className="flex items-center gap-2.5">
              <span className="px-3 py-1 rounded-full text-[10px] font-bold bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 uppercase tracking-wider font-mono">
                Faculty Governance Portal
              </span>
              <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>Qdrant FastEmbed Active</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {getGreeting()},{' '}
              <span className="gradient-text-cyan">
                {user?.full_name || 'Professor'}
              </span>
            </h1>

            <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
              Supervise student legal drafting submissions, review automated 100-point rubric evaluations, ingest statutory reference deeds into Qdrant, and track cohort skill distributions.
            </p>

            {/* Quick Action Chips */}
            <div className="flex flex-wrap items-center gap-2 pt-2">
              <button
                onClick={() => setActiveTab('teacher_classes')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'teacher_classes'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <School className="w-3.5 h-3.5 text-primary-400" />
                <span>Classes &amp; Roster</span>
              </button>

              <button
                onClick={() => setActiveTab('teacher_assignments')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'teacher_assignments'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <FileCheck className="w-3.5 h-3.5 text-accent-cyan" />
                <span>Manage Assignments</span>
              </button>

              <button
                onClick={() => setActiveTab('teacher_submissions')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'teacher_submissions'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <ClipboardCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Submissions Auditor</span>
              </button>

              <button
                onClick={() => setActiveTab('teacher_reference')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'teacher_reference' || activeTab === 'teacher_references'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <UploadCloud className="w-3.5 h-3.5 text-indigo-400" />
                <span>Ingest Reference Deeds</span>
              </button>

              <button
                onClick={() => setActiveTab('teacher_analytics')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'teacher_analytics'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <Users className="w-3.5 h-3.5 text-accent-amber" />
                <span>Cohort Analytics</span>
              </button>
            </div>
          </div>

          {/* Right Real Metrics Ribbon */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950/70 p-4 rounded-2xl border border-slate-800/80 shadow-inner">
            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-center space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono block">
                Active Briefs
              </span>
              <span className="text-xl font-extrabold text-white font-mono">{assignmentsCount}</span>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-center space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono block">
                Total Students
              </span>
              <span className="text-xl font-extrabold text-accent-cyan font-mono">
                {cohort?.total_students ?? 0}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-center space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono block">
                Cohort Avg
              </span>
              <span className="text-xl font-extrabold text-emerald-400 font-mono">
                {cohort ? Math.round(cohort.cohort_average_score) : 0}
                <span className="text-[10px] font-normal text-slate-400">/100</span>
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-center space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-semibold font-mono block">
                Evaluations
              </span>
              <span className="text-xl font-extrabold text-primary-400 font-mono">
                {cohort?.total_evaluations ?? 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 2. ACTIVE TEACHER TAB VIEW */}
      {/* ========================================================================= */}
      <div className="space-y-6">
        {activeTab === 'teacher_classes' && <ClassManager />}
        {activeTab === 'teacher_assignments' && (
          <AssignmentManager onSelectAssignment={handleSelectAssignment} />
        )}
        {activeTab === 'teacher_submissions' && (
          <SubmissionsAuditor assignmentId={selectedAssignmentId} />
        )}
        {activeTab === 'teacher_analytics' && <CohortAnalyticsView />}
        {(activeTab === 'teacher_reference' || activeTab === 'teacher_references') && (
          <ReferenceUploader />
        )}
      </div>
    </div>
  );
};