import pandas as pd
from .metrics import compute_returns

def backtest_buy_hold(price_df, ticker, benchmark):
    r=compute_returns(price_df[[ticker, benchmark]])
    cum=(1+r).cumprod()-1
    return cum
