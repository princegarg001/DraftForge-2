import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Roadmap, StudentSkill } from '../../types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useToast } from '../common/Toast';
import { AIRoadmapGenerator } from '../ai/AIRoadmapGenerator';

export const RoadmapView: React.FC = () => {
  const { showToast } = useToast();
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [skills, setSkills] = useState<StudentSkill[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [completingItemId, setCompletingItemId] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [rRes, sRes] = await Promise.all([
        api.getActiveRoadmap().catch(() => ({ data: null })),
        api.getSkills().catch(() => ({ data: [] })),
      ]);
      setRoadmap(rRes.data);
      setSkills(sRes.data || []);
    } catch (err: any) {
      showToast('Error loading personalized learning roadmap', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await api.generateRoadmap();
      setRoadmap(res.data);
      showToast('New 5-phase personalized roadmap synthesized!', 'success');
      const sRes = await api.getSkills();
      setSkills(sRes.data || []);
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Roadmap generation failed', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleToggleComplete = async (itemId: string) => {
    setCompletingItemId(itemId);
    try {
      const res = await api.completeRoadmapItem(itemId);
      showToast('Phase milestone marked as completed!', 'success');
      if (roadmap) {
        const updatedItems = roadmap.roadmap_items.map((it) =>
          it.id === itemId ? { ...it, is_completed: true, completed_at: res.data.completed_at } : it
        );
        setRoadmap({ ...roadmap, roadmap_items: updatedItems });
      }
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'Failed to update milestone', 'error');
    } finally {
      setCompletingItemId(null);
    }
  };

  if (loading) {
    return (
      <div className="py-24 flex justify-center">
        <LoadingSpinner size="xl" label="Calibrating personalized legal drafting trajectory..." />
      </div>
    );
  }

  return (
    <AIRoadmapGenerator
      roadmap={roadmap}
      skills={skills}
      generating={generating}
      onCompleteItem={handleToggleComplete}
      completingItemId={completingItemId}
      onGenerateNew={handleGenerate}
    />
  );
};