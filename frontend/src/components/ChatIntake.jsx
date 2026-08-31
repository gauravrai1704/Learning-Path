import React, { useState } from 'react';
import { ArrowRight, BookOpen, Target, CheckCircle2, Bookmark } from 'lucide-react';

const PRESETS = [
  {
    title: "SQL & Query Performance",
    goal: "I want to master database indexing, query execution plans, and multi-table joins for high-throughput APIs.",
    bg: "I already write basic SELECT and WHERE statements in PostgreSQL."
  },
  {
    title: "LangGraph Multi-Agent Workflows",
    goal: "I want to build stateful multi-agent workflows with conditional routing and memory persistence.",
    bg: "I know basic Python and have used simple LLM prompt wrappers."
  },
  {
    title: "Distributed Caching & System Design",
    goal: "I want to design fault-tolerant distributed caching architectures with Redis and consistency guarantees.",
    bg: "I understand basic REST APIs and monolithic backend architecture."
  }
];

export default function ChatIntake({ onStart, isSubmitting, skillGaps }) {
  const [goal, setGoal] = useState('');
  const [background, setBackground] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!goal.trim()) return;
    onStart(goal, background || 'Beginner with foundational background');
  };

  const applyPreset = (preset) => {
    setGoal(preset.goal);
    setBackground(preset.bg);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Main Intake Form Card */}
      <div className="paper-card" style={{ padding: '32px' }}>
        {/* Quick Presets */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
            <Bookmark size={14} color="var(--text-muted)" />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Example Curriculums
            </span>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {PRESETS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                className="btn-secondary"
                onClick={() => applyPreset(p)}
                style={{ fontSize: '0.82rem', padding: '6px 12px' }}
              >
                {p.title}
              </button>
            ))}
          </div>
        </div>

        {/* Form Fields */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
              What is your primary learning goal?
            </label>
            <textarea
              required
              rows={3}
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g., Master database indexing, query plans, and complex multi-table joins for backend systems..."
              style={{
                width: '100%',
                padding: '12px 14px',
                lineHeight: 1.5,
                resize: 'vertical'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
              What is your current background / known skills?
            </label>
            <input
              type="text"
              value={background}
              onChange={(e) => setBackground(e.target.value)}
              placeholder="e.g., Basic SQL SELECT queries, Python familiarity..."
              style={{
                width: '100%',
                padding: '10px 14px'
              }}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '4px' }}>
            <button
              type="submit"
              disabled={isSubmitting || !goal.trim()}
              className="btn-primary"
            >
              {isSubmitting ? (
                'Building Curriculum...'
              ) : (
                <>
                  Generate Learning Path
                  <ArrowRight size={15} />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Identified Skill Gaps Breakdown */}
      {skillGaps && skillGaps.length > 0 && (
        <div className="paper-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-main)' }}>
            <CheckCircle2 size={16} color="var(--accent-sage)" />
            Skill Gap Breakdown
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px' }}>
            {skillGaps.map((gap, idx) => (
              <div 
                key={idx}
                style={{
                  background: 'var(--bg-canvas)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '14px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.9rem' }}>{gap.name}</span>
                  <span className={`badge ${gap.level_confidence === 'high' ? 'badge-sage' : 'badge-amber'}`}>
                    {gap.level_confidence} confidence
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '8px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  <span>Current: <strong>{gap.current_level}</strong></span>
                  <span>→</span>
                  <span>Target: <strong>{gap.required_level}</strong></span>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-body)', lineHeight: 1.4, marginTop: '4px' }}>
                  {gap.reason}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
