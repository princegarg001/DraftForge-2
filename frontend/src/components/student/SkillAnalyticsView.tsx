import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { StudentProgress, LeaderboardEntry, StudentSkill } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import {
  Award,
  TrendingUp,
  CheckCircle2,
  AlertTriangle,
  Trophy,
  Layers,
  Crown,
  Compass,
} from 'lucide-react';

export const SkillAnalyticsView: React.FC = () => {
  const { showToast } = useToast();
  const [progress, setProgress] = useState<StudentProgress | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [skills, setSkills] = useState<StudentSkill[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [pRes, lRes, sRes] = await Promise.all([
        api.getProgress().catch(() => ({ data: null })),
        api.getLeaderboard().catch(() => ({ data: { entries: [] } })),
        api.getSkills().catch(() => ({ data: [] })),
      ]);
      setProgress(pRes.data);
      setLeaderboard(lRes.data?.entries || (Array.isArray(lRes.data) ? lRes.data : []));
      setSkills(sRes.data || []);
    } catch (err: any) {
      showToast('Failed to aggregate student analytics', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <LoadingSpinner size="xl" label="Aggregating continuous evaluation analytics & standings..." />
      </div>
    );
  }

  const averageScore = progress?.average_score || 0;
  const scoreHistory = progress?.score_history || [];
  const docAverages = progress?.document_type_averages || {};

  return (
    <div className="space-y-6 animate-fade-in font-sans">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl glass-panel-glow border border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Drafting Proficiency & Skill Analytics
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              Continuous EMA Evaluation
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Track your score trajectories across revisions, document category averages, and classroom standing.
          </p>
        </div>
      </div>

      {/* 4 Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
            <Award className="w-4 h-4 text-emerald-400" />
            <span>Average Evaluation Score</span>
          </span>
          <p className="text-3xl font-extrabold text-white">
            {averageScore.toFixed(1)} <span className="text-xs font-normal text-slate-500">/ 100</span>
          </p>
          <span className="text-[10px] text-slate-500 font-mono block">
            Across {progress?.total_evaluations || 0} evaluated drafts
          </span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-accent-cyan" />
            <span>Mastered Skills</span>
          </span>
          <p className="text-3xl font-extrabold text-accent-cyan">
            {progress?.mastered_skills_count || 0}
          </p>
          <span className="text-[10px] text-slate-500 font-mono block">
            Proficiency Score ≥ 75%
          </span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>Target Areas</span>
          </span>
          <p className="text-3xl font-extrabold text-rose-400">
            {progress?.weak_skills_count || 0}
          </p>
          <span className="text-[10px] text-slate-500 font-mono block">
            Proficiency Score &lt; 60%
          </span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
            <TrendingUp className="w-4 h-4 text-indigo-400" />
            <span>Skill Trajectory</span>
          </span>
          <p className="text-xl font-bold text-indigo-300 my-1 font-mono">CALIBRATING</p>
          <span className="text-[10px] text-slate-500 font-mono block">
            Active RAG & Neo4j Grounded
          </span>
        </div>
      </div>

      {/* Skill Galaxy & Legal DNA Visualization */}
      {skills.length > 0 && (
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-accent-cyan" />
              <h3 className="font-bold text-sm text-white">
                Legal DNA & Skill Galaxy ({skills.length} Active Vectors)
              </h3>
            </div>
            <span className="text-[10px] font-mono text-slate-400">
              Exponential Moving Average (EMA) Scoring
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {skills.map((sk) => {
              const isMastered = sk.proficiency_score >= 75;
              const isDeveloping = sk.proficiency_score >= 50 && sk.proficiency_score < 75;

              return (
                <div
                  key={sk.id}
                  className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-primary-500/40 space-y-2 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                      {sk.skill?.category || 'LEGAL'}
                    </span>
                    <span
                      className={`text-xs font-mono font-extrabold ${
                        isMastered ? 'text-emerald-400' : isDeveloping ? 'text-amber-400' : 'text-rose-400'
                      }`}
                    >
                      {Math.round(sk.proficiency_score)}%
                    </span>
                  </div>

                  <h4 className="font-bold text-xs text-white truncate">
                    {sk.skill?.name || 'Statutory Drafting'}
                  </h4>

                  {/* Proficiency Bar */}
                  <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${
                        isMastered
                          ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                          : isDeveloping
                          ? 'bg-gradient-to-r from-amber-500 to-yellow-400'
                          : 'bg-gradient-to-r from-rose-500 to-pink-500'
                      }`}
                      style={{ width: `${Math.min(100, sk.proficiency_score)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-12 gap-6">
        {/* Left 6 Cols: Score Trajectory History & Category Averages */}
        <div className="col-span-12 lg:col-span-6 space-y-6">
          {/* Score Trajectory Sparkline */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <h3 className="font-bold text-xs uppercase tracking-wider text-white">
                  Score Progression Across Evaluations
                </h3>
              </div>
              <span className="text-[10px] font-mono text-slate-400">
                {scoreHistory.length} Submissions
              </span>
            </div>

            {scoreHistory.length > 0 ? (
              <div className="space-y-3 pt-2">
                <div className="flex items-end gap-2 h-36 pt-4 px-2">
                  {scoreHistory.map((score, idx) => {
                    const heightPercent = Math.max(10, Math.min(100, score));
                    const isHigh = score >= 75;
                    const isMed = score >= 50;
                    return (
                      <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 group relative">
                        {/* Tooltip */}
                        <div className="absolute -top-7 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white font-mono text-[10px] px-2 py-0.5 rounded border border-slate-700 pointer-events-none whitespace-nowrap z-10">
                          Eval #{idx + 1}: {score} pts
                        </div>
                        <div
                          className={`w-full rounded-t-lg transition-all duration-500 ${
                            isHigh
                              ? 'bg-gradient-to-t from-emerald-600 to-teal-400'
                              : isMed
                              ? 'bg-gradient-to-t from-amber-600 to-yellow-400'
                              : 'bg-gradient-to-t from-rose-600 to-pink-400'
                          }`}
                          style={{ height: `${heightPercent}%` }}
                        />
                        <span className="text-[9px] font-mono text-slate-500">
                          #{idx + 1}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="text-center py-10 text-xs text-slate-500">
                Complete more evaluations to populate your score trajectory.
              </div>
            )}
          </div>

          {/* Document Type Category Averages */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
              <Layers className="w-4 h-4 text-primary-400" />
              <h3 className="font-bold text-xs uppercase tracking-wider text-white">
                Performance by Document Category
              </h3>
            </div>

            <div className="space-y-3">
              {Object.keys(docAverages).length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-500">
                  No category averages recorded yet.
                </div>
              ) : (
                Object.entries(docAverages).map(([type, avg]) => (
                  <div key={type} className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1.5">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-slate-200">{type.replace(/_/g, ' ')}</span>
                      <span className="font-mono text-emerald-400 font-bold">{avg.toFixed(1)} pts</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary-500 to-emerald-400 rounded-full"
                        style={{ width: `${Math.min(100, avg)}%` }}
                      />
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right 6 Cols: Global Classroom Leaderboard */}
        <div className="col-span-12 lg:col-span-6 space-y-6">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Trophy className="w-5 h-5 text-accent-amber" />
                <h3 className="font-bold text-sm text-white">
                  Classroom Standings & Leaderboard
                </h3>
              </div>
              <span className="text-[10px] font-mono text-slate-400">
                {leaderboard.length} Ranked Peers
              </span>
            </div>

            <div className="space-y-2.5">
              {leaderboard.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-500">
                  Leaderboard rankings will update as students complete draft evaluations.
                </div>
              ) : (
                leaderboard.map((entry, idx) => {
                  const isFirst = idx === 0;
                  const isSecond = idx === 1;
                  const isThird = idx === 2;

                  return (
                    <div
                      key={entry.user_id || idx}
                      className={`p-3.5 sm:p-4 rounded-2xl border transition-all flex items-center justify-between ${
                        isFirst
                          ? 'bg-gradient-to-r from-amber-500/15 via-slate-900 to-slate-900 border-amber-500/40 shadow-lg shadow-amber-500/10'
                          : isSecond
                          ? 'bg-gradient-to-r from-slate-300/10 via-slate-900 to-slate-900 border-slate-600'
                          : isThird
                          ? 'bg-gradient-to-r from-amber-700/15 via-slate-900 to-slate-900 border-amber-700/30'
                          : 'bg-slate-900/60 border-slate-800'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-7 h-7 rounded-xl flex items-center justify-center font-bold text-xs shrink-0 ${
                            isFirst
                              ? 'bg-amber-400 text-slate-950 shadow-md'
                              : isSecond
                              ? 'bg-slate-300 text-slate-950'
                              : isThird
                              ? 'bg-amber-700 text-white'
                              : 'bg-slate-800 text-slate-400 font-mono text-[11px]'
                          }`}
                        >
                          {isFirst ? (
                            <Crown className="w-4 h-4" />
                          ) : (
                            `#${idx + 1}`
                          )}
                        </div>

                        <div>
                          <p className="font-bold text-xs text-white">
                            {entry.full_name || `Student ${entry.user_id?.substring(0, 6)}`}
                          </p>
                          <span className="text-[10px] text-slate-500 font-mono">
                            {entry.evaluations_completed || 0} evaluations
                          </span>
                        </div>
                      </div>

                      <div className="text-right">
                        <span className="font-mono font-extrabold text-sm text-emerald-400">
                          {entry.average_score?.toFixed(1) || 0}
                        </span>
                        <span className="text-[10px] text-slate-500 block font-mono">
                          pts avg
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};