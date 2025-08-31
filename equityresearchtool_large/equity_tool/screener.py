import yfinance as yf
import pandas as pd

def screen_sp500(metric="ROE", top=10):
    tickers=yf.Ticker("^GSPC").constituents.keys() if hasattr(yf.Ticker("^GSPC"),"constituents") else []
    rows=[]
    for t in list(tickers)[:50]:  # demo: limit to 50 for runtime
        try:
            fin=yf.Ticker(t).financials
            if fin is None or fin.empty: continue
            ni=fin.loc["Net Income"].iloc[0]
            eq=yf.Ticker(t).balance_sheet.loc["Total Stockholder Equity"].iloc[0]
            roe=ni/eq if eq!=0 else None
            rows.append({"Ticker":t,"ROE":roe})
        except: continue
    df=pd.DataFrame(rows).dropna()
    return df.sort_values(metric,ascending=False).head(top)
