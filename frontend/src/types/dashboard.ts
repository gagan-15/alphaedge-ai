/**
 * Dashboard Models.
 *
 * Sprint:
 *     2.50 - Frontend Foundation
 */

export interface PortfolioResult {
    total_positions: number;
    invested_capital: number;
    available_capital: number;
    total_capital: number;
}

export interface BacktestResult {
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
}

export interface AlertResult {
    title: string;
    message: string;
    priority: string;
    requires_action: boolean;
}

export interface AIExplanationResult {
    decision: string;
    reasons: string[];
    confidence_score: number;
    summary: string;
}

export interface MarketScannerResult {
    scanned_symbols: number;
}

export interface MarketOverviewResult {
    nifty50: number;
    nifty_change: number;

    sensex: number;
    sensex_change: number;

    bank_nifty: number;
    bank_nifty_change: number;

    india_vix: number;
    india_vix_change: number;
}

export interface DashboardResult {
    market: MarketOverviewResult;
    portfolio: PortfolioResult;
    alerts: AlertResult[];
    scanner: MarketScannerResult;
    backtest: BacktestResult;
    ai_explanation: AIExplanationResult;
}