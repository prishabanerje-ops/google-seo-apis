# Step 1: Create a Google Cloud Project

**Goal:** Create the project container that holds your API keys and service accounts.

**Why:** Google APIs require a Cloud project. You won't be charged for Search Console
or PageSpeed Insights at normal usage volumes.

---

## 1.1 Go to Google Cloud Console

Open [https://console.cloud.google.com](https://console.cloud.google.com) in your browser.
Sign in with the Google account that owns your Search Console property.

> **Screenshot placeholder:** Google Cloud Console home page

## 1.2 Create a New Project

1. Click the project selector at the top of the page (it may say "Select a project")
2. Click **New Project** in the top-right of the dialog
3. Enter a project name, e.g. `seo-apis`
4. Click **Create**

> **Screenshot placeholder:** New Project dialog with name field

## 1.3 Note Your Project ID

After creation your project is selected automatically.
The project ID (e.g. `seo-apis-123456`) appears in the header.
You don't need to copy it now — it will appear in all API configuration screens.

## 1.4 Enable Billing (optional for these APIs)

PageSpeed Insights and Search Console are **free APIs** — billing is **not required**
to enable or use them. You can skip this step.

If Google prompts you to enable billing when activating an API (this does not happen
for PSI or GSC), you can add a billing account at that point. New accounts receive
$300 in free credits and you will not be charged for these two APIs.

---

## Verify

Your new project should be selected in the top header.

**Next step:** [Enable APIs →](02-enable-apis.md)
