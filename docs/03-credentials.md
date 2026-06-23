# Step 3: Set Up Credentials

Choose based on what you need:

| What you want | Credential type | Section |
|---------------|----------------|---------|
| PageSpeed Insights only | API Key | Part A |
| Google Search Console | Service Account | Part B |
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

## Part B: Service Account (for Google Search Console)

### B.1 Create a Service Account

1. In Google Cloud Console, go to **IAM & Admin** → **Service Accounts**
2. Click **+ Create Service Account**
3. Name it `gsc-reader`, click **Create and continue**
4. Skip the role assignment step — click **Done**

> **Screenshot placeholder:** Service Account creation form

### B.2 Download the JSON Key

1. Click on your new service account in the list
2. Go to the **Keys** tab
3. Click **Add Key** → **Create new key** → **JSON**
4. A `.json` file downloads — save it somewhere permanent
   (e.g. `~/google-credentials/gsc-service-account.json`)

> **Warning:** This file is your private key. Never commit it to git or share it.

### B.3 Grant Access in Search Console

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Select your property
3. Click **Settings** (gear icon) → **Users and permissions** → **Add user**
4. Paste the `client_email` from your downloaded JSON file
   (looks like `gsc-reader@your-project.iam.gserviceaccount.com`)
5. Set permission to **Full**
6. Click **Add**

> **Screenshot placeholder:** Search Console — Users and permissions page

### B.4 Add to Config File

Open `~/.config/google-seo-apis/config.json` and update it:

```json
{
  "api_key": "YOUR_API_KEY",
  "service_account_path": "/absolute/path/to/gsc-service-account.json",
  "gsc_property": "sc-domain:yourdomain.com"
}
```

**Finding your property format:**
- Domain property (recommended): `sc-domain:example.com`
- URL prefix property: `https://www.example.com/`

**Windows path format:**
```json
{
  "service_account_path": "C:\\Users\\YourName\\google-credentials\\gsc-service-account.json"
}
```

### B.5 Verify

```bash
python scripts/auth.py --check
```

All three lines should show `✓ OK`.

---

**Next step:** [Run PageSpeed Insights →](04-running-psi.md)
