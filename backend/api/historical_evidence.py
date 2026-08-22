"""Read-only Historical Evidence API backed by frozen Milestone 9C data."""

from fastapi import APIRouter, HTTPException, Query

from backend.historical_evidence.constants import HISTORICAL_EVIDENCE_VERSION
from backend.config.canonical_methodology import SCANNER_METHODOLOGY_CACHE_VERSION
from backend.historical_evidence.service import (
    HistoricalEvidenceService,
    HistoricalEvidenceValidationError,
    HistoricalEvidenceVersionMismatch,
)

historical_evidence_router = APIRouter(
    prefix="/historical-evidence", tags=["Historical Evidence"]
)
_service = HistoricalEvidenceService()


def _filters(**values):
    try:
        return _service.filters(**values)
    except HistoricalEvidenceValidationError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception


def _call(method, *args, **kwargs):
    try:
        return method(*args, **kwargs)
    except HistoricalEvidenceVersionMismatch as exception:
        raise HTTPException(status_code=409, detail=str(exception)) from exception


@historical_evidence_router.get("/metadata")
def metadata(dataset_version: str = HISTORICAL_EVIDENCE_VERSION):
    return _call(_service.metadata, dataset_version)


def _query_filters(
    timeframe: str | None,
    zone_type: str | None,
    pattern: str | None,
    zone_quality_label: str | None,
    trade_confidence_label: str | None,
    year: int | None,
    symbol: str | None,
    interaction_status: str,
):
    return _filters(
        timeframe=timeframe,
        zone_type=zone_type,
        pattern=pattern,
        zone_quality_label=zone_quality_label,
        trade_confidence_label=trade_confidence_label,
        year=year,
        symbol=symbol,
        interaction_status=interaction_status,
    )


@historical_evidence_router.get("/summary")
def summary(
    dataset_version: str = HISTORICAL_EVIDENCE_VERSION,
    timeframe: str | None = None,
    zone_type: str | None = None,
    pattern: str | None = None,
    zone_quality_label: str | None = None,
    trade_confidence_label: str | None = None,
    year: int | None = None,
    symbol: str | None = None,
    interaction_status: str = "ALL",
):
    filters = _query_filters(
        timeframe,
        zone_type,
        pattern,
        zone_quality_label,
        trade_confidence_label,
        year,
        symbol,
        interaction_status,
    )
    return _call(_service.summary, dataset_version, filters)


@historical_evidence_router.get("/zones")
def zones(
    dataset_version: str = HISTORICAL_EVIDENCE_VERSION,
    timeframe: str | None = None,
    zone_type: str | None = None,
    pattern: str | None = None,
    zone_quality_label: str | None = None,
    trade_confidence_label: str | None = None,
    year: int | None = None,
    symbol: str | None = None,
    interaction_status: str = "ALL",
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("formation_timestamp"),
    sort_direction: str = Query("desc", pattern="^(asc|desc)$"),
):
    if sort_by not in _service.repository.SORT_COLUMNS:
        raise HTTPException(
            status_code=422, detail=f"Unsupported sort field: {sort_by}"
        )
    filters = _query_filters(
        timeframe,
        zone_type,
        pattern,
        zone_quality_label,
        trade_confidence_label,
        year,
        symbol,
        interaction_status,
    )
    return _call(
        _service.zones,
        dataset_version,
        filters,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )


@historical_evidence_router.get("/comparable-zone")
def comparable_zone(
    zone_id: str,
    timeframe: str,
    zone_type: str,
    pattern: str,
    zone_quality_label: str,
    trade_confidence_label: str,
    dataset_version: str = HISTORICAL_EVIDENCE_VERSION,
    current_methodology_version: str = SCANNER_METHODOLOGY_CACHE_VERSION,
):
    try:
        return _service.comparable_zone(
            dataset_version,
            zone_id=zone_id,
            timeframe=timeframe,
            zone_type=zone_type,
            pattern=pattern,
            zone_quality_label=zone_quality_label,
            trade_confidence_label=trade_confidence_label,
            current_methodology_version=current_methodology_version,
        )
    except HistoricalEvidenceVersionMismatch as exception:
        raise HTTPException(status_code=409, detail=str(exception)) from exception
    except HistoricalEvidenceValidationError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
