# equity_tool/report.py
from __future__ import annotations
import os
import datetime
from typing import List
import pandas as pd

def markdown_report(
    title: str,
    tickers: List[str],
    start: str,
    end: str,
    metrics_table: pd.DataFrame,
    fundamentals_table: pd.DataFrame,
    insights_text: str,
    chart_paths: List[str],
) -> str:
    """
    Build a Markdown report string. `chart_paths` should be relative or absolute
    file paths to PNGs that already exist on disk.
    """
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"_Generated on {ts}_")
    lines.append("")
    lines.append(f"**Tickers**: {', '.join(tickers)} | **Range**: {start} → {end}")
    lines.append("")

    for p in chart_paths or []:
        name = os.path.basename(p)
        lines.append(f"![{name}]({p})")
        lines.append("")

    if isinstance(metrics_table, pd.DataFrame) and not metrics_table.empty:
        lines.append("## Risk/Return Metrics")
        # Display with index
        lines.append(metrics_table.to_markdown(index=True))
        lines.append("")

    if isinstance(fundamentals_table, pd.DataFrame) and not fundamentals_table.empty:
        lines.append("## Fundamentals (latest period)")
        lines.append(fundamentals_table.to_markdown(index=True))
        lines.append("")

    lines.append("## Insights")
    lines.append(insights_text or "(No insights available.)")

    return "\n".join(lines)

def save_markdown(md: str, out_dir: str, filename: str) -> str:
    """
    Save a markdown string to `out_dir/filename` and return the full path.
    """
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    return path