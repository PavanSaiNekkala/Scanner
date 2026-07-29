"""
workflow_service.py
===================

Institutional Workflow Orchestrator

Coordinates the complete investment workflow by orchestrating all
business services in the correct execution order.

This module intentionally contains NO business logic.

Responsibilities
----------------
• Workflow Initialization
• Input Validation
• Batch Market Scan
• Portfolio Construction
• Risk Evaluation
• Order Execution
• Report Generation
• Workflow Statistics
• Metadata Collection
• Error Handling

Workflow
--------

Universe / Strategy
        │
        ▼
Batch Scanner
        │
        ▼
Portfolio Manager
        │
        ▼
Risk Manager
        │
        ▼
Execution Service
        │
        ▼
Report Service
        │
        ▼
Workflow Result

No Streamlit dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import logging
import time
import pandas as pd

from .batch_scanner import (
    BatchScanner,
    BatchScanResult,
)

from .portfolio_manager import (
    PortfolioManager,
    PortfolioResult,
)

from .risk_manager import (
    RiskManager,
    RiskResult,
)

from .execution_service import (
    ExecutionService,
    ExecutionResult,
)

from .report_service import (
    ReportService,
    ReportResult,
)

# =============================================================================
# Logger
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================


@dataclass(frozen=True)
class WorkflowConfig:
    """
    Institutional workflow configuration.
    """

    stop_on_scan_failure: bool = True

    stop_on_portfolio_failure: bool = True

    stop_on_risk_failure: bool = True

    stop_on_execution_failure: bool = True

    stop_on_report_failure: bool = True

    enable_logging: bool = True

    collect_metadata: bool = True

    collect_statistics: bool = True

    continue_on_warning: bool = True


# =============================================================================
# Statistics
# =============================================================================


@dataclass
class WorkflowStatistics:
    """
    Workflow execution statistics.
    """

    workflow_started: datetime | None = None

    workflow_completed: datetime | None = None

    total_duration: float = 0.0

    stages_completed: int = 0

    stages_failed: int = 0

    warnings: list[str] = field(
        default_factory=list,
    )

    status: str = "NOT_STARTED"


# =============================================================================
# Workflow Result
# =============================================================================


@dataclass
class WorkflowResult:
    """
    Final workflow output.
    """

    batch: BatchScanResult

    portfolio: PortfolioResult

    risk: RiskResult

    execution: ExecutionResult

    report: ReportResult

    statistics: WorkflowStatistics

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# =============================================================================
# Workflow Service
# =============================================================================


class WorkflowService:
    """
    Institutional workflow orchestrator.

    This service coordinates all platform services
    while intentionally containing no business logic.
    """

    def __init__(
        self,
        scanner: BatchScanner | None = None,
        portfolio: PortfolioManager | None = None,
        risk: RiskManager | None = None,
        execution: ExecutionService | None = None,
        report: ReportService | None = None,
        config: WorkflowConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else WorkflowConfig()
        )

        self.scanner = (
            scanner
            if scanner is not None
            else BatchScanner()
        )

        self.portfolio = (
            portfolio
            if portfolio is not None
            else PortfolioManager()
        )

        self.risk = (
            risk
            if risk is not None
            else RiskManager()
        )

        self.execution = (
            execution
            if execution is not None
            else ExecutionService()
        )

        self.report = (
            report
            if report is not None
            else ReportService()
        )

        logger.info(
            "WorkflowService initialized."
        )

    # =========================================================
    # Public API
    # =========================================================

    def run(
        self,
        tickers: list[str],
        strategy: str,
        params: dict,
        bt_kwargs: dict,
        start_date,
        end_date,
        idx_ret_window: float = 0.0,
        sector_map: dict[str, str] | None = None,
        max_workers: int = 8,
    ) -> WorkflowResult:
        """
        Execute the complete institutional workflow.

        Pipeline
        --------

        Batch Scanner
                │
                ▼
        Portfolio Manager
                │
                ▼
        Risk Manager
                │
                ▼
        Execution Service
                │
                ▼
        Report Service

        Returns
        -------
        WorkflowResult
        """

        start_time = time.perf_counter()

        statistics = WorkflowStatistics(
            workflow_started=datetime.now(),
            status="RUNNING",
        )

        logger.info(
            "Starting institutional workflow."
        )

        # -----------------------------------------------------
        # Validate Inputs
        # -----------------------------------------------------

        self._validate_inputs(
            tickers,
            strategy,
        )

        # -----------------------------------------------------
        # Initialize Metadata
        # -----------------------------------------------------

        metadata: dict[str, Any] = {
            "started_at": datetime.now(),
            "workflow": "Institutional Investment Workflow",
            "version": "1.0",
        }

        # -----------------------------------------------------
        # Stage 1
        # Batch Scanner
        # -----------------------------------------------------

        logger.info(
            "Running BatchScanner..."
        )

        batch = self.scanner.run(
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

        statistics.stages_completed += 1

        metadata["batch_completed"] = datetime.now()

        # -----------------------------------------------------
        # Stage 2
        # Portfolio Manager
        # -----------------------------------------------------

        logger.info(
            "Building portfolio..."
        )

        portfolio = self.portfolio.build_portfolio(
            batch,
        )

        statistics.stages_completed += 1

        metadata["portfolio_completed"] = datetime.now()

        # -----------------------------------------------------
        # Stage 3
        # Risk Manager
        # -----------------------------------------------------

        logger.info(
            "Evaluating portfolio risk..."
        )

        risk = self.risk.evaluate(
            portfolio,
        )

        statistics.stages_completed += 1

        metadata["risk_completed"] = datetime.now()

        # -----------------------------------------------------------------
        # Continue in Part 1B:
        # • Execution Service
        # • Report Service
        # • WorkflowResult construction
        # • Statistics finalization
        # • Private helper methods
        # -----------------------------------------------------------------

        # -----------------------------------------------------
        # Stage 4
        # Execution Service
        # -----------------------------------------------------

        logger.info(
            "Executing portfolio..."
        )

        execution = self.execution.execute(
            portfolio,
            risk,
        )

        statistics.stages_completed += 1

        metadata["execution_completed"] = (
            datetime.now()
        )

        # -----------------------------------------------------
        # Stage 5
        # Report Service
        # -----------------------------------------------------

        logger.info(
            "Generating reports..."
        )

        report = self.report.generate(
            portfolio,
            risk,
            execution,
        )

        statistics.stages_completed += 1

        metadata["report_completed"] = (
            datetime.now()
        )

        # -----------------------------------------------------
        # Final Statistics
        # -----------------------------------------------------

        statistics.workflow_completed = (
            datetime.now()
        )

        statistics.total_duration = (
            time.perf_counter()
            - start_time
        )

        statistics.status = "SUCCESS"

        metadata.update(
            {
                "completed_at": datetime.now(),
                "duration_seconds": round(
                    statistics.total_duration,
                    3,
                ),
                "status": "SUCCESS",
            }
        )

        logger.info(
            "Workflow completed successfully "
            "(%.3f sec).",
            statistics.total_duration,
        )

        return WorkflowResult(
            batch=batch,
            portfolio=portfolio,
            risk=risk,
            execution=execution,
            report=report,
            statistics=statistics,
            metadata=metadata,
        )

    # =========================================================
    # Internal Methods
    # =========================================================

    def _validate_inputs(
        self,
        tickers: list[str],
        strategy: str,
    ) -> None:
        """
        Validate workflow inputs before execution.
        """

        logger.debug(
            "Validating workflow inputs."
        )

        if not tickers:
            raise ValueError(
                "Ticker list cannot be empty."
            )

        if not strategy:
            raise ValueError(
                "Strategy name cannot be empty."
            )

    def _update_metadata(
        self,
        metadata: dict[str, Any],
        stage: str,
    ) -> None:
        """
        Record workflow stage completion.
        """

        metadata[f"{stage}_completed"] = (
            datetime.now()
        )

    def _handle_exception(
        self,
        exc: Exception,
        statistics: WorkflowStatistics,
    ) -> None:
        """
        Update workflow statistics when an error
        occurs.
        """

        statistics.status = "FAILED"

        statistics.stages_failed += 1

        statistics.workflow_completed = (
            datetime.now()
        )

        logger.exception(
            "Workflow execution failed: %s",
            exc,
        )

        raise

# =============================================================================
# Singleton
# =============================================================================

_WORKFLOW_SERVICE = WorkflowService()

# =============================================================================
# Convenience Function
# =============================================================================


def run_workflow(
    *args,
    **kwargs,
) -> WorkflowResult:
    """
    Execute the complete institutional workflow.

    Parameters
    ----------
    *args
        Forwarded to BatchScanner.

    **kwargs
        Forwarded to BatchScanner.

    Returns
    -------
    WorkflowResult
        Complete workflow output.
    """

    return _WORKFLOW_SERVICE.run(
        *args,
        **kwargs,
    )


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "WorkflowConfig",
    "WorkflowStatistics",
    "WorkflowResult",
    "WorkflowService",
    "run_workflow",
]