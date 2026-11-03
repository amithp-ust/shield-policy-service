CREATE TABLE policies (
    policy_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    coverage_cents INTEGER NOT NULL CHECK (coverage_cents > 0),
    deductible_cents INTEGER NOT NULL CHECK (
        deductible_cents >= 0 AND deductible_cents <= coverage_cents
    ),
    premium_cents INTEGER NOT NULL CHECK (premium_cents > 0),
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled'))
);

CREATE VIEW policy_risk_view AS
SELECT policy_id, coverage_cents, deductible_cents, status
FROM policies;
