import React from 'react';
import { Activity, RotateCcw, CheckCircle2, Info } from 'lucide-react';

export default function ProgressDashboard({ mastery, replanCount, currentPath, currentIndex, isCompleted, onReset }) {
  const skills = Object.entries(mastery || {});
  
  // Calculate average mastery
  const avgMastery = skills.length > 0 
    ? (skills.reduce((acc, [_, val]) => acc + val, 0) / skills.length) * 100 
    : 0;

  const completedCount = currentPath ? currentPath.filter(s => s.if_learned).length : 0;
  const totalCount = currentPath ? currentPath.length : 1;
  const progressPercent = Math.round((completedCount / totalCount) * 100);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Top Level Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        <div className="paper-card" style={{ padding: '14px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            BKT Mastery
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
            {avgMastery.toFixed(0)}%
          </div>
        </div>

        <div className="paper-card" style={{ padding: '14px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Completed
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
            {progressPercent}%
          </div>
        </div>

        <div className="paper-card" style={{ padding: '14px' }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Replans
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
            {replanCount || 0}
          </div>
        </div>
      </div>

      {/* Per-Skill BKT Probabilities */}
      <div className="paper-card" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h3 style={{ fontSize: '0.95rem', color: 'var(--text-main)', fontWeight: 600 }}>
            Knowledge State (BKT Posterior)
          </h3>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            Goal: ≥ 70%
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {skills.map(([skillId, prob]) => {
            const percent = Math.min(100, Math.round(prob * 100));
            const isMastered = percent >= 70;

            return (
              <div key={skillId} style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                  <span style={{ fontWeight: 500, color: 'var(--text-body)', textTransform: 'capitalize' }}>
                    {skillId.replace(/_/g, ' ')}
                  </span>
                  <span style={{ 
                    fontWeight: 600, 
                    color: isMastered ? 'var(--accent-sage)' : 'var(--text-main)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.78rem'
                  }}>
                    {percent}% {isMastered ? '✓' : ''}
                  </span>
                </div>

                {/* Progress Bar */}
                <div style={{ 
                  height: '6px', 
                  width: '100%', 
                  background: 'var(--bg-canvas-subtle)', 
                  borderRadius: '999px', 
                  overflow: 'hidden' 
                }}>
                  <div 
                    style={{ 
                      height: '100%', 
                      width: `${percent}%`, 
                      background: isMastered ? 'var(--accent-sage)' : 'var(--ink-primary)', 
                      borderRadius: '999px',
                      transition: 'width 0.3s ease'
                    }} 
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Minimalist Formula Note */}
        <div style={{ 
          marginTop: '16px', 
          padding: '10px 12px', 
          background: 'var(--bg-canvas)', 
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          gap: '8px',
          fontSize: '0.74rem',
          color: 'var(--text-muted)'
        }}>
          <Info size={13} style={{ flexShrink: 0, marginTop: '2px' }} />
          <span>
            BKT Parameters: P(Slip)=0.10, P(Guess)=0.25, P(Learn)=0.30.
          </span>
        </div>
      </div>
    </div>
  );
}
