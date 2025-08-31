import yfinance as yf
import pandas as pd

def fetch_price_history(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    return df[['Close']].rename(columns={'Close': ticker}).dropna() if not df.empty else pd.DataFrame()

def fetch_financials_latest(ticker):
    t = yf.Ticker(ticker)
    out = {}
    try:
        fin = t.financials
        if fin is not None and not fin.empty:
            out['income'] = fin.iloc[:, 0]
    except Exception:
        pass
    try:
        bs = t.balance_sheet
        if bs is not None and not bs.empty:
            out['balance'] = bs.iloc[:, 0]
    except Exception:
        pass
    return out
