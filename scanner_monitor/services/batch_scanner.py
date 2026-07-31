"""
batch_scanner.py
================

Institutional Batch Scanner

Runs scans for an entire watchlist / universe and produces:

• Individual ScanResults
• Summary DataFrame
• Market Breadth
• Market Regime
• Segment Analysis
• Composite Market State

No Streamlit code.
"""

from __future__ import annotations

import datetime as dt

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .scanner_service import (
    ScanResult,
    ScannerService,
    apply_universe_ranking,
    compute_breadth,
    compute_regime,
    composite_gate,
    fetch_index,
    fetch_segments,
)


# =============================================================================
# Result Model
# =============================================================================

@dataclass
class BatchScanResult:
    scans: list[ScanResult]

    summary: pd.DataFrame

    market: dict[str, Any]

    returns_matrix: pd.DataFrame


# =============================================================================
# Batch Scanner
# =============================================================================

class BatchScanner:
    """
    Portfolio / Watchlist scanner.

    Executes multiple scans using
    ScannerService and computes
    market-wide analytics.
    """

    def __init__(
        self,
        scanner: ScannerService | None = None,
    ) -> None:

        self.scanner = (
            scanner
            if scanner is not None
            else ScannerService()
        )

    def run(
        self,
        tickers: list[str],
        strategy: str,
        params: dict,
        bt_kwargs: dict,
        start_date: dt.date,
        end_date: dt.date,
        idx_ret_window: float = 0.0,
        sector_map: dict[str, str] | None = None,
        max_workers: int = 8,
    ) -> BatchScanResult:
        """
        Scan an entire watchlist.

        Parameters
        ----------
        tickers
            List of Yahoo Finance symbols.

        strategy
            Strategy name.

        params
            Strategy parameters.

        bt_kwargs
            Backtest parameters.

        start_date
            Historical start date.

        end_date
            Historical end date.

        idx_ret_window
            Benchmark return over RS window.

        sector_map
            Optional ticker → sector mapping.

        max_workers
            Parallel scan workers.

        Returns
        -------
        BatchScanResult
        """

        # ---------------------------------------------------------
        # Run all stock scans
        # ---------------------------------------------------------

        scans = self.scanner.run_batch(
            tickers=tickers,
            strategy=strategy,
            params=params,
            bt_kwargs=bt_kwargs,
            start_date=start_date,
            end_date=end_date,
            idx_ret_window=idx_ret_window,
            sector_map=sector_map,
            max_workers=max_workers,
        )

        if not scans:

            return BatchScanResult(
                scans=[],
                summary=pd.DataFrame(),
                market={},
                returns_matrix=pd.DataFrame(),
            )

        # ---------------------------------------------------------
        # Build summary DataFrame
        # ---------------------------------------------------------

        rows = [
            scan.summary
            for scan in scans
        ]

        summary = pd.DataFrame(rows)

        # ---------------------------------------------------------
        # Historical Returns Matrix
        # ---------------------------------------------------------

        return_series = [
            scan.returns
            for scan in scans
            if scan.returns is not None
            and not scan.returns.empty
        ]

        if return_series:

            returns_matrix = pd.concat(
                return_series,
                axis=1,
                join="inner",
            ).sort_index()

        else:

            returns_matrix = pd.DataFrame()

        # ---------------------------------------------------------
        # Institutional Universe Ranking
        # ---------------------------------------------------------

        if not summary.empty:

            summary = apply_universe_ranking(
                summary,
            )

        # ---------------------------------------------------------
        # Market Breadth
        # ---------------------------------------------------------

        breadth = compute_breadth(rows)

        # ---------------------------------------------------------
        # Benchmark Regime
        # ---------------------------------------------------------

        benchmark, idx_df = fetch_index(
            start_date,
            end_date,
        )

        regime = compute_regime(
            idx_df,
        )

        # ---------------------------------------------------------
        # Mid / Small Cap Segments
        # ---------------------------------------------------------

        segments = fetch_segments(
            start_date,
            end_date,
        )

        # ---------------------------------------------------------
        # Composite Market Gate
        # ---------------------------------------------------------

        composite = composite_gate(
            regime,
            segments,
            breadth,
        )

        # ---------------------------------------------------------
        # Complete Market Snapshot
        # ---------------------------------------------------------

        market = {
            "benchmark": benchmark,
            "breadth": breadth,
            "regime": regime,
            "segments": segments,
            "composite": composite,
            "returns_matrix": returns_matrix,
        }

        # ---------------------------------------------------------
        # Return Result
        # ---------------------------------------------------------

        return BatchScanResult(
            scans=scans,
            summary=summary,
            market=market,
            returns_matrix=returns_matrix,
        )

# =============================================================================
# Compatibility Wrapper
# =============================================================================

_BATCH_SCANNER = BatchScanner()


def run_batch(
    tickers: list[str],
    strategy: str,
    params: dict,
    bt_kwargs: dict,
    start_date: dt.date,
    end_date: dt.date,
    idx_ret_window: float = 0.0,
    sector_map: dict[str, str] | None = None,
    max_workers: int = 8,
) -> BatchScanResult:
    """
    Compatibility wrapper.

    Existing code can call:

        run_batch(...)

    instead of:

        BatchScanner().run(...)
    """

    return _BATCH_SCANNER.run(
        tickers=tickers,
        strategy=strategy,
        params=params,
        bt_kwargs=bt_kwargs,
        start_date=start_date,
        end_date=end_date,
        idx_ret_window=idx_ret_window,
        sector_map=sector_map,
        max_workers=max_workers,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BatchScanResult",
    "BatchScanner",
    "run_batch",
]