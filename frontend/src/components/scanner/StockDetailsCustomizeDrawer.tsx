import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import FormControlLabel from "@mui/material/FormControlLabel";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";

import {
    defaultStockDetailsVisibility,
    stockDetailsSectionOptions,
    type StockDetailsVisibility,
} from "./stockDetailsPreferences";

interface StockDetailsCustomizeDrawerProps {
    open: boolean;
    value: StockDetailsVisibility;
    onClose: () => void;
    onChange: (value: StockDetailsVisibility) => void;
}

function StockDetailsCustomizeDrawer({ open, value, onClose, onChange }: StockDetailsCustomizeDrawerProps) {
    const visibleCount = Object.values(value).filter(Boolean).length;

    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={onClose}
            sx={{ zIndex: (theme) => theme.zIndex.modal + 1 }}
            slotProps={{ paper: { sx: { width: { xs: "100%", sm: 440 }, maxWidth: "100%" } } }}
        >
            <Stack direction="row" sx={{ alignItems: "center", justifyContent: "space-between", p: 2.5 }}>
                <Box>
                    <Typography variant="h5">Customize details</Typography>
                    <Typography variant="body2" color="text.secondary">Choose what appears on the right side.</Typography>
                </Box>
                <IconButton aria-label="Close customize panel" onClick={onClose}><CloseRoundedIcon /></IconButton>
            </Stack>
            <Divider />
            <Stack spacing={.5} sx={{ p: 2.5, overflowY: "auto" }}>
                {stockDetailsSectionOptions.map((option) => {
                    const cannotHide = value[option.id] && visibleCount === 1;
                    return (
                        <Box key={option.id} sx={{ p: 1.25, borderRadius: 2, "&:hover": { bgcolor: "action.hover" } }}>
                            <FormControlLabel
                                sx={{ m: 0, width: "100%", justifyContent: "space-between" }}
                                labelPlacement="start"
                                control={
                                    <Switch
                                        checked={value[option.id]}
                                        disabled={cannotHide}
                                        onChange={(_, checked) => onChange({ ...value, [option.id]: checked })}
                                    />
                                }
                                label={<Typography sx={{ fontWeight: 800 }}>{option.label}</Typography>}
                            />
                            <Typography variant="caption" color="text.secondary">{option.note}</Typography>
                        </Box>
                    );
                })}
            </Stack>
            <Box sx={{ mt: "auto", p: 2.5, borderTop: "1px solid", borderColor: "divider" }}>
                <Stack direction="row" spacing={1}>
                    <Button fullWidth variant="outlined" onClick={() => onChange(defaultStockDetailsVisibility)}>Show everything</Button>
                    <Button fullWidth variant="contained" onClick={onClose}>Done</Button>
                </Stack>
                <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1 }}>
                    Your choices are saved on this device.
                </Typography>
            </Box>
        </Drawer>
    );
}

export default StockDetailsCustomizeDrawer;
