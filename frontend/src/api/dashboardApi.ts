/**
 * Dashboard API.
 *
 * Sprint:
 *     2.51 - Dashboard API
 */

import axios from "axios";
import { API_BASE_URL } from "./config";

import type { DashboardResult } from "../types/dashboard";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
});

export async function getDashboard(): Promise<DashboardResult> {
    try {
        const response = await api.get<DashboardResult>(
            "/dashboard/",
        );

        return response.data;
    } catch (error) {
        console.error(
            "Failed to fetch dashboard data.",
            error,
        );

        throw error;
    }
}
