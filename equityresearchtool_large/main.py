# main.py — EquityResearchTool (CLI)
# Run:
#   python main.py --tickers AAPL MSFT --benchmark SPY --start 2022-01-01 --end 2025-01-01 --rf 0.0
# Optional:
#   --outdir out --tag demo1

import argparse
import os
import datetime
import sys
import pandas as pd

from equity_tool.data import fetch_price_history, fetch_financials_latest
from equity_tool.metrics import (
    cumulative_returns,
    volatility,
    sharpe_ratio,
    max_drawdown,
    beta_vs_benchmark,
    fundamentals_ratios,
)
from equity_tool.plotting import plot_cumulative_returns, plot_price_series
from equity_tool.insights import generate_insights
from equity_tool.report import markdown_report, save_markdown


def run_analysis(
    tickers,
    benchmark,
    start,
    end,
    rf=0.0,
    outdir="reports",
    tag=None,
):
    # Ensure output directory exists
    os.makedirs(outdir, exist_ok=True)

    # Timestamp & filename helpers
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug_tickers = "_".join(tickers)
    slug_bench = benchmark
    tag_part = f"_{tag}" if tag else ""

    def outfile_png(name: str) -> str:
        return os.path.join(outdir, f"{ts}_{name}{tag_part}.png")

    def reportfile_md() -> str:
        return os.path.join(outdir, f"{ts}_equity_report_{slug_tickers}_{slug_bench}{tag_part}.md")

    # -------------------- Fetch prices --------------------
    price_parts = []
    for t in tickers + [benchmark]:
        try:
            df = fetch_price_history(t, start, end)
        except Exception as e:
            print(f"[WARN] Failed to fetch price history for {t}: {e}", file=sys.stderr)
            df = pd.DataFrame()
        if not df.empty:
            price_parts.append(df)

    if not price_parts:
        print("[ERROR] No price data downloaded for the provided tickers/date range.")
        return

    price_df = pd.concat(price_parts, axis=1).dropna(how="all")

    # -------------------- Charts --------------------
    from matplotlib import pyplot as plt

    # Price history chart (only for requested tickers that exist in data)
    present_tickers = [t for t in tickers if t in price_df.columns]
    if len(present_tickers) == 0:
        print("[ERROR] None of the requested tickers have price data in the selected range.")
        return

    fig1 = plot_price_series(price_df[present_tickers], "Price History")
    price_path = outfile_png(f"price_{'_'.join(present_tickers)}")
    fig1.savefig(price_path, dpi=150, bbox_inches="tight")
    plt.close(fig1)

    # Cumulative returns chart (include benchmark if present)
    cum_cols = present_tickers + ([benchmark] if benchmark in price_df.columns else [])
    cumret_df = cumulative_returns(price_df[cum_cols])
    fig2 = plot_cumulative_returns(cumret_df, "Cumulative Returns")
    cumret_path = outfile_png(f"cumret_{'_'.join(cum_cols)}")
    fig2.savefig(cumret_path, dpi=150, bbox_inches="tight")
    plt.close(fig2)

    # -------------------- Risk/Return Metrics --------------------
    vol = volatility(price_df[present_tickers])
    shrp = sharpe_ratio(price_df[present_tickers], rf=rf)
    mdd = price_df[present_tickers].apply(max_drawdown)

    if benchmark in price_df.columns:
        beta = beta_vs_benchmark(price_df[present_tickers + [benchmark]], benchmark)
    else:
        beta = pd.Series(dtype=float)

    risk_tbl = pd.DataFrame(
        {
            "Vol (ann.)": vol.round(3),
            "Sharpe": shrp.round(3),
            "Max Drawdown": mdd.round(3),
            f"Beta vs {benchmark}": beta.round(3),
        }
    )

    print("\n📊 Risk/Return Metrics")
    # to_string keeps a clean console table
    print(risk_tbl.to_string())

    # -------------------- Fundamentals --------------------
    fundamentals_map, fund_tbl_rows = {}, {}
    for t in present_tickers:
        try:
            latest = fetch_financials_latest(t)
            ratios = fundamentals_ratios(latest)
        except Exception as e:
            print(f"[WARN] Fundamentals unavailable for {t}: {e}", file=sys.stderr)
            ratios = {}
        fundamentals_map[t] = ratios
        # Keep a stable set of keys for display
        row = {
            "Gross Margin": ratios.get("Gross Margin"),
            "Operating Margin": ratios.get("Operating Margin"),
            "Net Margin": ratios.get("Net Margin"),
            "ROA": ratios.get("ROA"),
            "ROE": ratios.get("ROE"),
            "Current Ratio": ratios.get("Current Ratio"),
            "Debt to Equity": ratios.get("Debt to Equity"),
        }
        # round floats where present
        fund_tbl_rows[t] = {k: (round(v, 3) if (v is not None and pd.notna(v)) else None) for k, v in row.items()}

    fundamentals_table = pd.DataFrame(fund_tbl_rows)

    print("\n📑 Fundamentals (latest period)")
    print(fundamentals_table.to_string())

    # -------------------- Insights (LLM or heuristic) --------------------
    risk_map = {
        t: {
            "vol": float(vol.get(t)) if not vol.empty else None,
            "sharpe": float(shrp.get(t)) if not shrp.empty else None,
            "mdd": float(mdd.get(t)) if not mdd.empty else None,
            "beta": float(beta.get(t)) if not beta.empty else None,
        }
        for t in present_tickers
    }
    insights = generate_insights(present_tickers, fundamentals_map, risk_map)

    print("\n🧠 Insights")
    print(insights)

    # -------------------- Markdown Report --------------------
    md = markdown_report(
        title="Equity Research Report",
        tickers=present_tickers,
        start=str(start),
        end=str(end),
        metrics_table=risk_tbl.T,              # transpose for nicer markdown
        fundamentals_table=fundamentals_table.T,
        insights_text=insights,
        chart_paths=[price_path, cumret_path],
    )
    report_path = reportfile_md()
    save_markdown(md, outdir, os.path.basename(report_path))

    print("\n✅ Saved files:")
    print(f"  • {price_path}")
    print(f"  • {cumret_path}")
    print(f"  • {report_path}")


def cli():
    parser = argparse.ArgumentParser(description="Equity Research Tool (CLI)")
    parser.add_argument(
        "--tickers",
        nargs="+",
        required=True,
        help="Company tickers (e.g., AAPL MSFT)",
    )
    parser.add_argument(
        "--benchmark",
        default="SPY",
        help="Benchmark ticker (default: SPY)",
    )
    parser.add_argument(
        "--start",
        default="2022-01-01",
        help="Start date YYYY-MM-DD",
    )
    parser.add_argument(
        "--end",
        default=str(datetime.date.today()),
        help="End date YYYY-MM-DD",
    )
    parser.add_argument(
        "--rf",
        type=float,
        default=0.0,
        help="Annual risk-free rate in percent (e.g., 2.0 for 2%%). Default 0.0",
    )
    parser.add_argument(
        "--outdir",
        default="reports",
        help="Output directory (default: reports)",
    )
    parser.add_argument(
        "--tag",
        default=None,
        help="Optional tag appended to filenames (e.g., --tag backtest1)",
    )
    args = parser.parse_args()

    run_analysis(
        tickers=[t.upper() for t in args.tickers],
        benchmark=args.benchmark.upper(),
        start=args.start,
        end=args.end,
        rf=args.rf / 100.0,   # convert % to decimal
        outdir=args.outdir,
        tag=args.tag,
    )


if __name__ == "__main__":
    cli()