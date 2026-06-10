# Production Environment Example

Do not put real secrets in this file. Use it as a checklist for deployment environment variables.

```bash
# Feishu app
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="secret_from_secret_manager"

# LLM provider
export LMA_LLM_API_KEY="deepseek_or_other_key_from_secret_manager"
export LMA_LLM_BASE_URL="https://api.deepseek.com"
export LMA_LLM_MODEL="deepseek-v4-pro"

# Meeting agent production config
export LMA_PROVIDER_MODE="oapi"          # production target provider; cli remains diagnostic
export LARK_OAPI_ACCESS_TOKEN=""         # tenant/user token; do not commit real values
export LMA_STORAGE_BACKEND="sqlite"
export LMA_SQLITE_PATH="/var/lib/lark-meeting-agent/meeting-agent.sqlite3"
export LMA_WRITES_ENABLED="false"        # enable only after approval protocol is verified
export LMA_DRY_RUN_DEFAULT="true"

# Access policy
export LMA_ALLOWED_USERS="ou_user_1,ou_user_2"
export LMA_ALLOWED_CHAT_IDS="oc_chat_1"
export LMA_ADMIN_USERS="ou_admin"
export LMA_WRITE_APPROVERS="ou_admin,ou_approver"

# Runtime safety
export LARK_CLI_NO_PROXY="1"
```

Production config should keep secrets in environment variables, Keychain, 1Password, Bitwarden, systemd environment files, Docker secrets, or another secret manager.

Never commit `.env`, token dumps, device codes, authorization URLs, cookies, app secrets, access tokens, or private document URLs.
