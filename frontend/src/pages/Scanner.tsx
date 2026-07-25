/**
 * Scanner Page.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

import { useEffect, useState } from "react";

import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import Chip from "@mui/material/Chip";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { getResearchZones } from "../api/scannerApi";
import ScannerResultsTable from "../components/scanner/ScannerResultsTable";
import ScannerToolbar from "../components/scanner/ScannerToolbar";

import type { ZoneResearchResponse } from "../types/scanner";

const timeframes = [
    { value: "DAILY", label: "Daily" },
    { value: "WEEKLY", label: "Weekly" },
    { value: "MONTHLY", label: "Monthly" },
    { value: "QUARTERLY", label: "Quarterly" },
    { value: "HALFYEARLY", label: "Half-yearly" },
    { value: "YEARLY", label: "Yearly" },
] as const;

function Scanner() {
    const [scanner, setScanner] =
        useState<ZoneResearchResponse | null>(null);
    const [isLoading, setIsLoading] =
        useState(true);
    const [errorMessage, setErrorMessage] =
        useState<string | null>(null);
    const [searchQuery, setSearchQuery] =
        useState("");
    const [minimumScore, setMinimumScore] = useState(0);
    const [approvalFilter, setApprovalFilter] = useState("all");
    const [timeframe, setTimeframe] = useState("DAILY");
    const [market, setMarket] = useState("NSE");
    const [timeframeCounts, setTimeframeCounts] = useState<Record<string, number>>({});

    function loadScanner(selectedTimeframe = timeframe) {
        void getResearchZones(selectedTimeframe)
            .then((data) => {
                setScanner(data);
                setTimeframeCounts((current) => ({
                    ...current,
                    [selectedTimeframe]: data.total_zones,
                }));
            })
            .catch((error: unknown) => {
                console.error(
                    "Failed to load scanner.",
                    error,
                );

                setErrorMessage(
                    "Scanner data could not be loaded. Check that the backend is running.",
                );
            })
            .finally(() => {
                setIsLoading(false);
            });
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

    useEffect(() => {
        if (market !== "NSE") {
            return;
        }
        loadScanner(timeframe);
        // The selected timeframe is the request boundary.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [market, timeframe]);

    const visibleResults = (
        market === "NSE" ? scanner?.results ?? [] : []
    ).filter((result) => {
        const matchesSymbol = result.symbol
            .toLowerCase()
            .includes(searchQuery.toLowerCase());
        const matchesScore = result.zone_score >= minimumScore;
        const matchesApproval =
            approvalFilter === "all"
            || (approvalFilter === "approved" && result.zone_type === "DEMAND")
            || (approvalFilter === "rejected" && result.zone_type === "SUPPLY");
        return matchesSymbol && matchesScore && matchesApproval;
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
        <Stack spacing={3}>
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
            />

            {market === "BSE" && (
                <Alert severity="info">
                    BSE zone data is not connected yet. Select NSE to run the delayed scanner.
                </Alert>
            )}

            <Stack
                direction="row"
                spacing={1}
                sx={{ alignItems: "center", borderBottom: "1px solid", borderColor: "divider" }}
            >
                <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                    DELAYED ZONES
                </Typography>
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
                                    {timeframeCounts[item.value] !== undefined && (
                                        <Chip size="small" label={timeframeCounts[item.value]} />
                                    )}
                                </Stack>
                            )}
                        />
                    ))}
                </Tabs>
            </Stack>

            {errorMessage && (
                <Alert severity="error">
                    {errorMessage}
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

            <ScannerResultsTable
                results={visibleResults}
            />
        </Stack>
    );
}

export default Scanner;
