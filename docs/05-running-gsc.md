# Step 5: Run Google Search Console

**Goal:** Pull your top queries and pages with clicks, impressions, CTR, and position.

**Prerequisite:** OAuth Desktop App credentials configured —
see [docs/03-credentials.md Part B](03-credentials.md#part-b-oauth-desktop-app-for-google-search-console).

---

## 5.1 Activate the Virtual Environment

**Mac/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```powershell
venv\Scripts\activate
```

---

## 5.2 View Top Queries

```bash
python scripts/gsc.py --property sc-domain:yourdomain.com
```

**Example output:**
```
GSC Search Analytics — sc-domain:example.com
Last 30 days | Top 10 queries
──────────────────────────────────────────────────────────────────────
#   Query                                   Clicks  Impressions    CTR    Pos
──────────────────────────────────────────────────────────────────────
1   health insurance uae                      1240        18400   6.7%    3.2
2   buy health insurance online                830        12100   6.9%    2.8
3   cheap health insurance dubai               610         9800   6.2%    4.1
```

---

## 5.3 View Top Pages

```bash
python scripts/gsc.py --property sc-domain:yourdomain.com --dimension page
```

---

## 5.4 Change the Date Range

Default is last 30 days. For 90 days:

```bash
python scripts/gsc.py --property sc-domain:yourdomain.com --days 90
```

---

## 5.5 Export to CSV

```bash
python scripts/gsc.py --property sc-domain:yourdomain.com --csv queries.csv
```

Open `queries.csv` in Excel or Google Sheets to sort and filter.

---

## 5.6 Show More Results

```bash
python scripts/gsc.py --property sc-domain:yourdomain.com --top 25
```

---

**Next step:** [Advanced usage →](06-advanced.md)
