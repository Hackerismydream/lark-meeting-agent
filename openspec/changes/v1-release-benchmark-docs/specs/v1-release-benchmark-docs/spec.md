# Delta for V1 Release, Benchmark, and Docs

## ADDED Requirements

### Requirement: V1 Release, Benchmark, and Docs Scope

The system MUST implement the `v1-release-benchmark-docs` phase according to the V1.0 roadmap.

#### Scenario: Phase implementation

- GIVEN the current Lark Meeting Agent repository
- WHEN this phase is implemented
- THEN all acceptance gates for `v1-release-benchmark-docs` pass
- AND no unrelated phase is implemented prematurely.

### Requirement: Safety Boundary Preservation

The phase MUST preserve the existing Lark safety boundary.

All Lark operations MUST go through `LarkToolAdapter`.

Write operations MUST require dry-run and explicit approval.

#### Scenario: No LarkToolAdapter bypass

- GIVEN any workflow, bot entrypoint, simulator, evaluator, or test helper
- WHEN it needs Lark behavior
- THEN it uses fake providers or `LarkToolAdapter`
- AND it does not directly call `lark-cli`, Lark SDK, or Lark HTTP APIs outside provider implementations.

### Requirement: Validation

The phase MUST include automated validation.

#### Scenario: Phase validation

- GIVEN the phase implementation
- WHEN validation runs
- THEN meeting tests pass
- AND ruff passes
- AND OpenSpec validates
- AND real Lark/LLM tests remain opt-in.

### Requirement: Truthful Reporting

The phase MUST document what is implemented, fake-tested, real-tested, blocked, or deferred.

#### Scenario: No fabricated production claims

- GIVEN a capability has not been real-smoke tested
- WHEN docs or reports describe it
- THEN they mark it as unverified, fake-tested, opt-in, or blocked
- AND they do not claim production verification.
