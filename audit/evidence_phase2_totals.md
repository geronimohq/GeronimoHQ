# Phase 2 bug #2 - player and server totals, same minute

Run: 2026-11-10 02:24:32 +0800 · direct A2S finished +3.6s · backend answered +6.7s · backend requests used: 1

Alias check: `rsscs2.kr` resolves to `14.5.33.30` (catalog RSS entry is `14.5.33.30:27015`); alias query online=True players=0/64 bots=0

## Per server

| id | host:port | direct online | direct players (incl. bots) | direct bots | direct humans | backend online | backend players | backend bots field |
|---|---|---|---|---|---|---|---|---|
| gfl | 74.91.124.21:27015 | yes | 62 | 0 | 62 | yes | 62 | absent |
| possession | 103.62.49.55:27015 | yes | 0 | 0 | 0 | yes | 0 | absent |
| mapeadores | 87.98.228.196:27040 | yes | 24 | 0 | 24 | yes | 24 | absent |
| cola | 178.33.160.187:27015 | yes | 30 | 0 | 30 | yes | 31 | absent |
| rss | 14.5.33.30:27015 | yes | 0 | 0 | 0 | yes | 0 | absent |
| net4all | 46.174.54.231:27015 | yes | 29 | 0 | 29 | yes | 29 | absent |
| exg_8 | 202.189.10.89:27002 | no | - | - | - | no | - | absent |
| exg_3 | 202.189.4.122:27001 | yes | 0 | 0 | 0 | yes | 0 | absent |
| exg_16 | 202.189.10.208:27002 | no | - | - | - | no | - | absent |
| exg_11 | 202.189.10.208:27001 | no | - | - | - | no | - | absent |
| exg_pve2 | 202.189.5.229:27002 | yes | 0 | 0 | 0 | yes | 0 | absent |
| exg_pve1 | 202.189.5.229:27001 | yes | 0 | 0 | 0 | yes | 0 | absent |
| exg_13 | 202.189.5.227:27001 | yes | 0 | 0 | 0 | yes | 0 | absent |
| exg_5 | 202.189.4.230:27001 | yes | 0 | 0 | 0 | yes | 0 | absent |
| exg_12 | 202.189.5.225:27001 | no | - | - | - | no | - | absent |
| exg_6 | 202.189.4.230:27002 | yes | 0 | 0 | 0 | yes | 0 | absent |
| exg_10 | 202.189.10.203:27001 | no | - | - | - | no | - | absent |
| exg_9 | 202.189.5.221:27001 | no | - | - | - | no | - | absent |
| exg_17 | 202.189.5.225:27002 | no | - | - | - | no | - | absent |
| exg_7 | 202.189.10.196:27001 | yes | 64 | 0 | 64 | yes | 64 | absent |
| exg_18 | 202.189.5.227:27002 | no | - | - | - | no | - | absent |
| exg_14 | 202.189.5.236:27001 | no | - | - | - | no | - | absent |
| fys_8 | 110.42.9.107:27085 | yes | 0 | 0 | 0 | yes | 0 | absent |
| fys_3 | 110.42.9.139:27035 | yes | 0 | 0 | 0 | yes | 0 | absent |
| fys_7 | 110.42.9.139:27075 | yes | 0 | 0 | 0 | yes | 0 | absent |
| fys_1 | 110.42.9.155:27015 | yes | 0 | 0 | 0 | yes | 0 | absent |
| fys_5 | 110.42.9.138:27055 | yes | 3 | 0 | 3 | yes | 3 | absent |
| fys_4 | 110.42.9.138:27045 | yes | 0 | 0 | 0 | yes | 0 | absent |
| ub_3 | 110.42.9.188:27031 | yes | 1 | 0 | 1 | yes | 1 | absent |
| ub_1 | 110.42.9.188:27011 | yes | 0 | 0 | 0 | yes | 0 | absent |
| ub_2 | 110.42.9.188:27021 | yes | 14 | 8 | 6 | yes | 14 | absent |
| ub_11 | 110.42.9.195:27111 | yes | 0 | 0 | 0 | yes | 0 | absent |
| ub_12 | 110.42.9.195:27121 | yes | 0 | 0 | 0 | yes | 0 | absent |
| ub_13 | 110.42.9.195:27131 | yes | 0 | 0 | 0 | yes | 0 | absent |
| zl_2 | 110.42.9.181:27015 | no | - | - | - | no | - | absent |
| zl_1 | 110.42.9.22:27016 | yes | 0 | 0 | 0 | yes | 0 | absent |
| zl_3 | 110.42.9.181:27016 | no | - | - | - | no | - | absent |
| zl_4 | 110.42.9.149:27015 | yes | 0 | 0 | 0 | yes | 0 | absent |
| zl_5 | 110.42.9.149:27016 | yes | 0 | 0 | 0 | yes | 0 | absent |
| 93x_1 | 43.142.148.163:27015 | no | - | - | - | no | - | absent |
| 93x_2 | 43.142.148.163:27016 | no | - | - | - | no | - | absent |

## Totals

| Source / rule | players shown | servers online |
|---|---|---|
| BEFORE app Dashboard + ZE Game Servers (hard-coded text) | 646 | 34 / 41 |
| BEFORE website (sum of `players` incl. bots, live backend) | 228 | 28 / 41 |
| AFTER shared rule on live backend data | 228 (bots unknown on 28 servers: live backend is the pre-audit code) | 28 / 41 |
| AFTER shared rule on direct A2S (humans; bots = 8) | 219 | 28 / 41 |
| direct A2S, players incl. bots (for comparison) | 227 | - |
| shared rule, catalog + rsscs2.kr alias added (double-count check) | 219 (duplicates dropped: 1) | 28 / 41 |
