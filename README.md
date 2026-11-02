# StockIQ

Live stock dashboard built with Streamlit. Type a ticker and get technicals (RSI, MACD, moving averages, Bollinger Bands, volume), fundamentals, recent news, a 3-month trend projection, and an AI bull/bear verdict from Claude. There's also a watchlist and a trade journal.

**Not financial advice.** The 3-month projection is a weighted linear trend line. The app backtests that same method on about 5 years of each stock's history and shows the hit rate next to a naive baseline, so you can judge how much to trust it.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app_2_1.py
```
For the AI verdict, add `ANTHROPIC_KEY = "..."` to `.streamlit/secrets.toml` (git-ignored) or set it in Streamlit Cloud's app secrets. Without a key, the app still works and shows a simple signal tally instead.

## Keeping the hosted app awake
`.github/workflows/keep-awake.yml` opens the Streamlit Cloud app in a headless browser every 6 hours.
