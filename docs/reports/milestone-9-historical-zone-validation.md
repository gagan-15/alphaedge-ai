# Milestone 9 — Canonical Historical Zone Performance Validation

> Research/audit only. No production methodology or behavior changed.

## Executive Summary

- Period: 2021-08-18 00:00:00 to 2026-08-21 00:00:00
- Universe: 28 frozen deterministic NSE symbols (140/140 series succeeded)
- Timeframes: 15m, 75m, 125m, Daily, Weekly
- Point-in-time reconstructed zones: 1568
- Interacted: 1185/1568 (75.57%; 95% CI 73.39–77.64)
- Never interacted: 383
- Structural survival among interacted zones: 217/1185 (18.31%; 95% CI 16.21–20.62)
- >=1 zone-width reaction: 1062/1185 (89.62%; 95% CI 87.75–91.23)
- >=2 zone-width reaction: 862/1185 (72.74%; 95% CI 70.14–75.20)
- >=3 zone-width reaction: 728/1185 (61.43%; 95% CI 58.63–64.16)
- >=5 zone-width reaction: 541/1185 (45.65%; 95% CI 42.84–48.50)
- Structural target reached where available: 192/407 (47.17%; 95% CI 42.37–52.03)

## Scope and reliability

This is a deterministic, history-spanning validation sample, not a complete NSE 500 census. The frozen replay sampled at most eight zones per valid data segment. Daily and Weekly data cover the five-year target window; Yahoo intraday retention is shorter, so intraday rows do not represent five full years. Current NSE constituents were used, so survivorship bias remains. No profit, win-rate, CAGR, Sharpe, position sizing, protective-stop, or P&L claim is made.

Reporting rule: fewer than 30 observations is descriptive only; 30–99 supports cautious directional reading; 100+ supports stronger descriptive conclusions. These are reporting safeguards, not production thresholds.

## Table A — Overall historical performance

| Group | Zones | Interacted | Survival | >=1ZW | >=2ZW | >=3ZW | Target reached | Median MFE (ZW) | Median MAE (ZW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All zones | 1568 | 1185 | 217/1185 (18.31%; 95% CI 16.21–20.62) | 1062/1185 (89.62%; 95% CI 87.75–91.23) | 862/1185 (72.74%; 95% CI 70.14–75.20) | 728/1185 (61.43%; 95% CI 58.63–64.16) | 192/407 (47.17%; 95% CI 42.37–52.03) | 4.2979 | 3.8982 |

## Table B — Performance by timeframe

| Group | Zones | Interacted | Survival | >=1ZW | >=2ZW | >=3ZW | Target reached | Median MFE (ZW) | Median MAE (ZW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 125m | 118 | 80 | 20/80 (25.00%; 95% CI 16.81–35.48) | 71/80 (88.75%; 95% CI 79.98–93.97) | 53/80 (66.25%; 95% CI 55.36–75.65) | 39/80 (48.75%; 95% CI 38.11–59.51) | 6/17 (35.29%; 95% CI 17.31–58.70) | 2.8829 | 2.5836 |
| 15m | 275 | 228 | 29/228 (12.72%; 95% CI 9.00–17.67) | 209/228 (91.67%; 95% CI 87.35–94.60) | 183/228 (80.26%; 95% CI 74.61–84.91) | 169/228 (74.12%; 95% CI 68.07–79.37) | 48/101 (47.52%; 95% CI 38.06–57.18) | 6.976 | 6.2691 |
| 1D | 678 | 508 | 84/508 (16.54%; 95% CI 13.56–20.01) | 448/508 (88.19%; 95% CI 85.09–90.71) | 360/508 (70.87%; 95% CI 66.77–74.65) | 304/508 (59.84%; 95% CI 55.52–64.02) | 81/177 (45.76%; 95% CI 38.59–53.11) | 4.1399 | 4.353 |
| 1W | 312 | 225 | 61/225 (27.11%; 95% CI 21.72–33.27) | 199/225 (88.44%; 95% CI 83.61–91.99) | 151/225 (67.11%; 95% CI 60.73–72.92) | 120/225 (53.33%; 95% CI 46.81–59.74) | 37/68 (54.41%; 95% CI 42.66–65.70) | 3.3047 | 2.6279 |
| 75m | 185 | 144 | 23/144 (15.97%; 95% CI 10.89–22.83) | 135/144 (93.75%; 95% CI 88.55–96.68) | 115/144 (79.86%; 95% CI 72.57–85.60) | 96/144 (66.67%; 95% CI 58.62–73.84) | 20/44 (45.45%; 95% CI 31.71–59.93) | 4.5592 | 3.5416 |

## Table C — Demand vs Supply

| Group | Zones | Interacted | Survival | >=1ZW | >=2ZW | >=3ZW | Target reached | Median MFE (ZW) | Median MAE (ZW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DEMAND | 831 | 607 | 133/607 (21.91%; 95% CI 18.80–25.37) | 553/607 (91.10%; 95% CI 88.57–93.12) | 463/607 (76.28%; 95% CI 72.73–79.49) | 405/607 (66.72%; 95% CI 62.88–70.35) | 86/161 (53.42%; 95% CI 45.72–60.95) | 5.3303 | 3.5728 |
| SUPPLY | 737 | 578 | 84/578 (14.53%; 95% CI 11.89–17.64) | 509/578 (88.06%; 95% CI 85.16–90.46) | 399/578 (69.03%; 95% CI 65.15–72.66) | 323/578 (55.88%; 95% CI 51.81–59.88) | 106/246 (43.09%; 95% CI 37.05–49.34) | 3.7891 | 4.6645 |

## Table D — Pattern performance

| Group | Zones | Interacted | Survival | >=1ZW | >=2ZW | >=3ZW | Target reached | Median MFE (ZW) | Median MAE (ZW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DBD | 467 | 368 | 47/368 (12.77%; 95% CI 9.74–16.57) | 327/368 (88.86%; 95% CI 85.23–91.68) | 255/368 (69.29%; 95% CI 64.40–73.79) | 202/368 (54.89%; 95% CI 49.78–59.90) | 65/159 (40.88%; 95% CI 33.54–48.65) | 3.6487 | 4.9815 |
| DBR | 393 | 286 | 64/286 (22.38%; 95% CI 17.93–27.56) | 256/286 (89.51%; 95% CI 85.42–92.55) | 207/286 (72.38%; 95% CI 66.92–77.24) | 185/286 (64.69%; 95% CI 58.98–70.00) | 38/79 (48.10%; 95% CI 37.43–58.95) | 4.2158 | 3.6054 |
| RBD | 270 | 210 | 37/210 (17.62%; 95% CI 13.06–23.34) | 182/210 (86.67%; 95% CI 81.40–90.61) | 144/210 (68.57%; 95% CI 62.01–74.47) | 121/210 (57.62%; 95% CI 50.86–64.11) | 41/87 (47.13%; 95% CI 36.98–57.51) | 3.9649 | 4.2088 |
| RBR | 438 | 321 | 69/321 (21.50%; 95% CI 17.35–26.31) | 297/321 (92.52%; 95% CI 89.12–94.92) | 256/321 (79.75%; 95% CI 75.01–83.78) | 220/321 (68.54%; 95% CI 63.26–73.37) | 48/82 (58.54%; 95% CI 47.73–68.58) | 6.09 | 3.5591 |

## Table E — Zone Quality bands

Excluded: point-in-time Zone Quality was not stored in the frozen replay. Reconstructing it from a later snapshot would violate the no-look-ahead rule.

## Table F — Trade Confidence labels

Excluded: point-in-time HTF Location, Trend and Trade Confidence were not stored. No values were fabricated.

## Table G — Zone Quality x Trade Confidence

Excluded because both point-in-time dimensions are unavailable.

## Table H — Fresh vs Tested at planning time

| Group | Zones | Interacted | Survival | >=1ZW | >=2ZW | >=3ZW | Target reached | Median MFE (ZW) | Median MAE (ZW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FORMING | 1568 | 1185 | 217/1185 (18.31%; 95% CI 16.21–20.62) | 1062/1185 (89.62%; 95% CI 87.75–91.23) | 862/1185 (72.74%; 95% CI 70.14–75.20) | 728/1185 (61.43%; 95% CI 58.63–64.16) | 192/407 (47.17%; 95% CI 42.37–52.03) | 4.2979 | 3.8982 |

## Table I — Year-by-year

| Group | Zones | Interacted | Survival | >=1ZW | >=2ZW | >=3ZW | Target reached | Median MFE (ZW) | Median MAE (ZW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 54 | 50 | 10/50 (20.00%; 95% CI 11.24–33.04) | 50/50 (100.00%; 95% CI 92.87–100.00) | 46/50 (92.00%; 95% CI 81.16–96.85) | 43/50 (86.00%; 95% CI 73.81–93.05) | 6/7 (85.71%; 95% CI 48.69–97.43) | 6.6882 | 3.9103 |
| 2022 | 119 | 106 | 11/106 (10.38%; 95% CI 5.89–17.63) | 97/106 (91.51%; 95% CI 84.65–95.47) | 79/106 (74.53%; 95% CI 65.48–81.86) | 69/106 (65.09%; 95% CI 55.64–73.50) | 23/42 (54.76%; 95% CI 39.95–68.78) | 4.6632 | 5.0726 |
| 2023 | 118 | 98 | 19/98 (19.39%; 95% CI 12.78–28.31) | 89/98 (90.82%; 95% CI 83.46–95.09) | 78/98 (79.59%; 95% CI 70.57–86.38) | 67/98 (68.37%; 95% CI 58.62–76.73) | 26/39 (66.67%; 95% CI 50.98–79.37) | 6.7262 | 5.0883 |
| 2024 | 115 | 90 | 14/90 (15.56%; 95% CI 9.50–24.43) | 86/90 (95.56%; 95% CI 89.12–98.26) | 64/90 (71.11%; 95% CI 61.04–79.46) | 55/90 (61.11%; 95% CI 50.78–70.53) | 13/45 (28.89%; 95% CI 17.73–43.37) | 4.4029 | 5.4277 |
| 2025 | 300 | 213 | 36/213 (16.90%; 95% CI 12.47–22.51) | 191/213 (89.67%; 95% CI 84.86–93.08) | 149/213 (69.95%; 95% CI 63.49–75.71) | 122/213 (57.28%; 95% CI 50.56–63.73) | 40/83 (48.19%; 95% CI 37.76–58.78) | 3.8007 | 3.4457 |
| 2026 | 862 | 628 | 127/628 (20.22%; 95% CI 17.27–23.54) | 549/628 (87.42%; 95% CI 84.60–89.79) | 446/628 (71.02%; 95% CI 67.35–74.43) | 372/628 (59.24%; 95% CI 55.35–63.01) | 84/191 (43.98%; 95% CI 37.13–51.07) | 4.0093 | 3.4289 |

## Table J — Structural plan outcomes

| Group | Zones | Interacted | Survival | >=1ZW | >=2ZW | >=3ZW | Target reached | Median MFE (ZW) | Median MAE (ZW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Plans | 1568 | 1185 | 217/1185 (18.31%; 95% CI 16.21–20.62) | 1062/1185 (89.62%; 95% CI 87.75–91.23) | 862/1185 (72.74%; 95% CI 70.14–75.20) | 728/1185 (61.43%; 95% CI 58.63–64.16) | 192/407 (47.17%; 95% CI 42.37–52.03) | 4.2979 | 3.8982 |

## Table K — Symbol robustness

| Group | Zones | Interacted | Survival | >=1ZW | >=2ZW | >=3ZW | Target reached | Median MFE (ZW) | Median MAE (ZW) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 360ONE | 64 | 56 | 12/56 (21.43%; 95% CI 12.71–33.82) | 47/56 (83.93%; 95% CI 72.19–91.31) | 39/56 (69.64%; 95% CI 56.66–80.10) | 31/56 (55.36%; 95% CI 42.41–67.61) | 6/11 (54.55%; 95% CI 28.01–78.73) | 3.3956 | 2.8432 |
| ALKEM | 48 | 40 | 6/40 (15.00%; 95% CI 7.06–29.07) | 37/40 (92.50%; 95% CI 80.14–97.42) | 31/40 (77.50%; 95% CI 62.50–87.68) | 28/40 (70.00%; 95% CI 54.57–81.93) | 7/15 (46.67%; 95% CI 24.81–69.88) | 6.3213 | 3.5414 |
| AUBANK | 61 | 44 | 8/44 (18.18%; 95% CI 9.51–31.96) | 39/44 (88.64%; 95% CI 76.02–95.05) | 33/44 (75.00%; 95% CI 60.56–85.43) | 29/44 (65.91%; 95% CI 51.14–78.12) | 5/12 (41.67%; 95% CI 19.33–68.05) | 4.9327 | 3.1527 |
| BAJFINANCE | 51 | 39 | 11/39 (28.21%; 95% CI 16.54–43.78) | 36/39 (92.31%; 95% CI 79.68–97.35) | 25/39 (64.10%; 95% CI 48.42–77.26) | 18/39 (46.15%; 95% CI 31.57–61.43) | 6/13 (46.15%; 95% CI 23.21–70.86) | 2.9344 | 4.1972 |
| BSOFT | 54 | 34 | 7/34 (20.59%; 95% CI 10.35–36.80) | 31/34 (91.18%; 95% CI 77.04–96.95) | 23/34 (67.65%; 95% CI 50.84–80.87) | 19/34 (55.88%; 95% CI 39.45–71.12) | 5/13 (38.46%; 95% CI 17.71–64.48) | 3.3526 | 4.9292 |
| COHANCE | 51 | 36 | 6/36 (16.67%; 95% CI 7.87–31.89) | 33/36 (91.67%; 95% CI 78.17–97.13) | 28/36 (77.78%; 95% CI 61.92–88.28) | 26/36 (72.22%; 95% CI 56.01–84.15) | 6/11 (54.55%; 95% CI 28.01–78.73) | 5.6148 | 4.0233 |
| EIHOTEL | 45 | 36 | 9/36 (25.00%; 95% CI 13.75–41.07) | 27/36 (75.00%; 95% CI 58.93–86.25) | 22/36 (61.11%; 95% CI 44.86–75.22) | 16/36 (44.44%; 95% CI 29.54–60.42) | 2/7 (28.57%; 95% CI 8.22–64.11) | 2.6424 | 4.7022 |
| GLAXO | 54 | 36 | 5/36 (13.89%; 95% CI 6.08–28.66) | 36/36 (100.00%; 95% CI 90.36–100.00) | 32/36 (88.89%; 95% CI 74.69–95.59) | 26/36 (72.22%; 95% CI 56.01–84.15) | 7/16 (43.75%; 95% CI 23.10–66.82) | 6.1356 | 5.5243 |
| HDFCBANK | 65 | 50 | 13/50 (26.00%; 95% CI 15.87–39.55) | 42/50 (84.00%; 95% CI 71.49–91.66) | 30/50 (60.00%; 95% CI 46.18–72.39) | 24/50 (48.00%; 95% CI 34.80–61.49) | 6/15 (40.00%; 95% CI 19.82–64.25) | 2.7315 | 2.9915 |
| HINDALCO | 54 | 36 | 11/36 (30.56%; 95% CI 18.00–46.86) | 31/36 (86.11%; 95% CI 71.34–93.92) | 27/36 (75.00%; 95% CI 58.93–86.25) | 25/36 (69.44%; 95% CI 53.14–82.00) | 6/15 (40.00%; 95% CI 19.82–64.25) | 6.3158 | 2.3847 |
| ICICIBANK | 62 | 53 | 11/53 (20.75%; 95% CI 12.00–33.46) | 50/53 (94.34%; 95% CI 84.63–98.06) | 38/53 (71.70%; 95% CI 58.43–82.03) | 33/53 (62.26%; 95% CI 48.81–74.06) | 5/16 (31.25%; 95% CI 14.16–55.60) | 3.7 | 2.8568 |
| INDUSINDBK | 52 | 35 | 2/35 (5.71%; 95% CI 1.58–18.61) | 34/35 (97.14%; 95% CI 85.47–99.49) | 28/35 (80.00%; 95% CI 64.11–89.96) | 25/35 (71.43%; 95% CI 54.95–83.67) | 6/12 (50.00%; 95% CI 25.38–74.62) | 7.502 | 3.974 |
| INFY | 56 | 44 | 7/44 (15.91%; 95% CI 7.93–29.37) | 40/44 (90.91%; 95% CI 78.84–96.41) | 31/44 (70.45%; 95% CI 55.78–81.84) | 30/44 (68.18%; 95% CI 53.44–80.00) | 7/16 (43.75%; 95% CI 23.10–66.82) | 4.6719 | 3.6146 |
| ITC | 57 | 40 | 5/40 (12.50%; 95% CI 5.46–26.11) | 39/40 (97.50%; 95% CI 87.12–99.56) | 30/40 (75.00%; 95% CI 59.81–85.81) | 24/40 (60.00%; 95% CI 44.60–73.65) | 7/12 (58.33%; 95% CI 31.95–80.67) | 3.9129 | 2.6733 |
| JSWENERGY | 51 | 43 | 8/43 (18.60%; 95% CI 9.74–32.62) | 38/43 (88.37%; 95% CI 75.52–94.93) | 34/43 (79.07%; 95% CI 64.79–88.58) | 24/43 (55.81%; 95% CI 41.11–69.57) | 10/17 (58.82%; 95% CI 36.01–78.39) | 3.6985 | 3.6819 |
| LLOYDSME | 63 | 52 | 12/52 (23.08%; 95% CI 13.72–36.13) | 47/52 (90.38%; 95% CI 79.39–95.82) | 41/52 (78.85%; 95% CI 65.97–87.76) | 34/52 (65.38%; 95% CI 51.80–76.85) | 12/18 (66.67%; 95% CI 43.75–83.72) | 4.1368 | 3.4517 |
| MARUTI | 59 | 41 | 11/41 (26.83%; 95% CI 15.69–41.93) | 38/41 (92.68%; 95% CI 80.57–97.48) | 32/41 (78.05%; 95% CI 63.29–88.00) | 28/41 (68.29%; 95% CI 53.02–80.44) | 5/15 (33.33%; 95% CI 15.18–58.29) | 5.2024 | 2.6091 |
| MAXHEALTH | 56 | 42 | 11/42 (26.19%; 95% CI 15.30–41.07) | 38/42 (90.48%; 95% CI 77.93–96.23) | 33/42 (78.57%; 95% CI 64.06–88.29) | 30/42 (71.43%; 95% CI 56.43–82.83) | 8/18 (44.44%; 95% CI 24.56–66.28) | 5.9317 | 4.0044 |
| MRPL | 69 | 47 | 11/47 (23.40%; 95% CI 13.60–37.22) | 43/47 (91.49%; 95% CI 80.07–96.64) | 34/47 (72.34%; 95% CI 58.24–83.06) | 31/47 (65.96%; 95% CI 51.67–77.83) | 6/12 (50.00%; 95% CI 25.38–74.62) | 6.0556 | 4.1837 |
| OIL | 57 | 43 | 8/43 (18.60%; 95% CI 9.74–32.62) | 36/43 (83.72%; 95% CI 70.03–91.88) | 29/43 (67.44%; 95% CI 52.52–79.51) | 27/43 (62.79%; 95% CI 47.86–75.62) | 13/25 (52.00%; 95% CI 33.50–69.97) | 5.0959 | 8.2726 |
| PREMIERENE | 52 | 40 | 4/40 (10.00%; 95% CI 3.96–23.05) | 39/40 (97.50%; 95% CI 87.12–99.56) | 27/40 (67.50%; 95% CI 52.02–79.92) | 22/40 (55.00%; 95% CI 39.83–69.29) | 11/17 (64.71%; 95% CI 41.30–82.69) | 3.2323 | 2.7232 |
| RELIANCE | 62 | 51 | 6/51 (11.76%; 95% CI 5.51–23.38) | 47/51 (92.16%; 95% CI 81.50–96.91) | 37/51 (72.55%; 95% CI 59.05–82.89) | 30/51 (58.82%; 95% CI 45.17–71.25) | 7/17 (41.18%; 95% CI 21.61–63.99) | 4.537 | 5.7368 |
| SBIN | 55 | 37 | 1/37 (2.70%; 95% CI 0.48–13.82) | 32/37 (86.49%; 95% CI 72.02–94.09) | 27/37 (72.97%; 95% CI 57.02–84.60) | 22/37 (59.46%; 95% CI 43.49–73.65) | 3/14 (21.43%; 95% CI 7.57–47.59) | 4.3362 | 6.4166 |
| SUNPHARMA | 56 | 47 | 4/47 (8.51%; 95% CI 3.36–19.93) | 40/47 (85.11%; 95% CI 72.31–92.59) | 34/47 (72.34%; 95% CI 58.24–83.06) | 25/47 (53.19%; 95% CI 39.23–66.67) | 3/7 (42.86%; 95% CI 15.82–74.95) | 3.3772 | 4.935 |
| TATACHEM | 50 | 44 | 6/44 (13.64%; 95% CI 6.40–26.71) | 38/44 (86.36%; 95% CI 73.29–93.60) | 31/44 (70.45%; 95% CI 55.78–81.84) | 27/44 (61.36%; 95% CI 46.62–74.28) | 8/14 (57.14%; 95% CI 32.59–78.62) | 4.3909 | 7.9404 |
| TCS | 51 | 41 | 7/41 (17.07%; 95% CI 8.53–31.26) | 36/41 (87.80%; 95% CI 74.46–94.68) | 28/41 (68.29%; 95% CI 53.02–80.44) | 26/41 (63.41%; 95% CI 48.12–76.41) | 8/13 (61.54%; 95% CI 35.52–82.29) | 3.822 | 3.0002 |
| TVSMOTOR | 62 | 42 | 10/42 (23.81%; 95% CI 13.48–38.53) | 35/42 (83.33%; 95% CI 69.40–91.68) | 28/42 (66.67%; 95% CI 51.55–78.99) | 22/42 (52.38%; 95% CI 37.72–66.64) | 9/17 (52.94%; 95% CI 30.96–73.83) | 3.2036 | 4.0861 |
| ZYDUSWELL | 51 | 36 | 5/36 (13.89%; 95% CI 6.08–28.66) | 33/36 (91.67%; 95% CI 78.17–97.13) | 30/36 (83.33%; 95% CI 68.11–92.13) | 26/36 (72.22%; 95% CI 56.01–84.15) | 8/19 (42.11%; 95% CI 23.14–63.72) | 5.5439 | 3.9021 |

## Table L — Data quality and exclusions

| Item | Result |
|---|---|
| Requested series | 140 |
| Successful series | 140 |
| Failed series | 0 |
| Reconstruction failures | 0 |
| Provider | YahooProvider |
| Corporate actions | Provider-adjusted history; independent corporate-action audit unavailable |
| Historical membership | Unavailable; current-constituent survivorship bias remains |
| Intraday history | Provider retention shorter than five years |
| Complete-zone census | No; maximum eight zones per valid segment |

## Direct answers

A. The frozen sample reconstructed 1568 canonical zones; this is not the total five-year NSE 500 count.
B. 1185/1568 (75.57%; 95% CI 73.39–77.64) interacted within the frozen horizon.
C. 217/1185 (18.31%; 95% CI 16.21–20.62) of interacted zones structurally survived.
D. >=1ZW 1062/1185 (89.62%; 95% CI 87.75–91.23); >=2ZW 862/1185 (72.74%; 95% CI 70.14–75.20); >=3ZW 728/1185 (61.43%; 95% CI 58.63–64.16); >=5ZW 541/1185 (45.65%; 95% CI 42.84–48.50).
E. 192/407 (47.17%; 95% CI 42.37–52.03) reached the structural target where a point-in-time target existed.
F–H. Demand/Supply, pattern and timeframe comparisons are shown in Tables B–D; small samples must be treated cautiously.
I–L. Zone Quality and Trade Confidence predictive ordering cannot be answered from this frozen replay without look-ahead leakage; they are explicitly excluded.
M. Year stability is shown in Table I, with partial 2021 and 2026 periods.
N. Symbol dispersion is shown in Table K. The deterministic 28-symbol sample is too small for an NSE-wide robustness claim.
O. Main uncertainty: current-constituent survivorship bias, limited intraday history, sampled zones, provider-adjusted corporate actions, and missing point-in-time ZQ/TC context.
P. The sample provides descriptive evidence about structural zone behavior, but it is not sufficient for a final claim about the complete AlphaEdge methodology.
Q. Formation/lifecycle/structural-plan behavior can be evaluated here. ZQ and TC predictive power remain unvalidated until a new replay stores those fields at T.

## Point-in-time controls

Zones were first discovered for audit indexing, then reconstructed from a candle prefix ending at the historical planning timestamp. Lifecycle, authenticity and opposing targets were computed from that prefix. Later candles were exposed only to outcome observation. Any metric not frozen at T was excluded rather than backfilled.

## Production impact

None. This report and its aggregation utilities are isolated research artifacts. Frozen Formation V1.1, boundaries, lifecycle, authenticity, Zone Quality, HTF Location, Trend, Trade Confidence, Dashboard qualification, ranking and Trade Planning V1 were not changed.
