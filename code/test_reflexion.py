from nodes import (
    intake_node,
    planner_node,
    quiz_gen_node,
    assessor_node,
    reflexion_node,
)

from router import router_node


def main():

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
    # Intake
    # ---------------------------------------------------------

    state.update(intake_node(state))

    # ---------------------------------------------------------
    # Planner
    # ---------------------------------------------------------

    state.update(planner_node(state))

    print("\nORIGINAL PATH")

    for session in state["current_path"]:
        print(
            session["id"],
            "->",
            session["title"]
        )

    # ---------------------------------------------------------
    # Generate quiz
    # ---------------------------------------------------------

    state.update(quiz_gen_node(state))

    quiz = state["last_quiz"]

    # ---------------------------------------------------------
    # Intentionally answer everything incorrectly
    # ---------------------------------------------------------

    state["submitted_answers"] = [
        (question["correct_option_index"] + 1)
        % len(question["options"])
        for question in quiz["questions"]
    ]

    print("\nSubmitted incorrect answers:")
    print(state["submitted_answers"])

    # ---------------------------------------------------------
    # Assessment
    # ---------------------------------------------------------

    state.update(assessor_node(state))

    print("\nQUIZ RESULT")
    print(state["quiz_result"])

    print("\nMASTERY")

    for skill, mastery in state["mastery"].items():
        print(
            f"{skill}: {mastery:.3f}"
        )

    # ---------------------------------------------------------
    # Router
    # ---------------------------------------------------------

    decision = router_node(state)

    print("\nROUTER DECISION:")
    print(decision)

    # ---------------------------------------------------------
    # Reflexion
    # ---------------------------------------------------------

    if decision == "reflexion":

        state.update(
            reflexion_node(state)
        )

        print("\nREFLEXION PATH")

        for session in state["current_path"]:
            print(
                session["id"],
                "->",
                session["title"]
            )

    else:
        print("\nReflexion was not triggered.")


if __name__ == "__main__":
    main()