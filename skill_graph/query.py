"""
query.py

Read-only queries over the skill prerequisite graph.

Exposes:
    get_prerequisites(skill_id) -> list[skill_id]
    get_path(known_skills, goal_skill) -> list[skill_id]
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

import networkx as nx

from build_graph import get_skill_graph, SkillGraphError


class SkillNotFoundError(SkillGraphError):
    """Raised when a requested skill id does not exist in the graph."""


def normalize_skill_id(raw: str) -> str:
    """Match the id convention used elsewhere in the project: lowercase,
    spaces replaced with underscores.
    """
    return raw.strip().lower().replace(" ", "_")


def _require_skill(graph: nx.DiGraph, skill_id: str) -> str:
    normalized = normalize_skill_id(skill_id)
    if normalized not in graph:
        raise SkillNotFoundError(f"Unknown skill id: {skill_id!r}")
    return normalized


def get_prerequisites(skill_id: str) -> List[str]:
    """Direct prerequisites (immediate predecessors) of a skill."""
    graph = get_skill_graph()
    normalized = _require_skill(graph, skill_id)
    return sorted(graph.predecessors(normalized))


def get_all_prerequisites(skill_id: str) -> List[str]:
    """All transitive prerequisites of a skill, in topological order."""
    graph = get_skill_graph()
    normalized = _require_skill(graph, skill_id)
    ancestors = nx.ancestors(graph, normalized)
    subgraph = graph.subgraph(ancestors)
    return list(nx.topological_sort(subgraph))


def get_skill_info(skill_id: str) -> Dict[str, Any]:
    """Metadata (name, description, tags, difficulty) for a skill."""
    graph = get_skill_graph()
    normalized = _require_skill(graph, skill_id)
    return dict(graph.nodes[normalized])


def get_path(known_skills: Iterable[str], goal_skill: str) -> List[str]:
    """Topological candidate order of skills the learner still needs to
    reach `goal_skill`, excluding anything already in `known_skills`.

    This is the pre-BKT candidate order: the Planner/Scheduler layer is
    expected to turn this into sessions and BKT then governs pacing/replans.
    """
    graph = get_skill_graph()
    normalized_goal = _require_skill(graph, goal_skill)

    known_normalized = {normalize_skill_id(s) for s in known_skills}

    required = nx.ancestors(graph, normalized_goal) | {normalized_goal}
    required -= known_normalized

    subgraph = graph.subgraph(required)
    return list(nx.topological_sort(subgraph))


if __name__ == "__main__":
    path = get_path(
        known_skills=["Python Basics", "Git Version Control"],
        goal_skill="Data Engineering Job-Ready",
    )
    print("Candidate path:", path)
    print("Prerequisites of data_warehousing:", get_prerequisites("data_warehousing"))
