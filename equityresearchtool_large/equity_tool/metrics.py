import pandas as pd, numpy as np

# ---------- Returns & Risk ----------
def compute_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Daily pct returns, dropping rows that are all NaN."""
    if price_df is None or price_df.empty:
        return pd.DataFrame()
    return price_df.pct_change().dropna(how="all")

def cumulative_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    r = compute_returns(price_df)
    if r.empty:
        return r
    return (1.0 + r).cumprod() - 1.0

def volatility(price_df: pd.DataFrame, trading_days: int = 252) -> pd.Series:
    r = compute_returns(price_df)
    if r.empty:
        return pd.Series(dtype=float)
    return r.std(ddof=1) * np.sqrt(trading_days)

def sharpe_ratio(price_df: pd.DataFrame, rf: float = 0.0, trading_days: int = 252) -> pd.Series:
    """
    Annualized Sharpe (excess mean / stdev).
    rf is annual (e.g., 0.02 for 2%); converted to daily internally.
    """
    r = compute_returns(price_df)
    if r.empty:
        return pd.Series(dtype=float)
    excess = r - (rf / trading_days)
    mu = excess.mean() * trading_days
    sigma = r.std(ddof=1) * np.sqrt(trading_days)
    with np.errstate(divide="ignore", invalid="ignore"):
        s = mu / sigma
    return s.replace([np.inf, -np.inf], np.nan)

def max_drawdown(price_series: pd.Series) -> float:
    """Max drawdown from a price series."""
    if price_series is None or price_series.dropna().empty:
        return float("nan")
    s = price_series.dropna()
    running_max = s.cummax()
    dd = s / running_max - 1.0
    return float(dd.min()) if not dd.empty else float("nan")

def beta_vs_benchmark(price_df: pd.DataFrame, benchmark: str) -> pd.Series:
    """
    Beta of each asset vs benchmark using daily returns.
    - Aligns on common dates
    - Drops NaNs
    - Uses sample stats (ddof=1)
    """
    r = compute_returns(price_df)
    if r.empty or benchmark not in r.columns:
        return pd.Series(dtype=float)

    betas = {}
    bench = r[benchmark]
    for col in r.columns:
        if col == benchmark:
            continue
        pair = pd.concat([r[col], bench], axis=1, join="inner").dropna()
        if pair.shape[0] < 2:
            betas[col] = float("nan")
            continue
        y = pair.iloc[:, 0].values
        x = pair.iloc[:, 1].values
        var_x = np.var(x, ddof=1)
        if var_x == 0 or np.isnan(var_x):
            betas[col] = float("nan")
        else:
            cov_yx = np.cov(y, x, ddof=1)[0, 1]
            betas[col] = float(cov_yx / var_x)
    return pd.Series(betas)

# ---------- Fundamentals ----------
def _safe_div(a, b) -> float:
    try:
        if b is None or b == 0 or pd.isna(b):
            return float("nan")
        return float(a) / float(b)
    except Exception:
        return float("nan")

def fundamentals_ratios(latest: dict) -> dict:
    """
    Compute a minimal set of fundamental ratios from latest statements
    (dict with 'income', 'balance' as pandas.Series), compatible with yfinance.
    """
    out = {}
    income = latest.get('income')
    balance = latest.get('balance')

    # Income statement margins
    if income is not None and isinstance(income, pd.Series):
        rev = income.get('Total Revenue') or income.get('TotalRevenue') or income.get('Revenue')
        gp  = income.get('Gross Profit') or income.get('GrossProfit')
        op  = income.get('Operating Income') or income.get('OperatingIncome')
        ni  = income.get('Net Income') or income.get('NetIncome')
        out['Gross Margin'] = _safe_div(gp, rev)
        out['Operating Margin'] = _safe_div(op, rev)
        out['Net Margin'] = _safe_div(ni, rev)
    else:
        out['Gross Margin'] = out['Operating Margin'] = out['Net Margin'] = float('nan')

    # Balance sheet & profitability
    if balance is not None and isinstance(balance, pd.Series):
        assets = balance.get('Total Assets') or balance.get('TotalAssets')
        equity = (balance.get('Total Stockholder Equity')
                  or balance.get('Total Stockholders Equity')
                  or balance.get('TotalEquity')
                  or balance.get('StockholdersEquity'))
        current_assets = balance.get('Total Current Assets') or balance.get('TotalCurrentAssets')
        current_liab   = balance.get('Total Current Liabilities') or balance.get('TotalCurrentLiabilities')

        # debt best-effort
        total_debt = balance.get('Total Debt')
        if total_debt is None:
            short_lt = balance.get('Short Long Term Debt') or 0
            long_t   = balance.get('Long Term Debt') or 0
            total_debt = (short_lt or 0) + (long_t or 0)

        ni = income.get('Net Income') if (income is not None and isinstance(income, pd.Series)) else None
        out['ROA'] = _safe_div(ni, assets)
        out['ROE'] = _safe_div(ni, equity)
        out['Current Ratio'] = _safe_div(current_assets, current_liab)
        out['Debt to Equity'] = _safe_div(total_debt, equity)
    else:
        out['ROA'] = out['ROE'] = out['Current Ratio'] = out['Debt to Equity'] = float('nan')

    return out