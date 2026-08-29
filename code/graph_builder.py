"""
graph_builder.py

Builds the LangGraph workflow for the PathFinder learning system.
"""

from langgraph.graph import StateGraph, START, END

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
        Assessor
          |
        Router
        /    \
    Advance  Reflexion
       |        |
       |        |
       |     Quiz Generator
       |        |
       |     Assessor
       |        |
       └----> Router

    The loop continues until the learner demonstrates sufficient
    mastery and advances through the learning path.
    """

    graph = StateGraph(LearningState)

    # ---------------------------------------------------------
    # Register nodes
    # ---------------------------------------------------------

    graph.add_node("intake", intake_node)
    graph.add_node("planner", planner_node)
    graph.add_node("quiz_gen", quiz_gen_node)
    graph.add_node("assessor", assessor_node)
    graph.add_node("reflexion", reflexion_node)
    graph.add_node("advance", advance_node)

    # ---------------------------------------------------------
    # Initial workflow
    # ---------------------------------------------------------

    graph.add_edge(START, "intake")

    graph.add_edge("intake", "planner")

    graph.add_edge("planner", "quiz_gen")

    graph.add_edge("quiz_gen", "assessor")

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
# Compile the graph
# ---------------------------------------------------------

    return graph.compile()


# ---------------------------------------------------------
# Create the compiled graph
# ---------------------------------------------------------

learning_graph = build_learning_graph()


# ---------------------------------------------------------
# Quick standalone test
# ---------------------------------------------------------

if __name__ == "__main__":
    print("PathFinder LangGraph built successfully.")