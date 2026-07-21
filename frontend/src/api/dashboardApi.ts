/**
 * Dashboard API.
 *
 * Sprint:
 *     2.51 - Dashboard API
 */

import axios from "axios";

import type { DashboardResult } from "../types/dashboard";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
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