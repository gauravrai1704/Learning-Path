"""
graph_runner.py

Interface between the PathFinder application and the LangGraph workflow.

The application uses:
    start_learning()  -> starts a learning session and returns the quiz
    submit_quiz()     -> submits learner answers and resumes the graph
"""

from typing import Any

from langgraph.types import Command

from graph_builder import learning_graph


def start_learning(
    user_id: str,
    learner_profile: dict[str, Any],
) -> dict[str, Any]:
    """
    Start a new learning session.

    The graph runs until Quiz Generator produces a quiz and
    wait_for_quiz_answers interrupts execution.

    Returns the generated quiz and a thread_id that must be
    supplied when submitting the answers.
    """

    thread_id = f"pathfinder-{user_id}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "user_id": user_id,
        "learner_profile": learner_profile,
        "current_index": 0,
        "mastery": {},
        "explanations": [],
    }

    result = learning_graph.invoke(
        initial_state,
        config=config,
    )

    return {
        "thread_id": thread_id,
        "quiz": result.get("last_quiz"),
        "current_index": result.get("current_index", 0),
        "state": result,
    }


def submit_quiz(
    thread_id: str,
    submitted_answers: list[int],
) -> dict[str, Any]:
    """
    Resume a paused learning session with the learner's answers.

    The graph continues from the interrupt, runs the Assessor,
    updates BKT mastery, and routes the learner to:

        advance
        reflexion
        complete
    """

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = learning_graph.invoke(
        Command(resume=submitted_answers),
        config=config,
    )

    return {
        "thread_id": thread_id,
        "quiz": result.get("last_quiz"),
        "quiz_result": result.get("quiz_result"),
        "mastery": result.get("mastery", {}),
        "current_index": result.get("current_index", 0),
        "current_path": result.get("current_path", []),
        "failed_skill": result.get("failed_skill"),
        "feedback": result.get("feedback"),
        "state": result,
    }


if __name__ == "__main__":
    print("Graph runner loaded successfully.")