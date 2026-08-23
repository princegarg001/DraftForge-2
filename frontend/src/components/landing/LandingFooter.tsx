import React from 'react';
import {
  Scale,
} from 'lucide-react';

interface LandingFooterProps {
  onOpenAuth: () => void;
  onOpenHealth?: () => void;
}

export const LandingFooter: React.FC<LandingFooterProps> = ({
  onOpenAuth,
  onOpenHealth,
}) => {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950/90 pt-16 pb-12 text-slate-400 font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Col 1: Brand & Positioning */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-primary-600 to-accent-cyan p-0.5 shadow-lg shadow-primary-500/20">
                <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                  <Scale className="w-5 h-5 text-primary-400" />
                </div>
              </div>
              <span className="text-xl font-extrabold text-white tracking-tight">
                Draft<span className="text-primary-400">Forge</span>
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed max-w-sm">
              The AI-powered legal drafting, evaluation, and learning platform. Built for law students, legal scholars, and faculty with deterministic rubric precision, dense vector retrieval, and Neo4j knowledge graph reasoning.
            </p>

            {onOpenHealth && (
              <button
                onClick={onOpenHealth}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-mono text-emerald-400 transition-colors"
              >
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>System Telemetry & Architecture Health</span>
              </button>
            )}
          </div>

          {/* Col 2: Core Platform */}
          <div className="space-y-3 text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px]">
              Platform Modules
            </h4>
            <ul className="space-y-2 text-slate-400">
              <li>
                <a href="#scanner" className="hover:text-primary-300 transition-colors">
                  Interactive Scanner
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-primary-300 transition-colors">
                  AI Drafting Copilot
                </a>
              </li>
              <li>
                <a href="#ai-evaluation" className="hover:text-primary-300 transition-colors">
                  Deterministic Rubrics
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-primary-300 transition-colors">
                  GraphRAG Loopholes
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-primary-300 transition-colors">
                  Reference Precedent Corpus
                </a>
              </li>
            </ul>
          </div>

          {/* Col 3: Student Studio */}
          <div className="space-y-3 text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px]">
              For Students
            </h4>
            <ul className="space-y-2 text-slate-400">
              <li>
                <a href="#students" className="hover:text-primary-300 transition-colors">
                  Legal Drafting Workspace
                </a>
              </li>
              <li>
                <a href="#students" className="hover:text-primary-300 transition-colors">
                  5-Phase Learning Roadmap
                </a>
              </li>
              <li>
                <a href="#students" className="hover:text-primary-300 transition-colors">
                  Socratic AI Tutor Chat
                </a>
              </li>
              <li>
                <a href="#students" className="hover:text-primary-300 transition-colors">
                  Interactive Statutory Quizzes
                </a>
              </li>
              <li>
                <a href="#students" className="hover:text-primary-300 transition-colors">
                  Skill Mastery Matrix (EMA)
                </a>
              </li>
            </ul>
          </div>

          {/* Col 4: Faculty Studio */}
          <div className="space-y-3 text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px]">
              For Faculty
            </h4>
            <ul className="space-y-2 text-slate-400">
              <li>
                <a href="#faculty" className="hover:text-primary-300 transition-colors">
                  Assignment Manager
                </a>
              </li>
              <li>
                <a href="#faculty" className="hover:text-primary-300 transition-colors">
                  Submissions Auditor & Grading
                </a>
              </li>
              <li>
                <a href="#faculty" className="hover:text-primary-300 transition-colors">
                  Audited Score Overrides
                </a>
              </li>
              <li>
                <a href="#faculty" className="hover:text-primary-300 transition-colors">
                  Reference Corpus Ingestion
                </a>
              </li>
              <li>
                <a href="#faculty" className="hover:text-primary-300 transition-colors">
                  Cohort Weak-Skill Analytics
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs text-slate-500">
          <p>© {new Date().getFullYear()} DraftForge AI. All rights reserved. Deterministic LegalTech Platform.</p>
          <div className="flex items-center gap-6">
            <span className="font-mono text-[11px]">
              FastEmbed • Qdrant • Neo4j Aura • Supabase
            </span>
            <button
              onClick={onOpenAuth}
              className="text-primary-400 hover:text-primary-300 font-semibold"
            >
              Sign In to Portal →
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};
