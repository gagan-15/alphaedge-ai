from backend.api.models.scanner_response import ZoneQualityComponentResponse
from tests.engines.test_canonical_zone_quality_engine import context, score, zone


def test_canonical_quality_components_serialize_without_recalculation():
    canonical = score(zone(), context())
    serialized = tuple(
        ZoneQualityComponentResponse(
            key=component.key,
            score=component.score,
            maximum_score=component.maximum_score,
            evidence=component.evidence,
            reason_codes=component.reason_codes,
        )
        for component in canonical.components
    )

    assert len(serialized) == 6
    assert round(sum(component.score for component in serialized), 1) == (
        canonical.total_score
    )
    assert sum(component.maximum_score for component in serialized) == 100
    serialized_reasons = tuple(
        code for component in serialized for code in component.reason_codes
    )
    assert serialized_reasons == canonical.reason_codes
