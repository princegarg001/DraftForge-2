import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle2, XCircle, RefreshCw, Server, Database, Network } from 'lucide-react';
import { Modal } from './Modal';
import { api } from '../../services/api';
import { HealthCheckResponse } from '../../types';
import { LoadingSpinner } from './LoadingSpinner';

interface HealthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HealthModal: React.FC<HealthModalProps> = ({ isOpen, onClose }) => {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.checkHealth();
      setHealth(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to connect to backend telemetry service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) fetchHealth();
  }, [isOpen]);

  const getServiceIcon = (key: string) => {
    if (key.includes('postgresql')) return <Database className="w-5 h-5 text-indigo-400" />;
    if (key.includes('qdrant')) return <Server className="w-5 h-5 text-cyan-400" />;
    if (key.includes('neo4j')) return <Network className="w-5 h-5 text-amber-400" />;
    return <Activity className="w-5 h-5 text-primary-400" />;
  };

  const getServiceLabel = (key: string) => {
    if (key === 'supabase_postgresql') return 'Supabase PostgreSQL';
    if (key === 'qdrant_cloud') return 'Qdrant Cloud Vector DB';
    if (key === 'neo4j_aura') return 'Neo4j Aura Knowledge Graph';
    return key.replace(/_/g, ' ').toUpperCase();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="System Architecture Health"
      subtitle="Live end-to-end telemetry across managed database clusters"
      icon={<Activity className="w-5 h-5" />}
      maxWidth="lg"
    >
      <div className="space-y-6">
        {loading ? (
          <div className="py-12 flex justify-center">
            <LoadingSpinner size="lg" label="Querying cloud infrastructure status..." />
          </div>
        ) : error ? (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-start gap-3">
            <XCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Health Verification Failed</p>
              <p className="text-xs text-rose-300/80 mt-1">{error}</p>
            </div>
          </div>
        ) : health ? (
          <>
            {/* Top Status Banner */}
            <div
              className={`p-4 rounded-xl border flex items-center justify-between ${
                health.status === 'healthy'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
              }`}
            >
              <div className="flex items-center gap-3">
                {health.status === 'healthy' ? (
                  <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                ) : (
                  <XCircle className="w-6 h-6 text-amber-400" />
                )}
                <div>
                  <h4 className="font-semibold text-sm capitalize">
                    System State: {health.status}
                  </h4>
                  <p className="text-xs opacity-80">
                    DraftForge API Runtime v{health.app_version}
                  </p>
                </div>
              </div>
              <button
                onClick={fetchHealth}
                className="p-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
                title="Refresh telemetry"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            {/* Services List */}
            <div className="space-y-3">
              <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Managed Cloud Nodes
              </h5>
              {Object.entries(health.services).map(([key, s]) => {
                if (!s) return null;
                return (
                  <div
                    key={key}
                    className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/50 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center">
                        {getServiceIcon(key)}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">
                          {getServiceLabel(key)}
                        </p>
                        <p className="text-xs text-slate-400">{s.details}</p>
                      </div>
                    </div>
                    <div>
                      {s.reachable ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                          ONLINE
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          OFFLINE
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        ) : null}

        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
};
