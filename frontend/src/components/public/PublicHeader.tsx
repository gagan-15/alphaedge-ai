import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link as RouterLink } from "react-router-dom";

import BrandLogo from "../brand/BrandLogo";

const links = [
    ["Platform", "/#platform"],
    ["Features", "/#features"],
    ["How it works", "/#how-it-works"],
    ["Safety", "/#safety"],
] as const;

export default function PublicHeader() {
    return (
        <Box
            component="header"
            sx={{
                position: "sticky",
                top: 0,
                zIndex: 20,
                height: 68,
                bgcolor: "rgba(255,255,255,.96)",
                borderBottom: "1px solid #E7EAF0",
                backdropFilter: "blur(12px)",
            }}
        >
            <Box
                sx={{
                    width: "min(1380px, calc(100% - 32px))",
                    height: "100%",
                    mx: "auto",
                    display: "flex",
                    alignItems: "center",
                    gap: 2,
                }}
            >
                <Box
                    component={RouterLink}
                    to="/"
                    aria-label="AlphaEdge AI home"
                    sx={{ display: "flex", color: "inherit", textDecoration: "none" }}
                >
                    <BrandLogo />
                </Box>
                <Stack
                    component="nav"
                    direction="row"
                    spacing={{ md: 3.5, lg: 5 }}
                    sx={{ ml: "auto", display: { xs: "none", md: "flex" }, alignItems: "center" }}
                >
                    {links.map(([label, href]) => (
                        <Typography
                            key={label}
                            component="a"
                            href={href}
                            sx={{
                                color: "#344054",
                                textDecoration: "none",
                                fontSize: ".82rem",
                                fontWeight: 550,
                                "&:hover": { color: "#4F46E5" },
                            }}
                        >
                            {label}
                        </Typography>
                    ))}
                </Stack>
                <Button
                    component={RouterLink}
                    to="/login"
                    variant="outlined"
                    size="small"
                    sx={{ ml: { xs: "auto", md: 2 }, minWidth: 78, bgcolor: "white" }}
                >
                    Log In
                </Button>
            </Box>
        </Box>
    );
}
