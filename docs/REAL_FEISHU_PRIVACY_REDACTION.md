# Real Feishu Privacy Redaction

Stage 3 evidence packs must not commit private Feishu content or credentials.

## Redacted Keys

Evidence helpers redact values for keys matching:

```text
token
secret
cookie
authorization
password
passcode
open_id
user_id
email
mobile
phone
chat_id
```

## Redacted Values

Evidence helpers also redact obvious API key and bearer-token values.

## Not Captured Automatically

- Private meeting transcript.
- Private chat screenshots.
- Access tokens.
- Cookies.
- App secrets.
- Raw lark-cli auth output.

## Manual Review

Before publishing a run artifact or screenshot, verify that it contains only sandbox objects and public fixture content.
