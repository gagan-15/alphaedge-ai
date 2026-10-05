/**
 * Scanner Page.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Chip from "@mui/material/Chip";
import IconButton from "@mui/material/IconButton";
import MenuItem from "@mui/material/MenuItem";
import LinearProgress from "@mui/material/LinearProgress";
import Select from "@mui/material/Select";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { cancelDhanIncrementalUpdate, getDhanRuntimeStatus, getPersistedZonePage, getResearchZones, getScannerCapabilities, startDhanIncrementalUpdate, type DhanRuntimeStatus } from "../api/scannerApi";
import ScannerResultsTable from "../components/scanner/ScannerResultsTable";
import DhanDataStatus from "../components/scanner/DhanDataStatus";
import ScannerToolbar, { type ScannerQuickPreset } from "../components/scanner/ScannerToolbar";
import TradingChart from "../components/dashboard/TradingChart";
import {
    rowsForSelectedTimeframe,
    scannerSelectionMatches,
    shouldRequestScannerBuild,
    timeframeStatusMessage,
} from "../components/scanner/scannerTimeframeState";

import type { ZoneResearchResponse } from "../types/scanner";
import { marketUniverseOptions, useMarketUniverse, type MarketUniverse } from "../market-universe/MarketUniverseState";

const scannerResultCache = new Map<string, ZoneResearchResponse>();
const scannerMethodologyVersion = "formation-1.1";

const timeframes = [
    { value: "DAILY", label: "Daily" }, { value: "WEEKLY", label: "Weekly" },
    { value: "MONTHLY", label: "Monthly" }, { value: "QUARTERLY", label: "Quarterly" },
    { value: "HALFYEARLY", label: "Half-yearly" }, { value: "YEARLY", label: "Yearly" },
] as const;
const intradayTimeframes = [
    { value: "MINUTE_15", label: "15m" },
    { value: "MINUTE_75", label: "75m" }, { value: "MINUTE_125", label: "125m" },
    { value: "HOUR_1", label: "1H" },
] as const;

function scannerPreference<T>(key: "defaultTimeframe" | "minimumQuality", fallback: T): T {
    try {
        const preferences = JSON.parse(localStorage.getItem("alphaedge.local.preferences") ?? "{}");
        return (preferences[key] ?? fallback) as T;
    } catch {
        return fallback;
    }
}

function Scanner() {
    const { marketUniverse, setMarketUniverse, customSymbols } = useMarketUniverse();
    const location = useLocation();
    const navigate = useNavigate();
    const { symbol: routeSymbol } = useParams();
    const initialFilters = location.state as {
        zoneType?: "DEMAND" | "SUPPLY";
        timeframe?: string;
        symbol?: string;
        selectedZone?: "demand" | "supply";
        proximalPrice?: number;
        distalPrice?: number;
        baseIndex?: number;
        instrumentOnly?: boolean;
        instrumentName?: string;
    } | null;
    const [scanner, setScanner] =
        useState<ZoneResearchResponse | null>(null);
    const [isLoading, setIsLoading] =
        useState(true);
    const [errorMessage, setErrorMessage] =
        useState<string | null>(null);
    const [searchQuery, setSearchQuery] =
        useState("");
    const [minimumScore, setMinimumScore] = useState(() => scannerPreference("minimumQuality", 40));
    const [approvalFilter, setApprovalFilter] = useState(
        initialFilters?.zoneType === "DEMAND" || initialFilters?.selectedZone === "demand"
            ? "approved"
            : initialFilters?.zoneType === "SUPPLY" || initialFilters?.selectedZone === "supply"
                ? "rejected"
                : "approved",
    );
    const [timeframe, setTimeframe] = useState(
        () => initialFilters?.timeframe ?? scannerPreference("defaultTimeframe", "DAILY"),
    );
    const [market, setMarket] = useState("NSE");
    const [universeOptions, setUniverseOptions] = useState<Array<{ value: MarketUniverse; label: string }>>(
        marketUniverseOptions.map((option) => ({ ...option })),
    );
    const [patternFilter, setPatternFilter] = useState("all");
    const [statusFilter, setStatusFilter] = useState("all");
    const [proximityFilter, setProximityFilter] = useState(100);
    const [actionableActive, setActionableActive] = useState(false);
    const [effectiveFilters, setEffectiveFilters] = useState(() => ({
        searchQuery: "",
        minimumScore: scannerPreference("minimumQuality", 40),
        approvalFilter: initialFilters?.zoneType === "DEMAND" || initialFilters?.selectedZone === "demand"
            ? "approved"
            : initialFilters?.zoneType === "SUPPLY" || initialFilters?.selectedZone === "supply"
                ? "rejected"
                : "approved",
        patternFilter: "all",
        statusFilter: "all",
        proximityFilter: 100,
        market: "NSE",
    }));
    const [insightVisible, setInsightVisible] = useState(true);
    const [resultPage, setResultPage] = useState(1);
    const [resultSort, setResultSort] = useState<"contextual_rank" | "symbol" | "trade_confidence" | "zone_quality" | "distance" | "current_price">("contextual_rank");
    const [resultSortDirection, setResultSortDirection] = useState<"asc" | "desc">("asc");
    const [persistedResults, setPersistedResults] = useState<ZoneResearchResponse["results"]>([]);
    const [persistedTotal, setPersistedTotal] = useState(0);
    const [persistedState, setPersistedState] = useState<
        "LOADING" | "READY" | "BUILDING" | "STALE" | "FAILED" | "UNAVAILABLE"
    >("LOADING");
    const [persistedRefreshState, setPersistedRefreshState] = useState<"BUILDING" | null>(null);
    const [persistedProgress, setPersistedProgress] = useState({ processed: 0, total: 0 });
    const [persistedReloadNonce, setPersistedReloadNonce] = useState(0);
    const [dhanRuntimeStatus, setDhanRuntimeStatus] = useState<DhanRuntimeStatus | null>(null);
    const [persistedSelection, setPersistedSelection] = useState({
        timeframe,
        universe: marketUniverse,
    });
    const requestVersion = useRef(0);
    const updateWasRunning = useRef(false);
    const instrumentOnly = location.pathname.startsWith("/stock-details/")
        && (!initialFilters?.selectedZone || initialFilters.instrumentOnly === true);

    function loadScanner(selectedTimeframe = timeframe) {
        const version = ++requestVersion.current;
        const watchlist = marketUniverse === "watchlist"
            ? JSON.parse(localStorage.getItem("alphaedge.local.watchlist") ?? "[]")
            : [];
        const suppliedSymbols = marketUniverse === "custom"
            ? customSymbols
            : watchlist;
        const cacheKey = `${scannerMethodologyVersion}:${selectedTimeframe}:${marketUniverse}:${suppliedSymbols.join(",")}`;
        const cached = scannerResultCache.get(cacheKey);
        let receivedScannerResponse = Boolean(cached);
        if (cached) {
            queueMicrotask(() => {
                if (version !== requestVersion.current) return;
                setScanner(cached);
                setIsLoading(false);
                setErrorMessage(null);
            });
        }
        const poll = () => void getResearchZones(
            selectedTimeframe,
            marketUniverse,
            suppliedSymbols,
            location.pathname.startsWith("/stock-details/"),
        )
            .then((data) => {
                if (version !== requestVersion.current) return;
                receivedScannerResponse = true;
                const hasCompletedSnapshot = Boolean(data.last_completed_at)
                    || data.status === "completed";
                if (
                    hasCompletedSnapshot
                    && data.methodology_version === scannerMethodologyVersion
                ) {
                    scannerResultCache.set(cacheKey, data);
                }
                setScanner(data);
                // The request itself has completed. A queued/background scan is
                // refresh progress, not a reason to block the whole Dashboard.
                setIsLoading(false);
                setErrorMessage(null);
                if (data.status === "refreshing" || data.status === "queued") {
                    window.setTimeout(poll, 5000);
                }
            })
            .catch((error: unknown) => {
                if (version !== requestVersion.current) return;
                console.error(
                    "Failed to load scanner.",
                    error,
                );

                if (!receivedScannerResponse) {
                    setIsLoading(false);
                    setErrorMessage(
                        "Scanner data could not be loaded. Check that the backend is running.",
                    );
                }
            })
            .finally(() => undefined);
        poll();
    }

    function reloadScanner() {
        // Dashboard Refresh is strictly a read of the currently published
        // persisted snapshot.  It must never enter the legacy scanner route
        // or start a Dhan incremental/canonical recalculation.
        if (market !== "NSE") {
            setIsLoading(false);
            return;
        }
        setIsLoading(true);
        setErrorMessage(null);
        setPersistedReloadNonce((value) => value + 1);
    }

    function updateDhanData() {
        setErrorMessage(null);
        void startDhanIncrementalUpdate().then(() => {
            updateWasRunning.current = true;
            return getDhanRuntimeStatus();
        }).then((status) => {
            setDhanRuntimeStatus(status);
        }).catch(() => {
            setErrorMessage("Unable to start the Dhan update. Existing AlphaEdge data remains available.");
        });
    }

    function cancelDhanDataUpdate() {
        const runId = dhanRuntimeStatus?.last_update.run_id;
        if (!runId) return;
        setErrorMessage(null);
        void cancelDhanIncrementalUpdate(runId).then((status) => {
            setDhanRuntimeStatus((current) => current ? {
                ...current,
                data_status: "CANCELLING",
                last_update: { ...current.last_update, status: status.status, stage: status.message },
            } : current);
        }).catch(() => {
            setErrorMessage("Unable to cancel the Dhan update. Existing AlphaEdge data remains available.");
        });
    }

    function changeTimeframe(value: string) {
        setIsLoading(true);
        setErrorMessage(null);
        setPersistedResults([]);
        setPersistedTotal(0);
        setPersistedState("LOADING");
        setPersistedRefreshState(null);
        setTimeframe(value);
        try {
            const preferences = JSON.parse(localStorage.getItem("alphaedge.local.preferences") ?? "{}");
            localStorage.setItem(
                "alphaedge.local.preferences",
                JSON.stringify({ ...preferences, defaultTimeframe: value }),
            );
        } catch {
            // A storage failure must not block timeframe selection.
        }
    }

    function changeUniverse(value: MarketUniverse) {
        setMarketUniverse(value);
        setIsLoading(true);
        setErrorMessage(null);
        setPersistedResults([]);
        setPersistedTotal(0);
        setPersistedState("LOADING");
    }

    function toggleActionableZones() {
        setActionableActive((active) => {
            if (!active) {
                // Existing server-side filters preserve global ordering and
                // pagination; this only applies a convenience filter set.
                setMinimumScore(70); // Canonical Zone Quality: GOOD and above.
                setStatusFilter("APPROACHING");
                setProximityFilter(5);
            }
            return !active;
        });
    }

    function changeManualFilter(change: () => void) {
        setActionableActive(false);
        change();
    }

    function applyQuickPreset(preset: ScannerQuickPreset) {
        if (preset === "fresh-demand") {
            setApprovalFilter("approved");
            setStatusFilter("APPROACHING");
        } else if (preset === "fresh-supply") {
            setApprovalFilter("rejected");
            setStatusFilter("APPROACHING");
        } else if (preset === "near-entry") {
            setProximityFilter(5);
        } else if (preset === "high-confidence") {
            setMinimumScore(90);
        } else if (preset === "swing") {
            changeTimeframe("DAILY");
        } else if (preset === "intraday") {
            changeTimeframe("HOUR_1");
        } else if (preset === "todays-best") {
            setMinimumScore(75);
            setStatusFilter("APPROACHING");
            setProximityFilter(3);
        } else {
            setActionableActive(false);
            setSearchQuery("");
            setMinimumScore(scannerPreference("minimumQuality", 40));
            setApprovalFilter("approved");
            setMarket("NSE");
            setPatternFilter("all");
            setStatusFilter("all");
            setProximityFilter(100);
            changeTimeframe(scannerPreference("defaultTimeframe", "DAILY"));
        }
    }

    useEffect(() => {
        void getScannerCapabilities(marketUniverse).then((capabilities) => {
            const supported = capabilities.universes.filter((item) => item.instrument_count > 0);
            setUniverseOptions(supported.map((item) => ({
                value: item.id,
                label: `${marketUniverseOptions.find((option) => option.value === item.id)?.label.replace(/ \([\d,]+\)$/, "") ?? item.id} (${item.instrument_count.toLocaleString("en-IN")})`,
            })));
        }).catch(() => undefined);
    }, [marketUniverse]);

    useEffect(() => {
        if (market !== "NSE") {
            return;
        }
        if (location.pathname.startsWith("/stock-details/") && !instrumentOnly) {
            loadScanner(timeframe);
        } else {
            queueMicrotask(() => setIsLoading(false));
        }
        return () => {
            requestVersion.current += 1;
        };
        // The selected timeframe is the request boundary.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [customSymbols, instrumentOnly, market, marketUniverse, timeframe]);

    useEffect(() => {
        const handleSearch = (event: Event) => setSearchQuery(String((event as CustomEvent).detail ?? ""));
        window.addEventListener("alphaedge:global-search", handleSearch);
        return () => window.removeEventListener("alphaedge:global-search", handleSearch);
    }, []);

    useEffect(() => {
        const timeout = window.setTimeout(() => {
            setEffectiveFilters({ searchQuery, minimumScore, approvalFilter, patternFilter, statusFilter, proximityFilter, market });
        }, 350);
        return () => window.clearTimeout(timeout);
    }, [approvalFilter, market, minimumScore, patternFilter, proximityFilter, searchQuery, statusFilter]);

    useEffect(() => {
        if (location.pathname.startsWith("/stock-details/") || market !== "NSE") return;
        const watchlist = marketUniverse === "watchlist"
            ? JSON.parse(localStorage.getItem("alphaedge.local.watchlist") ?? "[]")
            : [];
        const suppliedSymbols = marketUniverse === "custom" ? customSymbols : watchlist;
        let active = true;
        queueMicrotask(() => {
            if (!active) return;
            setPersistedResults([]);
            setPersistedTotal(0);
            setPersistedState("LOADING");
            setPersistedRefreshState(null);
            setPersistedProgress({ processed: 0, total: 0 });
        });
        void getPersistedZonePage({
            timeframe,
            universe: marketUniverse,
            symbols: suppliedSymbols,
            zoneType: effectiveFilters.approvalFilter === "approved" ? "DEMAND"
                : effectiveFilters.approvalFilter === "rejected" ? "SUPPLY" : undefined,
            pattern: effectiveFilters.patternFilter === "all" ? undefined : effectiveFilters.patternFilter,
            minimumQuality: effectiveFilters.minimumScore,
            status: effectiveFilters.statusFilter === "all" ? undefined : effectiveFilters.statusFilter,
            maxDistance: effectiveFilters.proximityFilter < 100 ? effectiveFilters.proximityFilter : undefined,
            symbol: effectiveFilters.searchQuery || undefined,
            sort: resultSort,
            descending: resultSortDirection === "desc",
            page: resultPage,
            pageSize: 14,
        }).then((response) => {
            if (!active) return;
            setPersistedState(response.state);
            setPersistedRefreshState(response.refresh_state ?? null);
            setPersistedProgress({
                processed: response.processed_symbols ?? 0,
                total: response.total_symbols ?? 0,
            });
            setPersistedSelection({
                timeframe: response.selected_timeframe ?? timeframe,
                universe: response.selected_universe ?? marketUniverse,
            });
            setPersistedResults(rowsForSelectedTimeframe(response, timeframe));
            setPersistedTotal(response.total);
            setIsLoading(false);
            if (shouldRequestScannerBuild(response.state, timeframe)) {
                loadScanner(timeframe);
            }
        }).catch(() => {
            if (!active) return;
            setPersistedResults([]);
            setPersistedTotal(0);
            setPersistedState("FAILED");
            setPersistedRefreshState(null);
            setPersistedProgress({ processed: 0, total: 0 });
            setIsLoading(false);
        });
        return () => { active = false; };
        // loadScanner is intentionally invoked only for a missing/building
        // materialization; READY switches remain database reads.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [customSymbols, effectiveFilters, location.pathname, market, marketUniverse, persistedReloadNonce, resultPage, resultSort, resultSortDirection, scanner?.last_completed_at, timeframe]);

    useEffect(() => {
        queueMicrotask(() => setResultPage(1));
    }, [effectiveFilters, marketUniverse, timeframe]);

    useEffect(() => {
        let active = true;
        const refreshStatus = () => void getDhanRuntimeStatus()
            .then((status) => {
                if (!active) return;
                setDhanRuntimeStatus(status);
                if (status.data_status === "UPDATING") {
                    updateWasRunning.current = true;
                } else if (updateWasRunning.current && status.data_status === "READY") {
                    updateWasRunning.current = false;
                    setResultPage(1);
                    reloadScanner();
                }
            })
            .catch(() => { if (active) setDhanRuntimeStatus(null); });
        refreshStatus();
        const timer = window.setInterval(
            refreshStatus,
            dhanRuntimeStatus?.data_status === "UPDATING" ? 3_000 : 60_000,
        );
        return () => { active = false; window.clearInterval(timer); };
        // reloadScanner only reloads the current persisted page after a
        // completed server-side update; it never starts a historical scan.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [dhanRuntimeStatus?.data_status]);

    const filtersSettling = effectiveFilters.searchQuery !== searchQuery
        || effectiveFilters.minimumScore !== minimumScore
        || effectiveFilters.approvalFilter !== approvalFilter
        || effectiveFilters.patternFilter !== patternFilter
        || effectiveFilters.statusFilter !== statusFilter
        || effectiveFilters.proximityFilter !== proximityFilter
        || effectiveFilters.market !== market;
    const isInitialLoad = isLoading && scanner === null;
    const selectedTimeframeLabel = [...timeframes, ...intradayTimeframes]
        .find((item) => item.value === timeframe)?.label ?? timeframe;
    const persistedStatusMessage = timeframeStatusMessage(
        persistedState,
        selectedTimeframeLabel,
        persistedTotal,
        persistedRefreshState,
        persistedProgress.processed,
        persistedProgress.total,
        universeOptions.find((option) => option.value === marketUniverse)?.label
            .replace(/ \([\d,]+\)$/, "") ?? "NSE Main Equity",
    );

    const fullResults = effectiveFilters.market === "NSE" ? scanner?.results ?? [] : [];
    const persistedSelectionMatches = scannerSelectionMatches(
        persistedSelection,
        { timeframe, universe: marketUniverse },
    );
    const visibleResults = location.pathname.startsWith("/stock-details/") ? fullResults.filter((result) => {
        const matchesSymbol = result.symbol
            .toLowerCase()
            .includes(effectiveFilters.searchQuery.toLowerCase());
        const matchesScore = result.zone_score >= effectiveFilters.minimumScore;
        const matchesApproval =
            effectiveFilters.approvalFilter === "all"
            || (effectiveFilters.approvalFilter === "approved" && result.zone_type === "DEMAND")
            || (effectiveFilters.approvalFilter === "rejected" && result.zone_type === "SUPPLY");
        const matchesPattern = effectiveFilters.patternFilter === "all"
            || result.pattern_type === effectiveFilters.patternFilter;
        const matchesStatus = effectiveFilters.statusFilter === "all"
            || result.status === effectiveFilters.statusFilter;
        const matchesProximity = result.distance_percent <= effectiveFilters.proximityFilter;
        return matchesSymbol
            && matchesScore
            && matchesApproval
            && matchesPattern
            && matchesStatus
            && matchesProximity;
    }) : persistedSelectionMatches ? persistedResults : [];

    function exportResults() {
        const header = [
            "Symbol",
            "Zone Type",
            "Pattern",
            "Proximal",
            "Distal",
            "Distance Percent",
            "Score",
            "Current Price",
            "Timeframe",
            "Base Date",
        ];
        const rows = visibleResults.map((result) => [
            result.symbol,
            result.zone_type,
            result.pattern_type ?? "",
            result.proximal_price,
            result.distal_price,
            result.distance_percent,
            result.zone_score,
            result.current_price,
            result.timeframe,
            result.base_date,
        ]);
        const csv = [header, ...rows]
            .map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(","))
            .join("\n");
        const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
        const link = document.createElement("a");
        link.href = url;
        link.download = `alphaedge-scanner-${new Date().toISOString().slice(0, 10)}.csv`;
        link.click();
        URL.revokeObjectURL(url);
    }

    if (instrumentOnly && routeSymbol) {
        return (
            <Stack spacing={1.5} sx={{ bgcolor: "#ffffff", p: 2 }}>
                <Stack direction="row" sx={{ alignItems: "center", justifyContent: "space-between" }}>
                    <Box>
                        <Typography sx={{ fontSize: "1rem", fontWeight: 750 }}>
                            {routeSymbol.toUpperCase()} · NSE
                        </Typography>
                        <Typography color="text.secondary" sx={{ fontSize: "0.72rem" }}>
                            {initialFilters?.instrumentName ?? "Instrument market research"} · no qualifying zone selected
                        </Typography>
                    </Box>
                    <Button variant="outlined" onClick={() => navigate("/dashboard")}>Back to Dashboard</Button>
                </Stack>
                <Alert severity="info">
                    This is an instrument chart. Zone-specific analysis is unavailable because no qualifying canonical zone is selected.
                </Alert>
                <TradingChart symbol={routeSymbol.toUpperCase()} displayName={initialFilters?.instrumentName} />
            </Stack>
        );
    }

    return (
        <Stack spacing={0} sx={{ bgcolor: "#ffffff" }}>
            <ScannerToolbar
                isLoading={isInitialLoad}
                searchQuery={searchQuery}
                onRefresh={reloadScanner}
                onUpdateData={updateDhanData}
                onCancelUpdate={cancelDhanDataUpdate}
                isUpdatingData={dhanRuntimeStatus?.data_status === "UPDATING" || dhanRuntimeStatus?.data_status === "CANCELLING"}
                isCancellingUpdate={dhanRuntimeStatus?.data_status === "CANCELLING"}
                updateStage={dhanRuntimeStatus?.last_update.stage}
                onSearchChange={setSearchQuery}
                minimumScore={minimumScore}
                approvalFilter={approvalFilter}
                onMinimumScoreChange={(value) => changeManualFilter(() => setMinimumScore(value))}
                onApprovalFilterChange={(value) => changeManualFilter(() => setApprovalFilter(value))}
                onExport={exportResults}
                canExport={visibleResults.length > 0}
                universe={marketUniverse}
                universeOptions={universeOptions}
                timeframe={timeframe}
                onUniverseChange={changeUniverse}
                onTimeframeChange={changeTimeframe}
                patternFilter={patternFilter}
                statusFilter={statusFilter}
                proximityFilter={proximityFilter}
                onPatternFilterChange={(value) => changeManualFilter(() => setPatternFilter(value))}
                onStatusFilterChange={(value) => changeManualFilter(() => setStatusFilter(value))}
                onProximityFilterChange={(value) => changeManualFilter(() => setProximityFilter(value))}
                onQuickPreset={applyQuickPreset}
                actionableActive={actionableActive}
                actionableCount={persistedState === "READY" ? persistedTotal : null}
                onToggleActionable={toggleActionableZones}
            />
            <DhanDataStatus status={dhanRuntimeStatus} currentResult={visibleResults[0]} />
            <Box sx={{ height: 2 }}>
                {(filtersSettling || isInitialLoad) && <LinearProgress sx={{ height: 2, borderRadius: 1 }} />}
            </Box>

            {market === "BSE" && (
                <Alert severity="info">
                    BSE zone data is not connected yet. Select NSE to run the delayed scanner.
                </Alert>
            )}

            <Stack
                direction="row"
                spacing={1}
                sx={{
                    display: "none",
                    px: 1,
                    alignItems: "center",
                    border: "1px solid",
                    borderColor: "divider",
                    borderRadius: 2,
                    bgcolor: "background.paper",
                    overflow: "hidden",
                }}
            >
                <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                    DELAYED ZONES
                </Typography>
                <Select
                    size="small"
                    displayEmpty
                    value={intradayTimeframes.some((item) => item.value === timeframe) ? timeframe : ""}
                    onChange={(event) => changeTimeframe(event.target.value)}
                    sx={{ minWidth: 128 }}
                    renderValue={(value) => value
                        ? `Intraday · ${intradayTimeframes.find((item) => item.value === value)?.label}`
                        : "Intraday"}
                >
                    {intradayTimeframes.map((item) => <MenuItem key={item.value} value={item.value}>{item.label}</MenuItem>)}
                </Select>
                <Tabs
                    value={timeframe}
                    onChange={(_, value: string) => changeTimeframe(value)}
                    variant="scrollable"
                    scrollButtons="auto"
                >
                    {timeframes.map((item) => (
                        <Tab
                            key={item.value}
                            value={item.value}
                            label={(
                                <Stack direction="row" spacing={0.75} sx={{ alignItems: "center" }}>
                                    <span>{item.label}</span>
                                    {timeframe === item.value && !isLoading && (
                                        <Chip size="small" label={visibleResults.length} />
                                    )}
                                </Stack>
                            )}
                        />
                    ))}
                </Tabs>
            </Stack>

            {insightVisible && visibleResults[0] && (
                <Alert
                    icon={<AutoAwesomeRoundedIcon fontSize="small" />}
                    severity="info"
                    sx={{
                        display: "none",
                        py: 0.25,
                        px: 0.5,
                        bgcolor: "transparent",
                        border: 0,
                        alignItems: "center",
                        "& .MuiAlert-message": { width: "100%", py: 0.45 },
                        "& .MuiAlert-action": { display: "none" },
                    }}
                    action={(
                        <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
                            <Button
                                size="small"
                                onClick={() => navigate(`/stock-details/${encodeURIComponent(visibleResults[0].symbol)}`, {
                                    state: {
                                        symbol: visibleResults[0].symbol,
                                        timeframe,
                                        selectedZone: visibleResults[0].zone_type === "DEMAND" ? "demand" : "supply",
                                    },
                                })}
                            >
                                Analyze {visibleResults[0].symbol} →
                            </Button>
                            <IconButton size="small" aria-label="Dismiss AI Insight" onClick={() => setInsightVisible(false)}>
                                <CloseRoundedIcon fontSize="small" />
                            </IconButton>
                        </Stack>
                    )}
                >
                    <Box sx={{ display: "flex", gap: 0.75, alignItems: "baseline", minWidth: 0 }}>
                        <Typography sx={{ flex: "0 0 auto", fontSize: "0.72rem", fontWeight: 800 }}>AI Insight</Typography>
                        <Typography color="text.secondary" noWrap sx={{ minWidth: 0, fontSize: "0.7rem" }}>
                            {visibleResults[0].symbol} has the strongest matching {visibleResults[0].zone_type.toLowerCase()} zone in this scan, with {visibleResults[0].timeframe} context and {visibleResults[0].distance_percent.toFixed(2)}% distance from entry.
                        </Typography>
                    </Box>
                </Alert>
            )}

            {errorMessage && (
                <Alert severity="error">
                    {errorMessage}
                </Alert>
            )}

            {!errorMessage && dhanRuntimeStatus?.data_status === "FAILED" && (
                <Alert severity="warning">
                    {dhanRuntimeStatus.last_update.error?.startsWith("DHAN_HTTP_401")
                        ? "Dhan authentication required. Existing AlphaEdge data remains available. Update your Dhan access token to download new market data."
                        : "Dhan data update failed. Existing AlphaEdge data remains available and the next scheduled update can retry safely."}
                </Alert>
            )}

            {!errorMessage && persistedStatusMessage && (
                <Alert severity={persistedState === "FAILED" ? "error" : "info"}>
                    {persistedStatusMessage}
                </Alert>
            )}

            {isInitialLoad && (
                <Stack
                    direction="row"
                    sx={{
                        justifyContent: "center",
                    }}
                >
                    <CircularProgress />
                </Stack>
            )}

            <Box sx={{ mt: 2.5 }}>
                <ScannerResultsTable
                    key={initialFilters?.symbol && initialFilters.selectedZone
                    ? `${initialFilters.symbol}:${initialFilters.timeframe ?? timeframe}:${initialFilters.selectedZone}:${scanner?.results.length ?? 0}`
                    : "scanner-results"}
                    results={location.pathname.startsWith("/stock-details/")
                    ? scanner?.results ?? []
                    : visibleResults}
                    serverTotal={location.pathname.startsWith("/stock-details/") ? undefined : persistedTotal}
                    serverPage={location.pathname.startsWith("/stock-details/") ? undefined : resultPage}
                    onServerPageChange={location.pathname.startsWith("/stock-details/") ? undefined : setResultPage}
                    serverSort={location.pathname.startsWith("/stock-details/") || resultSort === "contextual_rank"
                        ? undefined
                        : resultSort === "zone_quality" ? "zone_score"
                            : resultSort === "distance" ? "distance_percent" : resultSort}
                    serverSortDirection={location.pathname.startsWith("/stock-details/") || resultSort === "contextual_rank" ? undefined : resultSortDirection}
                    onServerSortChange={location.pathname.startsWith("/stock-details/") ? undefined : (sort, direction) => {
                        setResultSort(sort === "zone_score" ? "zone_quality" : sort === "distance_percent" ? "distance" : sort);
                        setResultSortDirection(direction);
                        setResultPage(1);
                    }}
                    emptyStateTitle={persistedState === "READY" && persistedTotal === 0
                        ? "No zones currently qualify for this timeframe."
                        : undefined}
                    emptyStateDescription={persistedState === "READY" && persistedTotal === 0
                        ? "This timeframe is ready; no rows meet the current frozen qualification rules."
                        : undefined}
                    methodologyVersion={scanner?.methodology_version}
                    candleRefreshKey={scanner?.last_completed_at}
                    initialSelection={initialFilters?.symbol && initialFilters.selectedZone
                    ? {
                        symbol: initialFilters.symbol,
                        timeframe: initialFilters.timeframe ?? timeframe,
                        selectedZone: initialFilters.selectedZone,
                        proximalPrice: initialFilters.proximalPrice,
                        distalPrice: initialFilters.distalPrice,
                        baseIndex: initialFilters.baseIndex,
                    }
                    : undefined}
                    onDetailsClose={location.pathname.startsWith("/stock-details/")
                    ? () => navigate("/dashboard")
                    : undefined}
                />
            </Box>
        </Stack>
    );
}

export default Scanner;
