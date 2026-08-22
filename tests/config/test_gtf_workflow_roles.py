import pytest

from backend.config.gtf_workflow_roles import (
    WorkflowSource,
    resolve_gtf_workflow,
)


@pytest.mark.parametrize(
    ("execution", "trend", "location"),
    (
        ("5m", "15m", "75m"),
        ("15m", "75m", "1D"),
        ("75m", "1D", "1W"),
        ("125m", "1D", "1W"),
        ("1D", "1W", "1M"),
    ),
)
def test_explicit_gtf_workflows(
    execution: str, trend: str, location: str
) -> None:
    workflow = resolve_gtf_workflow(execution)
    assert workflow.execution == execution
    assert workflow.trend == trend
    assert workflow.location == location
    assert workflow.source == WorkflowSource.EXPLICIT_GTF_MAPPING


@pytest.mark.parametrize("execution", ("3m", "10m"))
def test_unsupported_gtf_timeframes_are_not_silently_substituted(
    execution: str,
) -> None:
    workflow = resolve_gtf_workflow(execution)
    assert workflow.trend is None
    assert workflow.location is None
    assert workflow.source == WorkflowSource.NO_CANONICAL_GTF_WORKFLOW


def test_existing_non_gtf_workflow_is_retained_and_labelled_derived() -> None:
    workflow = resolve_gtf_workflow("4H")
    assert workflow.execution == "4H"
    assert workflow.trend == "1D"
    assert workflow.location == "1W"
    assert workflow.source == WorkflowSource.ALPHAEDGE_DERIVED


def test_yearly_execution_has_no_canonical_gtf_workflow() -> None:
    workflow = resolve_gtf_workflow("1Y")
    assert workflow.trend is None
    assert workflow.source == WorkflowSource.NO_CANONICAL_GTF_WORKFLOW
