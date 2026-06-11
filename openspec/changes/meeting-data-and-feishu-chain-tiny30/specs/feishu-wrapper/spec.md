# Delta for Feishu Chain Wrapper

## ADDED Requirements

### Requirement: Feishu-like Context Bridge

The system MUST convert public meeting fixtures into a Feishu-like meeting context.

#### Scenario: Fixture to Feishu context

- GIVEN a valid `MeetingFixture`
- WHEN it is wrapped
- THEN the result includes calendar event, agenda doc, participants, transcript stream, chat events, related docs, output targets, and approval policy.

### Requirement: Mock Lark Tools

Mock Lark tools MUST write local artifacts only.

#### Scenario: Local-only eval run

- GIVEN an evaluation run
- WHEN mock tools create minutes, action items, decisions, or follow-up messages
- THEN files are written under `runs/meeting_eval/<run_id>/`
- AND no real Lark API or `lark-cli` call is made.
