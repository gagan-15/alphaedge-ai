/**
 * Scanner Types.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

export interface ScannerResult {
    symbol: string;

    entry_price: number;

    stop_loss: number;

    target_price: number;

    risk_reward_ratio: number;

    confirmation_score: number;

    volume_confirmed: boolean;

    trend_confirmed: boolean;

    momentum_confirmed: boolean;

    confirmed: boolean;

    approved: boolean;

    rejection_reason: string | null;

    zone_type: string | null;
    proximal_price: number | null;
    distal_price: number | null;
    zone_score: number | null;
    distance_percent: number | null;
    zone_fresh: boolean | null;
    touch_count: number | null;
    base_index: number | null;
    timeframe: string | null;
}

export interface ScannerResponse {
    total_scanned: number;

    total_matches: number;

    results: ScannerResult[];
}
