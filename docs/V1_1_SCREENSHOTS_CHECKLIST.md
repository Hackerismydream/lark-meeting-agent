# V1.1 Screenshots Checklist

Capture screenshots only after verifying no tokens, private URLs, tenant IDs, or private meeting content are visible.

## Required Screenshots

- [ ] Menu bar status connected to local backend.
- [ ] Settings view with non-sensitive local API URL.
- [ ] Production environment warning with fake environment label.
- [ ] Approval inbox with fixture WritePlan operations.
- [ ] Selected-operation approval state.
- [ ] Rejected run state or safe backend error.
- [ ] Pre-brief result with source citations.
- [ ] Run trace timeline.
- [ ] Write results inside run detail.
- [ ] Search answer with meeting ID and segment ID.
- [ ] Insufficient evidence search result.
- [ ] Text transcript upload success.
- [ ] Unsupported audio upload rejection.

## Redaction Checklist

- [ ] No bearer token.
- [ ] No Lark app secret.
- [ ] No DeepSeek key.
- [ ] No real tenant-private URL.
- [ ] No real customer/private meeting content unless explicitly approved for demo.
- [ ] No `.env` file or shell history visible.

## Recommended Demo Data

Use fixture or synthetic meetings for screenshots. Real Feishu data should only be used when the tenant owner has explicitly approved demo use.
