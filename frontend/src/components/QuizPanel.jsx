import React, { useState } from 'react';
import { CheckCircle2, ArrowRight, HelpCircle, BookOpen, AlertCircle } from 'lucide-react';

export default function QuizPanel({ quiz, onSubmitAnswers, isSubmitting, lastResult, explanation, onAdvance }) {
  const [selectedAnswers, setSelectedAnswers] = useState({});

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return (
      <div className="paper-card" style={{ padding: '36px', textAlign: 'center' }}>
        <CheckCircle2 size={36} color="var(--accent-sage)" style={{ margin: '0 auto 12px' }} />
        <h3 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>Curriculum Completed</h3>
        <p style={{ color: 'var(--text-muted)', marginTop: '6px', maxWidth: '380px', margin: '6px auto 0', fontSize: '0.9rem' }}>
          All target skill competencies have met the Bayesian mastery threshold (P ≥ 0.70).
        </p>
      </div>
    );
  }

  const handleSelectOption = (qIdx, optIdx) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [qIdx]: optIdx
    }));
  };

  const isAllAnswered = quiz.questions.every((_, idx) => selectedAnswers[idx] !== undefined);

  const handleSubmit = (e) => {
    e.preventDefault();
    const answersArray = quiz.questions.map((_, idx) => selectedAnswers[idx]);
    onSubmitAnswers(answersArray);
  };

  return (
    <div className="paper-card" style={{ padding: '28px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Concept Verification
          </span>
          <h2 style={{ fontSize: '1.2rem', color: 'var(--text-main)', marginTop: '2px' }}>
            {quiz.skill_name || quiz.skill_id}
          </h2>
        </div>
        <span className="badge badge-neutral">
          {quiz.questions.length} Questions
        </span>
      </div>

      {/* Remedial Feedback Banner (if user missed previous attempt) */}
      {explanation && (
        <div 
          style={{
            background: 'var(--accent-amber-subtle)',
            border: '1px solid #FDE68A',
            borderRadius: 'var(--radius-md)',
            padding: '14px 16px',
            marginBottom: '20px',
            display: 'flex',
            gap: '10px',
            alignItems: 'flex-start'
          }}
        >
          <AlertCircle size={17} color="var(--accent-amber)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ color: 'var(--accent-amber)', fontSize: '0.88rem', fontWeight: 600, marginBottom: '2px' }}>
              Reflexion Note & Review
            </h4>
            <p style={{ color: 'var(--text-body)', fontSize: '0.82rem', lineHeight: 1.45 }}>
              {explanation}
            </p>
          </div>
        </div>
      )}

      {/* Form Questions */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {quiz.questions.map((q, qIdx) => {
          const selected = selectedAnswers[qIdx];
          const hasResult = lastResult !== undefined && lastResult !== null;

          return (
            <div 
              key={qIdx}
              style={{
                background: 'var(--bg-canvas)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '16px 18px'
              }}
            >
              <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', marginBottom: '12px' }}>
                <span style={{ 
                  background: 'var(--bg-card)', 
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-main)', 
                  fontSize: '0.75rem', 
                  fontWeight: 600,
                  width: '22px',
                  height: '22px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  {qIdx + 1}
                </span>
                <h4 style={{ fontSize: '0.92rem', color: 'var(--text-main)', lineHeight: 1.45, fontWeight: 600 }}>
                  {q.question}
                </h4>
              </div>

              {/* Options */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', paddingLeft: '32px' }}>
                {q.options.map((opt, optIdx) => {
                  const isSelected = selected === optIdx;
                  const optionLetters = ['A', 'B', 'C', 'D'];

                  return (
                    <div
                      key={optIdx}
                      onClick={() => handleSelectOption(qIdx, optIdx)}
                      style={{
                        padding: '10px 14px',
                        borderRadius: 'var(--radius-sm)',
                        background: isSelected ? 'var(--bg-card)' : 'transparent',
                        border: isSelected 
                          ? '1px solid var(--ink-primary)' 
                          : '1px solid var(--border-subtle)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        transition: 'all 0.1s ease',
                        boxShadow: isSelected ? '0 1px 3px rgba(0,0,0,0.05)' : 'none'
                      }}
                    >
                      <span style={{ 
                        fontSize: '0.75rem', 
                        fontWeight: 600, 
                        color: isSelected ? 'var(--text-main)' : 'var(--text-dim)',
                        width: '16px'
                      }}>
                        {optionLetters[optIdx]}.
                      </span>
                      <span style={{ fontSize: '0.86rem', color: isSelected ? 'var(--text-main)' : 'var(--text-body)', fontWeight: isSelected ? 500 : 400 }}>
                        {opt}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Explanation Note */}
              {hasResult && q.explanation && (
                <div style={{ marginTop: '10px', marginLeft: '32px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  Note: {q.explanation}
                </div>
              )}
            </div>
          );
        })}

        {/* Submit */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '4px' }}>
          <button
            type="submit"
            disabled={!isAllAnswered || isSubmitting}
            className="btn-primary"
          >
            {isSubmitting ? 'Evaluating...' : (
              <>
                Submit Responses
                <ArrowRight size={15} />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
