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
    ).filter((result) =>
        result.symbol
            .toLowerCase()
            .includes(searchQuery.toLowerCase()),
    );

    return (
        <Stack spacing={3}>
            <ScannerToolbar
                isLoading={isLoading}
                searchQuery={searchQuery}
                onRefresh={reloadScanner}
                onRunScan={reloadScanner}
                onSearchChange={setSearchQuery}
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
