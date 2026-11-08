# JobHunter AI — independent Google OIDC sandbox

Public **code-only** authentication test. **No real credentials, email addresses, profile records, job history, API keys or database connection are included**. This repository is not the real JobHunter AI application.

## Security boundaries

- The application imports only Streamlit and a small local authentication policy.
- Unauthorized visitors cannot view private data; this sandbox contains no such data at all.
- One verified, explicitly allowlisted Google email is required.
- All sensitive configuration must live in **hosting provider Secrets**, never in GitHub.
- The main JobHunter AI private repository and Streamlit deployment remain unchanged.

## Deployment configuration (in the hosting provider, not this repository)

```toml
SANDBOX_AUTH_MODE = "google"
APP_ALLOWED_EMAILS = "ONLY-YOUR-TEST-GOOGLE-EMAIL@example.com"

[auth]
redirect_uri = "https://YOUR-INDEPENDENT-TEST-HOST/oauth2callback"
cookie_secret = "REPLACE_WITH_A_PRIVATE_CRYPTOGRAPHICALLY_RANDOM_SECRET"
client_id = "REPLACE_WITH_REAL_PRIVATE_CLIENT_ID"
client_secret = "REPLACE_WITH_REAL_PRIVATE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

In Google Cloud's existing **Web application** OAuth client add the independent test site's exact /oauth2callback URI as an **additional** Authorized redirect URI. Do not remove the production URI. Test a permitted Google account, a nonpermitted one, and sign out. Never enable Google sign-in on the main application until all checks pass and the owner explicitly approves.

**Important Streamlit limit:** Streamlit Community Cloud documentation states that an authentication-configured app counts as the workspace's one allowed private app, even if the repository is public. Since the existing JobHunter AI deployment occupies that slot, avoid trying to configure OIDC for a second app in the same workspace. Use a truly separate suitable hosting environment that supports Streamlit's authentication flow, or hold the live test until one is available. Never delete or expose the original deployment to work around the limit.

Do **not** copy DATABASE_URL, APP_ACCESS_PASSWORD, Adzuna keys, Supabase credentials or any candidate data into this sandbox.

## Offline checks

Run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py sandbox_auth.py
```

These tests verify local policy only; they do not prove that Google sign-in or callback works on a deployed app.
