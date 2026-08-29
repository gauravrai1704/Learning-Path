"""
base_agent.py



Purpose: every LLM-calling node (Intake, Planner, Quiz Gen, Explainer) should
instantiate a BaseAgent instead of writing raw LangChain calls, so prompt
formatting and JSON-parsing/repair logic is written once.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage


def _extract_json(text: str) -> Dict[str, Any]:
    """Best-effort extraction of a JSON object from an LLM's raw text output.

    Handles the common failure modes: markdown code fences, leading/trailing
    prose, or minor trailing commas. Raises ValueError if nothing parseable
    is found, so callers can decide whether to retry.
    """
    text = text.strip()

    # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    # If there's leading/trailing prose around the JSON object, grab the
    # outermost {...} span.
    if not text.startswith("{"):
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # One common repair: trailing commas before a closing brace/bracket
        repaired = re.sub(r",\s*([}\]])", r"\1", text)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            raise ValueError(f"Could not parse JSON from model output: {e}\nRaw text: {text[:500]}")


class BaseAgent:
    """Thin wrapper around a LangChain chat model: system prompt in, validated
    JSON dict out. Subclasses (SkillGapIdentifier, LearningPathScheduler, etc.)
    layer pydantic validation and task-specific prompts on top of this.
    """

    name: str = "BaseAgent"

    def __init__(
        self,
        model: BaseChatModel,
        system_prompt: Optional[str] = None,
        jsonalize_output: bool = True,
    ) -> None:
        self._model = model
        self._system_prompt = system_prompt
        self.jsonalize_output = jsonalize_output

    def set_prompts(self, system_prompt: Optional[str] = None) -> None:
        """Update the system prompt (e.g. if you want to swap tone/domain mid-run)."""
        if system_prompt is not None:
            self._system_prompt = system_prompt

    def _build_messages(self, variables: Dict[str, Any], task_prompt: str) -> list:
        formatted_task = task_prompt.format(**variables)
        messages = []
        if self._system_prompt:
            messages.append(SystemMessage(content=self._system_prompt))
        messages.append(HumanMessage(content=formatted_task))
        return messages

    def invoke(self, input_dict: Dict[str, Any], task_prompt: str) -> Any:
        """Format the task prompt with input_dict, call the model, and return
        either the raw text (jsonalize_output=False) or a parsed dict.
        """
        messages = self._build_messages(input_dict, task_prompt)
        response = self._model.invoke(messages)
        raw_text = response.content if hasattr(response, "content") else str(response)

        if not self.jsonalize_output:
            return raw_text

        return _extract_json(raw_text)
