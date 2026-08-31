"""
learning_path_scheduler.py

This is the core of our Planner node.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Union

from pydantic import BaseModel, Field, field_validator

from base_agent import BaseAgent


# ---------------------------------------------------------------------------
# Schemas 
# ---------------------------------------------------------------------------

class Proficiency(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class DesiredOutcome(BaseModel):
    name: str = Field(..., description="Skill name")
    level: Proficiency = Field(..., description="Desired proficiency when completed")


class RecommendedResource(BaseModel):
    title: str = Field(..., description="Name of the recommended course, project, or resource")
    type: str = Field(..., description="One of: course, project, article, documentation, video")
    reason: str = Field(..., description="<=20 words on why this resource fits this session")
    url: Optional[str] = Field(default=None, description="Direct URL, documentation link, or tutorial link to the resource")


class SessionItem(BaseModel):
    id: str = Field(..., description="Session identifier, e.g. 'Session 1'")
    title: str
    abstract: str
    if_learned: bool
    associated_skills: List[str] = Field(default_factory=list)
    desired_outcome_when_completed: List[DesiredOutcome] = Field(default_factory=list)
    recommended_resources: List[RecommendedResource] = Field(
        default_factory=list,
        description="1-3 concrete courses/projects/resources that teach this session's skills.",
    )


class LearningPath(BaseModel):
    learning_path: List[SessionItem]

    @field_validator("learning_path")
    @classmethod
    def limit_sessions(cls, v: List[SessionItem]) -> List[SessionItem]:
        if not (1 <= len(v) <= 10):
            raise ValueError("Learning path must contain between 1 and 10 sessions.")
        return v


# ---------------------------------------------------------------------------
# Prompts 
# ---------------------------------------------------------------------------

learning_path_output_format = """
{
    "learning_path": [
        {
            "id": "Session 1",
            "title": "Session Title",
            "abstract": "Brief overview of the session content (max 200 words)",
            "if_learned": false,
            "associated_skills": ["Skill 1", "Skill 2"],
            "desired_outcome_when_completed": [
                {"name": "Skill 1", "level": "intermediate"}
            ],
            "recommended_resources": [
                {"title": "Name of course/project/resource", "type": "course", "reason": "Why it fits, <=20 words", "url": "https://example.com/resource"}
            ]
        }
    ]
}
""".strip()

learning_path_scheduler_system_prompt = f"""
You are the **Learning Path Scheduler** agent in a personalized learning path system.
Your role is to create, refine, or re-schedule a goal-oriented learning path.
You will be given one of three tasks (A, B, or C). Follow the rules for that task exactly.

**Universal Directives (all tasks)**:
1. **Goal-Oriented**: The path must be the most efficient route to close the
   learner's skill gaps and reach their goal.
2. **Progressive**: Sessions must build from foundational to advanced skills.
3. **Quality over Quantity**: Prefer a short, high-quality path (1-10 sessions).
4. **Recommend Resources**: Every session must include 1-3 `recommended_resources`
   (real, well-known course names, project ideas, or documentation/article
   titles that teach that session's skills). For each resource, provide an authentic `url`
   (e.g., official docs like `https://docs.python.org/3/`, reputable learning platforms,
   or GitHub repos) when applicable. Prefer widely-known, genuinely
   existing resources over invented ones; if unsure, recommend a project-based
   resource instead (e.g. "Build a small X to practice Y") rather than a
   fabricated course name.
5. **Strict JSON Output**: Output ONLY the JSON in the format below. No other text.

**Task A: New Path** — create a brand-new path from a learner profile.
All sessions get "if_learned": false.

**Task B: Reflexion (Refine)** — modify an existing path based on feedback about
a specific failure or gap. You MUST NOT change any session marked "if_learned": true.
Insert or adjust *unlearned* sessions to address the feedback — typically this
means inserting a remedial session before the session the learner struggled with.

**Task C: Reschedule** — regenerate the path for a changed learner profile
(e.g. goal changed). Preserve all "if_learned": true sessions exactly, placed
first, then generate new sessions for the remaining gap.

**Output Format**:
{learning_path_output_format}
""".strip()

learning_path_scheduler_task_prompt_session = """
**Task A: New Path**

Create a new, structured learning path based on the learner's profile and skill gaps.
Number of sessions should be within [1, 10].

**Learner Profile / Skill Gaps**: {learner_profile}
"""

learning_path_scheduler_task_prompt_reflexion = """
**Task B: Reflexion (Refine)**

The learner just failed an assessment on one session. Refine the unlearned
portion of the path to address this — typically insert a remedial session
directly before the failed one.

**Original Learning Path**: {learning_path}
**Feedback (what went wrong)**: {feedback}
"""

learning_path_scheduler_task_prompt_reschedule = """
**Task C: Reschedule**

Regenerate the path for the learner's updated profile/goal, preserving all
sessions marked if_learned=true exactly as-is, placed first.

**Original Learning Path**: {learning_path}
**Updated Learner Profile**: {learner_profile}
"""


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class LearningPathScheduler(BaseAgent):
    """Agent orchestrating learning path scheduling: initial creation,
    targeted refinement (reflexion), and full reschedule.
    """

    name: str = "LearningPathScheduler"

    def __init__(self, model: Any) -> None:
        super().__init__(model=model, system_prompt=learning_path_scheduler_system_prompt, jsonalize_output=True)

    def schedule_session(self, learner_profile: Union[str, Dict[str, Any]]) -> dict:
        """Task A: generate a brand-new path. Called once from the Planner
        node on first run (after Intake produces skill gaps).
        """
        raw_output = self.invoke(
            {"learner_profile": learner_profile},
            task_prompt=learning_path_scheduler_task_prompt_session,
        )
        return LearningPath.model_validate(raw_output).model_dump()

    def reflexion(self, learning_path: Sequence[Any], feedback: Union[str, Dict[str, Any]]) -> dict:
        """Task B: light-touch fix to the existing path. Call this from the
        Router node when a single quiz result drops mastery below threshold.

        `feedback` should describe what went wrong, e.g.:
            {"failed_skill": "SQL Joins", "quiz_score": 0.33,
             "note": "Learner missed questions on multi-table joins"}
        """
        raw_output = self.invoke(
            {"learning_path": learning_path, "feedback": feedback},
            task_prompt=learning_path_scheduler_task_prompt_reflexion,
        )
        return LearningPath.model_validate(raw_output).model_dump()

    def reschedule(self, learning_path: Sequence[Any], learner_profile: Union[str, Dict[str, Any]]) -> dict:
        """Task C: full replan. Call this when the learner's goal changes,
        not for routine quiz-driven adjustments (use reflexion for that).
        """
        raw_output = self.invoke(
            {"learning_path": learning_path, "learner_profile": learner_profile},
            task_prompt=learning_path_scheduler_task_prompt_reschedule,
        )
        return LearningPath.model_validate(raw_output).model_dump()


# ---------------------------------------------------------------------------
# Convenience functions (for quick calls from LangGraph nodes)
# ---------------------------------------------------------------------------

def schedule_learning_path_with_llm(llm: Any, learner_profile: Dict[str, Any]) -> dict:
    return LearningPathScheduler(llm).schedule_session(learner_profile)


def reflexion_learning_path_with_llm(llm: Any, learning_path: Sequence[Any], feedback: Dict[str, Any]) -> dict:
    return LearningPathScheduler(llm).reflexion(learning_path, feedback)


def reschedule_learning_path_with_llm(llm: Any, learning_path: Sequence[Any], learner_profile: Dict[str, Any]) -> dict:
    return LearningPathScheduler(llm).reschedule(learning_path, learner_profile)
