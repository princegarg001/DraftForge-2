import React, { useState } from 'react';
import { Search, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';
import { Modal } from './Modal';
import { api } from '../../services/api';
import { DocumentClassificationResult } from '../../types';
import { LoadingSpinner } from './LoadingSpinner';

interface ClassifierModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectType?: (type: string) => void;
}

export const ClassifierModal: React.FC<ClassifierModalProps> = ({
  isOpen,
  onClose,
  onSelectType,
}) => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DocumentClassificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleClassify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await api.classifyText(text);
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Document classification failed.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setText('');
    setResult(null);
    setError(null);
  };

  const handleApply = () => {
    if (result && onSelectType) {
      onSelectType(result.detected_type);
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {
        resetForm();
        onClose();
      }}
      title="Rule-Based Document Classifier"
      subtitle="Paste raw legal text to detect statutory document classification and structural confidence"
      icon={<Sparkles className="w-5 h-5" />}
      maxWidth="2xl"
    >
      <div className="space-y-5">
        <form onSubmit={handleClassify} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Legal Draft Content / Excerpt
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste deed text, recital preamble, or affidavit verification clause..."
              rows={6}
              className="w-full bg-slate-900/80 border border-slate-700/80 rounded-xl p-3.5 text-sm text-slate-100 placeholder-slate-500 font-mono focus-ring"
            />
          </div>

          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() =>
                setText(
                  "I, Ramesh Kumar, son of Late Shri Suresh Kumar, aged about 24 years, resident of Sector 14, Gurugram, do hereby solemnly affirm and declare on oath that I am applying for enrollment as an Advocate before the Bar Council..."
                )
              }
              className="text-xs text-primary-400 hover:text-primary-300 font-medium underline"
            >
              Insert sample affidavit excerpt
            </button>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={resetForm}
                className="px-3 py-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
              >
                Clear
              </button>
              <button
                type="submit"
                disabled={loading || !text.trim()}
                className="px-4 py-2 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white text-xs font-semibold rounded-xl flex items-center gap-2 shadow-lg shadow-primary-500/20 disabled:opacity-50 transition-all"
              >
                {loading ? <LoadingSpinner size="sm" /> : <Search className="w-3.5 h-3.5" />}
                Analyze Structure
              </button>
            </div>
          </div>
        </form>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}

        {result && (
          <div className="p-5 rounded-2xl bg-slate-800/50 border border-primary-500/30 space-y-3 animate-fade-in-up">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white">
                    {result.detected_type.replace(/_/g, ' ')}
                  </h4>
                  <p className="text-xs text-slate-400">
                    Structural Match Confidence:{' '}
                    <span className="text-emerald-400 font-semibold">
                      {(result.confidence * 100).toFixed(0)}%
                    </span>
                  </p>
                </div>
              </div>
              <span className="px-2.5 py-1 bg-primary-500/10 text-primary-400 text-xs font-semibold rounded-lg border border-primary-500/20 font-mono">
                {result.detected_type}
              </span>
            </div>

            <p className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-700/40">
              {result.summary}
            </p>

            {onSelectType && (
              <div className="flex justify-end pt-1">
                <button
                  onClick={handleApply}
                  className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-colors border border-slate-700"
                >
                  Apply Document Type <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </Modal>
  );
};
