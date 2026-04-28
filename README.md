# Stock Research Snapshot Skill

## What the skill does
This skill generates a structured stock research snapshot from a stock price CSV file and an optional news headline CSV file. It calculates key financial metrics and outputs a Markdown report.

## Why I chose it
I chose this skill because stock analysis requires precise calculations from structured data. A language model alone may not reliably compute returns, volatility, or moving averages, so a Python script is necessary.

## How to use it
Run the script from the project root:

python .agents/skills/stock-research-snapshot/scripts/stock_snapshot.py \
--prices sample_data/prices.csv \
--news sample_data/news.csv

The script will generate a file called `stock_snapshot_report.md`.

## What the script does
The script reads CSV files, validates the required columns, computes metrics such as latest close price, total return, average daily return, volatility, moving average, highest and lowest close, and average volume. If a news CSV is provided, it also counts headlines and extracts common keywords.

## What worked well
The skill is narrow and reusable. The script handles the deterministic part of the workflow reliably, and the Markdown output is clear and structured.

## What limitations remain
The skill assumes clean CSV input, does not fetch live data, uses simple keyword extraction, and does not provide investment advice.

## Demo Video
https://www.youtube.com/watch?v=VpoOjsWfwmw