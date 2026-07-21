/**
 * AlphaEdge AI Header.
 *
 * Sprint:
 *     2.60 - Professional Application Shell
 */

import AccountCircleOutlinedIcon from "@mui/icons-material/AccountCircleOutlined";
import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

function Header() {
    return (
        <AppBar
            position="fixed"
            color="inherit"
            elevation={0}
            sx={{
                zIndex: (theme) => theme.zIndex.drawer + 1,
                backgroundColor: "background.paper",
                borderBottom: "1px solid",
                borderColor: "divider",
            }}
        >
            <Toolbar sx={{ minHeight: 64 }}>
                <Box sx={{ flexGrow: 1 }}>
                    <Typography
                        variant="h6"
                        component="div"
                        sx={{
                            fontWeight: 700,
                            lineHeight: 1.2,
                        }}
                    >
                        AlphaEdge AI
                    </Typography>

                    <Typography
                        variant="caption"
                        color="text.secondary"
                    >
                        Trading Intelligence Platform
                    </Typography>
                </Box>

                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 0.5,
                    }}
                >
                    <IconButton
                        aria-label="Notifications"
                        color="inherit"
                    >
                        <NotificationsNoneOutlinedIcon />
                    </IconButton>

                    <IconButton
                        aria-label="User account"
                        color="inherit"
                    >
                        <AccountCircleOutlinedIcon />
                    </IconButton>
                </Box>
            </Toolbar>
        </AppBar>
    );
}

export default Header;