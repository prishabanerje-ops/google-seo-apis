# Advanced Usage

For developers and power users who want to automate, integrate, or troubleshoot.

---

## Environment Variables

Use these instead of the config file (useful for CI/CD or shared environments):

| Variable | Replaces config key | Example value |
|----------|-------------------|---------------|
| `GOOGLE_API_KEY` | `api_key` | `AIzaSy...` |
| `GOOGLE_APPLICATION_CREDENTIALS` | `service_account_path` | `/path/to/sa.json` |
| `GSC_PROPERTY` | `gsc_property` | `sc-domain:example.com` |

**Mac/Linux** (add to `~/.zshrc` or `~/.bashrc` to persist across sessions):
```bash
export GOOGLE_API_KEY="AIzaSy..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa.json"
export GSC_PROPERTY="sc-domain:example.com"
```

**Windows PowerShell** (add to `$PROFILE` to persist):
```powershell
$env:GOOGLE_API_KEY = "AIzaSy..."
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\sa.json"
$env:GSC_PROPERTY = "sc-domain:example.com"
```

---

## JSON Output (for scripting)

Both scripts support `--json` to output structured data for piping:

```bash
# Get just the performance score
python scripts/psi.py https://example.com --json | python3 -c "
import json, sys
data = json.load(sys.stdin)
score = data['lighthouseResult']['categories']['performance']['score']
print(f'Performance: {int(score * 100)}')
"

# Save GSC data as JSON
python scripts/gsc.py --json > gsc-data.json

# GSC output structure (wrapped for consistency):
python scripts/gsc.py --json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"Property: {data['property']}, Dimension: {data['dimension']}, Days: {data['days']}\")
for row in data['rows']:
    print(f\"{row['keys'][0]}: {row['clicks']} clicks\")
"
```

---

## Scheduled Runs

**Mac — run PSI daily at 9am via crontab:**
```bash
crontab -e
# Add this line (replace paths with your actual paths):
0 9 * * * /path/to/google-seo-apis/venv/bin/python /path/to/google-seo-apis/scripts/psi.py https://yourdomain.com >> /tmp/psi-daily.log 2>&1
```

**Windows — Task Scheduler:**
1. Open Task Scheduler → **Create Basic Task**
2. Trigger: **Daily** at 9:00 AM
3. Action: **Start a program**
4. Program: `C:\path\to\google-seo-apis\venv\Scripts\python.exe`
5. Arguments: `scripts\psi.py https://yourdomain.com`
6. Start in: `C:\path\to\google-seo-apis`

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Error: No API key configured` | `api_key` missing from config | See [docs/03-credentials.md Part A](03-credentials.md#part-a-api-key-for-pagespeed-insights) |
| `Error: GSC credentials not configured` | Service account not set up | See [docs/03-credentials.md Part B](03-credentials.md#part-b-service-account-for-google-search-console) |
| `HttpError 403: The caller does not have permission` | Service account not added to GSC | Add `client_email` from SA JSON to Search Console users |
| `HttpError 429: Quota exceeded` | Too many API calls | Wait a minute; add an API key to raise your rate limit |
| `No field data available for this URL` | URL has insufficient Chrome traffic | Normal for new/small pages; Lighthouse data is still shown |
| `ModuleNotFoundError: No module named 'googleapiclient'` | venv not activated | Run `source venv/bin/activate` (Mac) or `venv\Scripts\activate` (Windows) |
| `setup.ps1 cannot be loaded` | PowerShell execution policy | Run: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
