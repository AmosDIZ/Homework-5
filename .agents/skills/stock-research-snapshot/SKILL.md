---
name: stock-research-snapshot
description: Creates a deterministic stock research snapshot from stock price CSV data and optional news headline CSV data. Use when the user wants structured financial insights computed from raw data files.
---

## When to use this skill
- The user provides stock price CSV data
- The user wants a structured summary of stock performance
- The task requires precise numeric computation (returns, volatility, averages)
- The user includes news headlines and wants basic analysis

## When NOT to use this skill
- The user only wants general stock advice
- No structured data (CSV) is provided
- The request is purely opinion-based or speculative

## Expected inputs
- A stock price CSV file with columns:
  - date, open, high, low, close, volume
- (Optional) A news CSV file with columns:
  - date, headline

## Steps
1. Load the stock price CSV file
2. Validate required columns exist
3. Compute:
   - latest close price
   - total return over the dataset
   - average daily return
   - volatility (standard deviation of returns)
   - 7-day moving average (if enough data)
   - highest and lowest close price
   - average volume
4. If news CSV exists:
   - count total headlines
   - extract most common keywords
5. Call the Python script to perform all deterministic computations
6. Format results into a clean Markdown report

## Output format
The output should be a structured Markdown report:

- Summary section
- Price statistics
- Risk metrics
- News insights (if available)

## Limitations
- Assumes clean CSV format
- Does not fetch external data
- Does not provide investment advice
- Keyword extraction is simple frequency-based