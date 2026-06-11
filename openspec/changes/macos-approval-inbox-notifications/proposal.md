# Proposal: Phase 4: Approval Inbox and Notifications

## Why

V1.1 moves macOS into a dedicated release after V1.0 production bot readiness.

This change supports the macOS companion app while preserving the backend Agent as the source of truth.

## What

Implement pending WritePlan approval inbox and local notifications for pending approvals and pre-brief availability.

## Scope

- Fetch pending WritePlans.
- Show operations with preview/target/risk.
- Approve selected operation IDs.
- Reject run.
- Use UserNotifications for local notifications if macOS environment supports it.

## Non-goals

- No direct Lark writes.
- No remote push notification requirement.
- No live meeting control from macOS yet.
