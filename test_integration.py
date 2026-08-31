"""
test_integration.py

End-to-end check that skill_graph and mastery work together the way the
LangGraph nodes are expected to use them: get a candidate path for a goal,
then track/persist mastery per skill as the learner answers quizzes.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for subdir in ("skill_graph", "mastery"):
    path = str(ROOT / subdir)
    if path not in sys.path:
        sys.path.insert(0, path)

from query import get_path, get_prerequisites  # noqa: E402
from store import PersistentMasteryStore  # noqa: E402


class SkillGraphMasteryIntegrationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        self.db_path = Path(tmp.name)
        self.store = PersistentMasteryStore(self.db_path)

    def tearDown(self):
        if self.db_path.exists():
            os.remove(self.db_path)

    def test_path_respects_prerequisite_order(self):
        path = get_path(known_skills=[], goal_skill="data_engineering_capstone")
        position = {skill: i for i, skill in enumerate(path)}

        for skill in path:
            for prereq in get_prerequisites(skill):
                if prereq in position:
                    self.assertLess(position[prereq], position[skill])

    def test_learner_advances_through_path_via_mastery_updates(self):
        user_id = "learner_1"
        path = get_path(known_skills=["python_basics", "git_version_control"], goal_skill="cloud_fundamentals")

        for skill_id in path:
            mastery = self.store.get_mastery(user_id, skill_id)
            self.assertFalse(self.store.is_mastered(user_id, skill_id))

            for _ in range(5):
                mastery = self.store.record_quiz_result(user_id, skill_id, True)

            self.assertTrue(self.store.is_mastered(user_id, skill_id))
            self.assertGreaterEqual(mastery, 0.6)

    def test_struggling_learner_stays_below_threshold(self):
        user_id = "learner_2"
        skill_id = "sql_joins"

        for _ in range(3):
            mastery = self.store.record_quiz_result(user_id, skill_id, False)

        self.assertFalse(self.store.is_mastered(user_id, skill_id))
        self.assertLess(mastery, 0.6)

    def test_known_skills_shrink_the_required_path(self):
        goal = "data_engineering_capstone"
        full_path = get_path(known_skills=[], goal_skill=goal)
        partial_path = get_path(known_skills=full_path[:3], goal_skill=goal)

        self.assertLess(len(partial_path), len(full_path))
        for skill in full_path[:3]:
            self.assertNotIn(skill, partial_path)


if __name__ == "__main__":
    unittest.main()
