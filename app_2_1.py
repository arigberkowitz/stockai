import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="StockIQ", page_icon="⚡", layout="wide")

WATCHLIST_FILE = "watchlist.json"
TRADES_FILE    = "trades.json"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
.stApp { background: #0d0b1a; }
[data-testid="stSidebar"] { background: #17132b !important; border-right: 1px solid #221c3a; }
.hero { border-bottom: 1px solid #221c3a; padding: 30px 4px 24px 4px; margin-bottom: 26px; }
.hero h1 { font-size: 2.2rem; font-weight: 800; color: #f5f3ff; margin: 0; letter-spacing: -1px; }
.hero p  { color: #a29db8; font-size: 0.95rem; margin: 8px 0 0 0; max-width: 600px; line-height: 1.55; }
.metric-card { background: #17132b; border: 1px solid #221c3a; border-radius: 10px; padding: 18px 20px; text-align: center; }
.metric-label { color: #a29db8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.metric-value { color: #f5f3ff; font-size: 1.95rem; font-weight: 800; line-height: 1; }
.metric-value.green { color: #34d27b; }
.metric-value.red   { color: #f0584a; }
.section-title { color: #f5f3ff; font-size: 0.95rem; font-weight: 700; margin: 22px 0 12px 0; text-transform: uppercase; letter-spacing: 0.6px; border-left: 3px solid #8b5cf6; border-radius: 0; padding-left: 11px; }
.signal-pill { display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; margin: 3px 3px 3px 0; }
.pill-green  { background: rgba(52,210,123,0.12); color: #34d27b; border: 1px solid rgba(52,210,123,0.35); }
.pill-red    { background: rgba(240,88,74,0.12); color: #f0584a; border: 1px solid rgba(240,88,74,0.35); }
.pill-yellow { background: rgba(240,180,41,0.12); color: #f0b429; border: 1px solid rgba(240,180,41,0.35); }
.summary-box { background: #17132b; border: 1px solid #221c3a; border-left: 3px solid #8b5cf6; border-radius: 8px; padding: 16px 20px; color: #d8d2ee; font-size: 0.88rem; line-height: 1.65; margin-top: 16px; }
.fund-card { background: #17132b; border: 1px solid #221c3a; border-radius: 10px; padding: 14px 18px; margin-bottom: 8px; }
.fund-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #221c3a; }
.fund-row:last-child { border-bottom: none; }
.fund-key { color: #a29db8; font-size: 0.82rem; }
.fund-val { color: #f5f3ff; font-size: 0.88rem; font-weight: 600; }
.fund-val.green { color: #34d27b; }
.fund-val.red   { color: #f0584a; }
.news-item { background: #17132b; border: 1px solid #221c3a; border-radius: 8px; padding: 12px 16px; margin-bottom: 6px; }
.news-title { color: #d8d2ee; font-size: 0.88rem; font-weight: 600; }
.news-meta  { color: #a29db8; font-size: 0.78rem; margin-top: 3px; }
.ticker-card { background: #17132b; border: 1px solid #221c3a; border-radius: 8px; padding: 14px 16px; margin-bottom: 6px; }
.ticker-card:hover { border-color: #8b5cf6; }
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
.stTextInput input, .stNumberInput input { background: #0d0b1a !important; border: 1px solid #2a2440 !important; color: #f5f3ff !important; border-radius: 6px !important; }
.stButton > button { background: #221c3a !important; color: #f5f3ff !important; border: 1px solid #2a2440 !important; border-radius: 6px !important; font-weight: 600 !important; }
.stButton > button:hover { border-color: #8b5cf6 !important; color: #8b5cf6 !important; background: #1f1937 !important; }
.stTabs [data-baseweb="tab-list"] { background: #17132b; border: 1px solid #221c3a; border-radius: 8px; padding: 4px 8px; gap: 10px; }
.stTabs [data-baseweb="tab"] { border-radius: 6px !important; color: #a29db8 !important; font-weight: 600 !important; padding: 6px 18px !important; }
.stTabs [aria-selected="true"] { background: #241d3e !important; color: #f5f3ff !important; box-shadow: inset 0 -2px 0 #8b5cf6; }
hr { border-color: #221c3a !important; }
.stCaption, small { color: #a29db8 !important; }
.streamlit-expanderHeader { background: #17132b !important; border-radius: 6px !important; color: #f5f3ff !important; font-weight: 600 !important; }
.stRadio > div { flex-direction: row !important; gap: 4px; }
.stRadio label { background: #17132b; border: 1px solid #221c3a; border-radius: 6px; padding: 4px 14px !important; font-size: 0.82rem !important; color: #a29db8 !important; cursor: pointer; }
.stRadio label:has(input:checked) { border-color: #8b5cf6 !important; color: #8b5cf6 !important; }
.verdict-row { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
@media (max-width: 640px) {
  .hero { padding: 8px 2px 16px 2px; margin-bottom: 16px; }
  .hero h1 { font-size: 1.7rem; }
  .metric-card { padding: 12px 10px; }
  .metric-value { font-size: 1.45rem; }
  .verdict-row { flex-direction: column; align-items: stretch; }
  .stTabs [data-baseweb="tab"] { padding: 6px 10px !important; }
  [data-testid="stHorizontalBlock"]:has(.metric-card) { flex-wrap: wrap !important; gap: 8px !important; }
  [data-testid="stHorizontalBlock"]:has(.metric-card) > [data-testid="stColumn"] { flex: 1 1 calc(50% - 8px) !important; min-width: calc(50% - 8px) !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Persistence ───────────────────────────────────────────────────────────────
def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ── Session state ─────────────────────────────────────────────────────────────
# On Streamlit Cloud every visitor shares one server, so a JSON file on disk would
# let strangers see/edit each other's watchlists and trades (and it is wiped on every
# reboot anyway). Locally (no PERSIST=0) the files still work as before.
PERSIST = os.environ.get("STOCKIQ_PERSIST", "1") == "1" and not os.environ.get("STREAMLIT_SHARING_MODE") \
          and not os.path.exists("/mount/src")
def save_json(path, data):  # noqa: F811 (overrides the version above)
    if PERSIST:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_json(WATCHLIST_FILE, ["AAPL", "TSLA", "NVDA", "SPY"]) if PERSIST \
                                 else ["AAPL", "TSLA", "NVDA", "SPY"]
if "trades" not in st.session_state:
    st.session_state.trades = load_json(TRADES_FILE, []) if PERSIST else []

def get_secret(name):
    """Read a Streamlit secret without crashing when no secrets file exists."""
    try:
        return st.secrets.get(name, "") or os.environ.get(name, "")
    except Exception:
        return os.environ.get(name, "")

ANTHROPIC_KEY = get_secret("ANTHROPIC_KEY")
AI_MODEL = "claude-haiku-4-5-20251001"

def is_valid_ticker_text(t):
    import re
    return bool(re.fullmatch(r"[A-Z0-9.\-^=]{1,12}", t or ""))

# ── Data fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def fetch_quotes(tickers):
    rows = []
    for t in tickers:
        try:
            tk   = yf.Ticker(t)
            info = tk.fast_info
            prev  = info.previous_close or 0
            price = info.last_price or 0
            chg   = price - prev
            pct   = (chg / prev * 100) if prev else 0
            vol   = info.three_month_average_volume or 0
            yr_hi = getattr(info, "year_high", 0) or 0
            yr_lo = getattr(info, "year_low",  0) or 0
            rows.append({
                "Ticker":     t.upper(),
                "Price":      round(price, 2),
                "Change":     round(chg,   2),
                "% Change":   round(pct,   2),
                "Vol 3M (M)": round(vol / 1_000_000, 2),
                "52W High":   round(yr_hi, 2),
                "52W Low":    round(yr_lo, 2),
            })
        except Exception:
            rows.append({"Ticker": t.upper(), "Price": 0, "Change": 0,
                         "% Change": 0, "Vol 3M (M)": 0,
                         "52W High": 0, "52W Low": 0})
    return pd.DataFrame(rows)

@st.cache_data(ttl=3600)
def fetch_history(ticker, period="6mo"):
    try:
        df = yf.Ticker(ticker).history(period=period)
    except Exception:
        return pd.DataFrame()
    if df is None or df.empty:
        return pd.DataFrame()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df

@st.cache_data(ttl=300)
def fetch_last_price(ticker):
    try:
        return float(yf.Ticker(ticker).fast_info.last_price or 0)
    except Exception:
        return 0.0

@st.cache_data(ttl=3600)
def fetch_fundamentals(ticker):
    try:
        tk   = yf.Ticker(ticker)
        info = tk.info
        def fmt_large(n):
            if not n or not isinstance(n, (int, float)): return "N/A"
            if abs(n) >= 1e9: return f"${n/1e9:.1f}B"
            if abs(n) >= 1e6: return f"${n/1e6:.1f}M"
            return f"${n:,.0f}"
        def fmt_pct(n):
            if not n or not isinstance(n, (int, float)): return "N/A"
            return f"{n*100:.1f}%"
        pe  = info.get("trailingPE"); fpe = info.get("forwardPE")
        eps = info.get("trailingEps"); rev = info.get("totalRevenue")
        rev_g = info.get("revenueGrowth"); fcf = info.get("freeCashflow")
        de    = info.get("debtToEquity"); mkt = info.get("marketCap")
        sector   = info.get("sector",   "N/A")
        industry = info.get("industry", "N/A")
        rec    = (info.get("recommendationKey") or "N/A").upper()
        target = info.get("targetMeanPrice")
        analysts = info.get("numberOfAnalystOpinions", 0)
        div_y = info.get("dividendYield"); beta = info.get("beta")
        return {
            "P/E (Trailing)":  f"{pe:.1f}x"      if pe     else "N/A",
            "P/E (Forward)":   f"{fpe:.1f}x"     if fpe    else "N/A",
            "EPS (TTM)":       f"${eps:.2f}"      if eps    else "N/A",
            "Revenue":         fmt_large(rev),
            "Revenue Growth":  fmt_pct(rev_g),
            "Free Cash Flow":  fmt_large(fcf),
            "Debt/Equity":     f"{de:.1f}"        if de     else "N/A",
            "Market Cap":      fmt_large(mkt),
            "Sector":          sector,
            "Industry":        industry,
            "Analyst Rating":  rec,
            "Price Target":    f"${target:.2f}"   if target else "N/A",
            "# Analysts":      str(analysts),
            "Dividend Yield":  fmt_pct(div_y)     if div_y  else "None",
            "Beta":            f"{beta:.2f}"      if beta   else "N/A",
            "_raw": {
                "pe": pe, "fpe": fpe, "eps": eps, "rev_g": rev_g,
                "fcf": fcf, "de": de, "rec": rec, "target": target,
                "beta": beta, "sector": sector, "mkt": mkt,
            }
        }
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=1800)
def fetch_news(ticker):
    try:
        url  = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(url, timeout=10)
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:6]
        news  = []
        for item in items:
            title = item.findtext("title", "")
            pub   = item.findtext("pubDate", "")
            link  = item.findtext("link",    "")
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title, source = parts[0], parts[1]
            else:
                source = ""
            news.append({"title": title, "pub": pub[:22], "source": source, "link": link})
        return news
    except Exception:
        return []

# ── Chart helpers ─────────────────────────────────────────────────────────────
_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#17132b",
    font=dict(color="#a29db8", size=11),
    xaxis_rangeslider_visible=False,
    margin=dict(l=0, r=0, t=30, b=0),
)

def _apply_style(fig, height=360, legend=False):
    fig.update_layout(
        **_CHART_LAYOUT,
        height=height,
        showlegend=legend,
        legend=dict(
            orientation="h", y=1.08, x=0,
            bgcolor="rgba(0,0,0,0)", font=dict(size=10),
        ) if legend else {},
    )
    fig.update_xaxes(gridcolor="#221c3a", showgrid=True, zeroline=False)
    fig.update_yaxes(gridcolor="#221c3a", showgrid=True, zeroline=False)

def make_ohlcv_chart(df, ticker):
    """Candlestick + volume bars."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02, row_heights=[0.72, 0.28])
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        name=ticker,
        increasing=dict(line=dict(color="#34d27b"), fillcolor="#34d27b"),
        decreasing=dict(line=dict(color="#f0584a"), fillcolor="#f0584a"),
    ), row=1, col=1)
    vol_colors = ["#34d27b" if c >= o else "#f0584a"
                  for o, c in zip(df["Open"], df["Close"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        name="Volume", marker_color=vol_colors, opacity=0.65,
    ), row=2, col=1)
    _apply_style(fig, height=380)
    fig.update_yaxes(title_text="Volume", row=2, col=1,
                     title_font=dict(size=10), tickfont=dict(size=9))
    return fig

def make_analysis_chart(result):
    """Candlestick + MAs + Bollinger Bands + projection + volume."""
    hist = result["hist"]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02, row_heights=[0.72, 0.28])

    # Bollinger Band fill
    bb_x = hist.index.tolist() + hist.index.tolist()[::-1]
    bb_y = (hist["BB_upper"].ffill().tolist() +
            hist["BB_lower"].ffill().tolist()[::-1])
    fig.add_trace(go.Scatter(
        x=bb_x, y=bb_y, fill="toself",
        fillcolor="rgba(139,92,246,0.10)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Bollinger Bands", showlegend=True,
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=hist.index, y=hist["MA50"],
        name="MA50", line=dict(color="#f0b429", width=1.4),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist["MA200"],
        name="MA200", line=dict(color="#8b5cf6", width=1.4),
    ), row=1, col=1)

    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"], high=hist["High"],
        low=hist["Low"],   close=hist["Close"],
        name="Price",
        increasing=dict(line=dict(color="#34d27b"), fillcolor="#34d27b"),
        decreasing=dict(line=dict(color="#f0584a"), fillcolor="#f0584a"),
    ), row=1, col=1)

    # 3-month projection (dashed purple)
    proj_x = [hist.index[-1]] + result["future_dates"].tolist()
    proj_y = [hist["Close"].iloc[-1]] + result["future_series"].tolist()
    fig.add_trace(go.Scatter(
        x=proj_x, y=proj_y,
        name="3M Projection",
        line=dict(color="#22d3ee", dash="dash", width=2),
    ), row=1, col=1)

    # Volume bars
    vol_colors = ["#34d27b" if c >= o else "#f0584a"
                  for o, c in zip(hist["Open"], hist["Close"])]
    fig.add_trace(go.Bar(
        x=hist.index, y=hist["Volume"],
        name="Volume", marker_color=vol_colors, opacity=0.65,
    ), row=2, col=1)

    _apply_style(fig, height=430, legend=True)
    fig.update_yaxes(title_text="Volume", row=2, col=1,
                     title_font=dict(size=10), tickfont=dict(size=9))
    return fig

def make_rsi_chart(rsi_series):
    fig = go.Figure()
    # Shaded zones
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(240,88,74,0.08)",  line_width=0)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(52,210,123,0.08)",  line_width=0)
    fig.add_hline(y=70, line=dict(color="#f0584a", dash="dot", width=1))
    fig.add_hline(y=30, line=dict(color="#34d27b", dash="dot", width=1))
    fig.add_hline(y=50, line=dict(color="#a29db8", dash="dot", width=0.7))
    fig.add_trace(go.Scatter(
        x=rsi_series.index, y=rsi_series.values,
        name="RSI", line=dict(color="#8b5cf6", width=1.8),
    ))
    fig.update_layout(yaxis=dict(range=[0, 100]))
    _apply_style(fig, height=210)
    return fig

def make_macd_chart(hist):
    macd_df = hist[["MACD", "MACD_signal", "MACD_hist"]].dropna()
    fig = go.Figure()
    hist_colors = ["#34d27b" if v >= 0 else "#f0584a" for v in macd_df["MACD_hist"]]
    fig.add_trace(go.Bar(
        x=macd_df.index, y=macd_df["MACD_hist"],
        name="Histogram", marker_color=hist_colors, opacity=0.75,
    ))
    fig.add_trace(go.Scatter(
        x=macd_df.index, y=macd_df["MACD"],
        name="MACD", line=dict(color="#8b5cf6", width=1.8),
    ))
    fig.add_trace(go.Scatter(
        x=macd_df.index, y=macd_df["MACD_signal"],
        name="Signal", line=dict(color="#f0b429", width=1.8),
    ))
    _apply_style(fig, height=210, legend=True)
    return fig

def make_pnl_chart(trades_df):
    """Cumulative realized P&L equity curve."""
    closed = trades_df[trades_df["status"] == "Closed"].copy()
    if closed.empty or "P&L ($)" not in closed.columns:
        return None
    closed = closed.dropna(subset=["P&L ($)"]).sort_values("date")
    if closed.empty:
        return None
    closed["Cumulative P&L"] = closed["P&L ($)"].cumsum()
    final = closed["Cumulative P&L"].iloc[-1]
    fill_color = "rgba(52,210,123,0.14)" if final >= 0 else "rgba(240,88,74,0.14)"
    line_color  = "#34d27b"             if final >= 0 else "#f0584a"

    fig = go.Figure()
    fig.add_hline(y=0, line=dict(color="#a29db8", dash="dot", width=1))
    fig.add_trace(go.Scatter(
        x=closed["date"], y=closed["Cumulative P&L"],
        name="Cumulative P&L",
        line=dict(color=line_color, width=2),
        fill="tozeroy", fillcolor=fill_color,
        hovertemplate="$%{y:,.2f}<extra></extra>",
    ))
    _apply_style(fig, height=200)
    return fig

# ── Technical analysis ────────────────────────────────────────────────────────
def _trend_line(values, horizon):
    """Exponentially weighted linear fit (recent days count more), projected `horizon` days out."""
    x = np.arange(len(values))
    weights = np.exp(np.linspace(0, 1, len(values)))
    coeffs = np.polyfit(x, values, 1, w=weights)
    return coeffs, coeffs[0] * (len(values) - 1 + horizon) + coeffs[1]

@st.cache_data(ttl=3600)
def backtest_trend(ticker, window=252, horizon=63, step=21):
    """Walk-forward test of the exact same projection method on ~5 years of history:
    every month, fit on the prior year only, call the 3-month direction, then check
    what actually happened. No look-ahead."""
    full = fetch_history(ticker, "5y")
    if full.empty or len(full) < window + horizon + step * 6:
        return None
    c = full["Close"].values
    calls = []
    for i in range(window, len(c) - horizon, step):
        _, proj = _trend_line(c[i - window:i], horizon)
        now, later = c[i - 1], c[i - 1 + horizon]
        calls.append((proj > now, later > now, (proj - now) / now, (later - now) / now))
    if not calls:
        return None
    pred_up = np.array([x[0] for x in calls]); act_up = np.array([x[1] for x in calls])
    pred_pct = np.array([x[2] for x in calls]); act_pct = np.array([x[3] for x in calls])
    return {
        "n": len(calls),
        "hit_rate": float((pred_up == act_up).mean() * 100),
        "always_up": float(act_up.mean() * 100),   # naive baseline: "it always goes up"
        "mae": float(np.abs(pred_pct - act_pct).mean() * 100),
        "start": full.index[window].strftime("%b %Y"),
    }

def run_prediction(ticker):
    full = fetch_history(ticker, "2y")     # 2y so MA200 is filled on the visible year
    if full.empty or len(full) < 60:
        return None
    closes_full = full["Close"].copy()
    full["MA50"]  = closes_full.rolling(50).mean()
    full["MA200"] = closes_full.rolling(200).mean()
    hist = full.iloc[-252:].copy()         # show / fit the last 12 months, like before
    closes = hist["Close"].copy()
    delta = closes.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    hist["RSI"]      = 100 - (100 / (1 + rs))
    hist["BB_mid"]   = closes.rolling(20).mean()
    hist["BB_upper"] = hist["BB_mid"] + 2 * closes.rolling(20).std()
    hist["BB_lower"] = hist["BB_mid"] - 2 * closes.rolling(20).std()
    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    hist["MACD"]        = ema12 - ema26
    hist["MACD_signal"] = hist["MACD"].ewm(span=9, adjust=False).mean()
    hist["MACD_hist"]   = hist["MACD"] - hist["MACD_signal"]

    future_days = 63
    coeffs, _ = _trend_line(closes.values, future_days)
    slope, _ = coeffs
    x_future    = np.arange(len(closes), len(closes) + future_days)
    y_future    = coeffs[0] * x_future + coeffs[1]
    last_date    = hist.index[-1]
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=future_days, freq="B")
    future_series = pd.Series(y_future, index=future_dates)

    current_price   = closes.iloc[-1]
    projected_price = future_series.iloc[-1]
    trend_pct = ((projected_price - current_price) / current_price) * 100

    # Typical 3-month range: ±1 standard deviation of daily moves, scaled to 63 days
    daily_sigma = np.log(closes).diff().dropna().std()
    sigma_3m    = float(daily_sigma * np.sqrt(future_days))
    range_low   = float(projected_price * np.exp(-sigma_3m))
    range_high  = float(projected_price * np.exp(sigma_3m))

    rsi_val   = hist["RSI"].iloc[-1]
    ma50_val  = hist["MA50"].iloc[-1]
    ma200_val = hist["MA200"].iloc[-1]
    bb_upper  = hist["BB_upper"].iloc[-1]
    bb_lower  = hist["BB_lower"].iloc[-1]
    macd_val  = hist["MACD"].iloc[-1]
    macd_sig  = hist["MACD_signal"].iloc[-1]

    signals = []
    if pd.isna(ma200_val) or pd.isna(ma50_val):
        signals.append(("yellow", "🟡 MA200 n/a",     "Less than 200 days of history"))
    elif ma50_val > ma200_val:
        signals.append(("green",  "🟢 Golden Cross",  "MA50 above MA200 — bullish trend"))
    else:
        signals.append(("red",    "🔴 Death Cross",   "MA50 below MA200 — bearish trend"))
    if rsi_val < 30:
        signals.append(("green",  "🟢 Oversold",      f"RSI {rsi_val:.1f} — potential bounce"))
    elif rsi_val > 70:
        signals.append(("red",    "🔴 Overbought",    f"RSI {rsi_val:.1f} — potential pullback"))
    else:
        signals.append(("yellow", "🟡 Neutral RSI",   f"RSI {rsi_val:.1f} — no extreme"))
    if current_price < bb_lower:
        signals.append(("green",  "🟢 Below BB Lower","Statistically cheap vs recent range"))
    elif current_price > bb_upper:
        signals.append(("red",    "🔴 Above BB Upper","Statistically stretched vs recent range"))
    else:
        signals.append(("yellow", "🟡 Inside BB Bands","Price within normal range"))
    if macd_val > macd_sig:
        signals.append(("green",  "🟢 MACD Bullish",  f"MACD ({macd_val:.2f}) above signal ({macd_sig:.2f})"))
    else:
        signals.append(("red",    "🔴 MACD Bearish",  f"MACD ({macd_val:.2f}) below signal ({macd_sig:.2f})"))
    recent_vol = hist["Volume"].iloc[-5:].mean()
    avg_vol    = hist["Volume"].iloc[-30:].mean()
    if recent_vol > avg_vol * 1.3:
        signals.append(("green",  "🟢 Volume Surge",  f"Recent vol {recent_vol/1e6:.1f}M vs 30d avg {avg_vol/1e6:.1f}M"))
    elif recent_vol < avg_vol * 0.7:
        signals.append(("yellow", "🟡 Low Volume",    "Below-average volume — weak conviction"))
    else:
        signals.append(("yellow", "🟡 Normal Volume", "Volume in line with recent average"))

    return {
        "hist": hist, "future_dates": future_dates, "future_series": future_series,
        "signals": signals, "rsi": rsi_val, "ma50": ma50_val, "ma200": ma200_val,
        "bb_upper": bb_upper, "bb_lower": bb_lower,
        "macd": macd_val, "macd_signal": macd_sig,
        "current_price": current_price, "projected_price": projected_price,
        "trend_pct": trend_pct, "slope": slope,
        "recent_vol": recent_vol, "avg_vol": avg_vol,
        "range_low": range_low, "range_high": range_high, "sigma_3m": sigma_3m * 100,
        "as_of": hist.index[-1].strftime("%b %d, %Y"),
    }

# ── AI helpers ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def call_claude(prompt, max_tokens):
    """One cached Claude call; same prompt within an hour costs nothing extra."""
    if not ANTHROPIC_KEY:
        return None
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json",
                     "x-api-key": ANTHROPIC_KEY,
                     "anthropic-version": "2023-06-01"},
            json={"model": AI_MODEL, "max_tokens": max_tokens,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
        if r.status_code != 200:
            return None
        return r.json()["content"][0]["text"]
    except Exception:
        return None

def run_ai_analysis(ticker, tech_result, fundamentals, news, bt=None):
    try:
        if not ANTHROPIC_KEY:
            return None
        signals_text = "\n".join([f"- {label}: {desc}" for _, label, desc in tech_result["signals"]])
        news_text    = "\n".join([f"- {n['title']} ({n['source']})" for n in news[:5]]) if news else "No recent news found."
        fund_text    = "".join([f"- {k}: {v}\n" for k, v in fundamentals.items() if k != "_raw"])
        bt_text      = (f"called the 3-month direction right {bt['hit_rate']:.0f}% of the time over {bt['n']} monthly tests "
                        f"(the stock simply rose in {bt['always_up']:.0f}% of those windows)") if bt else "not available"
        prompt = f"""You are a professional equity analyst. Analyze {ticker} and give a clear investment verdict.

TECHNICAL SIGNALS:
{signals_text}

3-Month Price Projection: {tech_result['trend_pct']:+.1f}% (linear regression trend)
Current Price: ${tech_result['current_price']:.2f}
Typical 3-month range (±1σ): ${tech_result['range_low']:.2f} – ${tech_result['range_high']:.2f}
Backtest of this trend method on this stock: {bt_text}
RSI: {tech_result['rsi']:.1f}

FUNDAMENTAL DATA:
{fund_text}

RECENT NEWS HEADLINES:
{news_text}

Based on ALL of the above, provide:
VERDICT: [BUY/HOLD/SELL]
CONFIDENCE: [High/Medium/Low]
SUMMARY: [3-4 sentences]
BULLS:
- [point]
- [point]
- [point]
BEARS:
- [point]
- [point]
- [point]
CATALYSTS:
- [point]
- [point]

Weigh the backtest honestly: if the trend method is no better than the baseline, say so and lean on fundamentals and news instead."""
        return call_claude(prompt, 1000)
    except Exception:
        return None

def parse_ai_response(text):
    result = {}
    lines  = text.strip().split("\n")
    current_section = None
    for line in lines:
        line = line.strip()
        line = line.replace("**", "")
        if line.startswith("VERDICT:"):
            v = line.replace("VERDICT:", "").strip().upper()
            result["verdict"] = next((x for x in ("BUY", "HOLD", "SELL") if x in v), "HOLD")
        elif line.startswith("CONFIDENCE:"):
            result["confidence"] = line.replace("CONFIDENCE:", "").strip()
        elif line.startswith("SUMMARY:"):
            result["summary"] = line.replace("SUMMARY:", "").strip()
            current_section = "summary"
        elif line == "BULLS:":
            current_section = "bulls";  result["bulls"] = []
        elif line == "BEARS:":
            current_section = "bears";  result["bears"] = []
        elif line == "CATALYSTS:":
            current_section = "catalysts"; result["catalysts"] = []
        elif line[:2] in ("- ", "• ", "* ") and current_section in ("bulls", "bears", "catalysts"):
            result.setdefault(current_section, []).append(line[2:])
        elif current_section == "summary" and line and not any(
            line.startswith(s) for s in ["BULLS:", "BEARS:", "CATALYSTS:", "VERDICT:", "CONFIDENCE:"]):
            result["summary"] = result.get("summary", "") + " " + line
    return result

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 0 10px 0;'>
      <span style='font-size:2rem;color:#8b5cf6;'>⚡</span>
      <span style='color:white;font-size:1.4rem;font-weight:800;margin-left:8px;'>StockIQ</span>
      <div style='color:rgba(255,255,255,0.4);font-size:0.8rem;margin-top:4px;'>Your trading dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='color:rgba(255,255,255,0.7);font-weight:600;margin-bottom:8px;'>➕ Add Ticker</div>", unsafe_allow_html=True)
    new_ticker = st.text_input("Add ticker", placeholder="e.g. MSFT", label_visibility="collapsed").strip().upper()
    if st.button("Add to Watchlist", use_container_width=True):
        if new_ticker and not is_valid_ticker_text(new_ticker):
            st.error("That doesn't look like a ticker.")
        elif new_ticker and fetch_history(new_ticker, "5d").empty:
            st.error(f"Couldn't find {new_ticker} on Yahoo Finance.")
        elif new_ticker and new_ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_ticker)
            save_json(WATCHLIST_FILE, st.session_state.watchlist)
            fetch_quotes.clear()
            st.success(f"✅ {new_ticker} added!")
        elif new_ticker in st.session_state.watchlist:
            st.warning("Already on watchlist.")
    st.divider()
    st.markdown("<div style='color:rgba(255,255,255,0.7);font-weight:600;margin-bottom:8px;'>🗑️ Remove Ticker</div>", unsafe_allow_html=True)
    if st.session_state.watchlist:
        to_remove = st.selectbox("Remove ticker", st.session_state.watchlist, label_visibility="collapsed")
        if st.button("Remove", use_container_width=True):
            st.session_state.watchlist.remove(to_remove)
            save_json(WATCHLIST_FILE, st.session_state.watchlist)
            fetch_quotes.clear()
            st.rerun()
    st.divider()
    if st.button("🔄 Refresh Prices", use_container_width=True):
        fetch_quotes.clear(); fetch_last_price.clear()
        st.rerun()
    if not PERSIST:
        st.caption("Your watchlist and trades are private to this browser session.")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1><span style="color:#8b5cf6;">⚡</span> StockIQ</h1>
  <p>Know the case for and against — before you buy. Live prices, technicals, and an AI verdict on any stock.</p>
</div>
""", unsafe_allow_html=True)

tab3, tab1, tab2 = st.tabs(["🔮 Predictions", "📊 Watchlist", "📓 Trade Log"])

# ── TAB 1: Watchlist ──────────────────────────────────────────────────────────
with tab1:
    if not st.session_state.watchlist:
        st.info("Your watchlist is empty. Add tickers in the sidebar.")
    else:
        df    = fetch_quotes(st.session_state.watchlist)
        valid = df[df["Price"] != 0]

        if not valid.empty:
            up  = int((valid["% Change"] >= 0).sum())
            down = int((valid["% Change"] < 0).sum())
            avg  = valid["% Change"].mean()
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Watching</div><div class="metric-value">{len(st.session_state.watchlist)}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">▲ Up Today</div><div class="metric-value green">{up}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><div class="metric-label">▼ Down Today</div><div class="metric-value red">{down}</div></div>', unsafe_allow_html=True)
            with c4:
                avg_color = "green" if avg >= 0 else "red"
                st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Move</div><div class="metric-value {avg_color}">{avg:+.2f}%</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Live Prices</div>', unsafe_allow_html=True)
        st.caption("Auto-refreshes every 60s · prices from Yahoo Finance")

        for _, row in df.iterrows():
            pct    = row["% Change"]
            color  = "#34d27b" if pct >= 0 else "#f0584a"
            arrow  = "▲" if pct >= 0 else "▼"
            ticker = row["Ticker"]
            price  = row["Price"]
            change = row["Change"]
            vol    = row["Vol 3M (M)"]
            yr_hi  = row["52W High"]
            yr_lo  = row["52W Low"]

            # 52W range bar
            if yr_hi > yr_lo > 0:
                pct_range = min(max((price - yr_lo) / (yr_hi - yr_lo) * 100, 0), 100)
                range_html = (f'<div style="margin-top:6px;">'
                    f'<div style="display:flex;justify-content:space-between;color:rgba(255,255,255,0.3);font-size:0.7rem;margin-bottom:3px;">'
                    f'<span>${yr_lo:.0f}</span><span style="letter-spacing:0.5px;">52W RANGE</span><span>${yr_hi:.0f}</span>'
                    f'</div>'
                    f'<div style="background:#221c3a;border-radius:3px;height:3px;">'
                    f'<div style="background:#8b5cf6;width:{pct_range:.0f}%;height:100%;border-radius:3px;"></div>'
                    f'</div>'
                    f'</div>')
            else:
                range_html = ""

            if price == 0:
                st.markdown(f'<div class="ticker-card"><span style="color:white;font-weight:700;">{ticker}</span>'
                            f'<span style="color:#a29db8;font-size:0.82rem;margin-left:10px;">No price data. Check the symbol or try Refresh.</span></div>',
                            unsafe_allow_html=True)
                continue
            card_html = (f'<div class="ticker-card">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><span style="color:white;font-size:1.1rem;font-weight:700;">{ticker}</span>'
                f'<span style="color:rgba(255,255,255,0.3);font-size:0.78rem;margin-left:10px;">Vol {vol}M</span></div>'
                f'<div style="text-align:right;">'
                f'<span style="color:white;font-size:1.2rem;font-weight:700;">${price:.2f}</span>'
                f'<span style="color:{color};font-size:0.95rem;font-weight:600;margin-left:12px;">{arrow} {abs(pct):.2f}%</span>'
                f'<span style="color:{color};font-size:0.85rem;margin-left:6px;">({change:+.2f})</span>'
                f'</div></div>{range_html}</div>')
            st.markdown(card_html, unsafe_allow_html=True)

            col_sum, col_analyze, col_space = st.columns([1, 1, 3])
            with col_sum:
                if ANTHROPIC_KEY and st.button("✦ Summarize", key=f"sum_{ticker}"):
                    with st.spinner(""):
                        try:
                            prompt = (f"{ticker} is {arrow} {abs(pct):.2f}% today at ${price:.2f}, "
                                      f"with 3-month avg volume of {vol}M. Write exactly 2 sentences summarizing "
                                      f"how this stock is doing today and what it might mean. Be specific and concise.")
                            out = call_claude(prompt, 120)
                            st.session_state[f"summary_{ticker}"] = out.strip() if out else "Could not generate summary — try again."
                        except Exception:
                            st.session_state[f"summary_{ticker}"] = "Could not generate summary — try again."
            with col_analyze:
                if st.button("⚡ Analyze", key=f"analyze_{ticker}"):
                    st.session_state["pred_ticker"]      = ticker
                    st.session_state["auto_run_analysis"] = True
                    st.toast(f"{ticker} analysis is ready in the **Predictions** tab", icon="🔮")

            if f"summary_{ticker}" in st.session_state:
                st.markdown(
                    f'<div style="color:#a29db8;font-size:0.85rem;padding:4px 0 10px 0;line-height:1.6;">'
                    f'{st.session_state[f"summary_{ticker}"]}</div>',
                    unsafe_allow_html=True,
                )

        # ── Chart ──
        st.markdown('<div class="section-title" style="margin-top:28px;">📉 Price Chart</div>', unsafe_allow_html=True)

        chart_col_sel, chart_col_period = st.columns([2, 2])
        with chart_col_sel:
            chart_ticker = st.selectbox("Chart ticker", st.session_state.watchlist,
                                        key="chart_sel", label_visibility="collapsed")
        with chart_col_period:
            period_label = st.radio("Chart period", ["1W", "1M", "3M", "6M"], index=1,
                                    horizontal=True, key="chart_period",
                                    label_visibility="collapsed")

        period_map = {"1W": "5d", "1M": "1mo", "3M": "3mo", "6M": "6mo"}
        if chart_ticker:
            hist_chart = fetch_history(chart_ticker, period_map[period_label])
            if hist_chart.empty:
                st.info(f"No chart data for {chart_ticker} right now.")
            else:
                st.plotly_chart(make_ohlcv_chart(hist_chart, chart_ticker),
                                use_container_width=True, config={"displayModeBar": False})

# ── TAB 2: Trade Log ──────────────────────────────────────────────────────────
with tab2:
    with st.expander("➕ Log a New Trade", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            t_ticker = st.text_input("Ticker", placeholder="AAPL").strip().upper()
            t_date   = st.date_input("Date", value=datetime.today())
            t_side   = st.selectbox("Side", ["Long", "Short"])
        with col2:
            t_entry  = st.number_input("Entry Price ($)", min_value=0.0, step=0.01, format="%.2f")
            t_exit   = st.number_input("Exit Price (0 = open)", min_value=0.0, step=0.01, format="%.2f")
            t_shares = st.number_input("Shares", min_value=1, step=1)
        with col3:
            t_status = st.selectbox("Status", ["Open", "Closed"])
            t_notes  = st.text_area("Thesis / Notes", placeholder="Why you took the trade...", height=118)
        if st.button("💾 Save Trade", use_container_width=True):
            if not t_ticker:
                st.error("Enter a ticker.")
            else:
                st.session_state.trades.append({
                    "id": max([t["id"] for t in st.session_state.trades], default=0) + 1,
                    "ticker": t_ticker, "date": str(t_date), "side": t_side,
                    "entry": t_entry, "exit": t_exit if t_exit > 0 else None,
                    "shares": t_shares, "status": t_status, "notes": t_notes,
                })
                save_json(TRADES_FILE, st.session_state.trades)
                st.success(f"✅ Trade logged: {t_ticker}")
                st.rerun()

    if not st.session_state.trades:
        st.info("No trades logged yet.")
    else:
        trades_df = pd.DataFrame(st.session_state.trades)
        pnl_col   = []
        for _, row in trades_df.iterrows():
            try:
                if row["status"] == "Closed" and row["exit"]:
                    p = (row["exit"] - row["entry"]) * row["shares"]
                    pnl_col.append(round(-p if row["side"] == "Short" else p, 2))
                elif row["status"] == "Open":
                    live = fetch_last_price(row["ticker"])
                    p    = (live - row["entry"]) * row["shares"]
                    pnl_col.append(round(-p if row["side"] == "Short" else p, 2))
                else:
                    pnl_col.append(None)
            except Exception:
                pnl_col.append(None)

        trades_df["P&L ($)"] = pnl_col
        closed  = trades_df[trades_df["status"] == "Closed"]
        open_t  = trades_df[trades_df["status"] == "Open"]
        total_pnl = closed["P&L ($)"].sum()  if not closed.empty else 0
        winners   = (closed["P&L ($)"] > 0).sum() if not closed.empty else 0
        win_rate  = (winners / len(closed) * 100)  if len(closed) > 0  else 0
        open_pnl  = open_t["P&L ($)"].sum()  if not open_t.empty  else 0

        s1, s2, s3, s4 = st.columns(4)
        pnl_color = "green" if total_pnl >= 0 else "red"
        op_color  = "green" if open_pnl  >= 0 else "red"
        with s1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Realized P&L</div><div class="metric-value {pnl_color}">${total_pnl:,.0f}</div></div>', unsafe_allow_html=True)
        with s2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Win Rate</div><div class="metric-value">{"—" if not len(closed) else f"{win_rate:.0f}%"}</div></div>', unsafe_allow_html=True)
        with s3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Unrealized P&L</div><div class="metric-value {op_color}">${open_pnl:,.0f}</div></div>', unsafe_allow_html=True)
        with s4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Total Trades</div><div class="metric-value">{len(trades_df)}</div></div>', unsafe_allow_html=True)

        # P&L equity curve
        pnl_fig = make_pnl_chart(trades_df)
        if pnl_fig:
            st.markdown('<div class="section-title" style="margin-top:20px;">📈 Cumulative P&L</div>', unsafe_allow_html=True)
            st.plotly_chart(pnl_fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        display_cols = ["ticker","date","side","entry","exit","shares","status","P&L ($)","notes"]
        display_df   = trades_df[[c for c in display_cols if c in trades_df.columns]]

        def color_pnl(val):
            if isinstance(val, (int, float)):
                return f"color: {'#34d27b' if val >= 0 else '#f0584a'}; font-weight: 700"
            return ""

        styled_trades = (
            display_df.style
            .map(color_pnl, subset=["P&L ($)"])
            .format({"entry": "${:.2f}",
                     "exit":  lambda x: f"${x:.2f}" if x else "—",
                     "P&L ($)": "${:,.2f}"}, na_rep="—")
        )
        st.dataframe(styled_trades, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download trades (CSV)", display_df.to_csv(index=False),
                           file_name="stockiq_trades.csv", mime="text/csv")

        with st.expander("🗑️ Delete a Trade"):
            trade_ids = [f"#{t['id']} — {t['ticker']} ({t['date']})" for t in st.session_state.trades]
            sel = st.selectbox("Select", trade_ids, label_visibility="collapsed")
            if st.button("Delete"):
                st.session_state.trades.pop(trade_ids.index(sel))
                save_json(TRADES_FILE, st.session_state.trades)
                st.rerun()

# ── TAB 3: Predictions ────────────────────────────────────────────────────────
def metric(label, value, color="", sub=""):
    sub_html = f'<div style="color:#a29db8;font-size:0.72rem;margin-top:6px;">{sub}</div>' if sub else ""
    return f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value {color}">{value}</div>{sub_html}</div>'

with tab3:
    st.markdown("""
    <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                border-radius:14px;padding:18px 22px;margin-bottom:20px;'>
      <div style='color:white;font-weight:700;font-size:1.05rem;margin-bottom:4px;'>🔮 AI-Powered Stock Analysis</div>
      <div style='color:rgba(255,255,255,0.5);font-size:0.87rem;'>
        Technicals (RSI, MACD, MAs, Bollinger Bands, Volume) + Fundamentals (P/E, EPS, FCF, D/E) + Live News → AI verdict.
        Not financial advice.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # "Analyze" from the watchlist pre-fills and auto-runs
    if st.session_state.pop("auto_run_analysis", False):
        st.session_state["analysis_ticker"] = st.session_state.get("pred_ticker", "")
        st.session_state["pred_ticker_input"] = st.session_state["analysis_ticker"]

    with st.form("analyze_form", border=False):
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            pred_ticker = st.text_input("Ticker", placeholder="Enter ticker — e.g. AAPL, NVDA, TSLA",
                                        key="pred_ticker_input",
                                        label_visibility="collapsed").strip().upper()
        with col_btn:
            submitted = st.form_submit_button("⚡ Analyze", use_container_width=True)
    if submitted:
        st.session_state["analysis_ticker"] = pred_ticker

    st.markdown('<div style="color:#a29db8;font-size:0.78rem;margin:2px 0 6px 0;">Try one:</div>', unsafe_allow_html=True)
    quick = st.columns(5)
    for qc, qt in zip(quick, ["AAPL", "NVDA", "TSLA", "MSFT", "SPY"]):
        with qc:
            st.button(qt, key=f"quick_{qt}", use_container_width=True,
                      on_click=lambda t=qt: st.session_state.update(analysis_ticker=t, pred_ticker_input=t))

    # Results stay on screen across reruns (e.g. clicking "Add to Watchlist")
    pred_ticker = st.session_state.get("analysis_ticker", "")
    if not pred_ticker:
        st.markdown('<div style="color:#a29db8;font-size:0.88rem;padding:24px 0;">Pick a stock above to see live technicals, '
                    'fundamentals, news, a 3-month trend projection with an honest backtest, and an AI bull/bear verdict.</div>',
                    unsafe_allow_html=True)
    elif not is_valid_ticker_text(pred_ticker):
        st.error("That doesn't look like a ticker. Try something like AAPL or NVDA.")
    else:
        with st.status(f"Analyzing {pred_ticker}…", expanded=False) as status:
            status.update(label=f"Pulling price history for {pred_ticker}…")
            result = run_prediction(pred_ticker)
            if result is not None:
                status.update(label="Fundamentals + news…")
                fundamentals = fetch_fundamentals(pred_ticker)
                news         = fetch_news(pred_ticker)
                status.update(label="Backtesting the trend model on 5 years of data…")
                bt = backtest_trend(pred_ticker)
                status.update(label="Asking the AI analyst…")
                ai_raw = run_ai_analysis(pred_ticker, result, fundamentals, news, bt)
                status.update(label=f"{pred_ticker} analysis ready", state="complete")
            else:
                status.update(label="No data", state="error")

        if result is None:
            st.error(f"Couldn't find enough price history for **{pred_ticker}**. Check the symbol, "
                     "or Yahoo Finance may be temporarily unavailable — try again in a minute.")
        else:
            st.caption(f"Data as of {result['as_of']} · prices from Yahoo Finance")

            p1, p2, p3, p4 = st.columns(4)
            trend_color = "green" if result["trend_pct"] >= 0 else "red"
            with p1:
                st.markdown(metric("Current Price", f'${result["current_price"]:.2f}'), unsafe_allow_html=True)
            with p2:
                st.markdown(metric("3-Month Target", f'${result["projected_price"]:.2f}', trend_color,
                                   f'Typical range ${result["range_low"]:.0f}–${result["range_high"]:.0f}'), unsafe_allow_html=True)
            with p3:
                st.markdown(metric("Projected Move", f'{result["trend_pct"]:+.1f}%', trend_color,
                                   f'±{result["sigma_3m"]:.0f}% typical swing'), unsafe_allow_html=True)
            with p4:
                rsi_c = "red" if result["rsi"] > 70 else ("green" if result["rsi"] < 30 else "")
                st.markdown(metric("RSI (14-day)", f'{result["rsi"]:.1f}', rsi_c), unsafe_allow_html=True)

            # Backtest: how trustworthy is the projection for this stock?
            if bt:
                edge = bt["hit_rate"] - max(bt["always_up"], 100 - bt["always_up"])
                verdict_txt = ("beats" if edge > 3 else "roughly matches" if edge > -3 else "trails")
                st.markdown(f"""
                <div class="summary-box">
                  <b>How reliable is that target?</b> We ran this exact trend method on {pred_ticker} every month since
                  {bt['start']} ({bt['n']} tests, each using only data available at the time). It called the 3-month
                  direction right <b>{bt['hit_rate']:.0f}%</b> of the time, vs. a naive "always guess the majority" baseline of
                  {max(bt['always_up'], 100 - bt['always_up']):.0f}%, so it <b>{verdict_txt}</b> the baseline. Average miss on the
                  % move: {bt['mae']:.1f} points. Treat the target as a trend line, not a forecast.
                </div>""", unsafe_allow_html=True)

            if pred_ticker not in st.session_state.watchlist:
                st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
                if st.button(f"➕ Add {pred_ticker} to Watchlist"):
                    st.session_state.watchlist.append(pred_ticker)
                    save_json(WATCHLIST_FILE, st.session_state.watchlist)
                    fetch_quotes.clear()
                    st.toast(f"{pred_ticker} added to watchlist", icon="✅")
                    st.rerun()

            # AI Verdict (moved up: it's the headline)
            st.markdown('<div class="section-title" style="margin-top:24px;">🤖 AI Verdict</div>', unsafe_allow_html=True)
            ai = parse_ai_response(ai_raw) if ai_raw else None
            if ai and ai.get("summary"):
                verdict    = ai.get("verdict",    "HOLD")
                confidence = ai.get("confidence", "Medium")
                summary    = ai.get("summary",    "")
                bulls      = ai.get("bulls",      [])
                bears      = ai.get("bears",      [])
                catalysts  = ai.get("catalysts",  [])
                verdict_color = {"BUY": "#34d27b", "SELL": "#f0584a", "HOLD": "#f0b429"}.get(verdict, "#8b5cf6")
                st.markdown(f"""
                <div class="verdict-row">
                  <div style="background:#17132b;border:2px solid {verdict_color};border-radius:12px;
                              padding:12px 28px;text-align:center;min-width:100px;">
                    <div style="color:{verdict_color};font-size:1.8rem;font-weight:800;">{verdict}</div>
                    <div style="color:#a29db8;font-size:0.75rem;margin-top:2px;">{confidence} Confidence</div>
                  </div>
                  <div style="color:#d8d2ee;font-size:0.9rem;line-height:1.65;flex:1;">{summary}</div>
                </div>
                """, unsafe_allow_html=True)
                bull_col, bear_col, cat_col = st.columns(3)
                for col, title, color, pts in [(bull_col, "🟢 Bull Case", "#34d27b", bulls),
                                               (bear_col, "🔴 Bear Case", "#f0584a", bears),
                                               (cat_col,  "⚡ Catalysts", "#f0b429", catalysts)]:
                    with col:
                        st.markdown(f'<div style="color:{color};font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">{title}</div>', unsafe_allow_html=True)
                        for pt in pts:
                            st.markdown(f'<div style="color:#d8d2ee;font-size:0.85rem;padding:6px 0;border-bottom:1px solid #221c3a;">• {pt}</div>', unsafe_allow_html=True)
                st.caption(f"Generated by Claude ({AI_MODEL}) from the data on this page. Cached for 1 hour. Not financial advice.")
            else:
                greens = sum(1 for c, _, _ in result["signals"] if c == "green")
                reds   = sum(1 for c, _, _ in result["signals"] if c == "red")
                lean   = "Bullish" if greens > reds else ("Bearish" if reds > greens else "Mixed")
                lean_c = {"Bullish": "#34d27b", "Bearish": "#f0584a"}.get(lean, "#f0b429")
                why = "AI analyst is not configured on this deployment" if not ANTHROPIC_KEY else "AI analyst is temporarily unavailable"
                st.markdown(f"""
                <div class="verdict-row">
                  <div style="background:#17132b;border:2px solid {lean_c};border-radius:12px;padding:12px 28px;text-align:center;min-width:100px;">
                    <div style="color:{lean_c};font-size:1.5rem;font-weight:800;">{lean}</div>
                    <div style="color:#a29db8;font-size:0.75rem;margin-top:2px;">{greens} bullish · {reds} bearish signals</div>
                  </div>
                  <div style="color:#d8d2ee;font-size:0.9rem;line-height:1.65;flex:1;">
                    {why}, so this is a simple tally of the technical signals below instead of a full AI verdict.
                  </div>
                </div>""", unsafe_allow_html=True)

            # Technical signals
            st.markdown('<div class="section-title" style="margin-top:24px;">📡 Technical Signals</div>', unsafe_allow_html=True)
            pills_html = ""
            for color, label, desc in result["signals"]:
                pills_html += f'<div style="margin-bottom:6px;"><span class="signal-pill pill-{color}">{label}</span> <span style="color:rgba(255,255,255,0.6);font-size:0.82rem;">{desc}</span></div>'
            st.markdown(f'<div>{pills_html}</div>', unsafe_allow_html=True)

            # Charts
            st.markdown('<div class="section-title" style="margin-top:28px;">📈 Price History + 3-Month Projection</div>', unsafe_allow_html=True)
            st.plotly_chart(make_analysis_chart(result), use_container_width=True,
                            config={"displayModeBar": False})

            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.markdown('<div class="section-title">📊 RSI (14-Day)</div>', unsafe_allow_html=True)
                st.plotly_chart(make_rsi_chart(result["hist"]["RSI"].dropna()),
                                use_container_width=True, config={"displayModeBar": False})
                st.caption("RSI > 70 = overbought · RSI < 30 = oversold")
            with chart_col2:
                st.markdown('<div class="section-title">📊 MACD</div>', unsafe_allow_html=True)
                st.plotly_chart(make_macd_chart(result["hist"]),
                                use_container_width=True, config={"displayModeBar": False})
                st.caption("MACD above signal = bullish momentum")

            st.markdown('<div style="margin-top:24px;"></div>', unsafe_allow_html=True)
            left_col, right_col = st.columns([1, 1])
            with left_col:
                st.markdown('<div class="section-title">📊 Fundamentals</div>', unsafe_allow_html=True)
                if "error" not in fundamentals:
                    rows_html = ""
                    for k, v in {k: v for k, v in fundamentals.items() if k != "_raw"}.items():
                        color_class = ""
                        if k == "Revenue Growth" and v != "N/A":
                            color_class = "green" if not v.startswith("-") and v != "0.0%" else "red"
                        if k == "Analyst Rating":
                            color_class = "green" if "BUY" in v else ("red" if "SELL" in v else "")
                        rows_html += f'<div class="fund-row"><span class="fund-key">{k}</span><span class="fund-val {color_class}">{v}</span></div>'
                    st.markdown(f'<div class="fund-card">{rows_html}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#a29db8;font-size:0.88rem;">Fundamentals unavailable right now.</div>', unsafe_allow_html=True)
            with right_col:
                st.markdown('<div class="section-title">📰 Recent News</div>', unsafe_allow_html=True)
                if news:
                    for n in news:
                        st.markdown(
                            f'<a href="{n["link"]}" target="_blank" rel="noopener" style="text-decoration:none;">'
                            f'<div class="news-item" style="cursor:pointer;">'
                            f'<div class="news-title">{n["title"]}</div>'
                            f'<div class="news-meta">{n["source"]} &nbsp;·&nbsp; {n["pub"]}</div>'
                            f'</div></a>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown('<div style="color:#a29db8;font-size:0.88rem;">No recent news found.</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid #221c3a;margin-top:40px;padding:16px 0 8px 0;color:#a29db8;font-size:0.75rem;line-height:1.6;">
  StockIQ is an educational project, not financial advice. Data from Yahoo Finance and Google News may be delayed or incomplete.
  Projections are statistical trend lines, not predictions of future prices.
</div>""", unsafe_allow_html=True)
