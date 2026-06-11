# Error Taxonomy

`classify_error` maps internal failures to safe user-facing categories.

## Codes

- `permission`: missing permission, forbidden, or access denied.
- `gray`: tenant/account not enabled for a gated feature.
- `missing_transcript`: no readable transcript or meeting content.
- `unknown_event`: unrecognized live meeting event shape.
- `malformed_output`: invalid model or provider output.
- `approval_mismatch`: write attempted without explicit approval.
- `provider_mismatch`: approval provider differs from the run snapshot.
- `unknown`: fallback category with secret redaction.

## User Message Rule

User messages must not include secrets, raw tokens, cookies, private URLs, or full provider dumps.

## Retry Rule

Only malformed output is marked retryable by default. Permission, gray release, transcript absence, approval, and provider mismatch require config/user action rather than blind retry.
