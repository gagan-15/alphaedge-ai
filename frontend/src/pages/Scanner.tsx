/**
 * Scanner Page.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

import { useEffect, useState } from "react";

import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import Stack from "@mui/material/Stack";

import { getScanner } from "../api/scannerApi";
import ScannerResultsTable from "../components/scanner/ScannerResultsTable";
import ScannerSummary from "../components/scanner/ScannerSummary";
import ScannerToolbar from "../components/scanner/ScannerToolbar";

import type { ScannerResponse } from "../types/scanner";

function Scanner() {
    const [scanner, setScanner] =
        useState<ScannerResponse | null>(null);
    const [isLoading, setIsLoading] =
        useState(true);
    const [errorMessage, setErrorMessage] =
        useState<string | null>(null);
    const [searchQuery, setSearchQuery] =
        useState("");
    const [minimumScore, setMinimumScore] = useState(0);
    const [approvalFilter, setApprovalFilter] = useState("all");

    function loadScanner() {
        void getScanner()
            .then((data) => {
                setScanner(data);
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
        setIsLoading(true);
        setErrorMessage(null);

        loadScanner();
    }

    useEffect(() => {
        loadScanner();
    }, []);

    const visibleResults = (
        scanner?.results ?? []
    ).filter((result) => {
        const matchesSymbol = result.symbol
            .toLowerCase()
            .includes(searchQuery.toLowerCase());
        const matchesScore = result.confirmation_score >= minimumScore;
        const matchesApproval =
            approvalFilter === "all"
            || (approvalFilter === "approved" && result.approved)
            || (approvalFilter === "rejected" && !result.approved);
        return matchesSymbol && matchesScore && matchesApproval;
    });

    function exportResults() {
        const header = [
            "Symbol",
            "Possible Entry",
            "Invalidation",
            "Scenario Target",
            "Risk Reward",
            "Confidence",
            "Risk Checks Passed",
        ];
        const rows = visibleResults.map((result) => [
            result.symbol,
            result.entry_price,
            result.stop_loss,
            result.target_price,
            result.risk_reward_ratio,
            result.confirmation_score,
            result.approved ? "Yes" : "No",
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
            />

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

            <ScannerSummary scanner={scanner} />

            <ScannerResultsTable
                results={visibleResults}
            />
        </Stack>
    );
}

export default Scanner;
