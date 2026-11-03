"""Policy persistence and underwriting boundary (CM-POLICY)."""

from collections.abc import Callable
from datetime import datetime, timezone
import sqlite3
from uuid import uuid4


class PolicyService:
    def __init__(self, connection: sqlite3.Connection, evaluate: Callable):
        self.connection = connection
        self.evaluate = evaluate

    def issue_policy(self, policy_id: str, customer_id: str, applicant_age: int,
                     coverage_cents: int, deductible_cents: int) -> dict:
        if not policy_id or not customer_id:
            raise ValueError("policy_id and customer_id are required")
        if type(coverage_cents) is not int or coverage_cents <= 0:
            raise ValueError("coverage_cents must be a positive integer")
        if (type(deductible_cents) is not int
                or not 0 <= deductible_cents <= coverage_cents):
            raise ValueError("deductible_cents must be between zero and coverage")
        # shield-underwriting-rules: eligibility and pricing.
        decision = self.evaluate(applicant_age, coverage_cents)
        if not decision["eligible"]:
            raise ValueError("Applicant is not eligible")
        with self.connection:
            self.connection.execute(
                "INSERT INTO policies VALUES (?, ?, ?, ?, ?, 'active')",
                (policy_id, customer_id, coverage_cents, deductible_cents,
                 decision["premium_cents"]),
            )
        return {
            "policy": self.get_policy(policy_id),
            "event": {
                "event_id": str(uuid4()),
                "event_type": "policy.issued",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "policy_id": policy_id,
            },
        }

    def get_policy(self, policy_id: str) -> dict:
        cursor = self.connection.execute(
            "SELECT policy_id, customer_id, coverage_cents, deductible_cents, "
            "premium_cents, status FROM policies WHERE policy_id = ?",
            (policy_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise LookupError(f"Policy not found: {policy_id}")
        return dict(zip((column[0] for column in cursor.description), row))
