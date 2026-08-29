"""
skill_gap_identifier.py


This is used inside the Intake node: takes the learner's free-text goal plus
whatever background info they gave, returns a structured list of skill gaps
that the Planner node will turn into a path.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, List

from pydantic import BaseModel, Field, field_validator

from base_agent import BaseAgent
from skill_gap_prompts import skill_gap_identifier_system_prompt, skill_gap_identifier_task_prompt


class LevelRequired(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class LevelCurrent(str, Enum):
    unlearned = "unlearned"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class SkillGap(BaseModel):
    name: str
    is_gap: bool
    required_level: LevelRequired
    current_level: LevelCurrent
    reason: str = Field(..., description="<=20 words rationale for current level.")
    level_confidence: Confidence

    @field_validator("reason")
    @classmethod
    def limit_reason_words(cls, v: str) -> str:
        if len(v.split()) > 20:
            raise ValueError("Reason must be 20 words or fewer.")
        return v


class SkillGaps(BaseModel):
    skill_gaps: List[SkillGap]

    @field_validator("skill_gaps")
    @classmethod
    def limit_length_and_names(cls, v: List[SkillGap]):
        if not (1 <= len(v) <= 8):
            raise ValueError("Number of skill gaps must be within 1 to 8.")
        seen = set()
        for item in v:
            key = item.name.strip().lower()
            if key in seen:
                raise ValueError(f'Duplicate skill name detected: "{item.name}".')
            seen.add(key)
        return v


class SkillGapIdentifier(BaseAgent):
    """Agent wrapper: learner goal + background -> structured skill gaps."""

    name: str = "SkillGapIdentifier"

    def __init__(self, model: Any) -> None:
        super().__init__(model=model, system_prompt=skill_gap_identifier_system_prompt, jsonalize_output=True)

    def identify_skill_gap(self, learning_goal: str, learner_information: str) -> dict:
        raw_output = self.invoke(
            {"learning_goal": learning_goal, "learner_information": learner_information},
            task_prompt=skill_gap_identifier_task_prompt,
        )
        validated = SkillGaps.model_validate(raw_output)
        return validated.model_dump()


def identify_skill_gap_with_llm(llm: Any, learning_goal: str, learner_information: str) -> dict:
    """Convenience function for use inside the LangGraph Intake node.

    Example:
        result = identify_skill_gap_with_llm(
            llm,
            learning_goal="I want to become job-ready in data engineering",
            learner_information="I know Python and basic SQL, no cloud experience.",
        )
        # result["skill_gaps"] -> list of {name, is_gap, required_level, current_level, reason, level_confidence}
    """
    identifier = SkillGapIdentifier(llm)
    return identifier.identify_skill_gap(learning_goal, learner_information)


if __name__ == "__main__":
    # Quick manual test — replace with your actual LLM client.
    # from langchain_anthropic import ChatAnthropic
    # llm = ChatAnthropic(model="claude-sonnet-4-6")
    #
    # result = identify_skill_gap_with_llm(
    #     llm,
    #     learning_goal="Become job-ready in data engineering",
    #     learner_information="I have a stats background, know Python, no SQL or cloud experience.",
    # )
    # print(result)
    pass
