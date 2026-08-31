import unittest

import networkx as nx

from build_graph import (
    SkillGraphError,
    build_skill_graph,
    get_skill_graph,
    load_edges,
    load_nodes,
)
from query import (
    SkillNotFoundError,
    get_all_prerequisites,
    get_path,
    get_prerequisites,
    get_skill_info,
    normalize_skill_id,
)


class LoadDataTests(unittest.TestCase):
    def test_load_nodes_unique_ids(self):
        nodes = load_nodes()
        self.assertGreater(len(nodes), 0)
        self.assertIn("sql_basics", nodes)
        self.assertIn("data_engineering_capstone", nodes)

    def test_load_edges_reference_existing_nodes(self):
        nodes = load_nodes()
        edges = load_edges()
        self.assertGreater(len(edges), 0)
        for source, target in edges:
            self.assertIn(source, nodes)
            self.assertIn(target, nodes)


class BuildGraphTests(unittest.TestCase):
    def test_builds_valid_dag(self):
        graph = build_skill_graph()
        self.assertTrue(nx.is_directed_acyclic_graph(graph))
        self.assertGreater(graph.number_of_nodes(), 0)
        self.assertGreater(graph.number_of_edges(), 0)

    def test_node_metadata_preserved(self):
        graph = build_skill_graph()
        info = graph.nodes["sql_joins"]
        self.assertEqual(info["name"], "SQL Joins")
        self.assertIn("difficulty", info)

    def test_rejects_cycles(self):
        import json
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            nodes_path = Path(tmp) / "nodes.json"
            edges_path = Path(tmp) / "edges.json"

            nodes_path.write_text(json.dumps([
                {"id": "a", "name": "A"},
                {"id": "b", "name": "B"},
            ]))
            edges_path.write_text(json.dumps([
                {"source": "a", "target": "b"},
                {"source": "b", "target": "a"},
            ]))

            with self.assertRaises(SkillGraphError):
                build_skill_graph(nodes_path, edges_path)

    def test_rejects_unknown_edge_reference(self):
        import json
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            nodes_path = Path(tmp) / "nodes.json"
            edges_path = Path(tmp) / "edges.json"

            nodes_path.write_text(json.dumps([{"id": "a", "name": "A"}]))
            edges_path.write_text(json.dumps([{"source": "a", "target": "ghost"}]))

            with self.assertRaises(SkillGraphError):
                build_skill_graph(nodes_path, edges_path)

    def test_cached_graph_is_a_copy(self):
        g1 = get_skill_graph()
        g1.add_node("scratch_node")
        g2 = get_skill_graph()
        self.assertNotIn("scratch_node", g2)


class NormalizeSkillIdTests(unittest.TestCase):
    def test_lowercases_and_replaces_spaces(self):
        self.assertEqual(normalize_skill_id("SQL Joins"), "sql_joins")
        self.assertEqual(normalize_skill_id("  Python Basics  "), "python_basics")
        self.assertEqual(normalize_skill_id("sql_joins"), "sql_joins")


class GetPrerequisitesTests(unittest.TestCase):
    def test_direct_prerequisites(self):
        prereqs = get_prerequisites("data_warehousing")
        self.assertEqual(set(prereqs), {"etl_pipelines", "indexing"})

    def test_no_prerequisites_for_foundational_skill(self):
        self.assertEqual(get_prerequisites("python_basics"), [])

    def test_accepts_display_name(self):
        self.assertEqual(get_prerequisites("Data Warehousing"), get_prerequisites("data_warehousing"))

    def test_unknown_skill_raises(self):
        with self.assertRaises(SkillNotFoundError):
            get_prerequisites("not_a_real_skill")

    def test_transitive_prerequisites_are_topologically_ordered(self):
        graph = get_skill_graph()
        transitive = get_all_prerequisites("data_warehousing")
        positions = {skill: i for i, skill in enumerate(transitive)}
        for source, target in graph.edges:
            if source in positions and target in positions:
                self.assertLess(positions[source], positions[target])


class GetPathTests(unittest.TestCase):
    def test_full_path_from_scratch(self):
        path = get_path(known_skills=[], goal_skill="data_warehousing")
        self.assertIn("sql_basics", path)
        self.assertIn("data_warehousing", path)
        self.assertEqual(path[-1], "data_warehousing")

    def test_known_skills_are_excluded(self):
        path = get_path(known_skills=["sql_basics", "sql_joins", "relational_algebra"], goal_skill="data_modeling")
        self.assertNotIn("sql_basics", path)
        self.assertNotIn("sql_joins", path)
        self.assertIn("data_modeling", path)

    def test_result_is_topologically_valid(self):
        graph = get_skill_graph()
        path = get_path(known_skills=["python_basics"], goal_skill="data_engineering_capstone")
        positions = {skill: i for i, skill in enumerate(path)}
        for source, target in graph.edges:
            if source in positions and target in positions:
                self.assertLess(positions[source], positions[target])

    def test_already_knowing_goal_returns_empty(self):
        path = get_path(known_skills=["sql_basics"], goal_skill="sql_basics")
        self.assertEqual(path, [])

    def test_accepts_display_names_for_known_skills_and_goal(self):
        path = get_path(known_skills=["SQL Basics"], goal_skill="SQL Joins")
        self.assertEqual(path, ["sql_joins"])

    def test_unknown_goal_raises(self):
        with self.assertRaises(SkillNotFoundError):
            get_path(known_skills=[], goal_skill="not_a_real_skill")


class GetSkillInfoTests(unittest.TestCase):
    def test_returns_metadata(self):
        info = get_skill_info("sql_joins")
        self.assertEqual(info["name"], "SQL Joins")
        self.assertIn("description", info)

    def test_unknown_skill_raises(self):
        with self.assertRaises(SkillNotFoundError):
            get_skill_info("not_a_real_skill")


if __name__ == "__main__":
    unittest.main()
