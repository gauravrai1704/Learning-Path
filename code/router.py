"""
router.py

Decision logic for the PathFinder LangGraph.
"""

from typing import Literal

from state import LearningState


MASTERY_THRESHOLD = 0.6


def router_node(
    state: LearningState,
) -> Literal["advance", "reflexion", "complete"]:
    """
    Decide what happens after a quiz assessment.

    Returns:

        "advance"
            Learner has sufficient mastery.

        "reflexion"
            Learner needs additional learning.

        "complete"
            Learner has completed the entire learning path.
    """

    current_index = state.get("current_index", 0)
    current_path = state.get("current_path", [])

    # ---------------------------------------------------------
    # Check whether the current session is the final session.
    #
    # We only know whether the learner has completed the path
    # AFTER assessing the final session.
    # ---------------------------------------------------------

    if current_index >= len(current_path):
        return "complete"

    current_session = current_path[current_index]

    associated_skills = current_session.get(
        "associated_skills",
        [],
    )

    if not associated_skills:
        return "advance"

    mastery = state.get("mastery", {})

    # For the prototype, use the first associated skill
    # as the primary skill being assessed.
    skill_name = associated_skills[0]

    skill_id = skill_name.lower().replace(" ", "_")

    current_mastery = mastery.get(
        skill_id,
        0.0,
    )

    if current_mastery >= MASTERY_THRESHOLD:
        return "advance"

    return "reflexion"


def completion_router(
    state: LearningState,
) -> Literal["continue", "complete"]:
    """
    Determine whether there are more sessions remaining.

    This is called after advance_node increments current_index.
    """

    current_index = state.get("current_index", 0)
    current_path = state.get("current_path", [])

    if current_index >= len(current_path):
        return "complete"

    return "continue"