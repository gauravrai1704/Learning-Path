import React, { useState } from 'react';
import { MessageCircleQuestion, Loader2, Sparkles } from 'lucide-react';
import { apiClient } from '../api/client';

export default function ExplainPanel({ sessionId, prefillQuestion, onConsumePrefill }) {
  const [question, setQuestion] = useState(prefillQuestion || '');
  const [isAsking, setIsAsking] = useState(false);
  const [answer, setAnswer] = useState(null);

  React.useEffect(() => {
    if (prefillQuestion) {
      setQuestion(prefillQuestion);
      handleAsk(prefillQuestion);
      if (onConsumePrefill) onConsumePrefill();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [prefillQuestion]);

  const handleAsk = async (overrideQuestion) => {
    const q = (overrideQuestion || question).trim();
    if (!q || !sessionId) return;
    setIsAsking(true);
    setAnswer(null);
    try {
      const result = await apiClient.explainRecommendation(sessionId, q);
      setAnswer(result);
    } catch (err) {
      console.error('Failed to fetch explanation:', err);
      setAnswer({ answer: 'Something went wrong fetching an explanation. Please try again.' });
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <div className="paper-card" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
        <MessageCircleQuestion size={16} color="var(--text-main)" />
        <h3 style={{ fontSize: '0.95rem', color: 'var(--text-main)', fontWeight: 600 }}>
          Ask why
        </h3>
      </div>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
        Ask about any recommendation, prerequisite, or why the path changed.
      </p>

      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
          placeholder="e.g. Why do I need indexing before query plans?"
          style={{
            flex: 1,
            padding: '9px 12px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.85rem',
            background: 'var(--bg-canvas)'
          }}
        />
        <button
          onClick={() => handleAsk()}
          disabled={isAsking || !question.trim()}
          className="btn-secondary"
          style={{ padding: '9px 14px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          {isAsking ? <Loader2 size={14} className="spin" /> : <Sparkles size={14} />}
          Ask
        </button>
      </div>

      {answer && (
        <div style={{
          marginTop: '14px',
          padding: '12px 14px',
          background: 'var(--bg-canvas-subtle)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
          fontSize: '0.85rem',
          color: 'var(--text-body)',
          lineHeight: 1.5
        }}>
          {answer.answer}
          {answer.referenced_session_id && (
            <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              Ref: {answer.referenced_session_id}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
