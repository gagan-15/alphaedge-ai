"""
Market opportunity analysis service.

This service connects validated market data to the existing zone, setup,
confirmation, and risk engines for one symbol.
"""

from pandas import DataFrame

from backend.config.entry_confirmation_config import EntryConfirmationConfig
from backend.config.risk_management_config import RiskManagementConfig
from backend.config.scanner_config import ScannerConfig
from backend.engines.demand_supply_engine.demand_supply_engine import (
    DemandSupplyEngine,
)
from backend.engines.entry_confirmation.entry_confirmation_engine import (
    EntryConfirmationEngine,
)
from backend.engines.risk_management_engine.risk_management_engine import (
    RiskManagementEngine,
)
from backend.engines.trade_setup_engine.trade_setup_engine import TradeSetupEngine
from backend.engines.zone_ranking_engine.zone_ranking_engine import ZoneRankingEngine
from backend.engines.zone_scoring_engine.zone_scoring_engine import ZoneScoringEngine
from backend.models.screener.screened_opportunity import ScreenedOpportunity
from backend.models.zone import Zone, ZoneType
from backend.services.indicator.indicator_service import IndicatorService
from backend.services.market_data.market_data_service import MarketDataService


class MarketOpportunityService:
    """
    Build one risk-checked opportunity from a symbol's market data.
    """

    def __init__(
        self,
        market_data_service: MarketDataService,
        config: ScannerConfig,
        demand_supply_engine: DemandSupplyEngine | None = None,
        indicator_service: IndicatorService | None = None,
    ) -> None:
        """
        Initialize the analysis pipeline.
        """

        self._market_data_service = market_data_service
        self._config = config
        self._demand_supply_engine = demand_supply_engine or DemandSupplyEngine()
        self._indicator_service = indicator_service or IndicatorService()
        self._zone_scoring_engine = ZoneScoringEngine()
        self._zone_ranking_engine = ZoneRankingEngine()
        self._trade_setup_engine = TradeSetupEngine()
        self._entry_confirmation_engine = EntryConfirmationEngine(
            EntryConfirmationConfig(),
        )
        self._risk_management_engine = RiskManagementEngine(
            RiskManagementConfig(),
        )

    def analyze(
        self,
        symbol: str,
    ) -> ScreenedOpportunity | None:
        """
        Analyze one symbol and return its best approved long opportunity.
        """

        market_data = self._market_data_service.get_stock_data(
            symbol=symbol,
            period=self._config.period,
            interval=self._config.interval,
        )
        current_price = float(market_data["Close"].iloc[-1])
        zones = self._eligible_demand_zones(
            zones=self._demand_supply_engine.detect(market_data),
            current_price=current_price,
        )

        if not zones:
            return None

        scored = self._zone_scoring_engine.score(zones)
        ranked = self._zone_ranking_engine.rank(scored.scored_zones)
        setup_result = self._trade_setup_engine.generate(
            ranked.ranked_zones[:1],
        )
        trade_setup = setup_result.trade_setups[0]

        volume_confirmed = self._is_volume_confirmed(market_data)
        trend_confirmed = self._is_trend_confirmed(market_data)
        momentum_confirmed = self._is_momentum_confirmed(market_data)
        confirmation_score = self._confirmation_score(
            zone_score=ranked.ranked_zones[0].zone_score.total_score,
            volume_confirmed=volume_confirmed,
            trend_confirmed=trend_confirmed,
            momentum_confirmed=momentum_confirmed,
        )
        confirmation = self._entry_confirmation_engine.confirm(
            trade_setup=trade_setup,
            volume_confirmed=volume_confirmed,
            trend_confirmed=trend_confirmed,
            momentum_confirmed=momentum_confirmed,
            confirmation_score=confirmation_score,
        )
        risk_result = self._risk_management_engine.evaluate(
            entry_confirmation=confirmation,
            account_balance=self._config.account_balance,
            entry_price=trade_setup.entry_price,
            stop_loss_price=trade_setup.stop_loss,
            target_price=trade_setup.target_price,
        )

        return ScreenedOpportunity(
            symbol=symbol,
            risk_management_result=risk_result,
        )

    def _eligible_demand_zones(
        self,
        zones: list[Zone],
        current_price: float,
    ) -> list[Zone]:
        """
        Keep fresh demand zones close enough to the current price.
        """

        eligible: list[Zone] = []

        for zone in zones:
            if zone.zone_type != ZoneType.DEMAND or not zone.is_fresh:
                continue

            if current_price < zone.lower_price:
                continue

            distance = max(
                0.0,
                current_price - zone.upper_price,
            )
            distance_percent = distance / current_price * 100

            if distance_percent <= self._config.maximum_zone_distance_percent:
                eligible.append(zone)

        return eligible

    def _is_volume_confirmed(
        self,
        market_data: DataFrame,
    ) -> bool:
        result = self._indicator_service.calculate_volume_confirmation(
            market_data.copy(),
            self._config.volume_period,
        )

        return result["Volume_Confirmation"].iloc[-1] in {
            "Normal",
            "High",
            "Very High",
        }

    def _is_trend_confirmed(
        self,
        market_data: DataFrame,
    ) -> bool:
        result = self._indicator_service.calculate_sma(
            market_data.copy(),
            self._config.trend_period,
        )

        return bool(
            result["Close"].iloc[-1]
            > result[f"SMA_{self._config.trend_period}"].iloc[-1]
        )

    def _is_momentum_confirmed(
        self,
        market_data: DataFrame,
    ) -> bool:
        result = self._indicator_service.calculate_rsi(
            market_data.copy(),
            self._config.momentum_period,
        )
        current_momentum = float(result.iloc[-1])

        return (
            self._config.minimum_momentum
            <= current_momentum
            <= self._config.maximum_momentum
        )

    @staticmethod
    def _confirmation_score(
        zone_score: float,
        volume_confirmed: bool,
        trend_confirmed: bool,
        momentum_confirmed: bool,
    ) -> float:
        """
        Combine zone quality and three independent confirmations.
        """

        indicator_score = 20.0 * sum(
            (
                volume_confirmed,
                trend_confirmed,
                momentum_confirmed,
            )
        )

        return round(
            min(
                100.0,
                zone_score * 0.4 + indicator_score,
            ),
            2,
        )
