/**
 * Trading Chart.
 *
 * Sprint:
 *     2.59 - TradingView Chart
 */

import { useEffect, useRef } from "react";

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";

declare global {
    interface Window {
        TradingView: any;
    }
}

function TradingChart() {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const createWidget = () => {
            if (
                window.TradingView &&
                containerRef.current
            ) {
                containerRef.current.innerHTML = "";

                new window.TradingView.widget({
                    autosize: true,
                    symbol: "NASDAQ:AAPL",
                    interval: "D",
                    timezone: "Asia/Kolkata",
                    theme: "dark",
                    style: "1",
                    locale: "en",
                    enable_publishing: false,
                    hide_side_toolbar: false,
                    allow_symbol_change: true,
                    container_id: containerRef.current.id,
                });
            }
        };

        const existingScript = document.getElementById(
            "tradingview-widget-script",
        );

        if (existingScript) {
            createWidget();
        } else {
            const script = document.createElement("script");

            script.id = "tradingview-widget-script";
            script.src = "https://s3.tradingview.com/tv.js";
            script.async = true;
            script.onload = createWidget;

            document.body.appendChild(script);
        }

        return () => {
            if (containerRef.current) {
                containerRef.current.innerHTML = "";
            }
        };
    }, []);

    return (
        <Card
            elevation={2}
            sx={{
                height: 720,
            }}
        >
            <CardContent
                sx={{
                    height: "100%",
                    p: 0,
                }}
            >
                <div
                    id="tradingview_chart"
                    ref={containerRef}
                    style={{
                        width: "100%",
                        height: "100%",
                    }}
                />
            </CardContent>
        </Card>
    );
}

export default TradingChart;