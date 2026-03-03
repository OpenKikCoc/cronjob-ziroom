#!/bin/sh

# Setup virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
. .venv/bin/activate

# Install dependencies
pip install -r ./core/requirements.txt

# Run crypto data scraper
python ./modules/crypto/scraper.py

echo "Crypto airdrop scraping completed"
