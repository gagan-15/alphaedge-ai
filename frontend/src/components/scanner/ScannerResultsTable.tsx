/**
 * Scanner Results Table.
 *
 * Sprint:
 *     2.65 - Professional Scanner UI
 */

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import TableSortLabel from "@mui/material/TableSortLabel";
import { useMemo, useState } from "react";

import type { ScannerResult } from "../../types/scanner";

interface ScannerResultsTableProps {
    results: ScannerResult[];
}

function ScannerResultsTable({
    results,
}: ScannerResultsTableProps) {
    const [sortField, setSortField] = useState<"symbol" | "confirmation_score" | "risk_reward_ratio">("confirmation_score");
    const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

    const sortedResults = useMemo(() => [...results].sort((left, right) => {
        const first = left[sortField];
        const second = right[sortField];
        const comparison = typeof first === "string"
            ? first.localeCompare(String(second))
            : Number(first) - Number(second);
        return sortDirection === "asc" ? comparison : -comparison;
    }), [results, sortDirection, sortField]);

    function chooseSort(field: typeof sortField) {
        if (field === sortField) {
            setSortDirection((current) => current === "asc" ? "desc" : "asc");
        } else {
            setSortField(field);
            setSortDirection("desc");
        }
    }

    function sortableLabel(field: typeof sortField, label: string) {
        return (
            <TableSortLabel
                active={sortField === field}
                direction={sortField === field ? sortDirection : "asc"}
                onClick={() => chooseSort(field)}
            >
                {label}
            </TableSortLabel>
        );
    }

    return (
        <Card>
            <CardContent>
                <Typography
                    variant="h6"
                    sx={{ mb: 2 }}
                >
                    Scan Results
                </Typography>

                <Divider sx={{ mb: 3 }} />

                {results.length === 0 ? (
                    <>
                        <Typography
                            align="center"
                            variant="h6"
                            color="text.secondary"
                            sx={{ pt: 6 }}
                        >
                            No Scan Results
                        </Typography>

                        <Typography
                            align="center"
                            color="text.secondary"
                            sx={{ pb: 6 }}
                        >
                            Click "Run Scan" to analyze the market and
                            find research setups that match your rules.
                        </Typography>
                    </>
                ) : (
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>
                                        {sortableLabel("symbol", "Symbol")}
                                    </TableCell>

                                    <TableCell align="right">
                                        Zone
                                    </TableCell>

                                    <TableCell align="right">
                                        Proximal
                                    </TableCell>

                                    <TableCell align="right">
                                        Distal
                                    </TableCell>

                                    <TableCell align="right">
                                        Distance
                                    </TableCell>

                                    <TableCell align="right">
                                        Possible Entry
                                    </TableCell>

                                    <TableCell align="right">
                                        Invalidation
                                    </TableCell>

                                    <TableCell align="right">
                                        Scenario Target
                                    </TableCell>

                                    <TableCell align="right">
                                        {sortableLabel("risk_reward_ratio", "RR")}
                                    </TableCell>

                                    <TableCell align="right">
                                        {sortableLabel("confirmation_score", "Score")}
                                    </TableCell>

                                    <TableCell align="center">Trend</TableCell>
                                    <TableCell align="center">Volume</TableCell>
                                    <TableCell align="center">Momentum</TableCell>
                                    <TableCell align="center">Risk Status</TableCell>
                                </TableRow>
                            </TableHead>

                            <TableBody>
                                {sortedResults.map(
                                    (result) => (
                                        <TableRow
                                            hover
                                            key={
                                                result.symbol
                                            }
                                        >
                                            <TableCell>
                                                {
                                                    result.symbol
                                                }
                                            </TableCell>

                                            <TableCell align="right">
                                                {result.zone_type ?? "—"}
                                            </TableCell>

                                            <TableCell align="right">
                                                {result.proximal_price?.toLocaleString("en-IN", { maximumFractionDigits: 2 }) ?? "—"}
                                            </TableCell>

                                            <TableCell align="right">
                                                {result.distal_price?.toLocaleString("en-IN", { maximumFractionDigits: 2 }) ?? "—"}
                                            </TableCell>

                                            <TableCell align="right">
                                                {result.distance_percent === null ? "—" : `${result.distance_percent.toFixed(2)}%`}
                                            </TableCell>

                                            <TableCell align="right">
                                                {
                                                    result.entry_price.toLocaleString("en-IN", { maximumFractionDigits: 2 })
                                                }
                                            </TableCell>

                                            <TableCell align="right">
                                                {
                                                    result.stop_loss.toLocaleString("en-IN", { maximumFractionDigits: 2 })
                                                }
                                            </TableCell>

                                            <TableCell align="right">
                                                {
                                                    result.target_price.toLocaleString("en-IN", { maximumFractionDigits: 2 })
                                                }
                                            </TableCell>

                                            <TableCell align="right">
                                                {
                                                    result.risk_reward_ratio.toFixed(2)
                                                }
                                            </TableCell>

                                            <TableCell align="right">
                                                {
                                                    result.confirmation_score.toFixed(0)
                                                }
                                                %
                                            </TableCell>

                                            <TableCell align="center">
                                                <Chip
                                                    color={
                                                        result.trend_confirmed
                                                            ? "success"
                                                            : "error"
                                                    }
                                                    label={
                                                        result.trend_confirmed ? "✓" : "—"
                                                    }
                                                    size="small"
                                                />
                                            </TableCell>

                                            <TableCell align="center">
                                                <Chip
                                                    color={
                                                        result.volume_confirmed
                                                            ? "success"
                                                            : "default"
                                                    }
                                                    label={
                                                        result.volume_confirmed ? "✓" : "—"
                                                    }
                                                    size="small"
                                                />
                                            </TableCell>

                                            <TableCell align="center">
                                                <Chip
                                                    color={result.momentum_confirmed ? "success" : "default"}
                                                    label={result.momentum_confirmed ? "✓" : "—"}
                                                    size="small"
                                                />
                                            </TableCell>

                                            <TableCell align="center">
                                                <Chip
                                                    color={result.approved ? "success" : "warning"}
                                                    label={result.approved ? "Passed" : "Review"}
                                                    size="small"
                                                />
                                            </TableCell>
                                        </TableRow>
                                    ),
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}
            </CardContent>
        </Card>
    );
}

export default ScannerResultsTable;
