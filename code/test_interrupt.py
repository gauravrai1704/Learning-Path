from graph_runner import start_learning, submit_quiz


profile = {
    "learning_goal": "Become job-ready in data engineering",
    "learner_information": (
        "I know basic Python and SQL. "
        "I have no cloud or data engineering experience."
    ),
}


print("\n==============================")
print("START LEARNING")
print("==============================")

session = start_learning(
    user_id="demo_user",
    learner_profile=profile,
)

print("\nThread ID:")
print(session["thread_id"])

print("\nQuiz:")
quiz = session["quiz"]

for i, question in enumerate(quiz["questions"], 1):
    print(f"\nQ{i}: {question['question']}")

    for j, option in enumerate(question["options"]):
        print(f"  {j}. {option}")


print("\n==============================")
print("SUBMIT ANSWERS")
print("==============================")

# Deliberately submit wrong answers for testing.
answers = [0, 0, 0]

result = submit_quiz(
    thread_id=session["thread_id"],
    submitted_answers=answers,
)

print("\nQuiz Result:")
print(result["quiz_result"])

print("\nMastery:")
print(result["mastery"])

print("\nCurrent Index:")
print(result["current_index"])

print("\nFailed Skill:")
print(result["failed_skill"])

print("\nUpdated Path:")

for i, session_item in enumerate(result["current_path"], 1):
    print(
        f"Session {i}: "
        f"{session_item.get('title')}"
    )