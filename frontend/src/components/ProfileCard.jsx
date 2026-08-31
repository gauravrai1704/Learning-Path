import React from 'react';
import { User } from 'lucide-react';

export default function ProfileCard({ profile }) {
  if (!profile) return null;

  const { interests = [], experience_level, completed_courses = [], objectives = [] } = profile;

  const hasContent = interests.length || experience_level || completed_courses.length || objectives.length;
  if (!hasContent) return null;

  return (
    <div className="paper-card" style={{ padding: '18px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <User size={16} color="var(--text-main)" />
        <h3 style={{ fontSize: '0.95rem', color: 'var(--text-main)', fontWeight: 600 }}>
          Learner Profile
        </h3>
        {experience_level && (
          <span className="badge badge-neutral" style={{ fontSize: '0.7rem', textTransform: 'capitalize' }}>
            {experience_level}
          </span>
        )}
      </div>

      {interests.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '4px' }}>
            Interests
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
            {interests.map((interest, idx) => (
              <span key={idx} style={{ fontSize: '0.75rem', background: 'var(--bg-canvas-subtle)', color: 'var(--text-body)', padding: '2px 8px', borderRadius: '999px' }}>
                {interest}
              </span>
            ))}
          </div>
        </div>
      )}

      {objectives.length > 0 && (
        <div style={{ marginBottom: completed_courses.length ? '10px' : 0 }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '4px' }}>
            Objectives
          </div>
          <ul style={{ paddingLeft: '16px', margin: 0 }}>
            {objectives.map((obj, idx) => (
              <li key={idx} style={{ fontSize: '0.8rem', color: 'var(--text-body)', marginBottom: '2px' }}>{obj}</li>
            ))}
          </ul>
        </div>
      )}

      {completed_courses.length > 0 && (
        <div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '4px' }}>
            Completed
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
            {completed_courses.map((course, idx) => (
              <span key={idx} style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {course}{idx < completed_courses.length - 1 ? ',' : ''}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
