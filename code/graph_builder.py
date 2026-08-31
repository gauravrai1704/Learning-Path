"""
graph_builder.py

Builds the LangGraph workflow for the PathFinder learning system.

The graph pauses after quiz generation so that the learner can answer
the quiz before the assessment node continues execution.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from state import LearningState

from nodes import (
    intake_node,
    planner_node,
    quiz_gen_node,
    assessor_node,
    reflexion_node,
    advance_node,
)

from router import (
    router_node,
    completion_router,
)


# ---------------------------------------------------------
# QUIZ INPUT NODE
# ---------------------------------------------------------

def wait_for_quiz_answers(state: LearningState) -> dict:
    """
    Pause the LangGraph workflow and wait for the learner to submit
    answers to the generated quiz.

    The frontend will receive the quiz through the interrupt payload.

    Execution resumes when Command(resume=answers) is supplied.
    """

    quiz = state.get("last_quiz")

    if not quiz:
        raise ValueError("No quiz available to present to learner.")

    submitted_answers = interrupt(
        {
            "type": "quiz",
            "quiz": quiz,
            "current_index": state.get("current_index", 0),
        }
    )

    return {
        "submitted_answers": submitted_answers
    }


# ---------------------------------------------------------
# GRAPH BUILDER
# ---------------------------------------------------------

def build_learning_graph():
    """
    Construct and compile the PathFinder LangGraph.

    Workflow:

        START
          |
        Intake
          |
        Planner
          |
        Quiz Generator
          |
        Wait for Answers
          |
        Assessor
          |
        Router
        /    \
    Advance  Reflexion
       |        |
       |        |
       |     Quiz Generator
       |        |
       |     Wait for Answers
       |        |
       |     Assessor
       |        |
       └----> Router
    """

    graph = StateGraph(LearningState)

    # ---------------------------------------------------------
    # Register nodes
    # ---------------------------------------------------------

    graph.add_node("intake", intake_node)
    graph.add_node("planner", planner_node)
    graph.add_node("quiz_gen", quiz_gen_node)
    graph.add_node("wait_for_answers", wait_for_quiz_answers)
    graph.add_node("assessor", assessor_node)
    graph.add_node("reflexion", reflexion_node)
    graph.add_node("advance", advance_node)

    # ---------------------------------------------------------
    # Initial workflow
    # ---------------------------------------------------------

    graph.add_edge(START, "intake")

    graph.add_edge("intake", "planner")

    graph.add_edge("planner", "quiz_gen")

    graph.add_edge("quiz_gen", "wait_for_answers")

    graph.add_edge("wait_for_answers", "assessor")

    # ---------------------------------------------------------
    # Conditional routing after assessment
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "assessor",
        router_node,
        {
            "advance": "advance",
            "reflexion": "reflexion",
            "complete": END,
        },
    )

    # ---------------------------------------------------------
    # Successful learner
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "advance",
        completion_router,
        {
            "continue": "quiz_gen",
            "complete": END,
        },
    )

    # ---------------------------------------------------------
    # Struggling learner
    # ---------------------------------------------------------

    graph.add_edge("reflexion", "quiz_gen")

    # ---------------------------------------------------------
    # Compile with checkpointing
    # ---------------------------------------------------------

    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)


# ---------------------------------------------------------
# Create compiled graph
# ---------------------------------------------------------

learning_graph = build_learning_graph()


# ---------------------------------------------------------
# Standalone test
# ---------------------------------------------------------

if __name__ == "__main__":
    print("PathFinder LangGraph built successfully.")