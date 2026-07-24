/**
 * Scanner API.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

import axios from "axios";

import type { ScannerResponse } from "../types/scanner";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
    timeout: 10000,
});

export async function getScanner(): Promise<ScannerResponse> {
    try {
        const response = await api.get<ScannerResponse>(
            "/scanner/",
        );

        return response.data;
    } catch (error) {
        console.error(
            "Failed to fetch scanner data.",
            error,
        );

        throw error;
    }
}