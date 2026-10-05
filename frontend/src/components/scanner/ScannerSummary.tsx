/**
 * Scanner Summary.
 *
 * Sprint:
 *     2.64 - Scanner Results Foundation
 */

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";

import type { ScannerResponse } from "../../types/scanner";

interface ScannerSummaryProps {
    scanner: ScannerResponse | null;
}

function ScannerSummary({
    scanner,
}: ScannerSummaryProps) {
    const approved =
        scanner?.results.filter(
            (result) => result.approved,
        ).length ?? 0;

    const confirmed =
        scanner?.results.filter(
            (result) => result.confirmed,
        ).length ?? 0;

    return (
        <Grid
            container
            spacing={3}
        >
            <Grid size={{ xs: 12, md: 3 }}>
                <Card>
                    <CardContent>
                        <Typography color="text.secondary">
                            Stocks Scanned
                        </Typography>

                        <Typography variant="h4">
                            {scanner?.total_scanned ?? 0}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
                <Card>
                    <CardContent>
                        <Typography color="text.secondary">
                            Matches
                        </Typography>

                        <Typography variant="h4">
                            {scanner?.total_matches ?? 0}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
                <Card>
                    <CardContent>
                        <Typography color="text.secondary">
                            Approved
                        </Typography>

                        <Typography variant="h4">
                            {approved}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
                <Card>
                    <CardContent>
                        <Typography color="text.secondary">
                            Confirmed
                        </Typography>

                        <Typography variant="h4">
                            {confirmed}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
}

export default ScannerSummary;