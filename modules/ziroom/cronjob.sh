#!/bin/sh

# Install dependencies
pip3 install -r ./core/requirements.txt

# Run ziroom data scraper
python3 ./modules/ziroom/scraper.py

echo "Ziroom data scraping completed"