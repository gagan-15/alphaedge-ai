"""Role-aware Location/Trend/Execution workflows for canonical GTF context."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.config.timeframe_hierarchy import get_timeframe_hierarchy


class WorkflowSource(str, Enum):
    """State whether a workflow is explicit in GTF or retained by AlphaEdge."""

    EXPLICIT_GTF_MAPPING = "EXPLICIT_GTF_MAPPING"
    ALPHAEDGE_DERIVED = "ALPHAEDGE_DERIVED"
    NO_CANONICAL_GTF_WORKFLOW = "NO_CANONICAL_GTF_WORKFLOW"


@dataclass(frozen=True)
class TimeframeWorkflow:
    """Role assignment for one selected execution timeframe."""

    location: str | None
    trend: str | None
    execution: str
    source: WorkflowSource


# These mappings are printed explicitly in the GTF workflow table. The
# unsupported 3-minute and 10-minute alternatives are intentionally absent.
EXPLICIT_GTF_WORKFLOWS: dict[str, TimeframeWorkflow] = {
    "5m": TimeframeWorkflow("75m", "15m", "5m", WorkflowSource.EXPLICIT_GTF_MAPPING),
    "15m": TimeframeWorkflow("1D", "75m", "15m", WorkflowSource.EXPLICIT_GTF_MAPPING),
    "75m": TimeframeWorkflow("1W", "1D", "75m", WorkflowSource.EXPLICIT_GTF_MAPPING),
    "125m": TimeframeWorkflow("1W", "1D", "125m", WorkflowSource.EXPLICIT_GTF_MAPPING),
    "1D": TimeframeWorkflow("1M", "1W", "1D", WorkflowSource.EXPLICIT_GTF_MAPPING),
}

UNSUPPORTED_GTF_EXECUTION_TIMEFRAMES = frozenset({"3m", "10m"})


def resolve_gtf_workflow(execution_timeframe: str) -> TimeframeWorkflow:
    """Resolve roles without pretending derived mappings are explicit GTF."""

    normalized = execution_timeframe.strip()
    explicit = EXPLICIT_GTF_WORKFLOWS.get(normalized)
    if explicit is not None:
        return explicit
    if normalized in UNSUPPORTED_GTF_EXECUTION_TIMEFRAMES:
        return TimeframeWorkflow(
            None,
            None,
            normalized,
            WorkflowSource.NO_CANONICAL_GTF_WORKFLOW,
        )

    # Preserve existing product workflows for timeframes not defined by GTF,
    # while labelling them honestly as AlphaEdge-derived.
    legacy_key = normalized.upper()
    hierarchy = get_timeframe_hierarchy(legacy_key)
    if hierarchy.trend is None:
        return TimeframeWorkflow(
            hierarchy.location,
            None,
            normalized,
            WorkflowSource.NO_CANONICAL_GTF_WORKFLOW,
        )
    return TimeframeWorkflow(
        hierarchy.location,
        hierarchy.trend,
        normalized,
        WorkflowSource.ALPHAEDGE_DERIVED,
    )
