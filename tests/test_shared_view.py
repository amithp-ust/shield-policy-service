import json
from pathlib import Path
import sqlite3
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SharedViewTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.executescript(
            (ROOT / "db/migrations/001_policy.sql").read_text()
        )
        self.schema = json.loads(
            (ROOT / "contracts/shared/policy-risk-view.json").read_text()
        )

    def test_contract_matches_migration_columns(self):
        columns = self.connection.execute("PRAGMA table_info(policy_risk_view)").fetchall()
        self.assertEqual([column[1] for column in columns], self.schema["required"])
        self.assertEqual(self.schema["x-provider"], "CM-POLICY")
        self.assertEqual(self.schema["x-consumers"], ["CM-FRAUD"])
        self.assertEqual(self.schema["properties"]["status"]["enum"],
                         ["active", "cancelled"])

    def test_contract_preserves_existing_nullable_primary_key(self):
        self.connection.execute(
            "INSERT INTO policies VALUES (NULL, 'C-SYNTHETIC', 100, 0, 1, 'active')"
        )
        row = self.connection.execute("SELECT * FROM policy_risk_view").fetchone()
        self.assertIsNone(row[0])
        self.assertIn("null", self.schema["properties"]["policy_id"]["type"])

    def test_migration_enforces_documented_amount_and_status_constraints(self):
        for coverage, deductible, status in (
            (0, 0, "active"), (100, -1, "active"),
            (100, 101, "active"), (100, 0, "unknown"),
        ):
            with self.subTest(coverage=coverage, deductible=deductible, status=status):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.connection.execute(
                        "INSERT INTO policies VALUES ('P-SYNTHETIC', 'C-SYNTHETIC', ?, ?, 1, ?)",
                        (coverage, deductible, status),
                    )


if __name__ == "__main__":
    unittest.main()
