"""Provider-independent models for the canonical zone lifecycle engine.

These models intentionally live beside the legacy freshness models.  Stage 1
does not connect them to scanner, scoring, alerts, or stock-details flows.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ZoneLifecycleStatus(str, Enum):
    """Supported lifecycle states for a demand or supply zone."""

    FORMING = "FORMING"
    ACTIVATED = "ACTIVATED"
    FRESH = "FRESH"
    APPROACHING = "APPROACHING"
    TESTING_NOW = "TESTING_NOW"
    TESTED_RESPECTED = "TESTED_RESPECTED"
    RETESTED = "RETESTED"
    MITIGATED = "MITIGATED"
    INVALIDATED = "INVALIDATED"


class ZoneLifecycleType(str, Enum):
    """Direction of a canonical lifecycle zone."""

    DEMAND = "DEMAND"
    SUPPLY = "SUPPLY"


class ZoneInteractionType(str, Enum):
    """Observable price interactions kept separately for auditability."""

    PROXIMAL_TAG = "PROXIMAL_TAG"
    WICK_TEST = "WICK_TEST"
    BODY_OVERLAP = "BODY_OVERLAP"
    CLOSE_INSIDE = "CLOSE_INSIDE"
    DISTAL_WICK_BREACH = "DISTAL_WICK_BREACH"
    DISTAL_CLOSE_BREACH = "DISTAL_CLOSE_BREACH"


class ZoneInvalidationReason(str, Enum):
    """Confirmed reasons a lifecycle can become terminal."""

    DEMAND_CLOSE_BELOW_DISTAL = "DEMAND_CLOSE_BELOW_DISTAL"
    SUPPLY_CLOSE_ABOVE_DISTAL = "SUPPLY_CLOSE_ABOVE_DISTAL"


@dataclass(frozen=True)
class LifecycleCandle:
    """Minimal OHLC candle required by the lifecycle engine."""

    index: int
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    is_closed: bool = True

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("Candle index cannot be negative.")
        if self.high < self.low:
            raise ValueError("Candle high cannot be below candle low.")
        if not self.low <= self.open <= self.high:
            raise ValueError("Candle open must be inside its high-low range.")
        if not self.low <= self.close <= self.high:
            raise ValueError("Candle close must be inside its high-low range.")


@dataclass(frozen=True)
class ZoneActivation:
    """Explicit separation between formation, departure, and monitoring."""

    formation_start_index: int
    formation_end_index: int
    departure_confirmation_index: int | None
    activation_index: int | None
    monitoring_start_index: int | None
    departure_confirmed: bool
    activation_time: datetime | None = None

    def __post_init__(self) -> None:
        if self.formation_start_index < 0:
            raise ValueError("Formation start index cannot be negative.")
        if self.formation_end_index < self.formation_start_index:
            raise ValueError("Formation end must not precede formation start.")
        if not self.departure_confirmed:
            return
        required = (
            self.departure_confirmation_index,
            self.activation_index,
            self.monitoring_start_index,
        )
        if any(value is None for value in required):
            raise ValueError(
                "Confirmed departure requires confirmation, activation, "
                "and monitoring indices."
            )
        if self.departure_confirmation_index < self.formation_end_index:
            raise ValueError("Departure cannot be confirmed before formation ends.")
        if self.activation_index < self.departure_confirmation_index:
            raise ValueError("Activation cannot precede departure confirmation.")
        if self.monitoring_start_index <= self.activation_index:
            raise ValueError("Monitoring must begin after the activation candle.")


@dataclass(frozen=True)
class ZoneLifecycleDefinition:
    """Immutable zone boundaries and identity used during evaluation."""

    zone_id: str
    symbol: str
    timeframe: str
    zone_type: ZoneLifecycleType
    proximal: float
    distal: float
    activation: ZoneActivation
    tick_size: float | None = None
    atr: float | None = None

    def __post_init__(self) -> None:
        if not self.zone_id.strip():
            raise ValueError("Zone ID is required.")
        if not self.symbol.strip():
            raise ValueError("Symbol is required.")
        if not self.timeframe.strip():
            raise ValueError("Timeframe is required.")
        if self.zone_type == ZoneLifecycleType.DEMAND:
            if self.proximal <= self.distal:
                raise ValueError("Demand proximal must be above distal.")
        elif self.proximal >= self.distal:
            raise ValueError("Supply proximal must be below distal.")
        if self.tick_size is not None and self.tick_size <= 0:
            raise ValueError("Tick size must be positive.")
        if self.atr is not None and self.atr <= 0:
            raise ValueError("ATR must be positive.")

    @property
    def width(self) -> float:
        """Absolute width of the zone."""

        return abs(self.proximal - self.distal)


@dataclass(frozen=True)
class ZoneInteraction:
    """Facts observed for one candle during lifecycle evaluation."""

    interaction_type: ZoneInteractionType
    candle_index: int
    occurred_at: datetime
    price: float
    penetration_percent: float
    is_confirmed: bool
    visit_id: str | None


@dataclass(frozen=True)
class ZoneVisit:
    """One continuous visit, regardless of the candles spent in the zone."""

    visit_id: str
    start_index: int
    start_time: datetime
    end_index: int | None
    end_time: datetime | None
    maximum_penetration_percent: float
    interaction_types: tuple[ZoneInteractionType, ...]
    rejection_confirmed: bool
    respected: bool | None


@dataclass(frozen=True)
class ZoneLifecycleResult:
    """Complete, immutable lifecycle facts for one evaluation."""

    zone_id: str
    symbol: str
    source_timeframe: str
    lifecycle_status: ZoneLifecycleStatus
    structural_status: ZoneLifecycleStatus
    is_fresh: bool
    is_approaching: bool
    test_count: int
    visit_count: int
    penetration_percent: float
    max_penetration_percent: float
    current_interaction: ZoneInteractionType | None
    last_interaction: ZoneInteractionType | None
    last_tested_at: datetime | None
    invalidated_at: datetime | None
    invalidation_reason: ZoneInvalidationReason | None
    interactions: tuple[ZoneInteraction, ...] = field(default_factory=tuple)
    visits: tuple[ZoneVisit, ...] = field(default_factory=tuple)
