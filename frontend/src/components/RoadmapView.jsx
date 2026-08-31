import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Circle, 
  ArrowDown, 
  BookOpen, 
  AlertCircle, 
  MessageCircleQuestion, 
  Link2, 
  ExternalLink, 
  Plus, 
  X, 
  Check 
} from 'lucide-react';

export default function RoadmapView({ 
  currentPath, 
  currentIndex, 
  isCompleted, 
  onSelectSession, 
  onAskWhy,
  onAddResource 
}) {
  const [activeAddIdx, setActiveAddIdx] = useState(null);
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  const [type, setType] = useState('article');
  const [reason, setReason] = useState('');
  const [isSaving, setIsSaving] = useState(false);

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

  const handleOpenAdd = (idx, e) => {
    e.stopPropagation();
    setActiveAddIdx(activeAddIdx === idx ? null : idx);
    setTitle('');
    setUrl('');
    setType('article');
    setReason('');
  };

  const handleSaveResource = async (idx, e) => {
    e.preventDefault();
    if (!title.trim() || !url.trim()) return;

    let formattedUrl = url.trim();
    if (!/^https?:\/\//i.test(formattedUrl)) {
      formattedUrl = 'https://' + formattedUrl;
    }

    setIsSaving(true);
    try {
      if (onAddResource) {
        await onAddResource(idx, {
          title: title.trim(),
          url: formattedUrl,
          type: type || 'custom',
          reason: reason.trim() || 'Added by learner'
        });
      }
      setActiveAddIdx(null);
      setTitle('');
      setUrl('');
      setReason('');
    } catch (err) {
      console.error('Failed to add resource:', err);
    } finally {
      setIsSaving(false);
    }
  };

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
          const isAdding = activeAddIdx === idx;

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

                    {/* Recommended Resources List */}
                    <div style={{ marginTop: '12px' }}>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between',
                        marginBottom: '6px'
                      }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                          Learning Resources
                        </span>
                        
                        {onAddResource && (
                          <button
                            onClick={(e) => handleOpenAdd(idx, e)}
                            style={{
                              border: 'none',
                              background: 'none',
                              color: isAdding ? 'var(--text-muted)' : 'var(--ink-primary)',
                              fontSize: '0.75rem',
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '2px 6px',
                              borderRadius: '4px',
                              fontWeight: 500
                            }}
                          >
                            {isAdding ? (
                              <><X size={12} /> Cancel</>
                            ) : (
                              <><Plus size={12} /> Add Link</>
                            )}
                          </button>
                        )}
                      </div>

                      {session.recommended_resources && session.recommended_resources.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {session.recommended_resources.map((res, rIdx) => (
                            <div 
                              key={rIdx} 
                              style={{ 
                                display: 'flex', 
                                alignItems: 'flex-start', 
                                gap: '6px', 
                                fontSize: '0.78rem', 
                                color: 'var(--text-muted)',
                                background: 'var(--bg-card)',
                                padding: '6px 8px',
                                borderRadius: '6px',
                                border: '1px solid var(--border-subtle)'
                              }}
                            >
                              <Link2 size={13} style={{ marginTop: '2px', flexShrink: 0, color: 'var(--text-dim)' }} />
                              <div style={{ flex: 1, minWidth: 0, overflowWrap: 'break-word' }}>
                                {res.url ? (
                                  <a 
                                    href={res.url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    onClick={(e) => e.stopPropagation()}
                                    style={{
                                      color: 'var(--ink-primary)',
                                      fontWeight: 600,
                                      textDecoration: 'none',
                                      display: 'inline-flex',
                                      alignItems: 'center',
                                      gap: '4px'
                                    }}
                                  >
                                    <span>{res.title}</span>
                                    <ExternalLink size={11} style={{ flexShrink: 0 }} />
                                  </a>
                                ) : (
                                  <strong style={{ color: 'var(--text-body)' }}>{res.title}</strong>
                                )}
                                {res.type ? (
                                  <span style={{ 
                                    fontSize: '0.7rem', 
                                    background: 'var(--bg-canvas-subtle)', 
                                    padding: '1px 5px', 
                                    borderRadius: '3px',
                                    marginLeft: '6px',
                                    color: 'var(--text-muted)'
                                  }}>
                                    {res.type}
                                  </span>
                                ) : null}
                                {res.reason && (
                                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                                    {res.reason}
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontStyle: 'italic', margin: '2px 0' }}>
                          No resources attached yet.
                        </p>
                      )}

                      {/* Inline Add Resource Form */}
                      {isAdding && (
                        <form 
                          onSubmit={(e) => handleSaveResource(idx, e)}
                          onClick={(e) => e.stopPropagation()}
                          style={{
                            marginTop: '8px',
                            padding: '12px',
                            background: 'var(--bg-card)',
                            border: '1px solid var(--border-strong)',
                            borderRadius: '8px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '8px'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}>
                              Add Study Link / Resource
                            </span>
                            <button
                              type="button"
                              onClick={(e) => handleOpenAdd(idx, e)}
                              style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--text-dim)' }}
                            >
                              <X size={14} />
                            </button>
                          </div>

                          <input
                            type="text"
                            placeholder="Resource title (e.g. Official Docs, Tutorial Video)"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            required
                            style={{
                              padding: '6px 10px',
                              fontSize: '0.8rem',
                              border: '1px solid var(--border-subtle)',
                              borderRadius: '4px',
                              outline: 'none',
                              width: '100%'
                            }}
                          />

                          <input
                            type="url"
                            placeholder="https://example.com/guide"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            required
                            style={{
                              padding: '6px 10px',
                              fontSize: '0.8rem',
                              border: '1px solid var(--border-subtle)',
                              borderRadius: '4px',
                              outline: 'none',
                              width: '100%'
                            }}
                          />

                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '8px' }}>
                            <select
                              value={type}
                              onChange={(e) => setType(e.target.value)}
                              style={{
                                padding: '6px 8px',
                                fontSize: '0.78rem',
                                border: '1px solid var(--border-subtle)',
                                borderRadius: '4px',
                                background: '#fff'
                              }}
                            >
                              <option value="article">Article / Doc</option>
                              <option value="course">Course / Tutorial</option>
                              <option value="video">Video</option>
                              <option value="project">Project / Repo</option>
                              <option value="notes">Personal Notes</option>
                              <option value="custom">Other</option>
                            </select>

                            <input
                              type="text"
                              placeholder="Short note or why this fits (optional)"
                              value={reason}
                              onChange={(e) => setReason(e.target.value)}
                              style={{
                                padding: '6px 10px',
                                fontSize: '0.78rem',
                                border: '1px solid var(--border-subtle)',
                                borderRadius: '4px',
                                outline: 'none'
                              }}
                            />
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '6px', marginTop: '4px' }}>
                            <button
                              type="button"
                              onClick={(e) => handleOpenAdd(idx, e)}
                              className="btn-secondary"
                              style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                            >
                              Cancel
                            </button>
                            <button
                              type="submit"
                              disabled={isSaving || !title.trim() || !url.trim()}
                              className="btn-primary"
                              style={{ padding: '4px 12px', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            >
                              <Check size={12} />
                              {isSaving ? 'Saving...' : 'Add Link'}
                            </button>
                          </div>
                        </form>
                      )}
                    </div>

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
