#!/usr/bin/env python3
"""
web_extractor.py
Author: Bibhudendu Behera
Description: Simple, reusable scraper + cleaner CLI for Web-Extractor-Pro.
Usage:
    python scripts/web_extractor.py --urls data/raw_urls.txt --output data/cleaned/quotes.csv
"""
import argparse
import logging
from pathlib import Path
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def read_urls(file_path: Path) -> List[str]:
    if not file_path.exists():
        logging.error(f"URLs file not found: {file_path}")
        return []
    return [line.strip() for line in file_path.read_text(encoding='utf-8').splitlines() if line.strip()]

def fetch_page(url: str, timeout: int = 10) -> requests.Response:
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "web-extractor-pro/1.0 (+https://github.com)"})
    resp.raise_for_status()
    return resp

def parse_quotes_page(html: str) -> List[Dict]:
    """Example parser for quotes.toscrape.com pages. Returns list of dicts."""
    soup = BeautifulSoup(html, "lxml")
    items = []
    for q in soup.select(".quote"):
        text = q.select_one(".text").get_text(strip=True) if q.select_one(".text") else None
        author = q.select_one(".author").get_text(strip=True) if q.select_one(".author") else None
        tags = [t.get_text(strip=True) for t in q.select(".tags .tag")]
        items.append({"text": text, "author": author, "tags": ",".join(tags)})
    return items

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply standard cleaning: trim, remove duplicates, parse dates if present."""
    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Strip whitespace for object columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Drop duplicates
    df = df.drop_duplicates().reset_index(drop=True)
    return df

def save_output(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logging.info(f"Saved cleaned CSV to: {output_path.resolve()}")

def run(urls_file: Path, output_file: Path) -> None:
    urls = read_urls(urls_file)
    if not urls:
        logging.error("No URLs to process. Exiting.")
        return

    all_items = []
    for url in urls:
        logging.info(f"Fetching: {url}")
        try:
            resp = fetch_page(url)
            # For this starter, we assume the pages are quote pages — parse accordingly
            items = parse_quotes_page(resp.text)
            all_items.extend(items)
        except Exception as e:
            logging.error(f"Failed to fetch or parse {url} — {e}")

    if not all_items:
        logging.error("No items extracted. Exiting.")
        return

    df = pd.DataFrame(all_items)
    df = clean_dataframe(df)
    save_output(df, output_file)

def cli():
    parser = argparse.ArgumentParser(description="Web-Extractor-Pro — scrape, clean, export")
    parser.add_argument("--urls", required=True, help="Path to file containing URLs (one per line)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    run(Path(args.urls), Path(args.output))

if __name__ == "__main__":
    cli()
