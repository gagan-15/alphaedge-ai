import assert from "node:assert/strict";
import test from "node:test";
import type { UTCTimestamp } from "lightweight-charts";

import {
    clearUserChartRectangles,
    createUserChartRectangle,
    removeUserChartRectangle,
} from "../src/components/scanner/chartAnnotations.ts";

const time = (value: number) => value as UTCTimestamp;

test("normalizes top-to-bottom and bottom-to-top prices", () => {
    const topDown = createUserChartRectangle("one", "TCS", "1D", { time: time(100), price: 270.25 }, { time: time(200), price: 263.9 });
    const bottomUp = createUserChartRectangle("two", "TCS", "1D", { time: time(200), price: 263.9 }, { time: time(100), price: 270.25 });

    assert.equal(topDown.upperPrice, 270.25);
    assert.equal(topDown.lowerPrice, 263.9);
    assert.equal(bottomUp.upperPrice, 270.25);
    assert.equal(bottomUp.lowerPrice, 263.9);
    assert.equal(bottomUp.startTime, 100);
    assert.equal(bottomUp.endTime, 200);
});

test("supports multiple rectangles and deletes only the selected rectangle", () => {
    const first = createUserChartRectangle("one", "TCS", "1D", { time: time(100), price: 10 }, { time: time(200), price: 20 });
    const second = createUserChartRectangle("two", "TCS", "1D", { time: time(300), price: 30 }, { time: time(400), price: 40 });

    const remaining = removeUserChartRectangle([first, second], first.id);
    assert.deepEqual(remaining.map((item) => item.id), ["two"]);
});

test("clear drawings is isolated to the active symbol and timeframe", () => {
    const daily = createUserChartRectangle("daily", "TCS", "1D", { time: time(100), price: 10 }, { time: time(200), price: 20 });
    const weekly = createUserChartRectangle("weekly", "TCS", "1W", { time: time(100), price: 10 }, { time: time(200), price: 20 });
    const otherSymbol = createUserChartRectangle("other", "INFY", "1D", { time: time(100), price: 10 }, { time: time(200), price: 20 });

    const remaining = clearUserChartRectangles([daily, weekly, otherSymbol], "TCS", "1D");
    assert.deepEqual(remaining.map((item) => item.id), ["weekly", "other"]);
});

test("logical time and price coordinates remain unchanged for reprojection after pan or zoom", () => {
    const rectangle = createUserChartRectangle("one", "TCS", "1D", { time: time(100), price: 270.25 }, { time: time(200), price: 263.9 });
    assert.deepEqual(
        { startTime: rectangle.startTime, endTime: rectangle.endTime, upperPrice: rectangle.upperPrice, lowerPrice: rectangle.lowerPrice },
        { startTime: 100, endTime: 200, upperPrice: 270.25, lowerPrice: 263.9 },
    );
});
