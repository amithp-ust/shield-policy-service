from pathlib import Path
import sqlite3
import unittest

from src.policy.service import PolicyService


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.executescript(
            (Path(__file__).resolve().parents[1]
             / "db/migrations/001_policy.sql").read_text()
        )
        self.service = PolicyService(
            self.connection,
            lambda age, coverage: {"eligible": age >= 18, "premium_cents": 5000},
        )

    def test_issue_policy(self):
        result = self.service.issue_policy("P-1", "C-1", 35, 100000, 10000)
        self.assertEqual(result["policy"]["premium_cents"], 5000)
        self.assertEqual(result["event"]["policy_id"], "P-1")
        self.assertEqual(result["event"]["event_type"], "policy.issued")

    def test_ineligible(self):
        with self.assertRaises(ValueError):
            self.service.issue_policy("P-1", "C-1", 17, 100000, 10000)
        with self.assertRaises(LookupError):
            self.service.get_policy("P-1")

    def test_invalid_deductible(self):
        with self.assertRaises(ValueError):
            self.service.issue_policy("P-1", "C-1", 35, 100000, 100001)

    def test_unknown_policy(self):
        with self.assertRaises(LookupError):
            self.service.get_policy("missing")
