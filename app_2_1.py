import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="StockIQ", page_icon="⚡", layout="wide")

WATCHLIST_FILE = "watchlist.json"
TRADES_FILE    = "trades.json"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

.stApp { background: #0d1117; }

[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #21262d;
}

.hero {
    border-bottom: 1px solid #21262d;
    padding: 24px 4px 20px 4px;
    margin-bottom: 24px;
}
.hero h1 {
    font-size: 1.6rem;
    font-weight: 800;
    color: #e6edf3;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero p { color: #8b949e; font-size: 0.88rem; margin: 4px 0 0 0; }

.metric-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
}
.metric-label {
    color: #8b949e;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.metric-value { color: #e6edf3; font-size: 1.75rem; font-weight: 800; line-height: 1; }
.metric-value.green { color: #3fb950; }
.metric-value.red   { color: #f85149; }

.section-title {
    color: #e6edf3;
    font-size: 0.95rem;
    font-weight: 700;
    margin: 20px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.signal-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 3px 3px 3px 0;
}
.pill-green  { background: #0d2a1a; color: #3fb950; border: 1px solid #1e4d2e; }
.pill-red    { background: #2d0f0f; color: #f85149; border: 1px solid #5a1e1e; }
.pill-yellow { background: #2a1f00; color: #d29922; border: 1px solid #4a3800; }

.summary-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-left: 3px solid #58a6ff;
    border-radius: 8px;
    padding: 16px 20px;
    color: #c9d1d9;
    font-size: 0.88rem;
    line-height: 1.65;
    margin-top: 16px;
}

.ai-verdict-buy  { border-left: 3px solid #3fb950 !important; }
.ai-verdict-sell { border-left: 3px solid #f85149 !important; }
.ai-verdict-hold { border-left: 3px solid #d29922 !important; }

.fund-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
}
.fund-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #21262d;
}
.fund-row:last-child { border-bottom: none; }
.fund-key { color: #8b949e; font-size: 0.82rem; }
.fund-val { color: #e6edf3; font-size: 0.88rem; font-weight: 600; }
.fund-val.green { color: #3fb950; }
.fund-val.red   { color: #f85149; }

.news-item {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 6px;
}
.news-title { color: #c9d1d9; font-size: 0.88rem; font-weight: 600; }
.news-meta  { color: #8b949e; font-size: 0.78rem; margin-top: 3px; }

.ticker-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ticker-card:hover { border-color: #388bfd; }

[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

.stTextInput input, .stNumberInput input {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 6px !important;
}

.stButton > button {
    background: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
.stButton > button:hover { border-color: #58a6ff !important; color: #58a6ff !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 4px 8px;
    gap: 10px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    color: #8b949e !important;
    font-weight: 600 !important;
    padding: 6px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: #21262d !important;
    color: #e6edf3 !important;
}

hr { border-color: #21262d !important; }
.stCaption, small { color: #8b949e !important; }
.streamlit-expanderHeader {
    background: #161b22 !important;
    border-radius: 6px !important;
    color: #e6edf3 !important;
    font-weight: 600 !important;
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
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_json(WATCHLIST_FILE, ["AAPL", "TSLA", "NVDA", "SPY"])
if "trades" not in st.session_state:
    st.session_state.trades = load_json(TRADES_FILE, [])

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
            rows.append({
                "Ticker": t.upper(),
                "Price":  round(price, 2),
                "Change": round(chg, 2),
                "% Change": round(pct, 2),
                "Vol 3M (M)": round(vol / 1_000_000, 2),
            })
        except:
            rows.append({"Ticker": t.upper(), "Price": 0, "Change": 0, "% Change": 0, "Vol 3M (M)": 0})
    return pd.DataFrame(rows)

@st.cache_data(ttl=3600)
def fetch_history(ticker):
    df = yf.Ticker(ticker).history(period="2y")
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df

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
        pe       = info.get("trailingPE")
        fpe      = info.get("forwardPE")
        eps      = info.get("trailingEps")
        rev      = info.get("totalRevenue")
        rev_g    = info.get("revenueGrowth")
        fcf      = info.get("freeCashflow")
        de       = info.get("debtToEquity")
        mkt      = info.get("marketCap")
        sector   = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")
        rec      = info.get("recommendationKey", "N/A").upper()
        target   = info.get("targetMeanPrice")
        analysts = info.get("numberOfAnalystOpinions", 0)
        div_y    = info.get("dividendYield")
        beta     = info.get("beta")
        return {
            "P/E (Trailing)":   f"{pe:.1f}x" if pe else "N/A",
            "P/E (Forward)":    f"{fpe:.1f}x" if fpe else "N/A",
            "EPS (TTM)":        f"${eps:.2f}" if eps else "N/A",
            "Revenue":          fmt_large(rev),
            "Revenue Growth":   fmt_pct(rev_g),
            "Free Cash Flow":   fmt_large(fcf),
            "Debt/Equity":      f"{de:.1f}" if de else "N/A",
            "Market Cap":       fmt_large(mkt),
            "Sector":           sector,
            "Industry":         industry,
            "Analyst Rating":   rec,
            "Price Target":     f"${target:.2f}" if target else "N/A",
            "# Analysts":       str(analysts),
            "Dividend Yield":   fmt_pct(div_y) if div_y else "None",
            "Beta":             f"{beta:.2f}" if beta else "N/A",
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
        url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(url, timeout=10)
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:6]
        news = []
        for item in items:
            title = item.findtext("title", "")
            pub   = item.findtext("pubDate", "")
            link  = item.findtext("link", "")
            # Clean title (Google News appends source after " - ")
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0]
                source = parts[1]
            else:
                source = ""
            news.append({"title": title, "pub": pub[:22], "source": source, "link": link})
        return news
    except:
        return []

def run_prediction(ticker):
    hist = fetch_history(ticker)
    if hist.empty or len(hist) < 60:
        return None
    closes = hist["Close"].copy()
    hist["MA50"]  = closes.rolling(50).mean()
    hist["MA200"] = closes.rolling(200).mean()
    delta = closes.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    hist["RSI"]      = 100 - (100 / (1 + rs))
    hist["BB_mid"]   = closes.rolling(20).mean()
    hist["BB_upper"] = hist["BB_mid"] + 2 * closes.rolling(20).std()
    hist["BB_lower"] = hist["BB_mid"] - 2 * closes.rolling(20).std()

    # MACD
    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    hist["MACD"]        = ema12 - ema26
    hist["MACD_signal"] = hist["MACD"].ewm(span=9, adjust=False).mean()
    hist["MACD_hist"]   = hist["MACD"] - hist["MACD_signal"]

    x      = np.arange(len(closes))
    coeffs = np.polyfit(x, closes.values, 1)
    slope, intercept = coeffs
    future_days   = 63
    x_future      = np.arange(len(closes), len(closes) + future_days)
    y_future      = slope * x_future + intercept
    last_date     = hist.index[-1]
    future_dates  = pd.date_range(start=last_date + timedelta(days=1), periods=future_days, freq="B")
    future_series = pd.Series(y_future, index=future_dates)
    current_price    = closes.iloc[-1]
    projected_price  = future_series.iloc[-1]
    trend_pct        = ((projected_price - current_price) / current_price) * 100
    rsi_val   = hist["RSI"].iloc[-1]
    ma50_val  = hist["MA50"].iloc[-1]
    ma200_val = hist["MA200"].iloc[-1]
    bb_upper  = hist["BB_upper"].iloc[-1]
    bb_lower  = hist["BB_lower"].iloc[-1]
    macd_val  = hist["MACD"].iloc[-1]
    macd_sig  = hist["MACD_signal"].iloc[-1]

    signals = []
    if ma50_val > ma200_val:
        signals.append(("green", "🟢 Golden Cross", "MA50 above MA200 — bullish trend"))
    else:
        signals.append(("red",   "🔴 Death Cross",  "MA50 below MA200 — bearish trend"))
    if rsi_val < 30:
        signals.append(("green",  "🟢 Oversold",     f"RSI {rsi_val:.1f} — potential bounce"))
    elif rsi_val > 70:
        signals.append(("red",    "🔴 Overbought",   f"RSI {rsi_val:.1f} — potential pullback"))
    else:
        signals.append(("yellow", "🟡 Neutral RSI",  f"RSI {rsi_val:.1f} — no extreme"))
    if current_price < bb_lower:
        signals.append(("green", "🟢 Below BB Lower", "Statistically cheap vs recent range"))
    elif current_price > bb_upper:
        signals.append(("red",   "🔴 Above BB Upper", "Statistically stretched vs recent range"))
    else:
        signals.append(("yellow","🟡 Inside BB Bands","Price within normal range"))
    if macd_val > macd_sig:
        signals.append(("green", "🟢 MACD Bullish", f"MACD ({macd_val:.2f}) above signal ({macd_sig:.2f})"))
    else:
        signals.append(("red",   "🔴 MACD Bearish", f"MACD ({macd_val:.2f}) below signal ({macd_sig:.2f})"))

    # Volume trend
    recent_vol = hist["Volume"].iloc[-5:].mean()
    avg_vol    = hist["Volume"].iloc[-30:].mean()
    if recent_vol > avg_vol * 1.3:
        signals.append(("green", "🟢 Volume Surge", f"Recent vol {recent_vol/1e6:.1f}M vs 30d avg {avg_vol/1e6:.1f}M"))
    elif recent_vol < avg_vol * 0.7:
        signals.append(("yellow", "🟡 Low Volume", "Below-average volume — weak conviction"))
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
    }

def run_ai_analysis(ticker, tech_result, fundamentals, news):
    try:
        ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_KEY", "")
        if not ANTHROPIC_KEY:
            return None

        signals_text = "\n".join([f"- {label}: {desc}" for _, label, desc in tech_result["signals"]])
        news_text    = "\n".join([f"- {n['title']} ({n['source']})" for n in news[:5]]) if news else "No recent news found."

        fund_text = ""
        for k, v in fundamentals.items():
            if k != "_raw":
                fund_text += f"- {k}: {v}\n"

        prompt = f"""You are a professional equity analyst. Analyze {ticker} and give a clear investment verdict.

TECHNICAL SIGNALS:
{signals_text}

3-Month Price Projection: {tech_result['trend_pct']:+.1f}% (linear regression trend)
Current Price: ${tech_result['current_price']:.2f}
RSI: {tech_result['rsi']:.1f}

FUNDAMENTAL DATA:
{fund_text}

RECENT NEWS HEADLINES:
{news_text}

Based on ALL of the above (technicals, fundamentals, and news sentiment), provide:

1. VERDICT: BUY, HOLD, or SELL (one word)
2. CONFIDENCE: High, Medium, or Low
3. SUMMARY: 3-4 sentences explaining your reasoning, referencing specific data points
4. BULLS: 3 bullet points — strongest reasons to be bullish
5. BEARS: 3 bullet points — biggest risks or reasons to be cautious
6. CATALYSTS: 2 near-term catalysts to watch

Format your response EXACTLY like this:
VERDICT: [BUY/HOLD/SELL]
CONFIDENCE: [High/Medium/Low]
SUMMARY: [text]
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
- [point]"""

        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        return r.json()["content"][0]["text"]
    except Exception as e:
        return None

def parse_ai_response(text):
    result = {}
    lines  = text.strip().split("\n")
    current_section = None
    buffer = []

    for line in lines:
        line = line.strip()
        if line.startswith("VERDICT:"):
            result["verdict"] = line.replace("VERDICT:", "").strip()
        elif line.startswith("CONFIDENCE:"):
            result["confidence"] = line.replace("CONFIDENCE:", "").strip()
        elif line.startswith("SUMMARY:"):
            result["summary"] = line.replace("SUMMARY:", "").strip()
            current_section = "summary"
        elif line == "BULLS:":
            current_section = "bulls"
            result["bulls"] = []
        elif line == "BEARS:":
            current_section = "bears"
            result["bears"] = []
        elif line == "CATALYSTS:":
            current_section = "catalysts"
            result["catalysts"] = []
        elif line.startswith("- ") and current_section in ("bulls", "bears", "catalysts"):
            result.setdefault(current_section, []).append(line[2:])
        elif current_section == "summary" and line and not any(line.startswith(s) for s in ["BULLS:", "BEARS:", "CATALYSTS:", "VERDICT:", "CONFIDENCE:"]):
            result["summary"] = result.get("summary", "") + " " + line

    return result

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 0 10px 0;'>
        <span style='font-size:2rem;'>⚡</span>
        <span style='color:white;font-size:1.4rem;font-weight:800;margin-left:8px;'>StockIQ</span>
        <div style='color:rgba(255,255,255,0.4);font-size:0.8rem;margin-top:4px;'>Your trading dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("<div style='color:rgba(255,255,255,0.7);font-weight:600;margin-bottom:8px;'>➕ Add Ticker</div>", unsafe_allow_html=True)
    new_ticker = st.text_input("", placeholder="e.g. MSFT", label_visibility="collapsed").strip().upper()
    if st.button("Add to Watchlist", use_container_width=True):
        if new_ticker and new_ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_ticker)
            save_json(WATCHLIST_FILE, st.session_state.watchlist)
            st.cache_data.clear()
            st.success(f"✅ {new_ticker} added!")
        elif new_ticker in st.session_state.watchlist:
            st.warning("Already on watchlist.")

    st.divider()
    st.markdown("<div style='color:rgba(255,255,255,0.7);font-weight:600;margin-bottom:8px;'>🗑️ Remove Ticker</div>", unsafe_allow_html=True)
    if st.session_state.watchlist:
        to_remove = st.selectbox("", st.session_state.watchlist, label_visibility="collapsed")
        if st.button("Remove", use_container_width=True):
            st.session_state.watchlist.remove(to_remove)
            save_json(WATCHLIST_FILE, st.session_state.watchlist)
            st.cache_data.clear()
            st.rerun()

    st.divider()
    if st.button("🔄 Refresh Prices", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>⚡ StockIQ</h1>
    <p>Live prices &nbsp;·&nbsp; Trade log &nbsp;·&nbsp; 3-month predictions &nbsp;·&nbsp; AI analysis</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊  Watchlist", "📓  Trade Log", "🔮  Predictions"])

# ── TAB 1: Watchlist ──────────────────────────────────────────────────────────
with tab1:
    if not st.session_state.watchlist:
        st.info("Your watchlist is empty. Add tickers in the sidebar.")
    else:
        df = fetch_quotes(st.session_state.watchlist)
        valid = df[df["Price"] != 0]

        if not valid.empty:
            up   = int((valid["% Change"] >= 0).sum())
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
                color = "green" if avg >= 0 else "red"
                st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Move</div><div class="metric-value {color}">{avg:+.2f}%</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Live Prices</div>', unsafe_allow_html=True)
        st.caption("Auto-refreshes every 60s · prices from Yahoo Finance")

        for _, row in df.iterrows():
            pct   = row["% Change"]
            color = "#4ade80" if pct >= 0 else "#f87171"
            arrow = "▲" if pct >= 0 else "▼"
            st.markdown(f"""
            <div class="ticker-card">
                <div>
                    <span style="color:white;font-size:1.1rem;font-weight:700;">{row['Ticker']}</span>
                    <span style="color:rgba(255,255,255,0.35);font-size:0.8rem;margin-left:10px;">Vol {row['Vol 3M (M)']}M</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:white;font-size:1.2rem;font-weight:700;">${row['Price']:.2f}</span>
                    <span style="color:{color};font-size:0.95rem;font-weight:600;margin-left:12px;">{arrow} {abs(pct):.2f}%</span>
                    <span style="color:{color};font-size:0.85rem;margin-left:6px;">({row['Change']:+.2f})</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="margin-top:28px;">📉 30-Day Chart</div>', unsafe_allow_html=True)
        chart_ticker = st.selectbox("", st.session_state.watchlist, key="chart_sel", label_visibility="collapsed")
        if chart_ticker:
            hist = yf.Ticker(chart_ticker).history(period="1mo")
            if not hist.empty:
                st.line_chart(hist["Close"], height=240)

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
                    "id": len(st.session_state.trades) + 1,
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
        pnl_col = []
        for _, row in trades_df.iterrows():
            try:
                if row["status"] == "Closed" and row["exit"]:
                    p = (row["exit"] - row["entry"]) * row["shares"]
                    pnl_col.append(round(-p if row["side"] == "Short" else p, 2))
                elif row["status"] == "Open":
                    live = yf.Ticker(row["ticker"]).fast_info.last_price or 0
                    p = (live - row["entry"]) * row["shares"]
                    pnl_col.append(round(-p if row["side"] == "Short" else p, 2))
                else:
                    pnl_col.append(None)
            except:
                pnl_col.append(None)

        trades_df["P&L ($)"] = pnl_col
        closed    = trades_df[trades_df["status"] == "Closed"]
        open_t    = trades_df[trades_df["status"] == "Open"]
        total_pnl = closed["P&L ($)"].sum() if not closed.empty else 0
        winners   = (closed["P&L ($)"] > 0).sum() if not closed.empty else 0
        win_rate  = (winners / len(closed) * 100) if len(closed) > 0 else 0
        open_pnl  = open_t["P&L ($)"].sum() if not open_t.empty else 0

        s1, s2, s3, s4 = st.columns(4)
        pnl_color = "green" if total_pnl >= 0 else "red"
        op_color  = "green" if open_pnl >= 0 else "red"
        with s1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Realized P&L</div><div class="metric-value {pnl_color}">${total_pnl:,.0f}</div></div>', unsafe_allow_html=True)
        with s2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Win Rate</div><div class="metric-value">{"—" if not len(closed) else f"{win_rate:.0f}%"}</div></div>', unsafe_allow_html=True)
        with s3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Unrealized P&L</div><div class="metric-value {op_color}">${open_pnl:,.0f}</div></div>', unsafe_allow_html=True)
        with s4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Total Trades</div><div class="metric-value">{len(trades_df)}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        display_cols = ["ticker","date","side","entry","exit","shares","status","P&L ($)","notes"]
        display_df   = trades_df[[c for c in display_cols if c in trades_df.columns]]

        def color_pnl(val):
            if isinstance(val, (int, float)):
                return f"color: {'#4ade80' if val >= 0 else '#f87171'}; font-weight: 700"
            return ""

        styled_trades = (
            display_df.style
            .map(color_pnl, subset=["P&L ($)"])
            .format({"entry": "${:.2f}", "exit": lambda x: f"${x:.2f}" if x else "—", "P&L ($)": "${:,.2f}"}, na_rep="—")
        )
        st.dataframe(styled_trades, use_container_width=True, hide_index=True)

        with st.expander("🗑️ Delete a Trade"):
            trade_ids = [f"#{t['id']} — {t['ticker']} ({t['date']})" for t in st.session_state.trades]
            sel = st.selectbox("Select", trade_ids, label_visibility="collapsed")
            if st.button("Delete"):
                st.session_state.trades.pop(trade_ids.index(sel))
                save_json(TRADES_FILE, st.session_state.trades)
                st.rerun()

# ── TAB 3: Predictions ────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:18px 22px;margin-bottom:20px;'>
        <div style='color:white;font-weight:700;font-size:1.05rem;margin-bottom:4px;'>🔮 AI-Powered Stock Analysis</div>
        <div style='color:rgba(255,255,255,0.5);font-size:0.87rem;'>Technicals (RSI, MACD, MAs, Bollinger Bands, Volume) + Fundamentals (P/E, EPS, FCF, D/E) + Live News → AI verdict. Not financial advice.</div>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        pred_ticker = st.text_input("", placeholder="Enter ticker — e.g. AAPL, NVDA, TSLA", key="pred_ticker", label_visibility="collapsed").strip().upper()
    with col_btn:
        run_btn = st.button("⚡ Analyze", use_container_width=True)

    if run_btn:
        if not pred_ticker:
            st.error("Enter a ticker first.")
        else:
            with st.spinner(f"Pulling data for {pred_ticker}..."):
                result       = run_prediction(pred_ticker)
                fundamentals = fetch_fundamentals(pred_ticker)
                news         = fetch_news(pred_ticker)

            if result is None:
                st.error("Not enough historical data. Try a different ticker.")
            else:
                st.divider()

                # ── Price metrics ──
                p1, p2, p3, p4 = st.columns(4)
                trend_color = "green" if result["trend_pct"] >= 0 else "red"
                with p1:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Current Price</div><div class="metric-value">${result["current_price"]:.2f}</div></div>', unsafe_allow_html=True)
                with p2:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">3-Month Target</div><div class="metric-value {trend_color}">${result["projected_price"]:.2f}</div></div>', unsafe_allow_html=True)
                with p3:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Projected Move</div><div class="metric-value {trend_color}">{result["trend_pct"]:+.1f}%</div></div>', unsafe_allow_html=True)
                with p4:
                    rsi_c = "red" if result["rsi"] > 70 else ("green" if result["rsi"] < 30 else "")
                    st.markdown(f'<div class="metric-card"><div class="metric-label">RSI (14-day)</div><div class="metric-value {rsi_c}">{result["rsi"]:.1f}</div></div>', unsafe_allow_html=True)

                # ── Two column layout: Fundamentals + News ──
                st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
                left_col, right_col = st.columns([1, 1])

                with left_col:
                    st.markdown('<div class="section-title">📊 Fundamentals</div>', unsafe_allow_html=True)
                    if "error" not in fundamentals:
                        fund_display = {k: v for k, v in fundamentals.items() if k != "_raw"}
                        rows_html = ""
                        for k, v in fund_display.items():
                            color_class = ""
                            if k == "Revenue Growth" and v != "N/A":
                                color_class = "green" if v.startswith("-") is False and v != "0.0%" else "red"
                            if k == "Analyst Rating":
                                color_class = "green" if "BUY" in v else ("red" if "SELL" in v else "yellow")
                            rows_html += f'<div class="fund-row"><span class="fund-key">{k}</span><span class="fund-val {color_class}">{v}</span></div>'
                        st.markdown(f'<div class="fund-card">{rows_html}</div>', unsafe_allow_html=True)

                with right_col:
                    st.markdown('<div class="section-title">📰 Recent News</div>', unsafe_allow_html=True)
                    if news:
                        for n in news:
                            st.markdown(f"""
<a href="{n['link']}" target="_blank" style="text-decoration:none;">
    <div class="news-item" style="cursor:pointer;">
        <div class="news-title">{n['title']}</div>
        <div class="news-meta">{n['source']} &nbsp;·&nbsp; {n['pub']}</div>
    </div>
</a>
""", unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:#8b949e;font-size:0.88rem;">No recent news found.</div>', unsafe_allow_html=True)

                # ── Technical signals ──
                st.markdown('<div class="section-title" style="margin-top:24px;">📡 Technical Signals</div>', unsafe_allow_html=True)
                pills_html = ""
                for color, label, desc in result["signals"]:
                    pills_html += f'<span class="signal-pill pill-{color}">{label}</span> <span style="color:rgba(255,255,255,0.5);font-size:0.82rem;">{desc}</span><br style="margin-bottom:6px;">'
                st.markdown(f'<div style="line-height:2.2;">{pills_html}</div>', unsafe_allow_html=True)

                # ── AI Analysis ──
                st.markdown('<div class="section-title" style="margin-top:24px;">🤖 AI Verdict</div>', unsafe_allow_html=True)
                with st.spinner("Synthesizing AI analysis..."):
                    ai_raw = run_ai_analysis(pred_ticker, result, fundamentals, news)

                if ai_raw:
                    ai = parse_ai_response(ai_raw)
                    verdict    = ai.get("verdict", "HOLD")
                    confidence = ai.get("confidence", "Medium")
                    summary    = ai.get("summary", "")
                    bulls      = ai.get("bulls", [])
                    bears      = ai.get("bears", [])
                    catalysts  = ai.get("catalysts", [])

                    verdict_color = {"BUY": "#3fb950", "SELL": "#f85149", "HOLD": "#d29922"}.get(verdict, "#58a6ff")
                    verdict_class = {"BUY": "ai-verdict-buy", "SELL": "ai-verdict-sell", "HOLD": "ai-verdict-hold"}.get(verdict, "")

                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:16px;margin-bottom:16px;'>
                        <div style='background:#161b22;border:2px solid {verdict_color};border-radius:12px;padding:12px 28px;text-align:center;'>
                            <div style='color:{verdict_color};font-size:1.8rem;font-weight:800;'>{verdict}</div>
                            <div style='color:#8b949e;font-size:0.75rem;margin-top:2px;'>{confidence} Confidence</div>
                        </div>
                        <div style='color:#c9d1d9;font-size:0.9rem;line-height:1.65;flex:1;'>{summary}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    bull_col, bear_col, cat_col = st.columns(3)
                    with bull_col:
                        st.markdown('<div style="color:#3fb950;font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">🟢 Bull Case</div>', unsafe_allow_html=True)
                        for pt in bulls:
                            st.markdown(f'<div style="color:#c9d1d9;font-size:0.85rem;padding:6px 0;border-bottom:1px solid #21262d;">• {pt}</div>', unsafe_allow_html=True)
                    with bear_col:
                        st.markdown('<div style="color:#f85149;font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">🔴 Bear Case</div>', unsafe_allow_html=True)
                        for pt in bears:
                            st.markdown(f'<div style="color:#c9d1d9;font-size:0.85rem;padding:6px 0;border-bottom:1px solid #21262d;">• {pt}</div>', unsafe_allow_html=True)
                    with cat_col:
                        st.markdown('<div style="color:#d29922;font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">⚡ Catalysts</div>', unsafe_allow_html=True)
                        for pt in catalysts:
                            st.markdown(f'<div style="color:#c9d1d9;font-size:0.85rem;padding:6px 0;border-bottom:1px solid #21262d;">• {pt}</div>', unsafe_allow_html=True)
                else:
                    st.warning("AI analysis unavailable — check your ANTHROPIC_KEY in Streamlit secrets.")

                # ── Charts ──
                st.markdown('<div class="section-title" style="margin-top:28px;">📈 Price History + 3-Month Projection</div>', unsafe_allow_html=True)
                hist = result["hist"]
                chart_data = pd.DataFrame({
                    "Actual":   hist["Close"],
                    "MA50":     hist["MA50"],
                    "MA200":    hist["MA200"],
                    "BB Upper": hist["BB_upper"],
                    "BB Lower": hist["BB_lower"],
                })
                proj_df = pd.DataFrame({"Projection": result["future_series"]})
                st.line_chart(pd.concat([chart_data, proj_df]), height=320)

                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    st.markdown('<div class="section-title">📊 RSI (14-Day)</div>', unsafe_allow_html=True)
                    st.line_chart(hist["RSI"].dropna().to_frame(), height=180)
                    st.caption("RSI > 70 = overbought · RSI < 30 = oversold")
                with chart_col2:
                    st.markdown('<div class="section-title">📊 MACD</div>', unsafe_allow_html=True)
                    macd_df = hist[["MACD", "MACD_signal"]].dropna()
                    st.line_chart(macd_df, height=180)
                    st.caption("MACD above signal = bullish momentum")
