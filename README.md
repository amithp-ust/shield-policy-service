# Shield policy service

**Application:** Policy Administration (`policy-admin`)

**Component:** `CM-POLICY`

**Owner:** Policy platform

`src/policy/service.py` issues policies using the eligibility and pricing
callback supplied by `shield-underwriting-rules`. Policies are stored in SQLite;
apply `db/migrations/001_policy.sql` before constructing `PolicyService`.
The service owns Policy, Coverage, Premium, and Deductible.

`contracts/policy-api.yaml` defines the intended API;
`contracts/events/policy-issued.json` defines the policy-issued event schema.
`issue_policy` returns both the stored policy and its event; no message broker
is started by this fixture.

`contracts/shared/policy-risk-view.json` is the canonical existing SQLite
`policy_risk_view` row contract for consumer `CM-FRAUD`. The migration exposes
`policy_id`, `coverage_cents`, `deductible_cents`, and `status`; fraud reads the
last three using a `policy_id` lookup on its injected `policy_database`.
The schema documents SQLite's existing nullable TEXT primary-key edge case;
it does not change constraints or authorize production database sharing.
Coordinate view changes with Claims platform and the fraud consumer link in
`shield-fraud-scoring/contracts/policy-risk-view.json`.
Run the sibling `shield-context/scripts/verify_fixture.py --repos-root ..`
from the context checkout to check the real migration against the shared schema.
## Specification consumer

Canonical specs, authoring, gates, and requirement metrics live only in
[`amithp-ust/Intent-to-spec`](https://github.com/amithp-ust/Intent-to-spec).
Shared glossary, map, standards, and policy remain in
[`amithp-ust/shield-context`](https://github.com/amithp-ust/shield-context).
This repo owns `CM-POLICY` implementation, not spec authoring. See
[AGENTS.md](AGENTS.md) for immutable approved spec references, issue/PR traceability,
human review, and fixture-contract checks. Do not install authoring here or copy
specs; empty `specs/.gitkeep` is a legacy placeholder.

Python 3.11+, standard library only. Run `python -m unittest discover -s tests`
from this repository root; the unit-test CI runs the same command on Python 3.11.
These are local callable stubs, not deployed HTTP services.
