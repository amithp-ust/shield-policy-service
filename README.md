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

Shared context: `amithp-ust/shield-context` (`AGENTS.md`, glossary, scope,
standards, and component map). `specs/` is empty pending spec pull requests.
Python 3.12+, standard library only. Run `python -m unittest discover -s tests`.
These are local callable stubs, not deployed HTTP services.
