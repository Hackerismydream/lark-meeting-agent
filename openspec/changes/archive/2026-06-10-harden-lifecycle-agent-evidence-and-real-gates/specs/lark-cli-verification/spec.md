## ADDED Requirements

### Requirement: Lark CLI verification matrix
The repository MUST document fake coverage, real smoke status, blockers, and last verified date for each adapter operation.

#### Scenario: Unverified operation documented
- **WHEN** an adapter operation has not been real-smoke verified
- **THEN** the matrix marks it as unverified instead of implying success.

### Requirement: No fabricated real status
Documentation MUST distinguish implemented adapter support from real account verification.

#### Scenario: Real transcript blocked
- **WHEN** the account lacks readable meeting minutes
- **THEN** docs mark transcript retrieval as blocked by account data.
