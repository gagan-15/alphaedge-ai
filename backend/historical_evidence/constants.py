"""Frozen Historical Evidence package identity and supported query values."""

from pathlib import Path

HISTORICAL_EVIDENCE_ARCHITECTURE_VERSION = "historical-evidence-v1"
HISTORICAL_EVIDENCE_VERSION = "milestone-9c.1"
EXPECTED_METHODOLOGY_FINGERPRINT = (
    "034ebdd6c52e0c161fda7cde9be4157e9ad250786fe98c3b0f02bfbc5030d015"
)
EXPECTED_RECORD_COUNT = 37_725
EXPECTED_TC_COUNTS = {
    "VERY_HIGH": 0,
    "HIGH": 270,
    "MODERATE": 7_237,
    "LOW": 5_141,
    "CONFLICTED": 2_653,
    "INSUFFICIENT_CONTEXT": 22_424,
}
EXPECTED_SHARD_SHA256 = {
    "shard-0.json": "8c59886db2c96dfb082d7f1f06bb3e71d824699fb9a85b9b46e9732d0c64ba35",
    "shard-1.json": "5e3338e64fdd17f482515adda21e123c47d2b84be5041228f96e8cfd0ae4f8ff",
    "shard-2.json": "8f5e17882443fc0f99c4d11a0b1b882a4c634ccd677b5d76ac6c470f002be185",
    "shard-3.json": "9374fe63972fd0f9489717f851ea08efbda92292e93684531f94aaadd5142bd9",
}
DATASET_PERIOD = {"start": "2021-08-18", "end": "2026-08-18"}
SUPPORTED_TIMEFRAMES = frozenset({"1D", "1W"})
UNSUPPORTED_VALIDATION_TIMEFRAMES = frozenset({"15M", "75M", "125M"})
TC_LABELS = tuple(EXPECTED_TC_COUNTS)
ZQ_LABELS = ("ELITE", "STRONG", "GOOD", "AVERAGE", "MODERATE", "WEAK")
PATTERNS = ("DBR", "RBR", "RBD", "DBD")
ZONE_TYPES = ("DEMAND", "SUPPLY")
INTERACTION_STATUSES = ("ALL", "INTERACTED", "NOT_INTERACTED")

PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_DATABASE_PATH = (
    PACKAGE_ROOT / "data" / f"historical-evidence-{HISTORICAL_EVIDENCE_VERSION}.sqlite3"
)
