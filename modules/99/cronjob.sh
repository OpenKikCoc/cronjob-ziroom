#!/bin/sh

# Install dependencies
pip3 install -r ./core/requirements.txt

# Run 99.com data scraper
python3 ./modules/99/scraper.py

echo "99.com data scraping completed"
