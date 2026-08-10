/**
 * Scanner Page.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

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

import { getResearchZones } from "../api/scannerApi";
import ScannerResultsTable from "../components/scanner/ScannerResultsTable";
import ScannerToolbar, { type ScannerQuickPreset } from "../components/scanner/ScannerToolbar";

import type { ZoneResearchResponse } from "../types/scanner";
import { useMarketUniverse } from "../market-universe/MarketUniverseState";

const scannerResultCache = new Map<string, ZoneResearchResponse>();

const timeframes = [
    { value: "DAILY", label: "Daily" }, { value: "WEEKLY", label: "Weekly" },
    { value: "MONTHLY", label: "Monthly" }, { value: "QUARTERLY", label: "Quarterly" },
    { value: "HALFYEARLY", label: "Half-yearly" }, { value: "YEARLY", label: "Yearly" },
] as const;
const intradayTimeframes = [
    { value: "MINUTE_5", label: "5m" }, { value: "MINUTE_15", label: "15m" },
    { value: "MINUTE_75", label: "75m" }, { value: "MINUTE_125", label: "125m" },
    { value: "HOUR_1", label: "1H" }, { value: "HOUR_2", label: "2H" },
    { value: "HOUR_4", label: "4H" }, { value: "HOUR_6", label: "6H" },
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
    const { marketUniverse, customSymbols } = useMarketUniverse();
    const location = useLocation();
    const navigate = useNavigate();
    const initialFilters = location.state as {
        zoneType?: "DEMAND" | "SUPPLY";
        timeframe?: string;
        symbol?: string;
        selectedZone?: "demand" | "supply";
        proximalPrice?: number;
        distalPrice?: number;
        baseIndex?: number;
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
    const [patternFilter, setPatternFilter] = useState("all");
    const [statusFilter, setStatusFilter] = useState("all");
    const [proximityFilter, setProximityFilter] = useState(100);
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
    const requestVersion = useRef(0);

    function loadScanner(selectedTimeframe = timeframe) {
        const version = ++requestVersion.current;
        const watchlist = marketUniverse === "watchlist"
            ? JSON.parse(localStorage.getItem("alphaedge.local.watchlist") ?? "[]")
            : [];
        const suppliedSymbols = marketUniverse === "custom"
            ? customSymbols
            : watchlist;
        const cacheKey = `${selectedTimeframe}:${marketUniverse}:${suppliedSymbols.join(",")}`;
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
        )
            .then((data) => {
                if (version !== requestVersion.current) return;
                receivedScannerResponse = true;
                const hasCompletedSnapshot = Boolean(data.last_completed_at)
                    || data.status === "completed";
                if (hasCompletedSnapshot) {
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
        if (market !== "NSE") {
            setIsLoading(false);
            return;
        }
        setIsLoading(true);
        setErrorMessage(null);

        loadScanner();
    }

    function changeMarket(value: string) {
        setMarket(value);
        setIsLoading(value === "NSE");
        setErrorMessage(null);
    }

    function changeTimeframe(value: string) {
        setIsLoading(true);
        setErrorMessage(null);
        setTimeframe(value);
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
        if (market !== "NSE") {
            return;
        }
        loadScanner(timeframe);
        return () => {
            requestVersion.current += 1;
        };
        // The selected timeframe is the request boundary.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [customSymbols, market, marketUniverse, timeframe]);

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

    const filtersSettling = effectiveFilters.searchQuery !== searchQuery
        || effectiveFilters.minimumScore !== minimumScore
        || effectiveFilters.approvalFilter !== approvalFilter
        || effectiveFilters.patternFilter !== patternFilter
        || effectiveFilters.statusFilter !== statusFilter
        || effectiveFilters.proximityFilter !== proximityFilter
        || effectiveFilters.market !== market;

    const visibleResults = (
        effectiveFilters.market === "NSE" ? scanner?.results ?? [] : []
    ).filter((result) => {
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
    });

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

    return (
        <Stack spacing={0} sx={{ bgcolor: "#ffffff" }}>
            <ScannerToolbar
                isLoading={isLoading}
                searchQuery={searchQuery}
                onRefresh={reloadScanner}
                onRunScan={reloadScanner}
                onSearchChange={setSearchQuery}
                minimumScore={minimumScore}
                approvalFilter={approvalFilter}
                onMinimumScoreChange={setMinimumScore}
                onApprovalFilterChange={setApprovalFilter}
                onExport={exportResults}
                canExport={visibleResults.length > 0}
                market={market}
                timeframe={timeframe}
                onMarketChange={changeMarket}
                onTimeframeChange={changeTimeframe}
                patternFilter={patternFilter}
                statusFilter={statusFilter}
                proximityFilter={proximityFilter}
                onPatternFilterChange={setPatternFilter}
                onStatusFilterChange={setStatusFilter}
                onProximityFilterChange={setProximityFilter}
                onQuickPreset={applyQuickPreset}
            />
            <Box sx={{ height: 2 }}>
                {(filtersSettling || isLoading || scanner?.status === "refreshing" || scanner?.status === "queued") && <LinearProgress sx={{ height: 2, borderRadius: 1 }} />}
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

            {!isLoading && !errorMessage && scanner
                && (scanner.status === "refreshing" || scanner.status === "queued")
                && scanner.results.length === 0 && (
                <Alert severity="info">
                    Scanning this market for the first time: {scanner.processed_symbols} / {scanner.total_symbols} stocks checked. Results will appear automatically.
                </Alert>
            )}

            {isLoading && (
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
