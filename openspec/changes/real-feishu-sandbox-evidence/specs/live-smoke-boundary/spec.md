## ADDED Requirements

### Requirement: Live smoke remains out of scope

Stage 3 SHALL NOT join live meetings or claim live listening success.

#### Scenario: No live join

- **WHEN** Stage 3 demo scripts run
- **THEN** they SHALL NOT call `vc.meeting.join`, `vc.meeting.events`, or `vc.meeting.leave`
