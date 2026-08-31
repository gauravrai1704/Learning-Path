import React from 'react';
import { CheckCircle2, Circle, ArrowDown, BookOpen, AlertCircle, Award, MessageCircleQuestion, Link2 } from 'lucide-react';

export default function RoadmapView({ currentPath, currentIndex, isCompleted, onSelectSession, onAskWhy }) {
  if (!currentPath || currentPath.length === 0) {
    return (
      <div className="paper-card" style={{ padding: '32px', textAlign: 'center' }}>
        <BookOpen size={28} color="var(--text-dim)" style={{ margin: '0 auto 8px' }} />
        <h3 style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Curriculum Pending</h3>
        <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginTop: '2px' }}>
          Submit your learning goal to construct your customized syllabus.
        </p>
      </div>
    );
  }

  return (
    <div className="paper-card" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BookOpen size={17} color="var(--text-main)" />
            Learning Pathway
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '2px' }}>
            Sequenced by topological prerequisite dependencies.
          </p>
        </div>
        <span className="badge badge-neutral">
          {isCompleted ? 'Curriculum Complete' : `Step ${currentIndex + 1} of ${currentPath.length}`}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {currentPath.map((session, idx) => {
          const isPassed = session.if_learned || (idx < currentIndex);
          const isActive = idx === currentIndex && !isCompleted;
          const isRemedial = session.title.toLowerCase().includes('remedial') || session.title.toLowerCase().includes('drill');

          return (
            <div key={session.id || idx}>
              <div
                onClick={() => onSelectSession && onSelectSession(idx)}
                style={{
                  background: isActive 
                    ? '#FFFFFF' 
                    : isPassed 
                    ? 'var(--accent-sage-subtle)' 
                    : 'var(--bg-canvas)',
                  border: isActive 
                    ? '1.5px solid var(--ink-primary)' 
                    : isPassed 
                    ? '1px solid #BBF7D0' 
                    : '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  position: 'relative'
                }}
              >
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  {/* Status Indicator */}
                  <div style={{ marginTop: '2px', flexShrink: 0 }}>
                    {isPassed ? (
                      <CheckCircle2 size={18} color="var(--accent-sage)" />
                    ) : isActive ? (
                      <div style={{
                        width: '18px',
                        height: '18px',
                        borderRadius: '50%',
                        border: '2px solid var(--ink-primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--ink-primary)' }} />
                      </div>
                    ) : (
                      <Circle size={18} color="var(--border-strong)" />
                    )}
                  </div>

                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                        {session.id}
                      </span>
                      {isRemedial && (
                        <span className="badge badge-amber" style={{ fontSize: '0.7rem' }}>
                          <AlertCircle size={10} /> Targeted Drill
                        </span>
                      )}
                      {isActive && (
                        <span className="badge badge-neutral" style={{ fontSize: '0.7rem', background: 'var(--ink-primary)', color: '#fff' }}>
                          Current
                        </span>
                      )}
                      {isPassed && (
                        <span className="badge badge-sage" style={{ fontSize: '0.7rem' }}>
                          Mastered
                        </span>
                      )}
                    </div>

                    <h4 style={{ fontSize: '0.98rem', color: 'var(--text-main)', marginTop: '4px', fontWeight: 600 }}>
                      {session.title}
                    </h4>

                    <p style={{ fontSize: '0.82rem', color: 'var(--text-body)', marginTop: '4px', lineHeight: 1.45 }}>
                      {session.abstract}
                    </p>

                    {/* Associated Skills */}
                    {session.associated_skills && session.associated_skills.length > 0 && (
                      <div style={{ display: 'flex', gap: '6px', marginTop: '10px', flexWrap: 'wrap' }}>
                        {session.associated_skills.map((skill, sIdx) => (
                          <span 
                            key={sIdx}
                            style={{
                              fontSize: '0.72rem',
                              background: 'var(--bg-canvas-subtle)',
                              color: 'var(--text-muted)',
                              padding: '2px 6px',
                              borderRadius: '4px',
                              fontFamily: 'var(--font-mono)'
                            }}
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Recommended Resources */}
                    {session.recommended_resources && session.recommended_resources.length > 0 && (
                      <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        {session.recommended_resources.map((res, rIdx) => (
                          <div key={rIdx} style={{ display: 'flex', alignItems: 'flex-start', gap: '5px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                            <Link2 size={12} style={{ marginTop: '3px', flexShrink: 0 }} />
                            <span>
                              <strong style={{ color: 'var(--text-body)' }}>{res.title}</strong>
                              {res.type ? ` (${res.type})` : ''} — {res.reason}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Ask why this session was recommended */}
                    {onAskWhy && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onAskWhy(`Why was "${session.title}" (${session.id}) recommended, and why is it in this position in the path?`);
                        }}
                        className="btn-secondary"
                        style={{
                          marginTop: '10px',
                          padding: '4px 10px',
                          fontSize: '0.74rem',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '5px'
                        }}
                      >
                        <MessageCircleQuestion size={12} />
                        Why this?
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Minimalist Connector */}
              {idx < currentPath.length - 1 && (
                <div style={{ display: 'flex', justifyContent: 'center', margin: '3px 0' }}>
                  <ArrowDown size={14} color="var(--border-strong)" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
