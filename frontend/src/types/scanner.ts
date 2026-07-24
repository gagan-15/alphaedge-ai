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
}

export interface ScannerResponse {
    total_scanned: number;

    total_matches: number;

    results: ScannerResult[];
}