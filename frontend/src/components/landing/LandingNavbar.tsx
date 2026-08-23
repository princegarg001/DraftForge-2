import React, { useState, useEffect } from 'react';
import {
  Scale,
  Menu,
  X,
  ArrowRight,
} from 'lucide-react';

interface LandingNavbarProps {
  onOpenAuth: () => void;
  onOpenHealth?: () => void;
}

export const LandingNavbar: React.FC<LandingNavbarProps> = ({
  onOpenAuth,
  onOpenHealth,
}) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { label: 'Features', href: '#features' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'AI Evaluation & RAG', href: '#ai-evaluation' },
    { label: 'For Students', href: '#students' },
    { label: 'For Faculty', href: '#faculty' },
    { label: 'Live Scanner', href: '#scanner' },
  ];

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled
            ? 'bg-slate-950/85 backdrop-blur-xl border-b border-slate-800/80 shadow-xl shadow-black/40 py-3.5'
            : 'bg-transparent py-5'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          {/* Brand Logo */}
          <a href="#" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-primary-600 via-indigo-600 to-accent-cyan p-0.5 shadow-lg shadow-primary-500/25 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <Scale className="w-5 h-5 text-primary-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-extrabold tracking-tight text-white group-hover:text-primary-300 transition-colors">
                  Draft<span className="text-primary-400">Forge</span>
                </span>
                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-primary-500/10 text-primary-300 border border-primary-500/20 uppercase tracking-wider font-mono">
                  AI LegalTech
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-medium hidden sm:block">
                Evidence-Grounded Drafting & Evaluation
              </p>
            </div>
          </a>

          {/* Desktop Nav Links */}
          <nav className="hidden lg:flex items-center gap-1.5 p-1 bg-slate-900/60 backdrop-blur-md rounded-2xl border border-slate-800/80">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/80 rounded-xl transition-all"
              >
                {link.label}
              </a>
            ))}
          </nav>

          {/* Action CTAs */}
          <div className="flex items-center gap-3">
            {onOpenHealth && (
              <button
                onClick={onOpenHealth}
                className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-[11px] font-semibold border border-emerald-500/20 transition-all font-mono"
                title="Telemetry: Supabase, FastEmbed, Qdrant & Neo4j Aura"
              >
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Backend Live</span>
              </button>
            )}

            <button
              onClick={onOpenAuth}
              className="hidden sm:inline-flex px-4 py-2 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-900 border border-slate-800 transition-all"
            >
              Sign In
            </button>

            <button
              onClick={onOpenAuth}
              className="flex items-center gap-2 px-4 sm:px-5 py-2 bg-gradient-to-r from-primary-600 via-indigo-600 to-accent-cyan hover:from-primary-500 hover:to-accent-cyan text-white text-xs font-bold rounded-xl shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40 transition-all group"
            >
              <span>Get Started</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </button>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Slide-Over Menu */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-slate-950/95 backdrop-blur-2xl lg:hidden flex flex-col justify-between p-6 pt-24 animate-fade-in">
          <div className="space-y-3">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-3">
              Navigation
            </p>
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className="block p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800 text-sm font-bold text-slate-200 hover:text-white hover:border-primary-500/40 transition-colors"
              >
                {link.label}
              </a>
            ))}
          </div>

          <div className="space-y-3 pt-6 border-t border-slate-800">
            <button
              onClick={() => {
                setIsMobileMenuOpen(false);
                onOpenAuth();
              }}
              className="w-full py-3 rounded-2xl bg-gradient-to-r from-primary-600 to-indigo-600 text-white font-bold text-xs shadow-lg shadow-primary-500/25"
            >
              Enter DraftForge Studio
            </button>
            <button
              onClick={() => {
                setIsMobileMenuOpen(false);
                onOpenAuth();
              }}
              className="w-full py-3 rounded-2xl bg-slate-900 border border-slate-800 text-slate-300 font-bold text-xs"
            >
              Sign In to Account
            </button>
          </div>
        </div>
      )}
    </>
  );
};
