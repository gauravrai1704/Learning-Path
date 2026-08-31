"""
build_graph.py

Loads the curriculum from nodes.json/edges.json and builds a validated
NetworkX DAG of skills and their prerequisite relationships.

Exposes:
    load_nodes() -> dict[str, dict]
    load_edges() -> list[tuple[str, str]]
    build_skill_graph() -> nx.DiGraph
    get_skill_graph() -> nx.DiGraph   (cached singleton)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import networkx as nx

DATA_DIR = Path(__file__).resolve().parent
NODES_PATH = DATA_DIR / "nodes.json"
EDGES_PATH = DATA_DIR / "edges.json"


class SkillGraphError(Exception):
    """Raised when the curriculum data fails validation."""


def load_nodes(path: Path = NODES_PATH) -> Dict[str, Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        raw_nodes = json.load(f)

    nodes: Dict[str, Dict[str, Any]] = {}
    for node in raw_nodes:
        skill_id = node.get("id")
        if not skill_id:
            raise SkillGraphError(f"Node missing 'id': {node}")
        if skill_id in nodes:
            raise SkillGraphError(f"Duplicate skill id: {skill_id}")
        nodes[skill_id] = node

    return nodes


def load_edges(path: Path = EDGES_PATH) -> List[Tuple[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        raw_edges = json.load(f)

    edges: List[Tuple[str, str]] = []
    for edge in raw_edges:
        source = edge.get("source")
        target = edge.get("target")
        if not source or not target:
            raise SkillGraphError(f"Edge missing 'source'/'target': {edge}")
        edges.append((source, target))

    return edges


def build_skill_graph(
    nodes_path: Path = NODES_PATH,
    edges_path: Path = EDGES_PATH,
) -> nx.DiGraph:
    """Build and validate the prerequisite DAG from disk.

    Raises SkillGraphError if an edge references an unknown skill id, or if
    the resulting graph is not acyclic.
    """
    nodes = load_nodes(nodes_path)
    edges = load_edges(edges_path)

    graph = nx.DiGraph()

    for skill_id, metadata in nodes.items():
        graph.add_node(skill_id, **metadata)

    for source, target in edges:
        if source not in nodes:
            raise SkillGraphError(f"Edge references unknown source skill: {source}")
        if target not in nodes:
            raise SkillGraphError(f"Edge references unknown target skill: {target}")
        graph.add_edge(source, target)

    if not nx.is_directed_acyclic_graph(graph):
        cycle = nx.find_cycle(graph)
        raise SkillGraphError(f"Skill graph contains a cycle: {cycle}")

    return graph


_cached_graph: nx.DiGraph | None = None


def get_skill_graph(force_reload: bool = False) -> nx.DiGraph:
    """Return a cached, validated copy of the skill graph."""
    global _cached_graph

    if force_reload or _cached_graph is None:
        _cached_graph = build_skill_graph()

    return _cached_graph.copy()


if __name__ == "__main__":
    g = get_skill_graph()
    print(f"Loaded {g.number_of_nodes()} skills, {g.number_of_edges()} prerequisite edges.")
    print("Is DAG:", nx.is_directed_acyclic_graph(g))
