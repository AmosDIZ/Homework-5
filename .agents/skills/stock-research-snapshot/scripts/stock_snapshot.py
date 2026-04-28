import argparse
import csv
from collections import Counter
from datetime import datetime
import re
import statistics

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None


REQUIRED_PRICE_COLUMNS = {"date", "open", "high", "low", "close", "volume"}


def clean_keyword(text):
    return re.sub(r"[^a-zA-Z]", "", text).lower()


def is_na(value):
    if pd is not None:
        return pd.isna(value)
    return value is None


def analyze_prices(price_csv):
    if pd is None:
        return analyze_prices_without_pandas(price_csv)

    df = pd.read_csv(price_csv)

    missing = REQUIRED_PRICE_COLUMNS - set(df.columns.str.lower())
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df.columns = df.columns.str.lower()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    df["daily_return"] = df["close"].pct_change()

    latest_close = df["close"].iloc[-1]
    first_close = df["close"].iloc[0]
    total_return = (latest_close - first_close) / first_close
    avg_daily_return = df["daily_return"].mean()
    volatility = df["daily_return"].std()

    moving_avg_7 = None
    if len(df) >= 7:
        moving_avg_7 = df["close"].rolling(window=7).mean().iloc[-1]

    return {
        "start_date": df["date"].iloc[0].date(),
        "end_date": df["date"].iloc[-1].date(),
        "latest_close": latest_close,
        "total_return": total_return,
        "avg_daily_return": avg_daily_return,
        "volatility": volatility,
        "moving_avg_7": moving_avg_7,
        "highest_close": df["close"].max(),
        "lowest_close": df["close"].min(),
        "average_volume": df["volume"].mean(),
        "row_count": len(df),
    }


def analyze_prices_without_pandas(price_csv):
    with open(price_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("Price CSV is empty.")

    fieldnames = {name.lower() for name in (reader.fieldnames or [])}
    missing = REQUIRED_PRICE_COLUMNS - fieldnames
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    normalized_rows = []
    for row in rows:
        normalized_rows.append({
            "date": datetime.strptime(row["date"], "%Y-%m-%d").date(),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": float(row["volume"]),
        })

    normalized_rows.sort(key=lambda row: row["date"])
    closes = [row["close"] for row in normalized_rows]
    volumes = [row["volume"] for row in normalized_rows]

    daily_returns = []
    for idx in range(1, len(closes)):
        prev_close = closes[idx - 1]
        daily_returns.append((closes[idx] - prev_close) / prev_close)

    latest_close = closes[-1]
    first_close = closes[0]
    moving_avg_7 = statistics.mean(closes[-7:]) if len(closes) >= 7 else None

    return {
        "start_date": normalized_rows[0]["date"],
        "end_date": normalized_rows[-1]["date"],
        "latest_close": latest_close,
        "total_return": (latest_close - first_close) / first_close,
        "avg_daily_return": statistics.mean(daily_returns) if daily_returns else None,
        "volatility": statistics.stdev(daily_returns) if len(daily_returns) > 1 else None,
        "moving_avg_7": moving_avg_7,
        "highest_close": max(closes),
        "lowest_close": min(closes),
        "average_volume": statistics.mean(volumes),
        "row_count": len(normalized_rows),
    }


def analyze_news(news_csv):
    if pd is None:
        return analyze_news_without_pandas(news_csv)

    df = pd.read_csv(news_csv)

    if "headline" not in df.columns.str.lower():
        raise ValueError("News CSV must contain a headline column.")

    df.columns = df.columns.str.lower()

    stopwords = {
        "the", "a", "an", "and", "or", "to", "of", "in", "on", "for",
        "with", "as", "by", "from", "at", "is", "are", "was", "were",
        "stock", "stocks", "market", "markets"
    }

    words = []
    for headline in df["headline"].dropna():
        for word in str(headline).split():
            cleaned = clean_keyword(word)
            if cleaned and cleaned not in stopwords and len(cleaned) > 2:
                words.append(cleaned)

    common_keywords = Counter(words).most_common(10)

    return {
        "headline_count": len(df),
        "common_keywords": common_keywords,
    }


def analyze_news_without_pandas(news_csv):
    with open(news_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    fieldnames = {name.lower() for name in (reader.fieldnames or [])}
    if "headline" not in fieldnames:
        raise ValueError("News CSV must contain a headline column.")

    stopwords = {
        "the", "a", "an", "and", "or", "to", "of", "in", "on", "for",
        "with", "as", "by", "from", "at", "is", "are", "was", "were",
        "stock", "stocks", "market", "markets"
    }

    words = []
    for row in rows:
        headline = row.get("headline")
        if not headline:
            continue
        for word in str(headline).split():
            cleaned = clean_keyword(word)
            if cleaned and cleaned not in stopwords and len(cleaned) > 2:
                words.append(cleaned)

    return {
        "headline_count": len(rows),
        "common_keywords": Counter(words).most_common(10),
    }


def format_percent(value):
    if is_na(value):
        return "N/A"
    return f"{value * 100:.2f}%"


def generate_markdown_report(price_stats, news_stats=None):
    report = []

    report.append("# Stock Research Snapshot\n")

    report.append("## Summary")
    report.append(f"- Date range: {price_stats['start_date']} to {price_stats['end_date']}")
    report.append(f"- Rows analyzed: {price_stats['row_count']}")
    report.append(f"- Latest close price: ${price_stats['latest_close']:.2f}")
    report.append(f"- Total return: {format_percent(price_stats['total_return'])}")

    report.append("\n## Price Statistics")
    report.append(f"- Highest close: ${price_stats['highest_close']:.2f}")
    report.append(f"- Lowest close: ${price_stats['lowest_close']:.2f}")
    report.append(f"- Average volume: {price_stats['average_volume']:,.0f}")

    if price_stats["moving_avg_7"] is not None:
        report.append(f"- 7-day moving average: ${price_stats['moving_avg_7']:.2f}")
    else:
        report.append("- 7-day moving average: Not enough data")

    report.append("\n## Risk Metrics")
    report.append(f"- Average daily return: {format_percent(price_stats['avg_daily_return'])}")
    report.append(f"- Daily volatility: {format_percent(price_stats['volatility'])}")

    if news_stats:
        report.append("\n## News Insights")
        report.append(f"- Total headlines analyzed: {news_stats['headline_count']}")

        if news_stats["common_keywords"]:
            report.append("- Most common keywords:")
            for word, count in news_stats["common_keywords"]:
                report.append(f"  - {word}: {count}")
        else:
            report.append("- No meaningful keywords found.")

    report.append("\n## Important Note")
    report.append("This report is generated from provided CSV data only and is not financial advice.")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a deterministic stock research snapshot from CSV files."
    )

    parser.add_argument(
        "--prices",
        required=True,
        help="Path to stock price CSV file."
    )

    parser.add_argument(
        "--news",
        required=False,
        help="Optional path to news headline CSV file."
    )

    parser.add_argument(
        "--output",
        required=False,
        default="stock_snapshot_report.md",
        help="Output Markdown report path."
    )

    args = parser.parse_args()

    price_stats = analyze_prices(args.prices)

    news_stats = None
    if args.news:
        news_stats = analyze_news(args.news)

    report = generate_markdown_report(price_stats, news_stats)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()
