"""
explainer_agent.py

The "why" layer referenced in base_agent.py's module docstring. Answers a
learner's free-text question about the path/recommendations using the
CURRENT LangGraph session state as grounding context — it does not invent
reasoning, it explains decisions that already exist in state (skill_gaps,
current_path, mastery, feedback/failed_skill from the last reflexion).

Kept deliberately outside the LangGraph itself: it's a stateless, read-only
Q&A call over already-computed state, invoked directly from a FastAPI route,
so it never needs to touch the checkpointer or advance the session.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from base_agent import BaseAgent


class Explanation(BaseModel):
    answer: str = Field(..., description="Direct answer to the learner's question, grounded in the provided state.")
    referenced_session_id: Optional[str] = Field(
        None, description="Session id this explanation is primarily about, if applicable."
    )


explainer_output_format = """
{
    "answer": "Direct, concrete explanation grounded in the provided state.",
    "referenced_session_id": "Session 2"
}
""".strip()

explainer_system_prompt = f"""
You are the **Explainer** agent in a personalized learning path system.
Your job is to answer a learner's question about WHY the system recommended
something, using ONLY the state provided to you (skill gaps, the current
learning path with prerequisites, mastery/BKT scores, and any feedback from
a previous reflexion/replan).

Rules:
1. Ground every claim in the provided state — do not invent skills, scores,
   or sessions that are not present in it.
2. If the question references a specific session, cite its id and title.
3. If mastery data or a failed_skill/feedback explains the decision, mention
   the concrete number or reason (e.g. "mastery on X was 0.42, below the
   0.6 threshold, so a remedial session was inserted").
4. Keep the answer to 2-4 sentences. Plain language, no jargon dump.
5. Output ONLY the JSON in the format below. No other text.

**Output Format**:
{explainer_output_format}
""".strip()

explainer_task_prompt = """
**Learner Question**: {question}

**Current Session State**:
- Skill gaps: {skill_gaps}
- Current learning path (with prerequisites/order): {current_path}
- Mastery (BKT posteriors per skill): {mastery}
- Most recent reflexion feedback (if any): {feedback}
- Failed skill that triggered last replan (if any): {failed_skill}
"""


class Explainer(BaseAgent):
    """Agent wrapper: learner question + session state -> grounded explanation."""

    name: str = "Explainer"

    def __init__(self, model: Any) -> None:
        super().__init__(model=model, system_prompt=explainer_system_prompt, jsonalize_output=True)

    def explain(self, question: str, session_state: Dict[str, Any]) -> dict:
        raw_output = self.invoke(
            {
                "question": question,
                "skill_gaps": session_state.get("skill_gaps", {}),
                "current_path": session_state.get("current_path", []),
                "mastery": session_state.get("mastery", {}),
                "feedback": session_state.get("feedback", {}),
                "failed_skill": session_state.get("failed_skill", ""),
            },
            task_prompt=explainer_task_prompt,
        )
        validated = Explanation.model_validate(raw_output)
        return validated.model_dump()


def explain_with_llm(llm: Any, question: str, session_state: Dict[str, Any]) -> dict:
    """Convenience function for use directly inside the FastAPI /explain route.

    Example:
        result = explain_with_llm(
            llm,
            question="Why do I need to learn indexing before query plans?",
            session_state=graph.get_state(config).values,
        )
        # result -> {"answer": "...", "referenced_session_id": "Session 2"}
    """
    return Explainer(llm).explain(question, session_state)
