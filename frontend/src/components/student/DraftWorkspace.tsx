import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Draft, DocumentType, VersionCompareResponse, EvidenceChunk, AssistDraftingResponse, Evaluation } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import { AIEvaluationModal } from '../ai/AIEvaluationModal';
import {
  FileText,
  Upload,
  Sparkles,
  GitCompare,
  Plus,
  Search,
  BookOpen,
  Clock,
  Layers,
  Save,
  FileCheck2,
} from 'lucide-react';

interface DraftWorkspaceProps {
  onSelectEvaluation: (evalId: string) => void;
  onNavigateToLoopholes?: (evalId: string) => void;
}

export const DraftWorkspace: React.FC<DraftWorkspaceProps> = ({
  onSelectEvaluation,
  onNavigateToLoopholes,
}) => {
  const { showToast } = useToast();
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [selectedDraft, setSelectedDraft] = useState<Draft | null>(null);
  const [currentVersionNumber, setCurrentVersionNumber] = useState<number>(1);
  const [title, setTitle] = useState('');
  const [docType, setDocType] = useState<DocumentType>('AFFIDAVIT_OF_CHARACTER');
  const [rawContent, setRawContent] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('ALL');

  // UI state
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const [activeSidePanel, setActiveSidePanel] = useState<'ai_assist' | 'rag_search' | 'diff' | null>(null);

  // 3D AI Evaluation Modal State
  const [isAiEvalModalOpen, setIsAiEvalModalOpen] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<Evaluation | null>(null);

  // Version Comparison
  const [diffVersion1, setDiffVersion1] = useState<number>(1);
  const [diffVersion2, setDiffVersion2] = useState<number>(2);
  const [diffResult, setDiffResult] = useState<VersionCompareResponse | null>(null);
  const [diffLoading, setDiffLoading] = useState(false);

  // AI Assist State
  const [targetClause, setTargetClause] = useState('Verification & Perjury Jurat');
  const [userInstructions, setUserInstructions] = useState('');
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiAssistResult, setAiAssistResult] = useState<AssistDraftingResponse | null>(null);

  // RAG Search State
  const [ragQuery, setRagQuery] = useState('');
  const [ragLoading, setRagLoading] = useState(false);
  const [ragResults, setRagResults] = useState<EvidenceChunk[]>([]);

  const fetchDrafts = async () => {
    setLoading(true);
    try {
      const res = await api.getDrafts();
      setDrafts(res.data);
      if (res.data.length > 0 && !selectedDraft) {
        selectDraftItem(res.data[0]);
      }
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to fetch drafts', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrafts();
  }, []);

  const selectDraftItem = (draft: Draft) => {
    setSelectedDraft(draft);
    setIsCreatingNew(false);
    setDocType(draft.document_type);
    setTitle(draft.title);
    const versions = draft.versions || [];
    if (versions.length > 0) {
      const latest = versions[versions.length - 1];
      setCurrentVersionNumber(latest.version_number);
      setRawContent(latest.raw_content);
    } else {
      setRawContent('');
    }
    setDiffResult(null);
  };

  const handleSelectVersion = (versionNum: number) => {
    if (!selectedDraft) return;
    const v = selectedDraft.versions.find((item) => item.version_number === versionNum);
    if (v) {
      setCurrentVersionNumber(v.version_number);
      setRawContent(v.raw_content);
      showToast(`Loaded Version ${v.version_number}`, 'info');
    }
  };

  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !rawContent.trim()) {
      showToast('Please provide both draft title and initial legal content.', 'error');
      return;
    }
    setLoading(true);
    try {
      const res = await api.createDraft({
        title,
        raw_content: rawContent,
        document_type: docType,
      });
      showToast(`Draft "${res.data.title}" initialized as Version 1`, 'success');
      setIsCreatingNew(false);
      await fetchDrafts();
      selectDraftItem(res.data);
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Draft creation failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveRevision = async () => {
    if (!selectedDraft || !rawContent.trim()) return;
    setLoading(true);
    try {
      const res = await api.addDraftVersion(selectedDraft.id, rawContent);
      showToast(`Version ${res.data.version_number} saved successfully!`, 'success');
      const updatedDraft = await api.getDraft(selectedDraft.id);
      setSelectedDraft(updatedDraft.data);
      setCurrentVersionNumber(res.data.version_number);
      const updatedList = drafts.map((d) => (d.id === updatedDraft.data.id ? updatedDraft.data : d));
      setDrafts(updatedList);
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to save revision', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluate = async () => {
    if (!selectedDraft) return;
    setIsAiEvalModalOpen(true);
    setEvaluating(true);
    try {
      const res = await api.evaluateDraft(selectedDraft.id, currentVersionNumber);
      setEvaluationResult(res.data);
      showToast('Deterministic RAG Evaluation Completed!', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Evaluation failed to complete', 'error');
      setIsAiEvalModalOpen(false);
    } finally {
      setEvaluating(false);
    }
  };

  const handleCompareDiff = async () => {
    if (!selectedDraft) return;
    setDiffLoading(true);
    try {
      const res = await api.compareVersions(selectedDraft.id, diffVersion1, diffVersion2);
      setDiffResult(res.data);
      setActiveSidePanel('diff');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to generate diff', 'error');
    } finally {
      setDiffLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    const fd = new FormData();
    fd.append('file', file);
    fd.append('title', file.name.replace(/\.[^/.]+$/, ''));
    try {
      const res = await api.uploadDraftFile(fd);
      showToast(`Parsed "${file.name}" and created Version 1`, 'success');
      await fetchDrafts();
      selectDraftItem(res.data);
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'File upload and extraction failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAiAssist = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDraft) return;
    setAiGenerating(true);
    try {
      const res = await api.assistDrafting({
        document_type: selectedDraft.document_type,
        target_clause: targetClause,
        user_instructions: userInstructions,
        context_draft_id: selectedDraft.id,
      });
      setAiAssistResult(res.data);
      showToast('Draft clause synthesized from legal reference corpus', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'AI drafting assistance failed', 'error');
    } finally {
      setAiGenerating(false);
    }
  };

  const handleInsertAiClause = (clauseText: string) => {
    setRawContent((prev) => `${prev}\n\n/* AI Generated Clause (${targetClause}) */\n${clauseText}`);
    showToast('Clause appended to active editor', 'info');
  };

  const handleRagSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuery.trim()) return;
    setRagLoading(true);
    try {
      const res = await api.queryEvidence({
        query: ragQuery,
        document_type: selectedDraft?.document_type || docType,
        top_k: 4,
      });
      setRagResults(res.data.evidence);
      showToast(`Retrieved ${res.data.evidence.length} statutory evidence chunks`, 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'RAG Precedent Search failed', 'error');
    } finally {
      setRagLoading(false);
    }
  };

  const filteredDrafts = drafts.filter((d) => {
    const matchesSearch = d.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'ALL' || d.document_type === filterType;
    return matchesSearch && matchesType;
  });

  const wordCount = rawContent.trim() ? rawContent.trim().split(/\s+/).length : 0;
  const lineCount = rawContent.split('\n').length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Workspace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl glass-panel-glow border border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-white tracking-tight">Legal Drafting Workspace</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-primary-500/10 text-primary-400 border border-primary-500/20 font-mono">
              Live Editor
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Author, revise, and verify statutory compliance with automated RAG evidence grounding.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Upload Button */}
          <label className="flex items-center gap-2 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-200 rounded-xl text-xs font-semibold cursor-pointer transition-all shadow-sm group">
            <Upload className="w-3.5 h-3.5 text-primary-400 group-hover:-translate-y-0.5 transition-transform" />
            <span>Upload Document</span>
            <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileUpload} className="hidden" />
          </label>

          {/* AI Assist Drawer Toggle */}
          <button
            onClick={() => setActiveSidePanel(activeSidePanel === 'ai_assist' ? null : 'ai_assist')}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all ${
              activeSidePanel === 'ai_assist'
                ? 'bg-indigo-600 text-white border-indigo-500 shadow-lg shadow-indigo-500/25'
                : 'bg-slate-900 hover:bg-slate-800 border-slate-700/80 text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-accent-cyan" />
            <span>AI Copilot</span>
          </button>

          {/* RAG Precedent Search Drawer Toggle */}
          <button
            onClick={() => setActiveSidePanel(activeSidePanel === 'rag_search' ? null : 'rag_search')}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all ${
              activeSidePanel === 'rag_search'
                ? 'bg-primary-600 text-white border-primary-500 shadow-lg shadow-primary-500/25'
                : 'bg-slate-900 hover:bg-slate-800 border-slate-700/80 text-slate-200'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-accent-emerald" />
            <span>RAG Search</span>
          </button>

          {/* Run RAG Evaluation Trigger */}
          <button
            onClick={handleEvaluate}
            disabled={evaluating || !selectedDraft || isCreatingNew}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-primary-500/25 transition-all disabled:opacity-50"
          >
            {evaluating ? (
              <>
                <LoadingSpinner size="sm" />
                <span>Evaluating Evidence...</span>
              </>
            ) : (
              <>
                <FileCheck2 className="w-4 h-4" />
                <span>Run Evaluation</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Grid: Explorer + Editor + Side Drawer */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left Column: Drafts Inventory & Version History */}
        <div className="col-span-12 lg:col-span-3 space-y-4">
          {/* Drafts List Card */}
          <div className="glass-panel p-4 rounded-2xl space-y-3.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-primary-400" />
                <span>Drafts ({drafts.length})</span>
              </span>
              <button
                onClick={() => {
                  setIsCreatingNew(true);
                  setSelectedDraft(null);
                  setTitle('');
                  setRawContent('');
                }}
                className="p-1.5 rounded-lg bg-primary-500/10 hover:bg-primary-500/20 text-primary-400 transition-colors"
                title="Initialize New Blank Draft"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>

            {/* Search & Filter */}
            <div className="space-y-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search drafts..."
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus-ring"
                />
              </div>

              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-2.5 py-1.5 text-[11px] text-slate-300 focus-ring"
              >
                <option value="ALL">All Document Types</option>
                <option value="AFFIDAVIT_OF_CHARACTER">Affidavit of Character</option>
                <option value="EMPLOYMENT_AGREEMENT">Employment Agreement</option>
                <option value="RENT_AGREEMENT">Rent Agreement</option>
                <option value="LEGAL_NOTICE">Legal Notice</option>
              </select>
            </div>

            {/* Drafts List */}
            <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
              {loading ? (
                <div className="py-8 flex justify-center">
                  <LoadingSpinner size="sm" />
                </div>
              ) : filteredDrafts.length === 0 ? (
                <div className="text-center py-6 text-slate-500 text-xs">
                  <p>No drafts found.</p>
                  <button
                    onClick={() => setIsCreatingNew(true)}
                    className="mt-2 text-primary-400 hover:underline font-semibold"
                  >
                    + Create First Draft
                  </button>
                </div>
              ) : (
                filteredDrafts.map((d) => {
                  const isSelected = selectedDraft?.id === d.id && !isCreatingNew;
                  return (
                    <div
                      key={d.id}
                      onClick={() => selectDraftItem(d)}
                      className={`p-3 rounded-xl border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-primary-500/15 border-primary-500/50 shadow-md shadow-primary-500/10'
                          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900 text-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-1">
                        <span className="font-semibold text-xs text-white truncate">{d.title}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 shrink-0">
                          v{d.versions?.length || 1}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mt-1.5 text-[10px] text-slate-400">
                        <span className="truncate max-w-[120px]">{d.document_type.replace(/_/g, ' ')}</span>
                        <span>{new Date(d.updated_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Versions Timeline & Diff Trigger */}
          {selectedDraft && !isCreatingNew && (
            <div className="glass-panel p-4 rounded-2xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-accent-amber" />
                  <span>Version Timeline</span>
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {selectedDraft.versions.length} Revisions
                </span>
              </div>

              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {selectedDraft.versions.map((v) => {
                  const isCurrent = currentVersionNumber === v.version_number;
                  return (
                    <div
                      key={v.id}
                      onClick={() => handleSelectVersion(v.version_number)}
                      className={`flex items-center justify-between p-2 rounded-xl text-xs cursor-pointer transition-all border ${
                        isCurrent
                          ? 'bg-primary-500/20 border-primary-500/40 text-white'
                          : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 text-slate-300'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">Version {v.version_number}</span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {new Date(v.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      {isCurrent && (
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-primary-500 text-white uppercase tracking-wider">
                          Active
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Version Comparison Selector */}
              {selectedDraft.versions.length > 1 && (
                <div className="pt-2 border-t border-slate-800/80 space-y-2">
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-medium">
                    <span>Compare Diff</span>
                    <button
                      onClick={handleCompareDiff}
                      disabled={diffLoading}
                      className="text-accent-cyan hover:underline text-xs font-semibold flex items-center gap-1"
                    >
                      <GitCompare className="w-3 h-3" />
                      <span>Inspect</span>
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <select
                      value={diffVersion1}
                      onChange={(e) => setDiffVersion1(Number(e.target.value))}
                      className="bg-slate-900 border border-slate-800 rounded-lg p-1.5 text-xs text-slate-200"
                    >
                      {selectedDraft.versions.map((v) => (
                        <option key={v.id} value={v.version_number}>
                          v{v.version_number}
                        </option>
                      ))}
                    </select>
                    <select
                      value={diffVersion2}
                      onChange={(e) => setDiffVersion2(Number(e.target.value))}
                      className="bg-slate-900 border border-slate-800 rounded-lg p-1.5 text-xs text-slate-200"
                    >
                      {selectedDraft.versions.map((v) => (
                        <option key={v.id} value={v.version_number}>
                          v{v.version_number}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Center Column: Interactive Editor Workspace */}
        <div
          className={`${
            activeSidePanel ? 'col-span-12 lg:col-span-6' : 'col-span-12 lg:col-span-9'
          } space-y-4 transition-all duration-300`}
        >
          <div className="glass-panel p-5 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
            {/* Editor Top Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3.5 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center text-primary-400">
                  <FileText className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">
                    {isCreatingNew ? 'Initialize New Legal Draft' : selectedDraft?.title}
                  </h3>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {isCreatingNew ? docType : selectedDraft?.document_type}
                    </span>
                    {!isCreatingNew && (
                      <span className="text-[10px] font-mono text-slate-400">
                        Editing Version {currentVersionNumber}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Editor Right Controls */}
              <div className="flex items-center gap-2">
                <div className="hidden sm:flex items-center gap-3 text-[11px] font-mono text-slate-400 pr-2 border-r border-slate-800">
                  <span>{wordCount} words</span>
                  <span>{lineCount} lines</span>
                </div>

                {!isCreatingNew && selectedDraft && (
                  <button
                    onClick={handleSaveRevision}
                    disabled={loading}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white rounded-xl text-xs font-semibold border border-slate-700 transition-all"
                  >
                    <Save className="w-3.5 h-3.5 text-primary-400" />
                    <span>Save Version</span>
                  </button>
                )}
              </div>
            </div>

            {/* If creating new, show title and doc type form */}
            {isCreatingNew && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Draft Title
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g., Employment Agreement - Software Engineer 2026"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus-ring"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Document Category
                  </label>
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value as DocumentType)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus-ring"
                  >
                    <option value="AFFIDAVIT_OF_CHARACTER">Affidavit of Character (India)</option>
                    <option value="EMPLOYMENT_AGREEMENT">Employment Agreement (India)</option>
                    <option value="RENT_AGREEMENT">Residential Rent Deed (India)</option>
                    <option value="LEGAL_NOTICE">Legal Notice under Statutory Acts</option>
                  </select>
                </div>
              </div>
            )}

            {/* Monospace Legal Editor */}
            <div className="relative rounded-xl border border-slate-800/80 bg-slate-950/90 overflow-hidden focus-within:border-primary-500/50 transition-colors">
              <textarea
                value={rawContent}
                onChange={(e) => setRawContent(e.target.value)}
                rows={18}
                placeholder="Type or paste the complete legal draft here (including title, parties recitals, operative covenants, statutory jurisdiction, and deponent verification jurat)..."
                className="w-full bg-transparent p-4 font-mono text-xs text-slate-100 leading-relaxed focus:outline-none resize-none"
              />
            </div>

            {/* Bottom Actions */}
            {isCreatingNew ? (
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsCreatingNew(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateDraft}
                  disabled={loading || !title.trim() || !rawContent.trim()}
                  className="px-5 py-2 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-primary-500/20 transition-all disabled:opacity-50"
                >
                  {loading ? 'Initializing...' : 'Create Draft & Version 1'}
                </button>
              </div>
            ) : null}
          </div>
        </div>

        {/* Right Column: Dynamic Side Drawer (Diff Inspector, AI Copilot, RAG Search) */}
        {activeSidePanel && (
          <div className="col-span-12 lg:col-span-3 space-y-4 animate-slide-in-right">
            {/* Tab 1: Version Diff Inspector */}
            {activeSidePanel === 'diff' && (
              <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <GitCompare className="w-4 h-4 text-accent-cyan" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-white">
                      Unified Diff (v{diffVersion1} vs v{diffVersion2})
                    </h4>
                  </div>
                  <button
                    onClick={() => setActiveSidePanel(null)}
                    className="text-slate-400 hover:text-white text-xs"
                  >
                    ✕
                  </button>
                </div>

                {diffResult ? (
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between text-[11px] font-mono p-2 rounded-xl bg-slate-900 border border-slate-800">
                      <span className="text-emerald-400 font-semibold">
                        +{diffResult.additions} additions
                      </span>
                      <span className="text-rose-400 font-semibold">
                        -{diffResult.deletions} deletions
                      </span>
                    </div>

                    <div className="p-3 bg-slate-950/90 rounded-xl border border-slate-800/80 font-mono text-[11px] text-slate-300 max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                      {diffResult.diff_summary || 'No changes between selected versions.'}
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">Click inspect to compute version diff.</p>
                )}
              </div>
            )}

            {/* Tab 2: AI Drafting Copilot */}
            {activeSidePanel === 'ai_assist' && (
              <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-accent-cyan" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-white">
                      AI Legal Copilot
                    </h4>
                  </div>
                  <button
                    onClick={() => setActiveSidePanel(null)}
                    className="text-slate-400 hover:text-white text-xs"
                  >
                    ✕
                  </button>
                </div>

                <form onSubmit={handleAiAssist} className="space-y-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                      Target Legal Clause
                    </label>
                    <select
                      value={targetClause}
                      onChange={(e) => setTargetClause(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2 text-xs text-white focus-ring"
                    >
                      <option value="Verification & Perjury Jurat">Verification & Perjury Jurat</option>
                      <option value="Section 27 Compliant Restrictive Covenants">
                        Section 27 Compliant Restrictive Covenants
                      </option>
                      <option value="Statutory Notice Period & Termination">
                        Notice Period & Termination
                      </option>
                      <option value="Security Deposit Refund Mechanics">
                        Security Deposit Refund Mechanics
                      </option>
                      <option value="Arbitration & Territorial Jurisdiction">
                        Arbitration & Jurisdiction
                      </option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                      Custom Instructions / Facts
                    </label>
                    <textarea
                      value={userInstructions}
                      onChange={(e) => setUserInstructions(e.target.value)}
                      placeholder="e.g. Add 30-day notice with written registered post requirement..."
                      rows={3}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus-ring resize-none"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={aiGenerating || !selectedDraft}
                    className="w-full py-2 bg-gradient-to-r from-indigo-600 to-primary-600 hover:from-indigo-500 hover:to-primary-500 text-white text-xs font-bold rounded-xl shadow-md transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
                  >
                    {aiGenerating ? <LoadingSpinner size="sm" /> : <Sparkles className="w-3.5 h-3.5" />}
                    <span>Generate Grounded Clause</span>
                  </button>
                </form>

                {aiAssistResult && (
                  <div className="space-y-2.5 pt-2 border-t border-slate-800 animate-fade-in-up">
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-indigo-500/30 text-xs font-mono text-indigo-200">
                      {aiAssistResult.drafted_clause || aiAssistResult.generated_draft}
                    </div>

                    {aiAssistResult.commentary && (
                      <p className="text-[11px] text-slate-400 bg-slate-950 p-2.5 rounded-lg border border-slate-800 leading-relaxed">
                        <span className="font-semibold text-slate-200">Statutory Note: </span>
                        {aiAssistResult.commentary}
                      </p>
                    )}

                    <button
                      onClick={() =>
                        handleInsertAiClause(
                          aiAssistResult.drafted_clause || aiAssistResult.generated_draft || ''
                        )
                      }
                      className="w-full py-1.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-xl border border-slate-700 flex items-center justify-center gap-1.5 transition-colors"
                    >
                      <Plus className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Insert Clause into Editor</span>
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Tab 3: RAG Precedent & Evidence Search */}
            {activeSidePanel === 'rag_search' && (
              <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-accent-emerald" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-white">
                      RAG Precedent Search
                    </h4>
                  </div>
                  <button
                    onClick={() => setActiveSidePanel(null)}
                    className="text-slate-400 hover:text-white text-xs"
                  >
                    ✕
                  </button>
                </div>

                <form onSubmit={handleRagSearch} className="space-y-2.5">
                  <div className="relative">
                    <input
                      type="text"
                      value={ragQuery}
                      onChange={(e) => setRagQuery(e.target.value)}
                      placeholder="e.g., verification under oath bar council"
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2 text-xs text-white focus-ring"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={ragLoading || !ragQuery.trim()}
                    className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-xl border border-slate-700 flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
                  >
                    {ragLoading ? <LoadingSpinner size="sm" /> : <Search className="w-3.5 h-3.5" />}
                    <span>Query Qdrant Vector Corpus</span>
                  </button>
                </form>

                <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
                  {ragResults.length === 0 ? (
                    <p className="text-center py-6 text-[11px] text-slate-500">
                      Enter legal terms to retrieve dense vector and statutory citations.
                    </p>
                  ) : (
                    ragResults.map((chunk, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 space-y-1.5 text-xs"
                      >
                        <div className="flex items-center justify-between text-[10px] text-accent-emerald font-semibold">
                          <span>{chunk.source_document}</span>
                          <span>Page {chunk.page_number}</span>
                        </div>
                        <p className="font-mono text-[11px] text-slate-300 leading-relaxed">
                          "{chunk.content}"
                        </p>
                        <button
                          onClick={() => {
                            setRawContent((prev) => `${prev}\n\n${chunk.content}`);
                            showToast('Citation inserted into editor', 'info');
                          }}
                          className="text-[10px] text-primary-400 hover:underline font-semibold flex items-center gap-1"
                        >
                          <Plus className="w-3 h-3" />
                          Insert citation
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 3D AI Evaluation Modal */}
      <AIEvaluationModal
        isOpen={isAiEvalModalOpen}
        onClose={() => setIsAiEvalModalOpen(false)}
        evaluation={evaluationResult}
        evaluating={evaluating}
        draftTitle={selectedDraft?.title || 'Legal Draft'}
        draftContent={rawContent}
        onNavigateToLoopholes={onNavigateToLoopholes}
        onViewDetailedEvidence={() => {
          if (evaluationResult) onSelectEvaluation(evaluationResult.id);
        }}
      />
    </div>
  );
};