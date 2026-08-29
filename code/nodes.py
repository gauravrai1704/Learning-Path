"""
nodes.py

LangGraph nodes for the PathFinder Personalized Learning Path system.

These nodes orchestrate the agents implemented by the rest of the team.
The nodes themselves should remain relatively thin: they take information
from LearningState, call the appropriate agent, and return state updates.
"""

from __future__ import annotations

from typing import Any

from state import LearningState
from llm import get_llm

from skill_gap_identifier import identify_skill_gap_with_llm
from learning_path_scheduler import (
    schedule_learning_path_with_llm,
    reflexion_learning_path_with_llm,
)
from document_quiz_generator import (
    generate_quiz_with_llm,
    score_quiz,
)
from bkt_update import MasteryStore


# ---------------------------------------------------------------------------
# Shared resources
# ---------------------------------------------------------------------------

# The LLM is created lazily.
#
# We DON'T call get_llm() when this file is imported.
# This makes importing the nodes safe during testing and graph construction.
_llm = None

# In-memory mastery tracker for the prototype.
# This can later be replaced with a database-backed store.
mastery_store = MasteryStore()


def get_shared_llm():
    """
    Return the shared OpenAI LLM instance.

    The model is initialized only the first time an LLM node needs it.
    """

    global _llm

    if _llm is None:
        _llm = get_llm()

    return _llm


# ---------------------------------------------------------------------------
# INTAKE NODE
# ---------------------------------------------------------------------------

def intake_node(state: LearningState) -> dict[str, Any]:
    """
    Analyze the learner's goal and background.

    Calls:
        SkillGapIdentifier

    Input state:
        learner_profile

    Output state:
        skill_gaps
    """

    profile = state.get("learner_profile", {})

    learning_goal = profile.get("learning_goal", "")
    learner_information = profile.get("learner_information", "")

    if not learning_goal:
        raise ValueError("learner_profile must contain 'learning_goal'.")

    skill_gaps = identify_skill_gap_with_llm(
        get_shared_llm(),
        learning_goal=learning_goal,
        learner_information=learner_information,
    )

    return {
        "skill_gaps": skill_gaps,
    }


# ---------------------------------------------------------------------------
# PLANNER NODE
# ---------------------------------------------------------------------------

def planner_node(state: LearningState) -> dict[str, Any]:
    """
    Generate the learner's personalized learning path.

    Calls:
        LearningPathScheduler

    Input state:
        learner_profile
        skill_gaps

    Output state:
        current_path
        current_index
    """

    learner_profile = {
        "learner_profile": state.get("learner_profile", {}),
        "skill_gaps": state.get("skill_gaps", {}),
    }

    learning_path_result = schedule_learning_path_with_llm(
        get_shared_llm(),
        learner_profile,
    )

    return {
        "current_path": learning_path_result["learning_path"],
        "current_index": 0,
    }


# ---------------------------------------------------------------------------
# QUIZ GENERATION NODE
# ---------------------------------------------------------------------------

def quiz_gen_node(state: LearningState) -> dict[str, Any]:
    """
    Generate a quiz for the learner's current session.

    Calls:
        DocumentQuizGenerator

    Input state:
        current_path
        current_index

    Output state:
        last_quiz
    """

    path = state.get("current_path", [])
    current_index = state.get("current_index", 0)

    if not path:
        raise ValueError("No learning path exists.")

    if current_index >= len(path):
        raise ValueError(
            "Current session index is outside the learning path."
        )

    session = path[current_index]

    associated_skills = session.get("associated_skills", [])

    if not associated_skills:
        raise ValueError(
            f"Session '{session.get('title', 'Unknown')}' "
            "has no associated skills."
        )

    # For the prototype, the first associated skill is used
    # as the primary skill being assessed.
    skill_name = associated_skills[0]

    skill_id = skill_name.lower().replace(" ", "_")

    quiz = generate_quiz_with_llm(
        get_shared_llm(),
        skill_id=skill_id,
        skill_name=skill_name,
        skill_description=session.get("abstract", ""),
        question_count=3,
    )

    return {
        "last_quiz": quiz,
    }


# ---------------------------------------------------------------------------
# ASSESSOR NODE
# ---------------------------------------------------------------------------

def assessor_node(state: LearningState) -> dict[str, Any]:
    """
    Grade the submitted quiz and update BKT mastery.

    Calls:
        score_quiz()
        MasteryStore.record_quiz_result()

    Input state:
        last_quiz
        submitted_answers
        current_path
        current_index
        mastery

    Output state:
        quiz_result
        mastery
    """

    quiz = state.get("last_quiz")
    submitted_answers = state.get("submitted_answers", [])

    if not quiz:
        raise ValueError("No quiz available for assessment.")

    quiz_result = score_quiz(
        quiz,
        submitted_answers,
    )

    current_index = state.get("current_index", 0)
    current_path = state.get("current_path", [])

    if current_index >= len(current_path):
        raise ValueError(
            "Current session index is outside the learning path."
        )

    current_session = current_path[current_index]

    associated_skills = current_session.get("associated_skills", [])

    mastery = dict(state.get("mastery", {}))

    # Update mastery for every skill associated with the session.
    for skill_name in associated_skills:

        skill_id = skill_name.lower().replace(" ", "_")

        new_mastery = mastery_store.record_quiz_result(
            user_id=state.get("user_id", "default_user"),
            skill_id=skill_id,
            is_correct=quiz_result["is_correct_overall"],
        )

        mastery[skill_id] = new_mastery

    return {
        "quiz_result": quiz_result,
        "mastery": mastery,
    }


# ---------------------------------------------------------------------------
# REFLEXION NODE
# ---------------------------------------------------------------------------

def reflexion_node(state: LearningState) -> dict[str, Any]:
    """
    Adapt the unlearned portion of the learning path after
    the learner struggles with an assessment.

    Calls:
        LearningPathScheduler.reflexion()

    Input state:
        current_path
        current_index
        quiz_result

    Output state:
        current_path
        failed_skill
        feedback
    """

    path = state.get("current_path", [])
    current_index = state.get("current_index", 0)
    quiz_result = state.get("quiz_result", {})

    if not path:
        raise ValueError("No learning path exists.")

    if current_index >= len(path):
        raise ValueError(
            "Current session index is outside the learning path."
        )

    current_session = path[current_index]

    associated_skills = current_session.get("associated_skills", [])

    failed_skill = (
        associated_skills[0]
        if associated_skills
        else "Unknown skill"
    )

    feedback = {
        "failed_skill": failed_skill,
        "quiz_score": quiz_result.get("score", 0),
        "note": (
            "Learner did not demonstrate sufficient mastery "
            "of the current skill."
        ),
    }

    updated_path = reflexion_learning_path_with_llm(
        get_shared_llm(),
        learning_path=path,
        feedback=feedback,
    )

    return {
        "current_path": updated_path["learning_path"],
        "failed_skill": failed_skill,
        "feedback": feedback,
    }


# ---------------------------------------------------------------------------
# ADVANCE NODE
# ---------------------------------------------------------------------------

def advance_node(state: LearningState) -> dict[str, Any]:
    """
    Move the learner to the next session.

    This node does not call an LLM.
    """

    current_index = state.get("current_index", 0)

    return {
        "current_index": current_index + 1,
    }