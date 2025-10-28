# Evidence Data Updates - Documentation

## Overview

The Evidence Explorer now supports **live data fetching** from PubMed and ClinicalTrials.gov APIs. This document explains how to keep your evidence data up to date.

## How It Works

### Data Flow

1. **Primary Source**: The app reads from `data/evidence_counts.csv` 
2. **Automatic Selection**: If multiple CSV files exist, the newest one is used
3. **Manual Refresh**: Users can click a button to fetch live data
4. **Cached Results**: Data is cached for 1 hour to improve performance

### No More Sample Data!

The app no longer falls back to hardcoded sample data. If no CSV file is found, users will see:
- A clear error message
- Instructions on how to load data
- A button to fetch live data from APIs

## Update Methods

### Method 1: Manual Button (In-App)

1. Go to the **Evidence Explorer** tab
2. If no data exists, click **"🔄 Refresh Evidence Data"**
3. Wait 5-10 minutes while ~320 API calls are made
4. Data is automatically saved to `data/evidence_counts.csv`

### Method 2: Python Script (Recommended for Updates)

Run the existing script to generate/update the data:

```bash
python scripts/build_evidence_counts.py
```

This will:
- Fetch data from ClinicalTrials.gov (HTML scraping)
- Fetch data from PubMed (API)
- Save results to `data/raw/evidence_counts.csv`

### Method 3: Weekly Automatic Updates (For Production)

A new script has been created for scheduled updates:

```bash
python scripts/update_evidence_weekly.py
```

#### Scheduling with Cron (Linux/Mac)

Add to your crontab (`crontab -e`):

```cron
# Update evidence data every Sunday at midnight
0 0 * * 0 cd /path/to/painreliefmap && python scripts/update_evidence_weekly.py >> logs/evidence_update.log 2>&1
```

#### Scheduling with Windows Task Scheduler

1. Open **Task Scheduler**
2. Click **"Create Basic Task"**
3. Name it "Update Evidence Data"
4. Set trigger to **Weekly** → Sunday → 12:00 AM
5. Set action to **Start a program**:
   - Program: `pythonw.exe`
   - Arguments: `scripts\update_evidence_weekly.py`
   - Start in: `C:\path\to\painreliefmap`

## Data Locations

The app searches for CSV files in this order:
1. `data/evidence_counts.csv` (primary)
2. `data/raw/evidence_counts.csv` (backup)
3. `evidence_counts.csv` (root directory)

**The newest file by modification date is automatically selected.**

## Performance Considerations

- **API Rate Limits**: 
  - PubMed allows 3 requests/second without an API key
  - The script includes a 0.5-0.8 second delay between requests
  - Full update takes ~5-10 minutes

- **Caching**:
  - App-level cache: 1 hour
  - Prevents repeated API calls during the same session
  - Cache is cleared when data is refreshed

## Troubleshooting

### No Data Available

If you see "No evidence data available":

1. **Check for CSV files**: Look in `data/`, `data/raw/`, or repo root
2. **Run the script**: Use `python scripts/build_evidence_counts.py`
3. **Use manual refresh**: Click the button in the app
4. **Check logs**: Look for error messages

### Old Data Showing

1. **Check modification date**: The app shows "Last updated: YYYY-MM-DD"
2. **Clear browser cache**: Hard refresh (Ctrl+F5 or Cmd+Shift+R)
3. **Wait for cache**: App cache lasts 1 hour
4. **Re-run script**: Generate a fresh CSV file

### API Errors

If APIs are down or rate-limited:

1. **Wait and retry**: Some APIs have temporary issues
2. **Reduce batch size**: Edit the script to fetch fewer combinations
3. **Use old data**: The app will use the last available CSV

## Recommendations

### For Development
- Run `build_evidence_counts.py` once to create initial data
- Use manual refresh button for testing

### For Production
- Schedule weekly updates using the automatic script
- Keep backup of previous CSV in case update fails
- Monitor update logs for errors

### For Streamlit Cloud
- Upload the CSV file to the repository
- The app will automatically use it
- Consider using GitHub Actions to auto-update weekly

## Future Enhancements

Possible improvements:
- Add API keys for higher rate limits
- Implement incremental updates (only changed combinations)
- Add health checks for API availability
- Store historical versions for trend analysis
- Add data validation and quality checks

