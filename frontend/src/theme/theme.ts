import { createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        mode: "light",

        primary: {
            main: "#1976d2",
        },

        background: {
            default: "#f4f6f8",
            paper: "#ffffff",
        },
    },

    shape: {
        borderRadius: 10,
    },

    typography: {
        fontFamily: "Roboto, Arial, sans-serif",

        h6: {
            fontWeight: 700,
        },
    },
});

export default theme;