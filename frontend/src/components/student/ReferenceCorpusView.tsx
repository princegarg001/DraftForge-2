import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { ReferenceDocument, DocumentType } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import {
  BookOpen,
  Search,
  Copy,
  Check,
  ShieldCheck,
  FileText,
} from 'lucide-react';

export const ReferenceCorpusView: React.FC = () => {
  const { showToast } = useToast();
  const [documents, setDocuments] = useState<ReferenceDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const res = await api.getReferences(filterType === 'ALL' ? undefined : (filterType as DocumentType));
      setDocuments(res.data || []);
    } catch (err: any) {
      showToast('Failed to load legal reference corpus', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [filterType]);

  const handleCopyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    showToast('SHA-256 integrity hash copied to clipboard', 'info');
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const filtered = documents.filter((d) =>
    d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.document_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl glass-panel-glow border border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-white tracking-tight">Legal Reference Corpus</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              Qdrant Cloud Indexed
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Gold-standard statutory templates, precedent deeds, and benchmark judicial forms used for RAG grounding.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-xs font-mono text-slate-400 px-3.5 py-2 bg-slate-900 rounded-xl border border-slate-800">
            Total Reference Templates: <span className="text-emerald-400 font-bold">{documents.length}</span>
          </div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search reference corpus by title or keyword..."
            className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus-ring"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-semibold">Category:</span>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white focus-ring"
          >
            <option value="ALL">All Categories</option>
            <option value="AFFIDAVIT_OF_CHARACTER">Affidavit of Character</option>
            <option value="EMPLOYMENT_AGREEMENT">Employment Agreement</option>
            <option value="RENT_AGREEMENT">Rent Agreement</option>
            <option value="LEGAL_NOTICE">Legal Notice</option>
          </select>
        </div>
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="py-24 flex justify-center">
          <LoadingSpinner size="xl" label="Loading benchmark reference templates..." />
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-3xl border border-slate-800 space-y-3">
          <BookOpen className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No Reference Documents Found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            No templates match the selected filter. Try selecting &ldquo;All Categories&rdquo;.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((doc) => (
            <div
              key={doc.id}
              className="glass-panel p-6 rounded-3xl border border-slate-800 hover:border-emerald-500/40 transition-all space-y-4 flex flex-col justify-between group"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-slate-900 text-emerald-400 border border-emerald-500/20">
                    {doc.document_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {(doc.file_size_bytes / 1024).toFixed(1)} KB
                  </span>
                </div>

                <h3 className="font-bold text-sm text-white group-hover:text-emerald-300 transition-colors">
                  {doc.title}
                </h3>

                <div className="space-y-1 text-xs text-slate-400">
                  <p>
                    <span className="text-slate-500">Jurisdiction:</span> {doc.jurisdiction}
                  </p>
                  <p>
                    <span className="text-slate-500">Uploaded:</span>{' '}
                    {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {/* Bottom Actions & Hash */}
              <div className="pt-3 border-t border-slate-800/80 space-y-2">
                <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <div className="flex items-center gap-1 truncate max-w-[170px]">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>{doc.file_hash.substring(0, 14)}...</span>
                  </div>
                  <button
                    onClick={() => handleCopyHash(doc.file_hash)}
                    className="text-primary-400 hover:underline flex items-center gap-0.5"
                    title="Copy full SHA-256 Hash"
                  >
                    {copiedHash === doc.file_hash ? (
                      <Check className="w-3 h-3 text-emerald-400" />
                    ) : (
                      <Copy className="w-3 h-3" />
                    )}
                    <span>{copiedHash === doc.file_hash ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>

                <div className="w-full py-2 bg-slate-900 border border-slate-800 text-slate-400 rounded-xl text-[11px] font-mono flex items-center justify-center gap-1.5 truncate px-3">
                  <FileText className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span className="truncate">{doc.storage_path}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
