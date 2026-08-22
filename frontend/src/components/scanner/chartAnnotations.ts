import type { UTCTimestamp } from "lightweight-charts";

export interface UserChartRectangle {
    id: string;
    symbol: string;
    timeframe: string;
    startTime: UTCTimestamp;
    endTime: UTCTimestamp;
    upperPrice: number;
    lowerPrice: number;
}

export interface RectangleDraftPoint {
    time: UTCTimestamp;
    price: number;
}

export function createUserChartRectangle(
    id: string,
    symbol: string,
    timeframe: string,
    start: RectangleDraftPoint,
    end: RectangleDraftPoint,
): UserChartRectangle {
    return {
        id,
        symbol,
        timeframe,
        startTime: Math.min(Number(start.time), Number(end.time)) as UTCTimestamp,
        endTime: Math.max(Number(start.time), Number(end.time)) as UTCTimestamp,
        upperPrice: Math.max(start.price, end.price),
        lowerPrice: Math.min(start.price, end.price),
    };
}

export function formatAnnotationPrice(value: number): string {
    const magnitude = Math.abs(value);
    const maximumFractionDigits = magnitude < 1 ? 4 : magnitude < 100 ? 2 : 2;
    return value.toLocaleString("en-IN", {
        minimumFractionDigits: 0,
        maximumFractionDigits,
    });
}

export function removeUserChartRectangle(
    rectangles: UserChartRectangle[],
    rectangleId: string,
): UserChartRectangle[] {
    return rectangles.filter((rectangle) => rectangle.id !== rectangleId);
}

export function clearUserChartRectangles(
    rectangles: UserChartRectangle[],
    symbol: string,
    timeframe: string,
): UserChartRectangle[] {
    return rectangles.filter(
        (rectangle) => rectangle.symbol !== symbol || rectangle.timeframe !== timeframe,
    );
}
