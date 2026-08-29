from typing import Any, TypedDict


class LearningState(TypedDict, total=False):
    """
    Shared state passed between all nodes in the PathFinder LangGraph.

    Each node reads the information it needs from the state,
    performs its task, and returns the updated state.
    """

    # -----------------------------
    # Session / learner information
    # -----------------------------

    user_id: str

    learner_profile: dict[str, Any]

    # -----------------------------
    # Skill-gap analysis
    # -----------------------------

    skill_gaps: dict[str, Any]

    # -----------------------------
    # Learning path
    # -----------------------------

    current_path: list[dict[str, Any]]

    # Index of the session currently being learned
    current_index: int

    # -----------------------------
    # Quiz
    # -----------------------------

    last_quiz: dict[str, Any]

    # Answers submitted by learner
    submitted_answers: list[int]

    # Result after grading the quiz
    quiz_result: dict[str, Any]

    # -----------------------------
    # Learner mastery
    # -----------------------------

    # Example:
    # {
    #     "sql_joins": 0.73,
    #     "python": 0.91
    # }
    mastery: dict[str, float]

    # -----------------------------
    # Explanation / adaptation
    # -----------------------------

    explanations: list[str]

    # Skill responsible for the latest failure
    failed_skill: str

    # Information passed to the reflexion/replanning agent
    feedback: dict[str, Any]