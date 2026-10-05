# Milestone 8 - Historical Trade Planning Replay

> Research infrastructure only. Canonical Trade Planning V1 is not active.

## Dataset

- Symbols requested: 12
- Successful symbol/timeframe series: 60
- Failed series: 0
- Reconstructed canonical zones: 693
- Date range: 2021-08-17 00:00:00 to 2026-08-21 00:00:00
- Provider: YahooProvider
- Tick size: unavailable from the current provider contract; no universal tick was assumed.

## Coverage

- Timeframes: {'15m': 136, '75m': 80, '125m': 57, '1D': 290, '1W': 130}
- Zone types: {'DEMAND': 390, 'SUPPLY': 303}
- Patterns: {'DBR': 166, 'DBD': 180, 'RBR': 224, 'RBD': 123}

## Entry x stop results

| Timeframe | Entry | Stop | Zones | Fill % | Target first % | Stop first % | Median R:R | Median MAE/ATR | Median MFE/ATR |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 125m | DISTAL | ATR14_10 | 48 | 56.25 | 0.00 | 100.00 | 33.0528 | 0.4546 | 1.0998 |
| 125m | DISTAL | ATR14_15 | 48 | 56.25 | 0.00 | 100.00 | 22.0352 | 0.4717 | 1.1172 |
| 125m | DISTAL | ATR14_20 | 48 | 56.25 | 0.00 | 100.00 | 16.5264 | 0.4717 | 1.1299 |
| 125m | DISTAL | ATR14_5 | 48 | 56.25 | 0.00 | 100.00 | 66.1057 | 0.3911 | 1.0039 |
| 125m | DISTAL | HYBRID_MAX_ZW_ATR_10 | 48 | 56.25 | 0.00 | 100.00 | 32.3817 | 0.4546 | 1.0998 |
| 125m | DISTAL | HYBRID_MAX_ZW_ATR_15 | 48 | 56.25 | 0.00 | 100.00 | 21.5878 | 0.4717 | 1.1172 |
| 125m | DISTAL | HYBRID_MAX_ZW_ATR_20 | 48 | 56.25 | 0.00 | 100.00 | 16.1908 | 0.4717 | 1.1299 |
| 125m | DISTAL | HYBRID_MAX_ZW_ATR_5 | 48 | 56.25 | 0.00 | 100.00 | 64.7634 | 0.3911 | 1.0039 |
| 125m | DISTAL | ZONE_WIDTH_10 | 57 | 57.89 | 0.00 | 100.00 | 59.4319 | 0.3911 | 1.0039 |
| 125m | DISTAL | ZONE_WIDTH_15 | 57 | 57.89 | 0.00 | 100.00 | 39.6213 | 0.4251 | 1.0998 |
| 125m | DISTAL | ZONE_WIDTH_20 | 57 | 57.89 | 0.00 | 100.00 | 29.7159 | 0.4668 | 1.0998 |
| 125m | DISTAL | ZONE_WIDTH_5 | 57 | 57.89 | 0.00 | 100.00 | 118.8638 | 0.3911 | 1.0039 |
| 125m | MIDPOINT | ATR14_10 | 48 | 66.67 | 25.00 | 75.00 | 8.2734 | 0.6486 | 1.0182 |
| 125m | MIDPOINT | ATR14_15 | 48 | 66.67 | 25.00 | 75.00 | 7.3871 | 0.6896 | 1.119 |
| 125m | MIDPOINT | ATR14_20 | 48 | 66.67 | 25.00 | 75.00 | 6.6723 | 0.6896 | 1.1443 |
| 125m | MIDPOINT | ATR14_5 | 48 | 66.67 | 25.00 | 75.00 | 9.4016 | 0.5848 | 0.9721 |
| 125m | MIDPOINT | HYBRID_MAX_ZW_ATR_10 | 48 | 66.67 | 25.00 | 75.00 | 8.2734 | 0.6486 | 1.0182 |
| 125m | MIDPOINT | HYBRID_MAX_ZW_ATR_15 | 48 | 66.67 | 25.00 | 75.00 | 7.3871 | 0.6896 | 1.119 |
| 125m | MIDPOINT | HYBRID_MAX_ZW_ATR_20 | 48 | 66.67 | 25.00 | 75.00 | 6.6723 | 0.6896 | 1.1443 |
| 125m | MIDPOINT | HYBRID_MAX_ZW_ATR_5 | 48 | 66.67 | 25.00 | 75.00 | 9.4016 | 0.5848 | 0.9721 |
| 125m | MIDPOINT | ZONE_WIDTH_10 | 57 | 68.42 | 25.00 | 75.00 | 9.072 | 0.6099 | 0.9721 |
| 125m | MIDPOINT | ZONE_WIDTH_15 | 57 | 68.42 | 25.00 | 75.00 | 8.3741 | 0.627 | 1.0736 |
| 125m | MIDPOINT | ZONE_WIDTH_20 | 57 | 68.42 | 25.00 | 75.00 | 7.776 | 0.6704 | 1.0736 |
| 125m | MIDPOINT | ZONE_WIDTH_5 | 57 | 68.42 | 25.00 | 75.00 | 9.8967 | 0.5848 | 0.9721 |
| 125m | PROXIMAL | ATR14_10 | 48 | 70.83 | 25.00 | 75.00 | 4.2689 | 0.9711 | 1.0234 |
| 125m | PROXIMAL | ATR14_15 | 48 | 70.83 | 25.00 | 75.00 | 3.9963 | 0.9829 | 1.1171 |
| 125m | PROXIMAL | ATR14_20 | 48 | 70.83 | 25.00 | 75.00 | 3.7565 | 0.9829 | 1.2192 |
| 125m | PROXIMAL | ATR14_5 | 48 | 70.83 | 25.00 | 75.00 | 4.5813 | 0.89 | 0.9856 |
| 125m | PROXIMAL | HYBRID_MAX_ZW_ATR_10 | 48 | 70.83 | 25.00 | 75.00 | 4.2689 | 0.9711 | 1.0234 |
| 125m | PROXIMAL | HYBRID_MAX_ZW_ATR_15 | 48 | 70.83 | 25.00 | 75.00 | 3.9963 | 0.9829 | 1.1171 |
| 125m | PROXIMAL | HYBRID_MAX_ZW_ATR_20 | 48 | 70.83 | 25.00 | 75.00 | 3.7565 | 0.9829 | 1.2192 |
| 125m | PROXIMAL | HYBRID_MAX_ZW_ATR_5 | 48 | 70.83 | 25.00 | 75.00 | 4.5813 | 0.89 | 0.9856 |
| 125m | PROXIMAL | ZONE_WIDTH_10 | 57 | 71.93 | 25.00 | 75.00 | 4.4938 | 0.89 | 0.9856 |
| 125m | PROXIMAL | ZONE_WIDTH_15 | 57 | 71.93 | 25.00 | 75.00 | 4.2984 | 0.89 | 1.0234 |
| 125m | PROXIMAL | ZONE_WIDTH_20 | 57 | 71.93 | 25.00 | 75.00 | 4.1193 | 0.9711 | 1.0234 |
| 125m | PROXIMAL | ZONE_WIDTH_5 | 57 | 71.93 | 25.00 | 75.00 | 4.7078 | 0.89 | 0.9856 |
| 15m | DISTAL | ATR14_10 | 128 | 71.09 | 2.56 | 97.44 | 53.503 | 0.5024 | 1.1773 |
| 15m | DISTAL | ATR14_15 | 128 | 71.09 | 2.56 | 97.44 | 35.6686 | 0.5166 | 1.2236 |
| 15m | DISTAL | ATR14_20 | 128 | 71.09 | 2.56 | 97.44 | 26.7515 | 0.5326 | 1.2296 |
| 15m | DISTAL | ATR14_5 | 128 | 71.09 | 2.56 | 97.44 | 107.0059 | 0.4566 | 1.1748 |
| 15m | DISTAL | HYBRID_MAX_ZW_ATR_10 | 128 | 71.09 | 2.56 | 97.44 | 44.5523 | 0.5024 | 1.1773 |
| 15m | DISTAL | HYBRID_MAX_ZW_ATR_15 | 128 | 71.09 | 5.13 | 94.87 | 29.7016 | 0.5166 | 1.2236 |
| 15m | DISTAL | HYBRID_MAX_ZW_ATR_20 | 128 | 71.09 | 7.69 | 92.31 | 22.2762 | 0.5326 | 1.248 |
| 15m | DISTAL | HYBRID_MAX_ZW_ATR_5 | 128 | 71.09 | 2.56 | 97.44 | 89.1047 | 0.4643 | 1.1773 |
| 15m | DISTAL | ZONE_WIDTH_10 | 136 | 72.06 | 2.56 | 97.44 | 70.2439 | 0.5024 | 1.1773 |
| 15m | DISTAL | ZONE_WIDTH_15 | 136 | 72.06 | 7.50 | 92.50 | 46.8293 | 0.5024 | 1.1773 |
| 15m | DISTAL | ZONE_WIDTH_20 | 136 | 72.06 | 10.00 | 90.00 | 35.122 | 0.5166 | 1.2298 |
| 15m | DISTAL | ZONE_WIDTH_5 | 136 | 72.06 | 2.56 | 97.44 | 140.4878 | 0.4643 | 1.1773 |
| 15m | MIDPOINT | ATR14_10 | 128 | 75.00 | 9.76 | 90.24 | 10.1261 | 0.7318 | 1.1383 |
| 15m | MIDPOINT | ATR14_15 | 128 | 75.00 | 9.76 | 90.24 | 9.2936 | 0.7573 | 1.1849 |
| 15m | MIDPOINT | ATR14_20 | 128 | 75.00 | 9.76 | 90.24 | 8.5061 | 0.779 | 1.2001 |
| 15m | MIDPOINT | ATR14_5 | 128 | 75.00 | 9.76 | 90.24 | 11.6317 | 0.7054 | 1.1383 |
| 15m | MIDPOINT | HYBRID_MAX_ZW_ATR_10 | 128 | 75.00 | 9.76 | 90.24 | 10.0872 | 0.7318 | 1.1383 |
| 15m | MIDPOINT | HYBRID_MAX_ZW_ATR_15 | 128 | 75.00 | 12.20 | 87.80 | 9.0837 | 0.7573 | 1.1849 |
| 15m | MIDPOINT | HYBRID_MAX_ZW_ATR_20 | 128 | 75.00 | 14.63 | 85.37 | 8.262 | 0.779 | 1.2001 |
| 15m | MIDPOINT | HYBRID_MAX_ZW_ATR_5 | 128 | 75.00 | 9.76 | 90.24 | 11.5717 | 0.7054 | 1.1383 |
| 15m | MIDPOINT | ZONE_WIDTH_10 | 136 | 75.74 | 9.76 | 90.24 | 10.874 | 0.7318 | 1.1383 |
| 15m | MIDPOINT | ZONE_WIDTH_15 | 136 | 75.74 | 14.29 | 85.71 | 10.0375 | 0.7318 | 1.1383 |
| 15m | MIDPOINT | ZONE_WIDTH_20 | 136 | 75.74 | 16.67 | 83.33 | 9.3206 | 0.7731 | 1.1553 |
| 15m | MIDPOINT | ZONE_WIDTH_5 | 136 | 75.74 | 9.76 | 90.24 | 11.8625 | 0.7054 | 1.1383 |
| 15m | PROXIMAL | ATR14_10 | 128 | 82.81 | 20.45 | 79.55 | 5.3934 | 0.9244 | 1.156 |
| 15m | PROXIMAL | ATR14_15 | 128 | 82.81 | 20.45 | 79.55 | 5.0088 | 0.9338 | 1.1853 |
| 15m | PROXIMAL | ATR14_20 | 128 | 82.81 | 20.45 | 79.55 | 4.6771 | 0.9613 | 1.195 |
| 15m | PROXIMAL | ATR14_5 | 128 | 82.81 | 20.45 | 79.55 | 5.7819 | 0.9089 | 1.156 |
| 15m | PROXIMAL | HYBRID_MAX_ZW_ATR_10 | 128 | 82.81 | 20.45 | 79.55 | 5.3555 | 0.9244 | 1.156 |
| 15m | PROXIMAL | HYBRID_MAX_ZW_ATR_15 | 128 | 82.81 | 20.45 | 79.55 | 5.0088 | 0.9338 | 1.1853 |
| 15m | PROXIMAL | HYBRID_MAX_ZW_ATR_20 | 128 | 82.81 | 20.45 | 79.55 | 4.6771 | 0.9613 | 1.195 |
| 15m | PROXIMAL | HYBRID_MAX_ZW_ATR_5 | 128 | 82.81 | 20.45 | 79.55 | 5.757 | 0.9089 | 1.156 |
| 15m | PROXIMAL | ZONE_WIDTH_10 | 136 | 83.09 | 20.45 | 79.55 | 5.4767 | 0.9159 | 1.156 |
| 15m | PROXIMAL | ZONE_WIDTH_15 | 136 | 83.09 | 22.22 | 77.78 | 5.2386 | 0.9244 | 1.156 |
| 15m | PROXIMAL | ZONE_WIDTH_20 | 136 | 83.09 | 22.22 | 77.78 | 5.0203 | 0.9338 | 1.156 |
| 15m | PROXIMAL | ZONE_WIDTH_5 | 136 | 83.09 | 20.45 | 79.55 | 5.7375 | 0.9089 | 1.156 |
| 1D | DISTAL | ATR14_10 | 244 | 62.30 | 5.56 | 94.44 | 37.5017 | 0.4007 | 0.846 |
| 1D | DISTAL | ATR14_15 | 244 | 62.30 | 7.27 | 92.73 | 25.0012 | 0.4281 | 0.8601 |
| 1D | DISTAL | ATR14_20 | 244 | 62.30 | 7.41 | 92.59 | 18.7509 | 0.4742 | 0.8694 |
| 1D | DISTAL | ATR14_5 | 244 | 62.30 | 3.70 | 96.30 | 75.0035 | 0.37 | 0.8161 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_10 | 244 | 62.30 | 5.56 | 94.44 | 34.0123 | 0.4116 | 0.846 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_15 | 244 | 62.30 | 7.27 | 92.73 | 22.6749 | 0.4391 | 0.8601 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_20 | 244 | 62.30 | 7.41 | 92.59 | 17.0062 | 0.4796 | 0.8694 |
| 1D | DISTAL | HYBRID_MAX_ZW_ATR_5 | 244 | 62.30 | 3.70 | 96.30 | 68.0247 | 0.3732 | 0.8161 |
| 1D | DISTAL | ZONE_WIDTH_10 | 290 | 62.76 | 3.64 | 96.36 | 60.2223 | 0.3794 | 0.827 |
| 1D | DISTAL | ZONE_WIDTH_15 | 290 | 62.76 | 5.45 | 94.55 | 40.1482 | 0.3893 | 0.827 |
| 1D | DISTAL | ZONE_WIDTH_20 | 290 | 62.76 | 5.45 | 94.55 | 30.1111 | 0.4123 | 0.846 |
| 1D | DISTAL | ZONE_WIDTH_5 | 290 | 62.76 | 3.64 | 96.36 | 120.4445 | 0.365 | 0.8161 |
| 1D | MIDPOINT | ATR14_10 | 244 | 66.80 | 14.29 | 85.71 | 8.3759 | 0.6814 | 0.8457 |
| 1D | MIDPOINT | ATR14_15 | 244 | 66.80 | 15.79 | 84.21 | 7.4429 | 0.7211 | 0.8643 |
| 1D | MIDPOINT | ATR14_20 | 244 | 66.80 | 16.07 | 83.93 | 6.4825 | 0.777 | 0.9074 |
| 1D | MIDPOINT | ATR14_5 | 244 | 66.80 | 12.50 | 87.50 | 9.408 | 0.6461 | 0.8117 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_10 | 244 | 66.80 | 14.29 | 85.71 | 8.3612 | 0.6814 | 0.8457 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_15 | 244 | 66.80 | 15.79 | 84.21 | 7.4429 | 0.7211 | 0.8779 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_20 | 244 | 66.80 | 16.07 | 83.93 | 6.4825 | 0.777 | 0.9074 |
| 1D | MIDPOINT | HYBRID_MAX_ZW_ATR_5 | 244 | 66.80 | 12.50 | 87.50 | 9.3993 | 0.6461 | 0.8117 |
| 1D | MIDPOINT | ZONE_WIDTH_10 | 290 | 67.24 | 12.28 | 87.72 | 9.2037 | 0.6658 | 0.8351 |
| 1D | MIDPOINT | ZONE_WIDTH_15 | 290 | 67.24 | 14.04 | 85.96 | 8.4957 | 0.6731 | 0.8389 |
| 1D | MIDPOINT | ZONE_WIDTH_20 | 290 | 67.24 | 14.04 | 85.96 | 7.8889 | 0.6863 | 0.8545 |
| 1D | MIDPOINT | ZONE_WIDTH_5 | 290 | 67.24 | 12.28 | 87.72 | 10.0404 | 0.6403 | 0.8117 |
| 1D | PROXIMAL | ATR14_10 | 244 | 71.72 | 20.34 | 79.66 | 4.2658 | 1.0008 | 1.006 |
| 1D | PROXIMAL | ATR14_15 | 244 | 71.72 | 21.67 | 78.33 | 4.0169 | 1.0251 | 1.006 |
| 1D | PROXIMAL | ATR14_20 | 244 | 71.72 | 22.03 | 77.97 | 3.7971 | 1.0516 | 1.0313 |
| 1D | PROXIMAL | ATR14_5 | 244 | 71.72 | 18.64 | 81.36 | 4.5505 | 0.9808 | 1.006 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_10 | 244 | 71.72 | 20.34 | 79.66 | 4.2619 | 1.0008 | 1.006 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_15 | 244 | 71.72 | 21.67 | 78.33 | 4.0115 | 1.0251 | 1.006 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_20 | 244 | 71.72 | 22.03 | 77.97 | 3.7905 | 1.0516 | 1.0313 |
| 1D | PROXIMAL | HYBRID_MAX_ZW_ATR_5 | 244 | 71.72 | 18.64 | 81.36 | 4.5483 | 0.9808 | 1.006 |
| 1D | PROXIMAL | ZONE_WIDTH_10 | 290 | 73.10 | 19.67 | 80.33 | 4.5657 | 0.9861 | 0.9692 |
| 1D | PROXIMAL | ZONE_WIDTH_15 | 290 | 73.10 | 21.31 | 78.69 | 4.3672 | 0.9955 | 1.006 |
| 1D | PROXIMAL | ZONE_WIDTH_20 | 290 | 73.10 | 21.31 | 78.69 | 4.1852 | 1.005 | 1.006 |
| 1D | PROXIMAL | ZONE_WIDTH_5 | 290 | 73.10 | 19.67 | 80.33 | 4.7831 | 0.9808 | 0.9692 |
| 1W | DISTAL | ATR14_10 | 104 | 52.88 | 6.25 | 93.75 | 29.3589 | 0.5429 | 1.013 |
| 1W | DISTAL | ATR14_15 | 104 | 52.88 | 6.25 | 93.75 | 19.5726 | 0.5569 | 1.013 |
| 1W | DISTAL | ATR14_20 | 104 | 52.88 | 6.25 | 93.75 | 14.6795 | 0.584 | 1.013 |
| 1W | DISTAL | ATR14_5 | 104 | 52.88 | 6.25 | 93.75 | 58.7179 | 0.4823 | 1.013 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_10 | 104 | 52.88 | 6.25 | 93.75 | 29.3589 | 0.5429 | 1.013 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_15 | 104 | 52.88 | 6.25 | 93.75 | 19.5726 | 0.5569 | 1.013 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_20 | 104 | 52.88 | 6.25 | 93.75 | 14.6795 | 0.584 | 1.013 |
| 1W | DISTAL | HYBRID_MAX_ZW_ATR_5 | 104 | 52.88 | 6.25 | 93.75 | 58.7179 | 0.4823 | 1.013 |
| 1W | DISTAL | ZONE_WIDTH_10 | 130 | 53.85 | 6.25 | 93.75 | 40.9961 | 0.5315 | 0.9941 |
| 1W | DISTAL | ZONE_WIDTH_15 | 130 | 53.85 | 6.25 | 93.75 | 27.3308 | 0.5563 | 1.013 |
| 1W | DISTAL | ZONE_WIDTH_20 | 130 | 53.85 | 6.25 | 93.75 | 20.4981 | 0.5673 | 1.013 |
| 1W | DISTAL | ZONE_WIDTH_5 | 130 | 53.85 | 0.00 | 100.00 | 81.9923 | 0.4429 | 0.9941 |
| 1W | MIDPOINT | ATR14_10 | 104 | 61.54 | 31.58 | 68.42 | 5.7126 | 0.7043 | 1.1868 |
| 1W | MIDPOINT | ATR14_15 | 104 | 61.54 | 31.58 | 68.42 | 5.1827 | 0.797 | 1.1868 |
| 1W | MIDPOINT | ATR14_20 | 104 | 61.54 | 31.58 | 68.42 | 4.7555 | 0.8279 | 1.1868 |
| 1W | MIDPOINT | ATR14_5 | 104 | 61.54 | 31.58 | 68.42 | 6.3694 | 0.6465 | 1.1868 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_10 | 104 | 61.54 | 31.58 | 68.42 | 5.7126 | 0.7043 | 1.1868 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_15 | 104 | 61.54 | 31.58 | 68.42 | 5.1827 | 0.797 | 1.1868 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_20 | 104 | 61.54 | 31.58 | 68.42 | 4.7555 | 0.8279 | 1.1868 |
| 1W | MIDPOINT | HYBRID_MAX_ZW_ATR_5 | 104 | 61.54 | 31.58 | 68.42 | 6.3694 | 0.6465 | 1.1868 |
| 1W | MIDPOINT | ZONE_WIDTH_10 | 130 | 62.31 | 31.58 | 68.42 | 5.9994 | 0.6821 | 1.1748 |
| 1W | MIDPOINT | ZONE_WIDTH_15 | 130 | 62.31 | 31.58 | 68.42 | 5.5379 | 0.7326 | 1.1868 |
| 1W | MIDPOINT | ZONE_WIDTH_20 | 130 | 62.31 | 31.58 | 68.42 | 5.1423 | 0.8279 | 1.1868 |
| 1W | MIDPOINT | ZONE_WIDTH_5 | 130 | 62.31 | 27.78 | 72.22 | 6.5448 | 0.6315 | 1.1748 |
| 1W | PROXIMAL | ATR14_10 | 104 | 69.23 | 42.86 | 57.14 | 2.7423 | 0.9913 | 1.3575 |
| 1W | PROXIMAL | ATR14_15 | 104 | 69.23 | 42.86 | 57.14 | 2.5932 | 1.0309 | 1.3575 |
| 1W | PROXIMAL | ATR14_20 | 104 | 69.23 | 42.86 | 57.14 | 2.4595 | 1.0309 | 1.3575 |
| 1W | PROXIMAL | ATR14_5 | 104 | 69.23 | 42.86 | 57.14 | 2.9099 | 0.8907 | 1.3575 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_10 | 104 | 69.23 | 42.86 | 57.14 | 2.7423 | 0.9913 | 1.3575 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_15 | 104 | 69.23 | 42.86 | 57.14 | 2.5932 | 1.0309 | 1.3575 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_20 | 104 | 69.23 | 42.86 | 57.14 | 2.4595 | 1.0309 | 1.3575 |
| 1W | PROXIMAL | HYBRID_MAX_ZW_ATR_5 | 104 | 69.23 | 42.86 | 57.14 | 2.9099 | 0.8907 | 1.3575 |
| 1W | PROXIMAL | ZONE_WIDTH_10 | 130 | 70.00 | 42.86 | 57.14 | 2.8178 | 0.9408 | 1.3338 |
| 1W | PROXIMAL | ZONE_WIDTH_15 | 130 | 70.00 | 42.86 | 57.14 | 2.6953 | 0.9913 | 1.3575 |
| 1W | PROXIMAL | ZONE_WIDTH_20 | 130 | 70.00 | 42.86 | 57.14 | 2.583 | 1.0309 | 1.3575 |
| 1W | PROXIMAL | ZONE_WIDTH_5 | 130 | 70.00 | 40.00 | 60.00 | 2.952 | 0.8783 | 1.3338 |
| 75m | DISTAL | ATR14_10 | 70 | 57.14 | 9.09 | 90.91 | 33.0102 | 0.4211 | 0.952 |
| 75m | DISTAL | ATR14_15 | 70 | 57.14 | 9.09 | 90.91 | 22.0068 | 0.5302 | 0.952 |
| 75m | DISTAL | ATR14_20 | 70 | 57.14 | 9.09 | 90.91 | 16.5051 | 0.5628 | 1.0525 |
| 75m | DISTAL | ATR14_5 | 70 | 57.14 | 0.00 | 100.00 | 66.0204 | 0.3315 | 0.9358 |
| 75m | DISTAL | HYBRID_MAX_ZW_ATR_10 | 70 | 57.14 | 9.09 | 90.91 | 24.8044 | 0.4756 | 0.952 |
| 75m | DISTAL | HYBRID_MAX_ZW_ATR_15 | 70 | 57.14 | 9.09 | 90.91 | 16.5363 | 0.5302 | 0.952 |
| 75m | DISTAL | HYBRID_MAX_ZW_ATR_20 | 70 | 57.14 | 9.09 | 90.91 | 12.4022 | 0.5628 | 1.0525 |
| 75m | DISTAL | HYBRID_MAX_ZW_ATR_5 | 70 | 57.14 | 0.00 | 100.00 | 49.6089 | 0.3315 | 0.9358 |
| 75m | DISTAL | ZONE_WIDTH_10 | 80 | 61.25 | 0.00 | 100.00 | 55.2078 | 0.406 | 0.9358 |
| 75m | DISTAL | ZONE_WIDTH_15 | 80 | 61.25 | 0.00 | 100.00 | 36.8052 | 0.4756 | 0.952 |
| 75m | DISTAL | ZONE_WIDTH_20 | 80 | 61.25 | 0.00 | 100.00 | 27.6039 | 0.5034 | 0.952 |
| 75m | DISTAL | ZONE_WIDTH_5 | 80 | 61.25 | 0.00 | 100.00 | 110.4155 | 0.3315 | 0.9358 |
| 75m | MIDPOINT | ATR14_10 | 70 | 64.29 | 16.67 | 83.33 | 6.9853 | 0.676 | 1.1179 |
| 75m | MIDPOINT | ATR14_15 | 70 | 64.29 | 16.67 | 83.33 | 6.3239 | 0.7761 | 1.1179 |
| 75m | MIDPOINT | ATR14_20 | 70 | 64.29 | 16.67 | 83.33 | 5.7785 | 0.8696 | 1.2353 |
| 75m | MIDPOINT | ATR14_5 | 70 | 64.29 | 8.33 | 91.67 | 7.9207 | 0.6626 | 0.8821 |
| 75m | MIDPOINT | HYBRID_MAX_ZW_ATR_10 | 70 | 64.29 | 16.67 | 83.33 | 6.9853 | 0.754 | 1.1179 |
| 75m | MIDPOINT | HYBRID_MAX_ZW_ATR_15 | 70 | 64.29 | 16.67 | 83.33 | 6.3239 | 0.7761 | 1.2338 |
| 75m | MIDPOINT | HYBRID_MAX_ZW_ATR_20 | 70 | 64.29 | 16.67 | 83.33 | 5.7785 | 0.8696 | 1.2353 |
| 75m | MIDPOINT | HYBRID_MAX_ZW_ATR_5 | 70 | 64.29 | 8.33 | 91.67 | 7.9207 | 0.6626 | 0.8821 |
| 75m | MIDPOINT | ZONE_WIDTH_10 | 80 | 67.50 | 8.33 | 91.67 | 8.368 | 0.7462 | 0.8821 |
| 75m | MIDPOINT | ZONE_WIDTH_15 | 80 | 67.50 | 8.33 | 91.67 | 7.7243 | 0.754 | 1.1564 |
| 75m | MIDPOINT | ZONE_WIDTH_20 | 80 | 67.50 | 8.33 | 91.67 | 7.1725 | 0.7562 | 1.1564 |
| 75m | MIDPOINT | ZONE_WIDTH_5 | 80 | 67.50 | 8.33 | 91.67 | 9.1287 | 0.6626 | 0.8821 |
| 75m | PROXIMAL | ATR14_10 | 70 | 70.00 | 23.08 | 76.92 | 3.5567 | 0.9297 | 1.1748 |
| 75m | PROXIMAL | ATR14_15 | 70 | 70.00 | 23.08 | 76.92 | 3.2684 | 1.1038 | 1.1748 |
| 75m | PROXIMAL | ATR14_20 | 70 | 70.00 | 23.08 | 76.92 | 3.0967 | 1.1725 | 1.2817 |
| 75m | PROXIMAL | ATR14_5 | 70 | 70.00 | 15.38 | 84.62 | 3.9712 | 0.8789 | 1.1416 |
| 75m | PROXIMAL | HYBRID_MAX_ZW_ATR_10 | 70 | 70.00 | 23.08 | 76.92 | 3.5567 | 0.9297 | 1.1748 |
| 75m | PROXIMAL | HYBRID_MAX_ZW_ATR_15 | 70 | 70.00 | 23.08 | 76.92 | 3.2684 | 1.1038 | 1.1748 |
| 75m | PROXIMAL | HYBRID_MAX_ZW_ATR_20 | 70 | 70.00 | 23.08 | 76.92 | 3.0967 | 1.1725 | 1.2817 |
| 75m | PROXIMAL | HYBRID_MAX_ZW_ATR_5 | 70 | 70.00 | 15.38 | 84.62 | 3.9712 | 0.8789 | 1.1416 |
| 75m | PROXIMAL | ZONE_WIDTH_10 | 80 | 73.75 | 15.38 | 84.62 | 4.1098 | 0.8861 | 1.1416 |
| 75m | PROXIMAL | ZONE_WIDTH_15 | 80 | 73.75 | 15.38 | 84.62 | 3.9311 | 0.8861 | 1.1707 |
| 75m | PROXIMAL | ZONE_WIDTH_20 | 80 | 73.75 | 15.38 | 84.62 | 3.7673 | 0.8861 | 1.1707 |
| 75m | PROXIMAL | ZONE_WIDTH_5 | 80 | 73.75 | 15.38 | 84.62 | 4.3055 | 0.8789 | 1.1416 |

## Look-ahead protection

- Every accepted zone is re-detected on an OHLCV prefix ending at its Leg-Out planning candle.
- Wilder ATR(14) is calculated on that prefix only: first ATR is the mean of 14 True Ranges; later values use Wilder smoothing `(prior ATR * 13 + TR) / 14`.
- Opposing zones are limited to the same symbol, timeframe, and prefix snapshot.
- Targets must be directionally ahead, lifecycle-active, and Authentic at planning time.
- Future candles are read only after the snapshot is frozen and only for outcome measurement.
- If stop and target are both touched in one candle, the outcome is recorded as ambiguous rather than guessed.

## Data limitations

- Instrument-specific tick-size metadata unavailable; no tick component was added to hybrid stop candidates.

## Decision status

No production Entry, Protective Stop, or numerical constants were selected automatically. Review the row-level JSON and sensitivity table before approving a policy.

## Executive findings

- The sample contains 693 prefix-reconstructed canonical zones across 12 NSE symbols and all five requested timeframes. Demand/Supply and all four patterns are represented.
- A valid same-timeframe Authentic opposing target existed at planning time for 216 zones (31.17%). The remaining 477 zones (68.83%) correctly had no structural target; the replay did not manufacture one.
- Using the 10% zone-width stop family only as a common comparison, Proximal entry was reached for 516/693 zones (74.46%), Midpoint for 472/693 (68.11%), and Distal for 432/693 (62.34%).
- Forty-seven zones reacted from Proximal without reaching Midpoint. A further 41 reached Midpoint without reaching Distal. This is direct evidence that deeper entries create material missed-opportunity risk.
- Median wait after planning was 4 candles for Proximal, 6 for Midpoint, and 8 for Distal.
- Distal produced misleadingly attractive mathematical R:R because its risk denominator can become extremely small. In 216 cases its displayed structural R:R exceeded 10; observed examples above 300 mostly stopped before reaching the opposing zone.
- The 5%, 10%, 15%, and 20% stop families produced only small changes in target-before-stop outcomes in this sample. That is not enough evidence to freeze one buffer.
- Two Proximal/5%-zone-width cases traded slightly beyond Distal and later reached the target. This confirms that structural invalidation and a calibrated protective stop are different concepts, but two cases are not enough to set a constant.

## Entry comparison

| Candidate | Reached | Fill rate | Median candles to entry | Key finding |
|---|---:|---:|---:|---|
| Proximal | 516 / 693 | 74.46% | 4 | Highest realism and fewest missed reactions. |
| Midpoint | 472 / 693 | 68.11% | 6 | Missed 47 Proximal-only reactions. |
| Distal | 432 / 693 | 62.34% | 8 | Missed another 41 reactions and generated unstable high R:R values. |

The evidence makes Proximal the leading candidate for a later validation stage. It does **not** yet justify production activation because the study covers 12 symbols and has limited structural-target availability.

## Protective-stop comparison

For Proximal entries, target-first counts ranged only from 33 to 36 across the studied 5%-20% zone-width candidates. ATR and hybrid candidates produced similarly small differences, and 99 zones lacked a valid prefix ATR(14), so they were excluded from ATR-policy denominators rather than assigned fabricated ATR values.

No protective-stop constant is recommended for production from this sample. A larger symbol sample and a defined maximum replay horizon are still needed. Structural invalidation remains the canonical Distal boundary; it has not been redefined as an executable stop.

## Target study

- Target availability at planning time: 216 / 693 (31.17%).
- Target selection always used the nearest eligible opposing zone; no closer obstacle was skipped for a better R:R.
- Target eligibility required same symbol, timeframe, and prefix snapshot; opposite type; canonical boundaries; active lifecycle; Authentic status; and directional position ahead of the selected zone.
- Higher-timeframe zones were not substituted as targets.
- The high no-target rate is a real limitation of the approved same-timeframe policy in this sample, not an error to fill with a fixed-R target.

## Failure and misleading-R:R examples

The row-level audit recorded, among others:

- HDFCBANK 15m Demand RBR, Distal entry: mathematical R:R about 922.44; stop occurred before target.
- TCS 75m Supply RBD, Distal entry: mathematical R:R about 469.08; stop occurred before target.
- ICICIBANK 15m Demand DBR, Distal entry: mathematical R:R about 441.38; stop occurred before target.
- SUNPHARMA 15m Demand DBR, Distal entry: mathematical R:R 380; stop occurred before target.

These are why the replay must not choose Entry by maximizing R:R.

## Method and limitations

- Historical discovery is deterministically capped at eight zones per valid symbol/timeframe segment, distributed across the segment. This avoids cherry-picking while bounding audit runtime.
- Zero-range candles divide history into independent valid segments. No formation crosses a data break.
- Intraday provider history is materially shorter than Daily/Weekly history.
- Weekly candles use period-end labels (`W-FRI`). The current partial week can
  therefore display a label later than the download date; its OHLCV still
  contains only observations available when downloaded.
- YahooProvider does not expose reliable instrument-specific tick metadata through the current provider contract.
- Candle data cannot identify whether stop or target happened first when both prices occur inside one OHLC candle. Those cases are marked `AMBIGUOUS_SAME_CANDLE`.
- This is not an NSE-500-wide outcome study and is not sufficient to optimize per-timeframe constants.

## Recommended next decision

1. Keep Trade Planning unactivated.
2. Carry Proximal forward as the leading Entry candidate for a broader frozen replay; do not freeze it yet.
3. Do not approve a Protective Stop buffer yet. The 5%-20% sensitivity results are too close and tick metadata is unavailable.
4. Preserve `PARTIAL / NO_VALID_OPPOSING_ZONE` when no eligible target exists.
5. Obtain or maintain reliable tick-size metadata before evaluating the complete hybrid formula.

Decisions still requiring approval: production Entry policy, protective-stop family and constant, acceptable evidence/sample threshold, replay horizon, and treatment of same-candle ambiguity.
