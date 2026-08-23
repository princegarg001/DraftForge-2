import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
import { Conversation, ChatMessage, DocumentType } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import {
  Plus,
  Send,
  BookOpen,
  User,
  Bot,
  Sparkles,
  MessageSquare,
  Scale,
  ChevronRight,
} from 'lucide-react';

export const TutorChat: React.FC = () => {
  const { showToast } = useToast();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConv, setActiveConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMsg, setInputMsg] = useState('');
  const [docType, setDocType] = useState<DocumentType>('AFFIDAVIT_OF_CHARACTER');
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const fetchConversations = async () => {
    try {
      const res = await api.getConversations();
      setConversations(res.data || []);
      if (res.data && res.data.length > 0 && !activeConv) {
        setActiveConv(res.data[0]);
      }
    } catch (err: any) {
      showToast('Error loading conversation threads', 'error');
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (activeConv) {
      setLoadingHistory(true);
      api
        .getMessages(activeConv.id)
        .then((res) => setMessages(res.data || []))
        .catch(() => showToast('Failed to fetch messages', 'error'))
        .finally(() => setLoadingHistory(false));
    }
  }, [activeConv]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const handleCreateNewThread = async () => {
    try {
      const title = `Tutoring: ${docType.replace(/_/g, ' ')}`;
      const res = await api.createConversation(title);
      const newConv = res.data;
      setConversations((prev) => [newConv, ...prev]);
      setActiveConv(newConv);
      setMessages([]);
      showToast('Created new Socratic tutoring thread', 'info');
    } catch (err: any) {
      showToast('Failed to create thread', 'error');
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMsg.trim() || sending) return;

    const currentText = inputMsg;
    setInputMsg('');
    setSending(true);

    try {
      let targetConv = activeConv;

      if (!targetConv) {
        const createRes = await api.createConversation(
          currentText.length > 30 ? `${currentText.slice(0, 30)}...` : currentText
        );
        targetConv = createRes.data;
        setConversations((prev) => [targetConv!, ...prev]);
        setActiveConv(targetConv);
      }

      const payload = {
        conversation_id: targetConv.id,
        message: currentText,
        document_type: docType,
      };

      const res = await api.sendChatMessage(payload);
      setMessages((prev) => [...prev, res.data.user_message, res.data.ai_message]);
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to send message', 'error');
    } finally {
      setSending(false);
    }
  };

  const quickPrompts = [
    'What essential jurat elements are mandatory in an Indian Affidavit of Character?',
    'Under Section 27 of the Indian Contract Act, how should non-solicitation vs non-compete clauses be drafted?',
    'What standard notice period and security deposit clauses apply to residential rent agreements?',
    'How do I structure a statutory legal notice demanding performance of contract?',
  ];

  return (
    <div className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)] animate-fade-in">
      {/* Left Column: Conversation Threads */}
      <div className="col-span-12 lg:col-span-4 glass-panel p-5 rounded-3xl border border-slate-800 flex flex-col justify-between overflow-hidden">
        <div className="space-y-4 overflow-hidden flex flex-col flex-1">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-primary-400" />
              <h3 className="font-bold text-xs uppercase tracking-wider text-white">
                Tutoring Threads ({conversations.length})
              </h3>
            </div>
            <button
              onClick={handleCreateNewThread}
              className="p-1.5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white transition-colors"
              title="New Tutoring Session"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          {/* Conversation List */}
          <div className="space-y-2 overflow-y-auto pr-1 flex-1">
            {conversations.length === 0 ? (
              <p className="text-xs text-slate-500 p-4 text-center">
                No past threads. Start a conversation with the Socratic AI tutor.
              </p>
            ) : (
              conversations.map((c) => {
                const isActive = activeConv?.id === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => setActiveConv(c)}
                    className={`p-3.5 rounded-2xl cursor-pointer text-xs font-semibold transition-all border ${
                      isActive
                        ? 'bg-primary-600/15 border-primary-500/40 text-white shadow-md shadow-primary-500/10'
                        : 'bg-slate-900/40 border-slate-800/80 text-slate-300 hover:bg-slate-900 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="truncate max-w-[190px]">{c.title}</span>
                      <ChevronRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    </div>
                    <span className="block text-[10px] text-slate-500 font-mono mt-1">
                      {new Date(c.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Document Context Selector */}
        <div className="pt-4 border-t border-slate-800 space-y-1.5">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Active RAG Subject Context:
          </span>
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value as DocumentType)}
            className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white focus-ring"
          >
            <option value="AFFIDAVIT_OF_CHARACTER">Affidavit of Character (India)</option>
            <option value="EMPLOYMENT_AGREEMENT">Employment Agreement (India)</option>
            <option value="RENT_AGREEMENT">Residential Rent Deed (India)</option>
            <option value="LEGAL_NOTICE">Statutory Legal Notice</option>
          </select>
        </div>
      </div>

      {/* Right Column: Chat Stream */}
      <div className="col-span-12 lg:col-span-8 glass-panel rounded-3xl border border-slate-800 flex flex-col overflow-hidden">
        {/* Chat Messages Body */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {loadingHistory ? (
            <div className="py-20 flex justify-center">
              <LoadingSpinner size="lg" label="Loading Socratic dialogue..." />
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 max-w-md mx-auto my-auto py-8">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-primary-600 to-indigo-600 flex items-center justify-center shadow-xl shadow-primary-500/20 text-white">
                <Scale className="w-7 h-7" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Socratic Legal Drafting Tutor</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Ask conceptual or structural drafting questions. Responses are guided by the Socratic method and grounded in verified legal reference precedents.
                </p>
              </div>

              {/* Quick Prompts */}
              <div className="space-y-2 w-full text-left pt-2">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                  Suggested Prompts:
                </span>
                {quickPrompts.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputMsg(q)}
                    className="w-full p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 text-left transition-colors flex items-center justify-between group"
                  >
                    <span className="truncate">{q}</span>
                    <Sparkles className="w-3.5 h-3.5 text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m) => {
              const isUser = m.role === 'user';
              return (
                <div
                  key={m.id}
                  className={`flex items-start gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!isUser && (
                    <div className="w-8 h-8 rounded-xl bg-primary-600/20 border border-primary-500/30 flex items-center justify-center shrink-0 text-primary-400 mt-1">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-2xl p-4 sm:p-5 rounded-2xl text-xs leading-relaxed space-y-2.5 ${
                      isUser
                        ? 'bg-gradient-to-r from-primary-600 to-indigo-600 text-white rounded-tr-none shadow-lg shadow-primary-500/10'
                        : 'bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none'
                    }`}
                  >
                    <p className="whitespace-pre-wrap font-sans">{m.content}</p>

                    {/* Grounded Sources Drawer */}
                    {m.retrieved_sources && m.retrieved_sources.length > 0 && (
                      <div className="pt-2.5 border-t border-slate-700/60 text-[10px] space-y-1.5">
                        <div className="flex items-center gap-1.5 text-accent-cyan font-semibold">
                          <BookOpen className="w-3.5 h-3.5" />
                          <span>Grounded Legal Precedent Citations:</span>
                        </div>
                        <div className="space-y-1">
                          {m.retrieved_sources.map((s, i) => (
                            <div
                              key={i}
                              className="font-mono text-slate-300 bg-slate-950/60 p-1.5 rounded-lg border border-slate-800/80"
                            >
                              • {s.source_document} (Page {s.page_number || 1}) — {s.section}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 text-slate-300 mt-1">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {sending && (
            <div className="flex items-center gap-3 p-4 rounded-2xl bg-slate-900/60 border border-slate-800 w-fit">
              <LoadingSpinner size="sm" />
              <span className="text-xs text-slate-300 animate-pulse">
                Socratic tutor is retrieving statutory evidence and reasoning...
              </span>
            </div>
          )}
          <div ref={scrollRef} />
        </div>

        {/* Input Bar */}
        <form
          onSubmit={handleSendMessage}
          className="p-4 border-t border-slate-800 bg-slate-950/90 flex gap-3"
        >
          <input
            type="text"
            value={inputMsg}
            onChange={(e) => setInputMsg(e.target.value)}
            placeholder="Ask your legal drafting tutor a question (e.g., How do I draft a valid verification in an Affidavit?)..."
            className="flex-1 bg-slate-900 border border-slate-700/80 rounded-2xl px-4 py-3 text-xs text-white focus-ring placeholder-slate-500 font-sans"
          />
          <button
            type="submit"
            disabled={sending || !inputMsg.trim()}
            className="px-5 py-3 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white rounded-2xl text-xs font-bold transition-all disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-primary-500/20"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};