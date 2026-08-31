from nodes import (
    intake_node,
    planner_node,
    quiz_gen_node,
)


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
    }

    print("\n==============================")
    print("1. INTAKE")
    print("==============================")

    result = intake_node(state)

    state.update(result)

    print("Skill gaps:")
    print(state["skill_gaps"])

    print("\n==============================")
    print("2. PLANNER")
    print("==============================")

    result = planner_node(state)

    state.update(result)

    print("Learning path:")

    for session in state["current_path"]:
        print(
            f"{session['id']}: "
            f"{session['title']}"
        )

    print("\n==============================")
    print("3. QUIZ GENERATOR")
    print("==============================")

    result = quiz_gen_node(state)

    state.update(result)

    quiz = state["last_quiz"]

    print(f"Skill: {quiz['skill_id']}")
    print(f"Questions: {len(quiz['questions'])}")

    for i, question in enumerate(quiz["questions"], start=1):

        print(f"\nQ{i}: {question['question']}")

        for j, option in enumerate(question["options"]):
            print(f"  {j}. {option}")

    print("\n==============================")
    print("PIPELINE SUCCESS")
    print("==============================")


if __name__ == "__main__":
    main()