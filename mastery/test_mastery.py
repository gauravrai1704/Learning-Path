import os
import tempfile
import unittest
from pathlib import Path

from models import (
    DEFAULT_PROB_GUESS,
    DEFAULT_PROB_MASTERY,
    DEFAULT_PROB_SLIP,
    DEFAULT_PROB_TRANSIT,
    MasteryRecord,
)
from store import (
    PersistentMasteryStore,
    get_bkt_params,
    get_mastery,
    set_bkt_params,
    set_mastery,
)


class MastertyStoreTestCase(unittest.TestCase):
    db_path: Path

    def setUp(self) -> None:
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        self.db_path = Path(tmp.name)

    def tearDown(self) -> None:
        if self.db_path.exists():
            os.remove(self.db_path)


class GetSetMasteryTests(MastertyStoreTestCase):
    def test_unknown_user_skill_returns_default(self):
        value = get_mastery("new_user", "sql_joins", self.db_path)
        self.assertEqual(value, DEFAULT_PROB_MASTERY)

    def test_set_then_get_round_trips(self):
        set_mastery("u1", "sql_joins", 0.42, self.db_path)
        self.assertAlmostEqual(get_mastery("u1", "sql_joins", self.db_path), 0.42)

    def test_set_overwrites_previous_value(self):
        set_mastery("u1", "sql_joins", 0.2, self.db_path)
        set_mastery("u1", "sql_joins", 0.9, self.db_path)
        self.assertAlmostEqual(get_mastery("u1", "sql_joins", self.db_path), 0.9)

    def test_users_are_isolated(self):
        set_mastery("u1", "sql_joins", 0.8, self.db_path)
        set_mastery("u2", "sql_joins", 0.1, self.db_path)
        self.assertAlmostEqual(get_mastery("u1", "sql_joins", self.db_path), 0.8)
        self.assertAlmostEqual(get_mastery("u2", "sql_joins", self.db_path), 0.1)

    def test_skills_are_isolated_per_user(self):
        set_mastery("u1", "sql_joins", 0.8, self.db_path)
        set_mastery("u1", "indexing", 0.3, self.db_path)
        self.assertAlmostEqual(get_mastery("u1", "sql_joins", self.db_path), 0.8)
        self.assertAlmostEqual(get_mastery("u1", "indexing", self.db_path), 0.3)

    def test_rejects_out_of_range_values(self):
        with self.assertRaises(ValueError):
            set_mastery("u1", "sql_joins", 1.5, self.db_path)
        with self.assertRaises(ValueError):
            set_mastery("u1", "sql_joins", -0.1, self.db_path)

    def test_set_mastery_preserves_other_bkt_params(self):
        record = MasteryRecord(
            user_id="u1",
            skill_id="sql_joins",
            prob_mastery=DEFAULT_PROB_MASTERY,
            prob_slip=0.05,
            prob_guess=0.4,
            prob_transit=0.5,
        )
        set_bkt_params(record, self.db_path)

        set_mastery("u1", "sql_joins", 0.77, self.db_path)

        updated = get_bkt_params("u1", "sql_joins", self.db_path)
        self.assertAlmostEqual(updated.prob_mastery, 0.77)
        self.assertAlmostEqual(updated.prob_slip, 0.05)
        self.assertAlmostEqual(updated.prob_guess, 0.4)
        self.assertAlmostEqual(updated.prob_transit, 0.5)


class GetSetBktParamsTests(MastertyStoreTestCase):
    def test_defaults_for_unseen_skill(self):
        params = get_bkt_params("u1", "sql_joins", self.db_path)
        self.assertEqual(params.prob_mastery, DEFAULT_PROB_MASTERY)
        self.assertEqual(params.prob_slip, DEFAULT_PROB_SLIP)
        self.assertEqual(params.prob_guess, DEFAULT_PROB_GUESS)
        self.assertEqual(params.prob_transit, DEFAULT_PROB_TRANSIT)

    def test_round_trip(self):
        record = MasteryRecord("u1", "sql_joins", 0.6, 0.15, 0.2, 0.35)
        set_bkt_params(record, self.db_path)
        fetched = get_bkt_params("u1", "sql_joins", self.db_path)
        self.assertAlmostEqual(fetched.prob_mastery, 0.6)
        self.assertAlmostEqual(fetched.prob_slip, 0.15)
        self.assertAlmostEqual(fetched.prob_guess, 0.2)
        self.assertAlmostEqual(fetched.prob_transit, 0.35)


class PersistentMasteryStoreTests(MastertyStoreTestCase):
    def test_get_mastery_defaults(self):
        store = PersistentMasteryStore(self.db_path)
        self.assertEqual(store.get_mastery("u1", "sql_joins"), DEFAULT_PROB_MASTERY)

    def test_record_quiz_result_increases_mastery_on_correct(self):
        store = PersistentMasteryStore(self.db_path)
        before = store.get_mastery("u1", "sql_joins")
        after = store.record_quiz_result("u1", "sql_joins", True)
        self.assertGreater(after, before)
        self.assertAlmostEqual(store.get_mastery("u1", "sql_joins"), after)

    def test_record_quiz_result_persists_across_instances(self):
        PersistentMasteryStore(self.db_path).record_quiz_result("u1", "sql_joins", True)
        second_instance = PersistentMasteryStore(self.db_path)
        self.assertGreater(second_instance.get_mastery("u1", "sql_joins"), DEFAULT_PROB_MASTERY)

    def test_matches_bkt_update_reference_formula(self):
        import importlib.util
        import sys

        code_dir = Path(__file__).resolve().parent.parent / "code"
        spec = importlib.util.spec_from_file_location("bkt_update_reference", code_dir / "bkt_update.py")
        assert spec is not None and spec.loader is not None
        bkt_update = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = bkt_update
        spec.loader.exec_module(bkt_update)

        store = PersistentMasteryStore(self.db_path)
        actual = store.record_quiz_result("u1", "sql_joins", True)

        expected = bkt_update.update_mastery(
            DEFAULT_PROB_MASTERY, DEFAULT_PROB_SLIP, DEFAULT_PROB_GUESS, DEFAULT_PROB_TRANSIT, True
        )
        self.assertAlmostEqual(actual, expected)

    def test_is_mastered_threshold(self):
        store = PersistentMasteryStore(self.db_path)
        set_mastery("u1", "sql_joins", 0.5, self.db_path)
        self.assertFalse(store.is_mastered("u1", "sql_joins", threshold=0.6))
        set_mastery("u1", "sql_joins", 0.7, self.db_path)
        self.assertTrue(store.is_mastered("u1", "sql_joins", threshold=0.6))


if __name__ == "__main__":
    unittest.main()
