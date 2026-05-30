"""
Example: call the Google Finance API Apify Actor from Python.

Fetches a real-time quote, price history, and (when available) market data,
financials, and news for a symbol. Symbols use Google Finance format, the
ticker plus exchange, e.g. "GOOGL:NASDAQ", "AAPL:NASDAQ", "BTC-USD",
"EUR-USD", ".DJI:INDEXDJX". Plain names like "Google" do not resolve.

This example fetches one symbol to keep the first run inexpensive (each symbol
fetched is billed). Pass a list via "queries" to look up several at once.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3
Set it in a .env file (see .env.example) or export APIFY_API_TOKEN.
"""

import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
if not APIFY_API_TOKEN:
    raise SystemExit(
        "APIFY_API_TOKEN is not set. Copy .env.example to .env and add your key, "
        "or run: export APIFY_API_TOKEN=your_api_key_here"
    )

client = ApifyClient(APIFY_API_TOKEN)

run_input = {
    "q": "GOOGL:NASDAQ",   # ticker:exchange format; or use "queries": ["AAPL:NASDAQ", "BTC-USD"]
    "window": "1D",        # 1D, 5D, 1M, 6M, YTD, 1Y, 5Y, MAX
}

print(f"Fetching Google Finance quote for: {run_input['q']}")
run = client.actor("johnvc/google-finance-api").call(run_input=run_input)
if run is None:
    raise SystemExit("The Actor run did not start. Check your API token and inputs.")

for item in client.dataset(run.default_dataset_id).iterate_items():
    summary = item.get("summary") or {}
    movement = summary.get("price_movement") or {}
    pct = movement.get("percentage")
    pct_str = f"{pct:.2f}%" if isinstance(pct, (int, float)) else "n/a"

    print(f"\n{summary.get('title')} ({summary.get('stock')}:{summary.get('exchange')})")
    print(f"  Price:    {summary.get('price')}")
    print(f"  Movement: {movement.get('movement')} {pct_str}")
    print(f"  As of:    {summary.get('date')}")

    graph = item.get("graph") or []
    print(f"  Price-history points ({run_input['window']}): {len(graph)}")

    news = item.get("news_results") or []
    if news:
        print(f"  News articles attached: {len(news)}")
    if item.get("financials"):
        print("  Financials block present.")
