# One-time OAuth setup for the GLM-4.7-Flash QuickML endpoint

The `Authorization: Bearer YOUR_TOKEN` in Catalyst's sample code needs a real,
auto-refreshing Zoho OAuth token. Do this once, before your first deploy.

## 1. Register a Self Client

Go to https://api-console.zoho.in (IN data center, matches your login) →
**Add Client** → **Self Client** → **Create**.

You'll get a `client_id` and `client_secret`. Save both.

## 2. Generate a grant token (Self Client tab, same console)

Click **Self Client** in your client list → **Generate Code**.
- Scope: `QuickML.deployment.READ,ZohoCatalyst.mlkit.READ`
  (if the chat call later 401s, regenerate adding `ZohoCatalyst.zcql.CREATE`
  and `ZohoCatalyst.tables.rows.READ` too — Zoho's scope docs for QuickML
  chat specifically aren't public, so this may need one iteration)
- Duration: 10 minutes (you only need it long enough for step 3)
- Description: anything, e.g. "ksp-ai-backend"
- Click **Generate** → copy the code shown (valid only 60 seconds once used)

## 3. Exchange the grant code for access + refresh tokens

Run this immediately after generating the code (replace the bracketed values):

```
curl -X POST https://accounts.zoho.in/oauth/v2/token \
  -d "code=[GRANT_CODE_FROM_STEP_2]" \
  -d "client_id=[CLIENT_ID_FROM_STEP_1]" \
  -d "client_secret=[CLIENT_SECRET_FROM_STEP_1]" \
  -d "grant_type=authorization_code"
```

Response contains `access_token` (expires in 1hr — ignore it, we don't use it
directly) and `refresh_token` (**does not expire** — this is the one you need).

## 4. Store credentials as function environment variables

Catalyst console → your project → **Functions** → `backend` → **Configuration**
tab → **Environment Variables** → add:

| Key | Value |
|---|---|
| `ZOHO_CLIENT_ID` | from step 1 |
| `ZOHO_CLIENT_SECRET` | from step 1 |
| `ZOHO_REFRESH_TOKEN` | from step 3 |

`main.py`'s `_get_quickml_access_token()` uses these three to silently mint a
fresh access token every ~55 minutes — nothing to babysit during your demo.

## 5. Sanity-test before wiring it into the full backend

```python
import requests, os

resp = requests.post("https://accounts.zoho.in/oauth/v2/token", data={
    "refresh_token": "PASTE_HERE",
    "client_id": "PASTE_HERE",
    "client_secret": "PASTE_HERE",
    "grant_type": "refresh_token",
})
token = resp.json()["access_token"]

chat = requests.post(
    "https://api.catalyst.zoho.in/quickml/v1/project/44972000000032001/glm/chat",
    headers={"Authorization": f"Bearer {token}", "CATALYST-ORG": "60074366475"},
    json={"model": "crm-di-glm47b_30b_it",
          "messages": [{"role": "user", "content": "Say hello in one word."}],
          "max_tokens": 20},
)
print(chat.status_code, chat.json())
```

Run this locally first (not as a Catalyst function) to confirm the token
flow and response shape before trusting it inside `main.py`.
