import { useState } from "react";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import FormControlLabel from "@mui/material/FormControlLabel";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

interface Preferences {
    defaultTimeframe: string;
    minimumQuality: number;
    soundAlerts: boolean;
    desktopAlerts: boolean;
}

const storageKey = "alphaedge.local.preferences";
const defaults: Preferences = { defaultTimeframe: "DAILY", minimumQuality: 40, soundAlerts: false, desktopAlerts: false };

function loadPreferences(): Preferences {
    try { return { ...defaults, ...JSON.parse(localStorage.getItem(storageKey) ?? "{}") }; } catch { return defaults; }
}

export default function Settings() {
    const [preferences, setPreferences] = useState(loadPreferences);
    const [saved, setSaved] = useState(false);

    function save() {
        localStorage.setItem(storageKey, JSON.stringify(preferences));
        setSaved(true);
    }

    return <Stack spacing={1.5}>
        <Typography variant="h4">Settings</Typography>
        <Typography color="text.secondary">Local research preferences for this browser.</Typography>
        {saved && <Alert severity="success">Preferences saved locally.</Alert>}
        <Card><CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Scanner defaults</Typography>
            <Stack spacing={2}>
                <TextField select label="Default timeframe" value={preferences.defaultTimeframe} onChange={(e) => setPreferences({ ...preferences, defaultTimeframe: e.target.value })}>
                    {[["DAILY", "Daily"], ["WEEKLY", "Weekly"], ["MONTHLY", "Monthly"], ["HOUR_1", "1 hour"], ["MINUTE_15", "15 minutes"]].map(([value, label]) => <MenuItem key={value} value={value}>{label}</MenuItem>)}
                </TextField>
                <TextField select label="Minimum zone quality" value={preferences.minimumQuality} onChange={(e) => setPreferences({ ...preferences, minimumQuality: Number(e.target.value) })}>
                    {[0, 40, 60, 75, 90].map((value) => <MenuItem key={value} value={value}>{value === 0 ? "Show all" : `${value} and above`}</MenuItem>)}
                </TextField>
            </Stack>
        </CardContent></Card>
        <Card><CardContent>
            <Typography variant="h6">Notification preferences</Typography>
            <FormControlLabel control={<Switch checked={preferences.soundAlerts} onChange={(e) => setPreferences({ ...preferences, soundAlerts: e.target.checked })} />} label="Sound for local alert checks" />
            <FormControlLabel control={<Switch checked={preferences.desktopAlerts} onChange={(e) => setPreferences({ ...preferences, desktopAlerts: e.target.checked })} />} label="Desktop notifications when supported" />
            <Alert severity="info" sx={{ mt: 1 }}>Telegram and automatic background delivery are not connected.</Alert>
        </CardContent></Card>
        <Stack direction="row" spacing={1}>
            <Button variant="contained" onClick={save}>Save preferences</Button>
            <Button variant="outlined" onClick={() => { setPreferences(defaults); localStorage.removeItem(storageKey); setSaved(false); }}>Reset</Button>
        </Stack>
    </Stack>;
}
