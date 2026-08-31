import React, { useState } from 'react';
import { BookOpen, RefreshCw, Compass, GraduationCap, CheckCircle2, RotateCcw } from 'lucide-react';
import ChatIntake from './components/ChatIntake';
import RoadmapView from './components/RoadmapView';
import QuizPanel from './components/QuizPanel';
import ProgressDashboard from './components/ProgressDashboard';
import { apiClient } from './api/client';

export default function App() {
  const [session, setSession] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Start new learning path session
  const handleStartSession = async (goal, background) => {
    setIsSubmitting(true);
    try {
      const response = await apiClient.startSession(goal, background);
      setSession(response);
    } catch (err) {
      console.error('Failed to start session:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Submit quiz answer and update state
  const handleSubmitAnswers = async (answers) => {
    if (!session) return;
    setIsSubmitting(true);
    try {
      const response = await apiClient.submitQuizAnswer(session.session_id, answers);
      setSession(response);
    } catch (err) {
      console.error('Failed to submit answer:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Reset to create new session
  const handleResetSession = () => {
    setSession(null);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-canvas)' }}>
      {/* Editorial Navigation Bar */}
      <header style={{
        borderBottom: '1px solid var(--border-subtle)',
        background: 'var(--bg-card)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        padding: '14px 28px'
      }}>
        <div style={{ 
          maxWidth: '1280px', 
          margin: '0 auto', 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center' 
        }}>
          {/* Logo & Platform Name */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              background: 'var(--bg-canvas-subtle)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '6px 8px',
              display: 'flex',
              color: 'var(--text-main)'
            }}>
              <GraduationCap size={18} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1.05rem', color: 'var(--text-main)', fontWeight: 700, letterSpacing: '-0.02em' }}>
                  PathFinder
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', borderLeft: '1px solid var(--border-subtle)', paddingLeft: '8px' }}>
                  Curriculum Engine
                </span>
              </div>
            </div>
          </div>

          {/* Right Status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: '#166534' }} />
              <span>BKT Active</span>
            </div>
            {session && (
              <button 
                onClick={handleResetSession}
                className="btn-secondary" 
                style={{ padding: '6px 12px', fontSize: '0.8rem' }}
              >
                <RotateCcw size={13} />
                New Path
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ flex: 1, maxWidth: '1280px', margin: '0 auto', width: '100%', padding: '36px 24px' }}>
        {!session ? (
          // View 1: Goal Intake & Skill Gap Discovery
          <div style={{ maxWidth: '820px', margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: '36px' }}>
              <span className="badge badge-neutral" style={{ marginBottom: '12px' }}>
                Topological Prerequisite Planner
              </span>
              <h2 style={{ 
                fontSize: '2.4rem', 
                color: 'var(--text-main)', 
                fontWeight: 600, 
                lineHeight: 1.25,
                letterSpacing: '-0.03em'
              }}>
                Build your adaptive curriculum.
              </h2>
              <p style={{ 
                color: 'var(--text-muted)', 
                fontSize: '1.05rem', 
                maxWidth: '560px', 
                margin: '10px auto 0',
                lineHeight: 1.5
              }}>
                Specify what you want to learn. The engine analyzes skill dependencies and continuously calibrates your path using Bayesian Knowledge Tracing.
              </p>
            </div>

            <ChatIntake
              onStart={handleStartSession}
              isSubmitting={isSubmitting}
            />
          </div>
        ) : (
          // View 2: Active Curriculum & Study Dashboard
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(320px, 420px) 1fr',
            gap: '28px',
            alignItems: 'start'
          }}>
            {/* Left Column: Progress & Syllabus */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <ProgressDashboard
                mastery={session.mastery}
                replanCount={session.replan_count}
                currentPath={session.current_path}
                currentIndex={session.current_index}
                isCompleted={session.is_completed}
                onReset={handleResetSession}
              />

              <RoadmapView
                currentPath={session.current_path}
                currentIndex={session.current_index}
                isCompleted={session.is_completed}
              />
            </div>

            {/* Right Column: Quiz Verification & Assessment */}
            <div>
              <QuizPanel
                quiz={session.last_quiz}
                onSubmitAnswers={handleSubmitAnswers}
                isSubmitting={isSubmitting}
                lastResult={session.last_quiz_score}
                explanation={session.explanation}
              />
            </div>
          </div>
        )}
      </main>

      {/* Clean Editorial Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '20px 24px',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        background: 'var(--bg-canvas)'
      }}>
        PathFinder • Bayesian Knowledge Tracing & Directed Prerequisite Graph Architecture
      </footer>
    </div>
  );
}
