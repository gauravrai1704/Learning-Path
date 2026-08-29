from nodes import (
    intake_node,
    planner_node,
    quiz_gen_node,
    assessor_node,
)

from router import router_node


def main():

    # ---------------------------------------------------------
    # Initial learner state
    # ---------------------------------------------------------

    state = {
        "user_id": "demo_user",

        "learner_profile": {
            "learning_goal": "Become job-ready in data engineering",
            "learner_information": (
                "I know Python and basic SQL. "
                "I have no cloud experience."
            ),
        },

        "mastery": {},
    }

    # ---------------------------------------------------------
    # INTAKE
    # ---------------------------------------------------------

    print("\n==============================")
    print("INTAKE")
    print("==============================")

    state.update(
        intake_node(state)
    )

    print(
        f"Identified "
        f"{len(state['skill_gaps']['skill_gaps'])} skill gaps."
    )

    # ---------------------------------------------------------
    # PLANNER
    # ---------------------------------------------------------

    print("\n==============================")
    print("PLANNER")
    print("==============================")

    state.update(
        planner_node(state)
    )

    for session in state["current_path"]:
        print(
            f"{session['id']}: "
            f"{session['title']}"
        )

    # ---------------------------------------------------------
    # QUIZ
    # ---------------------------------------------------------

    print("\n==============================")
    print("QUIZ")
    print("==============================")

    state.update(
        quiz_gen_node(state)
    )

    quiz = state["last_quiz"]

    print(
        f"Generated {len(quiz['questions'])} questions "
        f"for {quiz['skill_id']}."
    )

    # ---------------------------------------------------------
    # SIMULATE LEARNER ANSWERS
    # ---------------------------------------------------------

    # For testing, intentionally answer everything correctly.
    submitted_answers = [
        question["correct_option_index"]
        for question in quiz["questions"]
    ]

    state["submitted_answers"] = submitted_answers

    print("\nSubmitted answers:")
    print(submitted_answers)

    # ---------------------------------------------------------
    # ASSESSOR + BKT
    # ---------------------------------------------------------

    print("\n==============================")
    print("ASSESSOR + BKT")
    print("==============================")

    state.update(
        assessor_node(state)
    )

    print(
        "Quiz score:",
        state["quiz_result"]["score"]
    )

    print(
        "Overall correct:",
        state["quiz_result"]["is_correct_overall"]
    )

    print("\nMastery:")

    for skill, mastery in state["mastery"].items():
        print(
            f"  {skill}: {mastery:.3f}"
        )

    # ---------------------------------------------------------
    # ROUTER
    # ---------------------------------------------------------

    print("\n==============================")
    print("ROUTER")
    print("==============================")

    decision = router_node(state)

    print("Router decision:", decision)


if __name__ == "__main__":
    main()