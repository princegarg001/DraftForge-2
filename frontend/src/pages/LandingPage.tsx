import React, { useState } from 'react';
import { LandingNavbar } from '../components/landing/LandingNavbar';
import { Hero3DVisual } from '../components/landing/Hero3DVisual';
import { InteractiveDocumentScanner } from '../components/landing/InteractiveDocumentScanner';
import { LandingFooter } from '../components/landing/LandingFooter';
import { HealthModal } from '../components/common/HealthModal';
import {
  Sparkles,
  ArrowRight,
  FileCheck,
  GraduationCap,
  TrendingUp,
  Users,
  CheckCircle2,
  XCircle,
  Database,
  Network,
  Cpu,
  ChevronRight,
  FileEdit,
  ClipboardCheck,
  ShieldCheck,
} from 'lucide-react';

interface LandingPageProps {
  onOpenAuth: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onOpenAuth }) => {
  const [isHealthOpen, setIsHealthOpen] = useState(false);
  const [activeRoleTab, setActiveRoleTab] = useState<'student' | 'faculty'>('student');
  const [activeFeatureIndex, setActiveFeatureIndex] = useState(0);

  const features = [
    {
      id: 'ai_copilot',
      title: 'In-Editor AI Drafting Copilot',
      badge: 'Statutory Synthesis',
      description:
        'Synthesize standard clauses, verification jurats, or dispute resolution mechanisms grounded in verified Indian precedents directly in the workspace editor.',
      icon: Sparkles,
      color: 'text-accent-cyan',
      bgGlow: 'from-cyan-500/20 to-blue-500/5',
      codeSnippet: `/* AI Synthesized Verification Clause */\n"Verified at New Delhi on this 23rd day of August, 2026, that the contents of paragraphs 1 to 4 are true and correct to my knowledge..."`,
    },
    {
      id: 'rubric_eval',
      title: 'Deterministic 100-Point Rubrics',
      badge: 'Zero Hallucination',
      description:
        'Mathematical score breakdowns across Structure (25 pts), Clause Matching (50 pts), Formatting Jurats (25 pts), and Contradiction Penalties (-15 pts).',
      icon: ClipboardCheck,
      color: 'text-accent-emerald',
      bgGlow: 'from-emerald-500/20 to-teal-500/5',
      codeSnippet: `Evaluation Result:\n• Structure Score: 25 / 25 pts\n• Clause Coverage: 42 / 50 pts\n• Verification Jurat: 20 / 25 pts\n• Penalty Deducted: 0 pts\n= Final Score: 87 / 100 pts`,
    },
    {
      id: 'graph_loopholes',
      title: 'Neo4j GraphRAG Loophole Detection',
      badge: 'Knowledge Graph',
      description:
        'Traverse graph prerequisite chains to discover missing statutory nodes, cross-clause contradictions, and procedural risks before filing in court.',
      icon: Network,
      color: 'text-accent-rose',
      bgGlow: 'from-rose-500/20 to-pink-500/5',
      codeSnippet: `Graph Loophole Detected:\n[Restrictive_Covenant] -> MISSING_PREREQUISITE -> [Garden_Leave_Compensation]\nSeverity: HIGH RISK\nStatutory Note: Restraint of trade void under Sec 27 ICA.`,
    },
    {
      id: 'rag_corpus',
      title: 'Qdrant Dense Vector Corpus',
      badge: 'FastEmbed 384-dim',
      description:
        'Every draft is compared against gold-standard judicial templates and statutory reference files with SHA-256 cryptographic integrity verification.',
      icon: Database,
      color: 'text-indigo-400',
      bgGlow: 'from-indigo-500/20 to-primary-500/5',
      codeSnippet: `Vector Search (Qdrant Cloud):\n• Collection: legal_reference_corpus\n• Top-K Semantic Chunks: 4 retrieved\n• Similarity Score: 0.964\n• SHA-256: 7f8a12e4b9c...`,
    },
    {
      id: 'roadmap_trajectory',
      title: 'Dynamic 5-Phase Learning Roadmap',
      badge: 'Adaptive Pedagogy',
      description:
        'AI analyzes your evaluation weaknesses across drafts to synthesize a personalized 5-phase legal drafting curriculum with real-time milestone checkoffs.',
      icon: GraduationCap,
      color: 'text-accent-amber',
      bgGlow: 'from-amber-500/20 to-yellow-500/5',
      codeSnippet: `5-Phase Milestone Trajectory:\n[Phase 1] Structural Identification & Preamble (Done)\n[Phase 2] Substantive Operative Covenants (Active)\n[Phase 3] Jurats & Statutory Oath Precision (Pending)`,
    },
    {
      id: 'faculty_oversight',
      title: 'Faculty Assignment & Override Studio',
      badge: 'Academic Governance',
      description:
        'Professors publish drafting briefs with deadline trackers, review automated evaluations, and submit score overrides with required audit logs.',
      icon: Users,
      color: 'text-primary-400',
      bgGlow: 'from-primary-500/20 to-indigo-500/5',
      codeSnippet: `Faculty Audited Override:\n• Student: Arjun Sharma (v2)\n• Automated Score: 78 pts -> Overridden: 88 pts\n• Audit Reason: "Approved creative arbitration seat structure"`,
    },
  ];

  return (
    <div className="min-h-screen bg-background text-slate-100 font-sans selection:bg-primary-500 selection:text-white relative overflow-hidden bg-grid-pattern">
      {/* Ambient Radial Background Glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-radial-glow pointer-events-none -z-10" />
      <div className="absolute top-[35%] -left-64 w-[600px] h-[600px] bg-primary-600/10 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-[65%] -right-64 w-[600px] h-[600px] bg-accent-cyan/10 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Navigation */}
      <LandingNavbar onOpenAuth={onOpenAuth} onOpenHealth={() => setIsHealthOpen(true)} />

      {/* ========================================================================= */}
      {/* 1. HERO SECTION */}
      {/* ========================================================================= */}
      <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-6 max-w-4xl mx-auto">
          {/* Small Premium Badge */}
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-slate-900/90 border border-primary-500/30 text-primary-300 text-xs font-semibold shadow-lg shadow-primary-500/10 animate-fade-in-up">
            <Sparkles className="w-3.5 h-3.5 text-accent-cyan animate-pulse" />
            <span>AI-Powered Legal Drafting & Deterministic Evaluation</span>
            <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan" />
            <span className="text-[11px] font-mono text-slate-400">Grounded in Real Corpus</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.12] animate-fade-in">
            Draft Smarter.{' '}
            <span className="gradient-text-primary">Learn Faster.</span>
            <br />
            Write Better <span className="gradient-text-cyan">Legal Documents.</span>
          </h1>

          {/* Supporting Subtitle */}
          <p className="text-sm sm:text-base lg:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed font-normal">
            DraftForge is the next-generation LegalTech platform empowering law students and faculty with deterministic rubric evaluations, FastEmbed vector precedent retrieval, and Neo4j GraphRAG loophole detection.
          </p>

          {/* Primary & Secondary CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <button
              onClick={onOpenAuth}
              className="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-primary-600 via-indigo-600 to-accent-cyan hover:from-primary-500 hover:to-accent-cyan text-white text-sm font-bold rounded-2xl shadow-xl shadow-primary-500/25 hover:shadow-primary-500/40 transition-all flex items-center justify-center gap-2 group"
            >
              <span>Start Drafting Free</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>

            <a
              href="#scanner"
              className="w-full sm:w-auto px-7 py-3.5 rounded-2xl text-sm font-bold text-slate-200 hover:text-white bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 transition-all flex items-center justify-center gap-2"
            >
              <span>Explore Platform Demo</span>
              <ChevronRight className="w-4 h-4 text-slate-400" />
            </a>
          </div>

          {/* Verified Stack Telemetry Tag */}
          <div className="pt-4 flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-xs text-slate-400 font-mono">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> FastEmbed 384-dim Vectors
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Neo4j Aura Graph Traversal
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Deterministic 100-pt Rubrics
            </span>
          </div>
        </div>

        {/* 3D Visual in Hero */}
        <div className="mt-14 sm:mt-16">
          <Hero3DVisual />
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 2. TRUST & ARCHITECTURAL FOUNDATION SECTION */}
      {/* ========================================================================= */}
      <section className="py-16 border-y border-slate-800/80 bg-slate-950/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <span className="text-[10px] font-bold uppercase tracking-widest text-primary-400 font-mono">
              Empirical Legal Precision
            </span>
            <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Engineered on a Four-Pillar Legal AI Architecture
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <ClipboardCheck className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-white">Deterministic Rubrics</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Objective scoring across Structure, Clause Matching, and Jurats without arbitrary LLM score hallucination.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <Database className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-white">Dense Vector Retrieval</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                FastEmbed 384-dim embeddings match clauses against official statutory precedents and bench forms in Qdrant.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
                <Network className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-white">GraphRAG Reasoning</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Neo4j Aura graph topology traverses dependency chains to catch missing prerequisite clauses and legal exposures.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-2xl bg-accent-amber/10 border border-accent-amber/20 flex items-center justify-center text-accent-amber">
                <GraduationCap className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-white">Socratic Pedagogy</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Adaptive 5-phase roadmaps and conversational AI tutoring grounded in retrieved statutory chunks.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 3. PROBLEM → SOLUTION SECTION */}
      {/* ========================================================================= */}
      <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <span className="text-[10px] font-bold uppercase tracking-widest text-rose-400 font-mono">
            Bridging the Legal Drafting Gap
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Why Traditional Drafting Education Fails & How DraftForge Solves It
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Legal drafting has historically suffered from subjective grading and invisible blind spots.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch">
          {/* Traditional Drafting (Problem) */}
          <div className="p-8 rounded-3xl bg-rose-950/15 border border-rose-500/20 space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center gap-2.5 text-rose-400 font-bold text-xs uppercase tracking-wider">
                <XCircle className="w-5 h-5" />
                <span>The Traditional Problem</span>
              </div>
              <h3 className="text-lg font-bold text-white">
                Unstructured Drafting with Invisible Risk Exposures
              </h3>
              <ul className="space-y-3 text-xs text-slate-300">
                <li className="flex items-start gap-2.5">
                  <span className="text-rose-400 font-bold">✕</span>
                  <span>Students never know which prerequisite clauses are missing until a judge or adversary rejects the filing.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-rose-400 font-bold">✕</span>
                  <span>Feedback is delayed, subjective, and lacks mathematical breakdown or statutory citation grounding.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-rose-400 font-bold">✕</span>
                  <span>Critical contradictions (like void Section 27 non-compete clauses) slip through unverified.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-rose-400 font-bold">✕</span>
                  <span>Faculty are overwhelmed with manual grading, lacking cohort-wide weak-skill intelligence.</span>
                </li>
              </ul>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-[11px] text-slate-400 font-mono">
              Outcome: High procedural rejection rates & fragmented student learning trajectories.
            </div>
          </div>

          {/* DraftForge Solution */}
          <div className="p-8 rounded-3xl bg-emerald-950/15 border border-emerald-500/20 space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center gap-2.5 text-emerald-400 font-bold text-xs uppercase tracking-wider">
                <CheckCircle2 className="w-5 h-5" />
                <span>The DraftForge Transformation</span>
              </div>
              <h3 className="text-lg font-bold text-white">
                Evidence-Grounded Intelligence with Knowledge Graphs
              </h3>
              <ul className="space-y-3 text-xs text-slate-300">
                <li className="flex items-start gap-2.5">
                  <span className="text-emerald-400 font-bold">✓</span>
                  <span>Deterministic 100-point rubrics immediately audit Structure, Clause Coverage, and Verification Jurats.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-emerald-400 font-bold">✓</span>
                  <span>Neo4j knowledge graph traversal highlights missing prerequisite dependencies and illegal restraints.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-emerald-400 font-bold">✓</span>
                  <span>Personalized 5-phase roadmaps and Socratic tutoring guide continuous draft revision.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-emerald-400 font-bold">✓</span>
                  <span>Faculty studio enables rapid brief creation, audited score overrides, and cohort analytics.</span>
                </li>
              </ul>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-[11px] text-emerald-300 font-mono">
              Outcome: Empirical mastery, verifiable statutory compliance, and commercial drafting confidence.
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 4. INTERACTIVE DOCUMENT SCANNER DEMO */}
      {/* ========================================================================= */}
      <section id="scanner" className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="text-[10px] font-bold uppercase tracking-widest text-accent-cyan font-mono">
            Live Product Simulation
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            See the Analysis Engine in Action
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Select a legal deed below to preview real-time clause extraction, statutory risk flags, and rubric scoring.
          </p>
        </div>

        <InteractiveDocumentScanner />
      </section>

      {/* ========================================================================= */}
      {/* 5. CORE FEATURES SHOWCASE */}
      {/* ========================================================================= */}
      <section id="features" className="py-24 border-t border-slate-800/80 bg-slate-950/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <span className="text-[10px] font-bold uppercase tracking-widest text-primary-400 font-mono">
              Full Spectrum Platform Capabilities
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Engineered for Law Students & Faculty Alike
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Every feature corresponds directly to verified backend algorithms and database tables.
            </p>
          </div>

          {/* Interactive Feature Showcase with Tabbed Preview */}
          <div className="grid grid-cols-12 gap-8 items-center">
            {/* Feature List (Left 5 Cols) */}
            <div className="col-span-12 lg:col-span-5 space-y-3">
              {features.map((feat, idx) => {
                const Icon = feat.icon;
                const isActive = activeFeatureIndex === idx;

                return (
                  <div
                    key={feat.id}
                    onClick={() => setActiveFeatureIndex(idx)}
                    className={`p-4 sm:p-5 rounded-2xl border cursor-pointer transition-all space-y-1.5 ${
                      isActive
                        ? 'bg-primary-600/15 border-primary-500/50 shadow-lg shadow-primary-500/10 text-white'
                        : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700 hover:bg-slate-900'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                            isActive ? 'bg-primary-500 text-white' : 'bg-slate-800 ' + feat.color
                          }`}
                        >
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <h4 className="font-bold text-xs sm:text-sm text-white">{feat.title}</h4>
                      </div>
                      <span
                        className={`text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider font-mono ${
                          isActive
                            ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {feat.badge}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed pl-9">
                      {feat.description}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Feature Visual Console Preview (Right 7 Cols) */}
            <div className="col-span-12 lg:col-span-7">
              <div className="glass-panel-glow p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
                <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-rose-500" />
                    <span className="w-3 h-3 rounded-full bg-amber-500" />
                    <span className="w-3 h-3 rounded-full bg-emerald-500" />
                    <span className="text-xs font-mono text-slate-400 ml-2">
                      engine_runtime / {features[activeFeatureIndex].id}.ts
                    </span>
                  </div>

                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20">
                    Active Execution
                  </span>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-white">
                    {features[activeFeatureIndex].title}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {features[activeFeatureIndex].description}
                  </p>

                  <div className="p-4 rounded-2xl bg-slate-950/90 border border-slate-800 font-mono text-xs text-slate-200 whitespace-pre-wrap leading-relaxed">
                    {features[activeFeatureIndex].codeSnippet}
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <button
                    onClick={onOpenAuth}
                    className="px-5 py-2.5 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary-500/20 transition-all flex items-center gap-2"
                  >
                    <span>Launch in Studio</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 6. THE AI EVALUATION & GRAPH RAG PIPELINE */}
      {/* ========================================================================= */}
      <section id="ai-evaluation" className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <span className="text-[10px] font-bold uppercase tracking-widest text-accent-cyan font-mono">
            System Architecture
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            How DraftForge Evaluates a Legal Document
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            A deterministic pipeline integrating semantic vector search with knowledge graph dependency checking.
          </p>
        </div>

        {/* 6-Step Pipeline Nodes */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            {
              step: '01',
              title: 'Draft Intake',
              desc: 'Author in Monaco editor or upload .pdf/.docx/.txt',
              icon: FileEdit,
              color: 'text-primary-400',
            },
            {
              step: '02',
              title: 'FastEmbed',
              desc: 'Vectorized into 384-dimensional dense embeddings',
              icon: Cpu,
              color: 'text-indigo-400',
            },
            {
              step: '03',
              title: 'Qdrant RAG',
              desc: 'Matched against gold-standard statutory precedent corpus',
              icon: Database,
              color: 'text-accent-cyan',
            },
            {
              step: '04',
              title: 'Neo4j Aura',
              desc: 'Knowledge graph traverses prerequisite clause links',
              icon: Network,
              color: 'text-rose-400',
            },
            {
              step: '05',
              title: 'Deterministic Rubric',
              desc: 'Evaluates Structure, Clauses, and Jurats (0–100 pts)',
              icon: ClipboardCheck,
              color: 'text-emerald-400',
            },
            {
              step: '06',
              title: 'Roadmap & Tutor',
              desc: 'Synthesizes Socratic tips & personalized 5-phase trajectory',
              icon: GraduationCap,
              color: 'text-accent-amber',
            },
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="glass-panel p-5 rounded-3xl border border-slate-800 space-y-3 relative group hover:border-slate-700 transition-all flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-slate-500">{item.step}</span>
                    <Icon className={`w-4 h-4 ${item.color}`} />
                  </div>
                  <h4 className="font-bold text-xs text-white">{item.title}</h4>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{item.desc}</p>
                </div>

                <div className="w-full h-1 bg-slate-900 rounded-full overflow-hidden">
                  <div className="h-full bg-primary-500/40 rounded-full" style={{ width: '100%' }} />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 7. DUAL EXPERIENCE: FOR STUDENTS VS FOR FACULTY */}
      {/* ========================================================================= */}
      <section id="students" className="py-24 border-t border-slate-800/80 bg-slate-950/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 font-mono">
              Tailored Portals
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Two Dedicated Studios. One Seamless Platform.
            </h2>
          </div>

          {/* Role Toggle Switch */}
          <div className="flex justify-center">
            <div className="p-1.5 bg-slate-900 rounded-2xl border border-slate-800 flex items-center gap-2">
              <button
                onClick={() => setActiveRoleTab('student')}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  activeRoleTab === 'student'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <GraduationCap className="w-4 h-4" />
                <span>For Law Students</span>
              </button>
              <button
                onClick={() => setActiveRoleTab('faculty')}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  activeRoleTab === 'faculty'
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Users className="w-4 h-4" />
                <span>For Law Faculty</span>
              </button>
            </div>
          </div>

          {/* Student Journey Showcase */}
          {activeRoleTab === 'student' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
              <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
                <div className="w-10 h-10 rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center text-primary-400">
                  <FileEdit className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-white">Drafting Studio & Unified Diff</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Author deeds with Monaco-style monospace precision, save numbered revision versions, and compare additions/deletions with live diff inspection.
                </p>
              </div>

              <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
                <div className="w-10 h-10 rounded-2xl bg-accent-cyan/10 border border-accent-cyan/20 flex items-center justify-center text-accent-cyan">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-white">Socratic AI Tutor Chat</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Engage in multi-turn legal reasoning sessions where answers are strictly grounded in retrieved statutory precedents and verified evidence.
                </p>
              </div>

              <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
                <div className="w-10 h-10 rounded-2xl bg-accent-amber/10 border border-accent-amber/20 flex items-center justify-center text-accent-amber">
                  <TrendingUp className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-white">5-Phase Personalized Curriculum</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Synthesize an adaptive milestone curriculum, verify knowledge with statutory MCQs, and track your exponential moving average (EMA) skill mastery.
                </p>
              </div>
            </div>
          )}

          {/* Faculty Journey Showcase */}
          {activeRoleTab === 'faculty' && (
            <div id="faculty" className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
              <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
                <div className="w-10 h-10 rounded-2xl bg-accent-cyan/10 border border-accent-cyan/20 flex items-center justify-center text-accent-cyan">
                  <FileCheck className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-white">Assignment Creator</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Publish drafting briefs with target document types, rubric constraints, and deadline trackers. Enforce structured coursework workflows.
                </p>
              </div>

              <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
                <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-white">Submissions Auditor & Overrides</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Inspect student submissions, review automated evaluation breakdowns, and submit faculty score overrides backed by required audit logs.
                </p>
              </div>

              <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
                <div className="w-10 h-10 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
                  <Users className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-sm text-white">Cohort Weak-Skill Analytics</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Gain class-wide intelligence into statutory clauses where students struggle, enabling targeted faculty lectures and intervention.
                </p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 8. 5-STEP HOW IT WORKS */}
      {/* ========================================================================= */}
      <section id="how-it-works" className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <span className="text-[10px] font-bold uppercase tracking-widest text-primary-400 font-mono">
            Step-by-Step Flow
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            How It Works in Practice
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            From raw draft to certified statutory compliance in five steps.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[
            {
              num: '01',
              title: 'Draft & Author',
              desc: 'Write or paste legal deeds into the Monaco workspace editor.',
            },
            {
              num: '02',
              title: 'Deterministic Scan',
              desc: 'FastEmbed and rule engines scan structure, clauses, and jurats.',
            },
            {
              num: '03',
              title: 'Graph Loophole Audit',
              desc: 'Neo4j Aura checks prerequisite dependencies and risk exposures.',
            },
            {
              num: '04',
              title: 'AI Copilot Refine',
              desc: 'Revise weak clauses with Socratic tutoring and precedent search.',
            },
            {
              num: '05',
              title: 'Submit & Master',
              desc: 'Submit to faculty, check milestones, and track EMA mastery score.',
            },
          ].map((step, idx) => (
            <div
              key={idx}
              className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3 relative group hover:border-primary-500/40 transition-all"
            >
              <span className="text-3xl font-extrabold font-mono text-primary-500/40 group-hover:text-primary-400 transition-colors">
                {step.num}
              </span>
              <h4 className="font-bold text-sm text-white">{step.title}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 9. STRATEGIC HIGH-IMPACT CTA BANNER */}
      {/* ========================================================================= */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative glass-panel-glow p-8 sm:p-14 rounded-[2.5rem] border border-primary-500/40 shadow-2xl text-center space-y-6 overflow-hidden">
          <div className="absolute -top-24 -left-24 w-72 h-72 bg-primary-500/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-accent-cyan/20 rounded-full blur-3xl pointer-events-none" />

          <div className="max-w-2xl mx-auto space-y-3 relative z-10">
            <span className="px-3 py-1 rounded-full text-[10px] font-bold bg-primary-500/10 text-primary-300 border border-primary-500/30 font-mono uppercase tracking-wider">
              Start Drafting Today
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Turn Every Draft into a Legal Mastery Milestone
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Experience the power of evidence-grounded legal drafting education. Enter the DraftForge Studio now to author, audit, and master statutory compliance.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 relative z-10 pt-2">
            <button
              onClick={onOpenAuth}
              className="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-primary-600 via-indigo-600 to-accent-cyan hover:from-primary-500 hover:to-accent-cyan text-white text-sm font-bold rounded-2xl shadow-xl shadow-primary-500/25 transition-all flex items-center justify-center gap-2 group"
            >
              <span>Launch DraftForge Portal</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <LandingFooter onOpenAuth={onOpenAuth} onOpenHealth={() => setIsHealthOpen(true)} />

      {/* System Telemetry Modal */}
      <HealthModal isOpen={isHealthOpen} onClose={() => setIsHealthOpen(false)} />
    </div>
  );
};
