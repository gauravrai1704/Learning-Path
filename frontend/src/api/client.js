/**
 * API Client for Adaptive Learning Path Engine.
 * Supports dual-mode:
 * 1. Connects to live FastAPI backend (POST /session/start, POST /session/:id/quiz/answer, etc.)
 * 2. Intelligent Mock Engine fallback with authentic Corbett & Anderson BKT updates and Reflexion replanning.
 */

const API_BASE = 'http://localhost:8000';

// In-memory simulation state for standalone mock mode
let mockDatabase = {
  sessionId: 'mock-session-' + Math.floor(Math.random() * 10000),
  userId: 'learner-alpha',
  userGoal: '',
  userBackground: '',
  currentIndex: 0,
  isCompleted: false,
  replanCount: 0,
  mastery: {
    'sql_joins': 0.15,
    'indexing_strategies': 0.10,
    'query_execution_plans': 0.10
  },
  skillGaps: [
    {
      name: 'SQL Multi-table Joins',
      is_gap: true,
      required_level: 'intermediate',
      current_level: 'beginner',
      reason: 'Learner knows SELECT & WHERE but lacks experience with complex JOIN conditions.',
      level_confidence: 'high'
    },
    {
      name: 'B-Tree & Hash Indexing',
      is_gap: true,
      required_level: 'intermediate',
      current_level: 'unlearned',
      reason: 'No prior indexing or performance tuning exposure.',
      level_confidence: 'high'
    },
    {
      name: 'Query Plan & Cost Estimation',
      is_gap: true,
      required_level: 'advanced',
      current_level: 'unlearned',
      reason: 'Needs to understand EXPLAIN ANALYZE for query optimization.',
      level_confidence: 'medium'
    }
  ],
  currentPath: [
    {
      id: 'Session 1',
      title: 'Mastering SQL Inner & Outer Joins',
      abstract: 'Foundational multi-table relational queries, CROSS JOIN vs FULL OUTER JOIN, and handling NULL matches.',
      if_learned: false,
      associated_skills: ['sql_joins'],
      desired_outcome_when_completed: [{ name: 'SQL Joins', level: 'intermediate' }],
      recommended_resources: [
        {
          title: 'PostgreSQL Official Documentation: Queries & Joins',
          type: 'documentation',
          reason: 'Clear reference on join syntax and join semantics',
          url: 'https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-FROM'
        },
        {
          title: 'SQLZoo Join Tutorial',
          type: 'course',
          reason: 'Interactive hands-on browser practice with multi-table queries',
          url: 'https://sqlzoo.net/wiki/The_JOIN_operation'
        }
      ]
    },
    {
      id: 'Session 2',
      title: 'Database Indexing Strategies',
      abstract: 'Clustered vs non-clustered indexes, B-Trees, selectivity, and avoiding index scan penalties.',
      if_learned: false,
      associated_skills: ['indexing_strategies'],
      desired_outcome_when_completed: [{ name: 'Indexing Strategies', level: 'intermediate' }],
      recommended_resources: [
        {
          title: 'Use The Index, Luke! - A Guide to Database Performance',
          type: 'article',
          reason: 'Comprehensive guide explaining index architecture & search paths',
          url: 'https://use-the-index-luke.com/'
        }
      ]
    },
    {
      id: 'Session 3',
      title: 'Query Optimization & EXPLAIN Plans',
      abstract: 'Reading execution plans, cost estimation, bottleneck detection, and query refactoring.',
      if_learned: false,
      associated_skills: ['query_execution_plans'],
      desired_outcome_when_completed: [{ name: 'Query Optimization', level: 'advanced' }],
      recommended_resources: [
        {
          title: 'PostgreSQL EXPLAIN Explained',
          type: 'article',
          reason: 'Deep-dive into interpreting cost metrics and node types',
          url: 'https://www.postgresql.org/docs/current/using-explain.html'
        }
      ]
    }
  ],
  quizzes: {
    0: {
      skill_id: 'sql_joins',
      skill_name: 'SQL Multi-table Joins',
      questions: [
        {
          question: 'Which SQL JOIN type returns all records when there is a match in either left or right table?',
          options: ['INNER JOIN', 'FULL OUTER JOIN', 'LEFT JOIN', 'CROSS JOIN'],
          correct_option_index: 1,
          explanation: 'FULL OUTER JOIN returns all matching and non-matching records from both tables, filling nulls where no match exists.'
        },
        {
          question: 'In a LEFT JOIN, what value appears in right-table columns if there is no corresponding match?',
          options: ['0', 'EMPTY STRING', 'NULL', 'UNDEFINED'],
          correct_option_index: 2,
          explanation: 'Columns from the right table are populated with NULL values when no matching foreign key is found.'
        },
        {
          question: 'What is the theoretical result set size of a CROSS JOIN between Table A (10 rows) and Table B (5 rows)?',
          options: ['15 rows', '50 rows', '5 rows', '10 rows'],
          correct_option_index: 1,
          explanation: 'A Cartesian product (CROSS JOIN) produces rows equal to count(A) * count(B) = 50 rows.'
        }
      ]
    },
    1: {
      skill_id: 'indexing_strategies',
      skill_name: 'B-Tree & Hash Indexing',
      questions: [
        {
          question: 'What is the primary benefit of a B-Tree index in relational databases?',
          options: [
            'Only supports exact hash lookups',
            'Supports efficient equality and range queries (BETWEEN, <, >) in O(log N)',
            'Compresses all database storage into RAM',
            'Eliminates all foreign key constraints'
          ],
          correct_option_index: 1,
          explanation: 'B-Trees maintain sorted order, making both point lookups and range scans very fast with O(log N) depth.'
        },
        {
          question: 'Why might an index NOT be used on a query containing `WHERE UPPER(email) = "TEST@EXAMPLE.COM"`?',
          options: [
            'Functions applied to columns prevent standard index range lookups unless an expression index exists',
            'Indexes only work on integer columns',
            'SQL prohibits lowercase strings in where clauses',
            'The database always skips indexes for email fields'
          ],
          correct_option_index: 0,
          explanation: 'Wrapping a column in a function like UPPER() obscures index bounds unless an explicit functional index was created.'
        }
      ]
    },
    2: {
      skill_id: 'query_execution_plans',
      skill_name: 'Query Plan & Cost Estimation',
      questions: [
        {
          question: 'What does a "Sequential Scan" (Seq Scan) in an EXPLAIN output signify?',
          options: [
            'The engine is reading the table sequentially from start to end without using an index',
            'The database is locked for writing',
            'A parallel thread is caching the result in Redis',
            'The query took 0 milliseconds'
          ],
          correct_option_index: 0,
          explanation: 'Seq Scan reads all data pages sequentially. For large tables, adding appropriate indexes avoids this overhead.'
        }
      ]
    },
    // Reflexion Remedial Quiz
    remedial: {
      skill_id: 'sql_joins',
      skill_name: 'Remedial: SQL Multi-table Joins Drill',
      questions: [
        {
          question: 'To combine two tables and keep only matching records where keys exist on BOTH sides, use:',
          options: ['FULL JOIN', 'INNER JOIN', 'CROSS JOIN', 'LEFT JOIN'],
          correct_option_index: 1,
          explanation: 'INNER JOIN strictly requires matching keys in both participating relations.'
        },
        {
          question: 'Which join produces a Cartesian product without an ON clause?',
          options: ['CROSS JOIN', 'INNER JOIN', 'RIGHT JOIN', 'SELF JOIN'],
          correct_option_index: 0,
          explanation: 'CROSS JOIN pairs every row of Table 1 with every row of Table 2.'
        }
      ]
    }
  }
};

/**
 * Pure Corbett & Anderson Bayesian Knowledge Tracing (BKT) math
 */
function calculateBKT(probMastery, isCorrect, probSlip = 0.1, probGuess = 0.25, probTransit = 0.3) {
  let numerator;
  let masteryAndGuess;
  if (isCorrect) {
    numerator = probMastery * (1 - probSlip);
    masteryAndGuess = (1 - probMastery) * probGuess;
  } else {
    numerator = probMastery * probSlip;
    masteryAndGuess = (1 - probMastery) * (1 - probGuess);
  }
  const probMasteryGivenObs = numerator / (numerator + masteryAndGuess);
  const updatedMastery = probMasteryGivenObs + (1 - probMasteryGivenObs) * probTransit;
  return Math.min(0.99, Math.max(0.01, parseFloat(updatedMastery.toFixed(3))));
}

export const apiClient = {
  /**
   * Start a new learning path session
   */
  async startSession(goal, background) {
    try {
      const response = await fetch(`${API_BASE}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal, background })
      });
      if (!response.ok) throw new Error('Network response not ok');
      return await response.json();
    } catch (err) {
      console.warn('[API Client] Backend not detected, running in high-fidelity mock engine mode.', err);
      // Initialize mock session
      mockDatabase.userGoal = goal;
      mockDatabase.userBackground = background;
      mockDatabase.currentIndex = 0;
      mockDatabase.isCompleted = false;
      mockDatabase.replanCount = 0;
      mockDatabase.mastery = {
        'sql_joins': 0.15,
        'indexing_strategies': 0.10,
        'query_execution_plans': 0.10
      };
      
      return {
        session_id: mockDatabase.sessionId,
        user_id: mockDatabase.userId,
        user_goal: goal,
        user_background: background,
        current_index: 0,
        is_completed: false,
        replan_count: 0,
        skill_gaps: mockDatabase.skillGaps,
        mastery: { ...mockDatabase.mastery },
        current_path: [...mockDatabase.currentPath],
        last_quiz: mockDatabase.quizzes[0],
        explanation: null
      };
    }
  },

  /**
   * Submit quiz answers and process BKT calculation / router transition
   */
  async submitQuizAnswer(sessionId, answers) {
    try {
      const response = await fetch(`${API_BASE}/session/${sessionId}/quiz/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers })
      });
      if (!response.ok) throw new Error('Network response not ok');
      return await response.json();
    } catch (err) {
      console.warn('[API Client] Mock processing answer submission...');
      const activeQuiz = mockDatabase.isReflexion 
        ? mockDatabase.quizzes.remedial 
        : (mockDatabase.quizzes[mockDatabase.currentIndex] || mockDatabase.quizzes[0]);
      
      let correctCount = 0;
      activeQuiz.questions.forEach((q, idx) => {
        if (answers[idx] === q.correct_option_index) {
          correctCount++;
        }
      });
      
      const score = correctCount / activeQuiz.questions.length;
      const isCorrect = score >= 0.66;
      const currentSkill = activeQuiz.skill_id;
      
      // Update BKT probability for current skill
      const currentProb = mockDatabase.mastery[currentSkill] || 0.15;
      const updatedProb = calculateBKT(currentProb, isCorrect);
      mockDatabase.mastery[currentSkill] = updatedProb;

      let explanation = null;
      let isReflexion = false;

      // Routing logic: Mastery >= 0.70 ? Advance : Replan/Reflexion
      if (updatedProb >= 0.6) {
        // Mark session as learned
        if (mockDatabase.currentPath[mockDatabase.currentIndex]) {
          mockDatabase.currentPath[mockDatabase.currentIndex].if_learned = true;
        }
        
        // Advance to next session
        if (mockDatabase.currentIndex + 1 < mockDatabase.currentPath.length) {
          mockDatabase.currentIndex += 1;
          mockDatabase.isReflexion = false;
        } else {
          mockDatabase.isCompleted = true;
        }
      } else {
        // Failed threshold - trigger Reflexion & Micro-Lesson
        mockDatabase.isReflexion = true;
        mockDatabase.replanCount += 1;
        explanation = `Concept Refresh: You answered ${correctCount}/${activeQuiz.questions.length} correctly. BKT belief update: ${(updatedProb * 100).toFixed(1)}%. Review the key rule: In relational queries, ensure join constraints match indexed keys and specify LEFT/INNER based on whether unmatched rows are needed.`;
      }

      const nextQuiz = mockDatabase.isCompleted 
        ? null 
        : (mockDatabase.isReflexion ? mockDatabase.quizzes.remedial : mockDatabase.quizzes[mockDatabase.currentIndex]);

      return {
        session_id: sessionId,
        user_id: mockDatabase.userId,
        current_index: mockDatabase.currentIndex,
        is_completed: mockDatabase.isCompleted,
        replan_count: mockDatabase.replanCount,
        mastery: { ...mockDatabase.mastery },
        current_path: [...mockDatabase.currentPath],
        last_quiz: nextQuiz,
        last_quiz_score: score,
        is_passed: updatedProb >= 0.6,
        explanation: explanation
      };
    }
  },

  /**
   * Ask why a recommendation was made (or any question about the current path)
   */
  async explainRecommendation(sessionId, question) {
    try {
      const response = await fetch(`${API_BASE}/session/${sessionId}/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      if (!response.ok) throw new Error('Network response not ok');
      return await response.json();
    } catch (err) {
      console.warn('[API Client] Backend not detected, using mock explanation.', err);
      const activeSession = mockDatabase.currentPath[mockDatabase.currentIndex];
      return {
        answer: `Mock mode: "${activeSession ? activeSession.title : 'this session'}" was placed here because its prerequisite skills were assessed as gaps in your intake, and it precedes sessions that build on those skills. Connect the backend for a live, state-grounded explanation.`,
        referenced_session_id: activeSession ? activeSession.id : null
      };
    }
  },

  /**
   * Fetch the explicit learner profile built during intake
   */
  async getLearnerProfile(sessionId) {
    try {
      const response = await fetch(`${API_BASE}/session/${sessionId}/profile`);
      if (!response.ok) throw new Error('Network response not ok');
      return await response.json();
    } catch (err) {
      console.warn('[API Client] Backend not detected, using mock profile.', err);
      return {
        learning_goal: mockDatabase.userGoal,
        learner_information: mockDatabase.userBackground,
        interests: ['SQL', 'Database Performance'],
        experience_level: 'beginner',
        completed_courses: [],
        objectives: ['Write efficient multi-table SQL queries', 'Understand indexing and query plans']
      };
    }
  },

  /**
   * Add a custom resource link to a specific session
   */
  async addResource(sessionId, sessionIndex, resource) {
    try {
      const response = await fetch(`${API_BASE}/session/${sessionId}/session/${sessionIndex}/resource`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(resource)
      });
      if (!response.ok) throw new Error('Network response not ok');
      return await response.json();
    } catch (err) {
      console.warn('[API Client] Backend not detected, using mock resource addition.', err);
      if (mockDatabase.currentPath[sessionIndex]) {
        if (!mockDatabase.currentPath[sessionIndex].recommended_resources) {
          mockDatabase.currentPath[sessionIndex].recommended_resources = [];
        }
        mockDatabase.currentPath[sessionIndex].recommended_resources.push({
          title: resource.title,
          url: resource.url,
          type: resource.type || 'custom',
          reason: resource.reason || 'Added by learner'
        });
      }
      return {
        session_id: sessionId,
        user_id: mockDatabase.userId,
        current_index: mockDatabase.currentIndex,
        is_completed: mockDatabase.isCompleted,
        replan_count: mockDatabase.replanCount,
        skill_gaps: mockDatabase.skillGaps,
        mastery: { ...mockDatabase.mastery },
        current_path: [...mockDatabase.currentPath],
        last_quiz: mockDatabase.quizzes[mockDatabase.currentIndex],
        explanation: null
      };
    }
  },

  /**
   * Fetch current session state
   */
  async getSessionState(sessionId) {
    try {
      const response = await fetch(`${API_BASE}/session/${sessionId}/state`);
      if (!response.ok) throw new Error('Network response not ok');
      return await response.json();
    } catch (err) {
      return {
        session_id: sessionId,
        user_id: mockDatabase.userId,
        current_index: mockDatabase.currentIndex,
        is_completed: mockDatabase.isCompleted,
        replan_count: mockDatabase.replanCount,
        skill_gaps: mockDatabase.skillGaps,
        mastery: { ...mockDatabase.mastery },
        current_path: [...mockDatabase.currentPath],
        last_quiz: mockDatabase.quizzes[mockDatabase.currentIndex],
        explanation: null
      };
    }
  }
};
