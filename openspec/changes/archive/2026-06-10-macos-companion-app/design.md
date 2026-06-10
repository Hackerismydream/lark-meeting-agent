## Context

The production Feishu bot should own meeting workflows, Lark provider access, approval policy, and audit. A macOS app can improve daily usability, but implementing it before production bot storage and approval APIs would create a thin shell.

## Goals / Non-Goals

**Goals:**

- Define macOS app role and phase ordering.
- Define first-version UX surfaces.
- Define security rule that all writes go through backend `LarkToolAdapter`.
- Define Cloud Bot Mode as the first target.

**Non-Goals:**

- No macOS runtime implementation.
- No direct Lark writes from the app.
- No local agent service in the first app version.
- No replacement for Feishu bot DM/group UX.

## Decisions

### Decision: Cloud Bot Mode first

The first macOS app should connect to the production bot service and act as a client for approvals, traces, search, and status. Local Agent Mode can follow later.

### Decision: SwiftUI when implementation starts

SwiftUI is the likely implementation path for menu bar, notifications, windows, and Keychain integration, but no Swift code is introduced in this change.

## Risks / Trade-offs

- [Risk] App scope distracts from production bot. -> Mitigation: keep this change roadmap-only.
- [Risk] Direct local writes bypass backend safety. -> Mitigation: state that all writes must flow through backend approval and `LarkToolAdapter`.
