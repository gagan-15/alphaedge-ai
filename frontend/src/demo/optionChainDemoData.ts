/**
 * Development-only option-chain examples.
 *
 * These values are not an exchange feed and are kept separate from the
 * production market-universe and scanner data.
 */
export const optionChainDemoUnderlyings: Record<
    string,
    { spot: number; step: number }
> = {
    NIFTY: { spot: 24731, step: 50 },
    BANKNIFTY: { spot: 54372, step: 100 },
    SAMPLE_STOCK: { spot: 2978, step: 50 },
};
