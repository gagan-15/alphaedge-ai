/**
 * Scanner API.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

import axios from "axios";
import { API_BASE_URL } from "./config";

import type { ScannerResponse, ZoneResearchResponse } from "../types/scanner";

const api = axios.create({
    baseURL: API_BASE_URL,
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

export async function getResearchZones(): Promise<ZoneResearchResponse> {
    const response = await api.get<ZoneResearchResponse>("/scanner/zones");
    return response.data;
}
