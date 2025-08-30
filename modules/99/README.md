# 99.com Data Scraping Module

## Function Overview
Automatically scrape game leaderboard data from https://hd.99.com/jz/qxhd/ page, including four fields: number, fwq, player, hkzs.

## File Description
- `scraper.py`: Python scraping script (enhanced version)
- `cronjob.sh`: Cron job execution script
- `data.json`: JSON format raw data
- `data.html`: HTML format data display (for email sending)

## Running Methods
```bash
# Run scraper
python3 ./modules/99/scraper.py

# Or use cron job script
bash ./modules/99/cronjob.sh
```

## Data Field Description
- `number`: Ranking number
- `fwq`: Server name
- `player`: Player name
- `hkzs`: Guild/Clan information

## Automated Execution
GitHub Actions will automatically run every 6 hours to check for data changes and send email notifications.
