/**
 * Dashboard API.
 *
 * Sprint:
 *     2.51 - Dashboard API
 */

import axios from "axios";

import type { DashboardResult } from "../types/dashboard";

const BASE_URL = "http://127.0.0.1:8000";

export async function getDashboard(): Promise<DashboardResult> {
    const response = await axios.get<DashboardResult>(
        `${BASE_URL}/dashboard/`,
    );

    return response.data;
}