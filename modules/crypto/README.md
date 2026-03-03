# Crypto Airdrop Monitor

This module monitors the web for cryptocurrency airdrops specifically targeting GitHub developers.

## How it works

1.  **Search**: It uses DuckDuckGo to search for keywords like "github developer airdrop", "claim airdrop github".
2.  **Scrape**: 
    *   **Airdrops.io**: Scrapes the latest airdrops and searches for "github"/"developer" keywords.
    *   **DefiLlama**: Fetches the list of claimable airdrops.
3.  **Strict Filter**: It strictly filters all results to only include those that mention developer-related keywords (e.g., `github`, `developer`, `testnet`, `node`, `contract`, `hackathon`). **General airdrops are excluded.**
4.  **Report**: Generates a JSON data file and an HTML report.

## Files

-   `scraper.py`: The main Python script.
-   `cronjob.sh`: Shell script to setup environment and run the scraper.
-   `data.json`: The latest scraped data.
-   `data.html`: The HTML report.

## Usage

Run the cronjob script:

```bash
sh modules/crypto/cronjob.sh
```

## Schedule

The GitHub Workflow runs every hour to ensure timely updates.
