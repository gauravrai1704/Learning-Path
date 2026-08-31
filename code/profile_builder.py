"""
profile_builder.py

Builds an explicit LearnerProfile (interests, experience_level,
completed_courses, objectives) from the learner's free-text goal and
background. This runs alongside SkillGapIdentifier inside the Intake node
so that `learner_profile` in LearningState carries structured fields instead
of just the raw goal/background strings.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, List

from pydantic import BaseModel, Field

from base_agent import BaseAgent


class ExperienceLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class LearnerProfileFields(BaseModel):
    interests: List[str] = Field(
        default_factory=list,
        description="Topics/domains the learner is interested in, inferred from goal + background.",
    )
    experience_level: ExperienceLevel = Field(
        ...,
        description="Overall self-reported/inferred experience level.",
    )
    completed_courses: List[str] = Field(
        default_factory=list,
        description="Courses, certifications, or prior learning explicitly mentioned by the learner.",
    )
    objectives: List[str] = Field(
        default_factory=list,
        description="Concrete, short objective statements derived from the learner's stated goal.",
    )


profile_builder_output_format = """
{
    "interests": ["Topic A", "Topic B"],
    "experience_level": "beginner",
    "completed_courses": ["Course/Certification mentioned by learner"],
    "objectives": ["Short, concrete objective 1", "Short, concrete objective 2"]
}
""".strip()

profile_builder_system_prompt = f"""
You are the **Learner Profile Builder** agent in a personalized learning
path system. Given a learner's free-text goal and background, extract a
structured profile.

Rules:
- `interests`: 1-6 short topic/domain names.
- `experience_level`: your best single overall estimate (beginner/intermediate/advanced).
- `completed_courses`: ONLY courses/certifications/degrees the learner explicitly
  mentioned. If none mentioned, return an empty list. Do not invent any.
- `objectives`: 1-5 short, concrete statements of what the learner wants to
  be able to do, derived from their goal.
- Output ONLY the JSON in the format below. No other text.

**Output Format**:
{profile_builder_output_format}
""".strip()

profile_builder_task_prompt = """
**Learner Goal**: {learning_goal}
**Learner Background**: {learner_information}
"""


class LearnerProfileBuilder(BaseAgent):
    """Agent wrapper: goal + background -> structured learner profile fields."""

    name: str = "LearnerProfileBuilder"

    def __init__(self, model: Any) -> None:
        super().__init__(model=model, system_prompt=profile_builder_system_prompt, jsonalize_output=True)

    def build_profile(self, learning_goal: str, learner_information: str) -> dict:
        raw_output = self.invoke(
            {"learning_goal": learning_goal, "learner_information": learner_information},
            task_prompt=profile_builder_task_prompt,
        )
        validated = LearnerProfileFields.model_validate(raw_output)
        return validated.model_dump()


def build_learner_profile_with_llm(llm: Any, learning_goal: str, learner_information: str) -> dict:
    """Convenience function for use inside the LangGraph Intake node.

    Example:
        fields = build_learner_profile_with_llm(
            llm,
            learning_goal="I want to become job-ready in data engineering",
            learner_information="I know Python and basic SQL, finished the CS50 course.",
        )
        # fields -> {interests, experience_level, completed_courses, objectives}
    """
    builder = LearnerProfileBuilder(llm)
    return builder.build_profile(learning_goal, learner_information)
