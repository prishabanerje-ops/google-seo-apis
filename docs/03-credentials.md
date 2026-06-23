# Step 3: Set Up Credentials

Choose based on what you need:

| What you want | Credential type | Section |
|---------------|----------------|---------|
| PageSpeed Insights only | API Key | Part A |
| Google Search Console | OAuth Desktop App | Part B |
| Both | Do both parts | A + B |

---

## Part A: API Key (for PageSpeed Insights)

### A.1 Create an API Key

1. In [Google Cloud Console](https://console.cloud.google.com), go to
   **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **API key**
3. Copy the key shown (it starts with `AIzaSy...`)

> **Screenshot placeholder:** Credentials page — Create Credentials dropdown

### A.2 Restrict the Key (recommended)

1. Click **Edit API key** (pencil icon next to your new key)
2. Under **API restrictions**, select **Restrict key**
3. Choose **PageSpeed Insights API** from the dropdown
4. Click **Save**

### A.3 Save to Config File

**Mac/Linux:**
```bash
mkdir -p ~/.config/google-seo-apis
nano ~/.config/google-seo-apis/config.json
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\google-seo-apis"
notepad "$env:USERPROFILE\.config\google-seo-apis\config.json"
```

Paste the following, replacing `YOUR_API_KEY`:
```json
{
  "api_key": "YOUR_API_KEY"
}
```

Save and close the file.

### A.4 Verify

```bash
python scripts/auth.py --check
```

You should see: `API Key (PSI/CrUX)  ✓ OK`

---

## Part B: OAuth Desktop App (for Google Search Console)

**Goal:** Create OAuth credentials so `gsc.py` can access your Search Console data as you.

**Why:** OAuth means you log in as yourself in a browser — no service account, no property
access grants needed. If you can see a property in Search Console, the script can too.

### B.1 Create an OAuth Client ID

1. In [Google Cloud Console](https://console.cloud.google.com), go to
   **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. If prompted for a consent screen: choose **External**, fill in App name
   (e.g. "SEO APIs"), add your email as a test user, and save
4. Application type: **Desktop app**
5. Name it (e.g. "SEO APIs Desktop")
6. Click **Create** → **Download JSON**
7. Save the file somewhere safe (e.g. `~/client_secret.json`) — never inside the repo

### B.2 Run the Auth Command

**Mac/Linux:**
```bash
source venv/bin/activate
python scripts/auth.py --auth --creds ~/client_secret.json
```

**Windows:**
```powershell
venv\Scripts\activate
python scripts/auth.py --auth --creds %USERPROFILE%\client_secret.json
```

A browser window opens → sign in with your Google account → grant access.
The terminal prints: `✓ Authenticated. Token saved.`

> **Note:** If you see "Google hasn't verified this app", click **Advanced** →
> **Go to SEO APIs (unsafe)**. This is normal for personal Desktop apps that
> haven't been through Google's verification process.

### B.3 Add GSC Property to Config

Open `~/.config/google-seo-apis/config.json` (created automatically by the auth command)
and add your GSC property:

```json
{
  "api_key": "YOUR_API_KEY",
  "oauth_client_path": "/absolute/path/to/client_secret.json",
  "gsc_property": "sc-domain:yourdomain.com"
}
```

**Finding your property format:**
- Domain property (recommended): `sc-domain:example.com`
- URL prefix property: `https://www.example.com/`

### B.4 Verify

```bash
python scripts/auth.py --check
```

All three lines should show `✓ OK`:
```
  API key            ✓ OK
  OAuth token        ✓ OK (expires YYYY-MM-DD)
  GSC property       ✓ OK (sc-domain:...)
```

**Notes:**
- The token auto-refreshes — you only need to run `--auth` once
- Token stored at `~/.config/google-seo-apis/oauth-token.json` (outside repo, never committed)

---

**Next step:** [Run PageSpeed Insights →](04-running-psi.md)
