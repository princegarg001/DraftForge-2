import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Quiz, DocumentType, QuizAttemptResponse } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import {
  Award,
  Sparkles,
  BookOpen,
  PenTool,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  HelpCircle,
  ArrowRight,
} from 'lucide-react';

export const QuizRunner: React.FC = () => {
  const { showToast } = useToast();
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizAttemptResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [filterType, setFilterType] = useState<string>('ALL');

  // AI Practice Studio
  const [activeTab, setActiveTab] = useState<'standard' | 'ai_exercise'>('standard');
  const [exerciseDocType, setExerciseDocType] = useState<DocumentType>('EMPLOYMENT_AGREEMENT');
  const [targetSkill, setTargetSkill] = useState('Termination & Section 27 Restrictive Covenants');
  const [difficulty, setDifficulty] = useState('INTERMEDIATE');
  const [generatingExercise, setGeneratingExercise] = useState(false);
  const [generatedExercise, setGeneratedExercise] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  const fetchQuizzes = async () => {
    setLoading(true);
    try {
      const res = await api.getQuizzes(filterType === 'ALL' ? undefined : filterType);
      setQuizzes(res.data || []);
    } catch (err: any) {
      showToast('Failed to load quizzes', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuizzes();
  }, [filterType]);

  const handleSelectQuiz = async (quizId: string) => {
    setLoading(true);
    try {
      const res = await api.getQuiz(quizId);
      setActiveQuiz(res.data);
      setAnswers({});
      setResult(null);
    } catch (err: any) {
      showToast('Failed to load quiz questions', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!activeQuiz) return;
    setSubmitting(true);
    try {
      const res = await api.submitQuiz({
        quiz_id: activeQuiz.id,
        answers,
      });
      setResult(res.data);
      if (res.data.passed) {
        showToast(`Congratulations! You passed with ${res.data.score}%`, 'success');
      } else {
        showToast(`Quiz completed: ${res.data.score}%. Review explanations below.`, 'info');
      }
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Quiz submission failed', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleGenerateAIExercise = async () => {
    setGeneratingExercise(true);
    setGeneratedExercise(null);
    setCopied(false);

    try {
      const res = await api.assistDrafting({
        document_type: exerciseDocType,
        target_clause: targetSkill,
        user_instructions: `Generate a drafting practice scenario with difficulty ${difficulty}. Include drafting instructions, pitfalls to avoid under Indian law, and a model compliant clause.`,
      });
      setGeneratedExercise(res.data);
      showToast('Practice scenario synthesized from statutory corpus', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to synthesize exercise', 'error');
    } finally {
      setGeneratingExercise(false);
    }
  };

  const copyClauseText = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    showToast('Model template copied to clipboard', 'info');
    setTimeout(() => setCopied(false), 2000);
  };

  const templateText = generatedExercise?.drafted_clause || generatedExercise?.generated_draft || '';
  const commentaryText = generatedExercise?.commentary || '';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl glass-panel-glow border border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-white tracking-tight">Legal Quizzes & Practice Studio</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-accent-amber/10 text-accent-amber border border-accent-amber/20 font-mono">
              Knowledge Verification
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Test statutory mechanics with interactive multiple-choice questions or generate AI drafting scenarios.
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 rounded-xl border border-slate-800">
          <button
            onClick={() => {
              setActiveTab('standard');
              setActiveQuiz(null);
            }}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'standard'
                ? 'bg-primary-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Statutory Quizzes ({quizzes.length})
          </button>
          <button
            onClick={() => {
              setActiveTab('ai_exercise');
              setActiveQuiz(null);
            }}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'ai_exercise'
                ? 'bg-primary-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-accent-cyan" />
            <span>AI Practice Studio</span>
          </button>
        </div>
      </div>

      {/* VIEW 1: Standard Quizzes Catalog */}
      {activeTab === 'standard' && !activeQuiz && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Available Tests
            </span>

            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300 focus-ring"
            >
              <option value="ALL">All Categories</option>
              <option value="AFFIDAVIT_OF_CHARACTER">Affidavit of Character</option>
              <option value="EMPLOYMENT_AGREEMENT">Employment Agreement</option>
              <option value="RENT_AGREEMENT">Rent Agreement</option>
              <option value="LEGAL_NOTICE">Legal Notice</option>
            </select>
          </div>

          {loading ? (
            <div className="py-20 flex justify-center">
              <LoadingSpinner size="lg" label="Loading legal quizzes..." />
            </div>
          ) : quizzes.length === 0 ? (
            <div className="glass-panel p-12 text-center rounded-3xl border border-slate-800 space-y-3">
              <HelpCircle className="w-12 h-12 text-slate-600 mx-auto" />
              <h3 className="text-sm font-semibold text-white">No Quizzes Found</h3>
              <p className="text-xs text-slate-400">
                No interactive quizzes match the selected category filter.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {quizzes.map((q) => (
                <div
                  key={q.id}
                  onClick={() => handleSelectQuiz(q.id)}
                  className="glass-panel p-6 rounded-3xl border border-slate-800 hover:border-primary-500/40 cursor-pointer transition-all space-y-4 flex flex-col justify-between group"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-slate-900 text-slate-300 border border-slate-700">
                        {q.document_type.replace(/_/g, ' ')}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          q.difficulty === 'ADVANCED'
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : q.difficulty === 'INTERMEDIATE'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}
                      >
                        {q.difficulty}
                      </span>
                    </div>

                    <h3 className="font-bold text-sm text-white group-hover:text-primary-300 transition-colors">
                      {q.title}
                    </h3>
                    {q.description && (
                      <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
                        {q.description}
                      </p>
                    )}
                  </div>

                  <button className="w-full py-2 bg-slate-900 group-hover:bg-primary-600 border border-slate-800 group-hover:border-primary-500 text-slate-300 group-hover:text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all">
                    <span>Start Test</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* VIEW 2: Active Quiz Runner */}
      {activeTab === 'standard' && activeQuiz && (
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-700">
                  {activeQuiz.document_type}
                </span>
                <span className="text-[10px] font-bold text-accent-amber">
                  Difficulty: {activeQuiz.difficulty}
                </span>
              </div>
              <h2 className="text-lg font-bold text-white mt-1">{activeQuiz.title}</h2>
            </div>

            <button
              onClick={() => {
                setActiveQuiz(null);
                setResult(null);
              }}
              className="text-xs text-slate-400 hover:text-white font-medium self-start sm:self-auto"
            >
              ← Back to Quizzes Catalogue
            </button>
          </div>

          {/* Questions Stream */}
          <div className="space-y-6">
            {activeQuiz.questions?.map((q, idx) => {
              const selectedOption = answers[q.id];
              return (
                <div
                  key={q.id}
                  className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-4"
                >
                  <p className="text-xs font-semibold text-white leading-relaxed">
                    <span className="font-mono text-primary-400 mr-2">Q{idx + 1}.</span>
                    {q.question_text}
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {q.options.map((opt) => {
                      const isSelected = selectedOption === opt.key;
                      return (
                        <button
                          key={opt.key}
                          type="button"
                          onClick={() => setAnswers({ ...answers, [q.id]: opt.key })}
                          className={`p-3.5 rounded-xl text-xs text-left border transition-all flex items-start gap-2.5 ${
                            isSelected
                              ? 'bg-primary-600/20 text-white border-primary-500 shadow-md shadow-primary-500/10'
                              : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-900/80'
                          }`}
                        >
                          <span
                            className={`font-mono text-xs font-bold px-1.5 py-0.5 rounded shrink-0 ${
                              isSelected
                                ? 'bg-primary-500 text-white'
                                : 'bg-slate-800 text-slate-400'
                            }`}
                          >
                            {opt.key}
                          </span>
                          <span className="leading-relaxed">{opt.text}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Submit Action or Evaluation Result Card */}
          {!result ? (
            <div className="flex justify-end pt-3">
              <button
                onClick={handleSubmit}
                disabled={submitting || Object.keys(answers).length === 0}
                className="px-6 py-2.5 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary-500/25 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {submitting ? <LoadingSpinner size="sm" /> : <CheckCircle2 className="w-4 h-4" />}
                <span>Submit Quiz for Instant Scoring</span>
              </button>
            </div>
          ) : (
            <div className="p-6 rounded-2xl bg-slate-900/90 border border-primary-500/30 space-y-5 animate-fade-in-up">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-accent-amber/10 border border-accent-amber/20 flex items-center justify-center text-accent-amber">
                    <Award className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-white">
                      Score: {result.score.toFixed(0)}%
                    </h3>
                    <p className="text-xs text-slate-400 font-mono">
                      Answered: {Object.keys(answers).length} of {result.total_questions} questions
                    </p>
                  </div>
                </div>

                <span
                  className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                    result.passed
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  }`}
                >
                  {result.passed ? 'PASSED (>= 70%)' : 'NEEDS REVISION'}
                </span>
              </div>

              {/* Explanations Breakdown */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Itemized Question Explanations
                </h4>
                {result.breakdown?.map((b, i) => (
                  <div
                    key={i}
                    className={`p-4 rounded-xl text-xs space-y-2 border ${
                      b.is_correct
                        ? 'bg-emerald-950/20 border-emerald-500/30'
                        : 'bg-rose-950/20 border-rose-500/30'
                    }`}
                  >
                    <div className="flex items-center justify-between font-semibold">
                      <div className="flex items-center gap-2">
                        {b.is_correct ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                          <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                        )}
                        <span className="text-white">Question {i + 1}</span>
                      </div>
                      <span className="font-mono text-[11px] text-slate-400">
                        Correct Option: <strong className="text-emerald-400 font-bold">{b.correct_answer}</strong>
                      </span>
                    </div>
                    <p className="text-slate-300 text-xs leading-relaxed">{b.explanation}</p>
                  </div>
                ))}
              </div>

              <div className="flex justify-end pt-2">
                <button
                  onClick={() => {
                    setActiveQuiz(null);
                    setResult(null);
                  }}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-xl transition-colors"
                >
                  Return to Catalogue
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* VIEW 3: AI Practice Exercise Generator Studio */}
      {activeTab === 'ai_exercise' && (
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 lg:col-span-5 glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800">
              <Sparkles className="w-5 h-5 text-accent-cyan" />
              <h3 className="font-bold text-sm text-white">AI Scenario Generator</h3>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Target Legal Document
              </label>
              <select
                value={exerciseDocType}
                onChange={(e) => setExerciseDocType(e.target.value as DocumentType)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus-ring"
              >
                <option value="AFFIDAVIT_OF_CHARACTER">Affidavit of Character (India)</option>
                <option value="EMPLOYMENT_AGREEMENT">Employment Agreement (India)</option>
                <option value="RENT_AGREEMENT">Residential Rent Deed (India)</option>
                <option value="LEGAL_NOTICE">Statutory Legal Notice</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Focus Legal Clause / Concept
              </label>
              <input
                type="text"
                value={targetSkill}
                onChange={(e) => setTargetSkill(e.target.value)}
                placeholder="e.g. Verification Jurat, Section 27 Restraint of Trade, Notice Period"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus-ring"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Difficulty Level
              </label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus-ring"
              >
                <option value="BEGINNER">Beginner (Foundational Structures)</option>
                <option value="INTERMEDIATE">Intermediate (Statutory Enforceability)</option>
                <option value="ADVANCED">Advanced (Cross-Clause Risk Mitigation)</option>
              </select>
            </div>

            <button
              onClick={handleGenerateAIExercise}
              disabled={generatingExercise || !targetSkill.trim()}
              className="w-full py-2.5 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary-500/25 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {generatingExercise ? <LoadingSpinner size="sm" /> : <Sparkles className="w-4 h-4" />}
              <span>Synthesize Practice Scenario</span>
            </button>
          </div>

          <div className="col-span-12 lg:col-span-7 glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <PenTool className="w-4 h-4 text-accent-cyan" />
                <h3 className="font-bold text-sm text-white">Generated Scenario & Model Solution</h3>
              </div>

              {templateText && (
                <button
                  onClick={() => copyClauseText(templateText)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white rounded-xl text-xs font-semibold border border-slate-700 transition-all"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy Clause'}</span>
                </button>
              )}
            </div>

            {generatingExercise ? (
              <div className="py-20 flex justify-center">
                <LoadingSpinner size="lg" label="Synthesizing compliant drafting challenge..." />
              </div>
            ) : templateText ? (
              <div className="space-y-4 animate-fade-in">
                <div className="p-4 bg-slate-950/90 rounded-2xl border border-slate-800 space-y-2">
                  <span className="font-bold text-xs text-primary-400 uppercase tracking-wider">
                    Model Statutory Draft:
                  </span>
                  <pre className="text-xs font-mono text-slate-200 whitespace-pre-wrap leading-relaxed p-3 bg-slate-900 rounded-xl border border-slate-800">
                    {templateText}
                  </pre>
                </div>

                {commentaryText && (
                  <div className="p-4 bg-primary-950/20 rounded-2xl border border-primary-500/20 space-y-2 text-xs">
                    <span className="font-bold text-emerald-400 uppercase tracking-wider">
                      Statutory Commentary & Enforceability Notes:
                    </span>
                    <p className="text-slate-300 leading-relaxed whitespace-pre-line">
                      {commentaryText}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="py-20 text-center text-xs text-slate-500 space-y-2">
                <BookOpen className="w-10 h-10 text-slate-700 mx-auto" />
                <p>Configure parameters on the left and click &ldquo;Synthesize Practice Scenario&rdquo; to generate bespoke drafting challenges.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};