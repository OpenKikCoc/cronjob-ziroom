# Ziroom Monitoring Module

## Function Overview
Monitor Ziroom rental listings for specific keywords, automatically detect changes and send email notifications.

## File Description
- `scraper.py`: Main Python scraping script
- `cronjob.sh`: Cron job execution script
- `data.html`: Output file (for email sending)

## Running Methods
```bash
# Run Python script directly
python3 ./modules/ziroom/scraper.py

# Or use cron job script
bash ./modules/ziroom/cronjob.sh
```

## Configuration Requirements
The following environment variables need to be set:
- `URI`: Target website URL
- `KEYWORD`: Search keyword

## Automated Execution
GitHub Actions will automatically run daily at 12:00 PM to check for rental listing changes.
