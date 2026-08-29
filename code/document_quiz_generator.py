"""
document_quiz_generator.py


Used by the Quiz Gen node: given the current skill in the path, generate a
short quiz whose score becomes the `is_correct` input to the Assessor node.
"""

from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field, field_validator

from base_agent import BaseAgent


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class SingleChoiceQuestion(BaseModel):
    question: str
    options: List[str]
    correct_option_index: int = Field(..., description="0-indexed position of the correct option")
    explanation: str

    @field_validator("options")
    @classmethod
    def between_two_and_five_options(cls, v: List[str]) -> List[str]:
        if not (2 <= len(v) <= 5):
            raise ValueError("Each question must have between 2 and 5 options.")
        return v


class SkillQuiz(BaseModel):
    skill_id: str
    questions: List[SingleChoiceQuestion]

    @field_validator("questions")
    @classmethod
    def limit_question_count(cls, v: List[SingleChoiceQuestion]) -> List[SingleChoiceQuestion]:
        if not (1 <= len(v) <= 5):
            raise ValueError("Quiz must have between 1 and 5 questions.")
        return v


# ---------------------------------------------------------------------------
# Prompts (adapted from GenMentor's document_quiz_generator prompts)
# ---------------------------------------------------------------------------

quiz_output_format = """
{
    "skill_id": "the_skill_id_passed_in",
    "questions": [
        {
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_option_index": 2,
            "explanation": "One sentence on why this option is correct."
        }
    ]
}
""".strip()

document_quiz_generator_system_prompt = f"""
You are the **Quiz Generator** agent in a personalized learning path system.
Given a skill name and a short description of what it covers, generate a
short single-choice quiz that tests whether a learner has grasped that
specific skill — not adjacent skills.

**Directives**:
1. Generate between 2 and 3 questions unless told otherwise.
2. Questions should test understanding, not just recall of a definition.
3. Include plausible distractors (wrong options that reflect common
   misconceptions), not obviously-wrong filler options.
4. Keep each question self-contained — a learner should be able to answer it
   using only general knowledge of the named skill, without needing the exact
   wording of a source document.
5. Provide a one-sentence `explanation` for the correct answer.

**Output Format**:
Output ONLY valid JSON matching this exact structure. No other text.
{quiz_output_format}
""".strip()

document_quiz_generator_task_prompt = """
Generate a quiz for this skill.

**Skill ID**: {skill_id}
**Skill Name**: {skill_name}
**Skill Description**: {skill_description}
**Number of Questions**: {question_count}
"""


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class DocumentQuizGenerator(BaseAgent):
    name: str = "DocumentQuizGenerator"

    def __init__(self, model: Any) -> None:
        super().__init__(model=model, system_prompt=document_quiz_generator_system_prompt, jsonalize_output=True)

    def generate(self, skill_id: str, skill_name: str, skill_description: str, question_count: int = 3) -> dict:
        raw_output = self.invoke(
            {
                "skill_id": skill_id,
                "skill_name": skill_name,
                "skill_description": skill_description,
                "question_count": question_count,
            },
            task_prompt=document_quiz_generator_task_prompt,
        )
        return SkillQuiz.model_validate(raw_output).model_dump()


def generate_quiz_with_llm(llm: Any, skill_id: str, skill_name: str, skill_description: str, question_count: int = 3) -> dict:
    """Convenience function for the Quiz Gen node.

    Example:
        quiz = generate_quiz_with_llm(
            llm, skill_id="sql_joins", skill_name="SQL Joins",
            skill_description="Combining rows from two or more tables using JOIN clauses.",
        )
    """
    return DocumentQuizGenerator(llm).generate(skill_id, skill_name, skill_description, question_count)


def score_quiz(quiz: dict, submitted_answers: List[int]) -> dict:
    """Grades a submitted quiz against the generated answer key.

    `submitted_answers` is a list of 0-indexed option choices, one per
    question, in the same order as `quiz["questions"]`.

    Returns: {"score": float in [0,1], "is_correct_overall": bool, "per_question": [...]}
    `is_correct_overall` uses a >=0.5 threshold — feed this directly into
    bkt_update.py's `is_correct` argument.
    """
    questions = quiz["questions"]
    if len(submitted_answers) != len(questions):
        raise ValueError("submitted_answers length must match number of questions")

    per_question = []
    correct_count = 0
    for q, submitted in zip(questions, submitted_answers):
        is_correct = submitted == q["correct_option_index"]
        correct_count += int(is_correct)
        per_question.append({"is_correct": is_correct, "explanation": q["explanation"]})

    score = correct_count / len(questions)
    return {"score": score, "is_correct_overall": score >= 0.5, "per_question": per_question}
