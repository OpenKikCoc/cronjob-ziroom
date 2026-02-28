# RentMiro Data Scraper

This module monitors apartment availability on [RentMiro](https://www.rentmiro.com/floorplans).

## Functionality

1.  **Dynamic Scraping**: Automatically discovers the API endpoint used by the SightMap iframe.
2.  **Data Extraction**: Extracts unit details including unit number, floor plan, area, price, and availability date.
3.  **Change Detection**: Compares current data with previous run to detect:
    *   New listings
    *   Price changes
    *   Availability date changes
    *   Removed listings
4.  **Reporting**: Generates an HTML report (`data.html`) summarizing the current state and changes.

## Usage

Run the scraper manually:

```bash
./modules/rentmiro/cronjob.sh
```

## Output

*   `data.json`: Current state of available units.
*   `data.html`: HTML report for email notification.
