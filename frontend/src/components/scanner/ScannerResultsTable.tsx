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

import type { ScannerResult } from "../../types/scanner";

interface ScannerResultsTableProps {
    results: ScannerResult[];
}

function ScannerResultsTable({
    results,
}: ScannerResultsTableProps) {
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
                                        Symbol
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
                                        RR
                                    </TableCell>

                                    <TableCell align="right">
                                        Conditions
                                    </TableCell>

                                    <TableCell align="center">
                                        Risk Check
                                    </TableCell>

                                    <TableCell align="center">
                                        Setup Valid
                                    </TableCell>
                                </TableRow>
                            </TableHead>

                            <TableBody>
                                {results.map(
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
                                                {
                                                    result.entry_price
                                                }
                                            </TableCell>

                                            <TableCell align="right">
                                                {
                                                    result.stop_loss
                                                }
                                            </TableCell>

                                            <TableCell align="right">
                                                {
                                                    result.target_price
                                                }
                                            </TableCell>

                                            <TableCell align="right">
                                                {
                                                    result.risk_reward_ratio
                                                }
                                            </TableCell>

                                            <TableCell align="right">
                                                {
                                                    result.confirmation_score
                                                }
                                                %
                                            </TableCell>

                                            <TableCell align="center">
                                                <Chip
                                                    color={
                                                        result.approved
                                                            ? "success"
                                                            : "error"
                                                    }
                                                    label={
                                                        result.approved
                                                            ? "Yes"
                                                            : "No"
                                                    }
                                                    size="small"
                                                />
                                            </TableCell>

                                            <TableCell align="center">
                                                <Chip
                                                    color={
                                                        result.confirmed
                                                            ? "success"
                                                            : "default"
                                                    }
                                                    label={
                                                        result.confirmed
                                                            ? "Yes"
                                                            : "No"
                                                    }
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
