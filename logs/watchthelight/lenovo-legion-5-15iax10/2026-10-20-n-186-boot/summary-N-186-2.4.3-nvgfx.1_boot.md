# gpubench summary: 2.4.3-nvgfx.1 boot (N-186)

2.4.3-nvgfx.1 boot: plugin fb7983353d66, attempts N-186

| metric | unit | n | median | min | max | CV % |
|---|---|---|---|---|---|---|
| caanim.fps | flips/s | 3 | 177 | 177 | 177 | 0.0 |
| caanim.miss | count | 3 | 0 | 0 | 0 | 0.0 |
| caanim.refused | count | 3 | 0 | 0 | 0 | 0.0 |
| caanim.stale | count | 3 | 0 | 0 | 0 | 0.0 |
| drag.early | flips/s | 12 | 9 | 3 | 99 | 281.7 |
| drag.flips | flips/s | 3 | 148 | 145 | 148 | 1.0 |
| drag.presents | per_s | 3 | 148 | 146 | 148 | 0.6 |
| draw.commit | ms | 3 | 0.01 | 0.01 | 0.01 | 0.0 |
| draw.encode | us/draw | 3 | 1.6 | 1.5 | 1.6 | 2.9 |
| fakews.rate | frames/s | 3 | 8920 | 8652 | 9007 | 1.7 |
| ft.degraded | count | 3 | 6 | 4 | 8 | 27.2 |
| ft.fail | count | 3 | 0 | 0 | 0 | 0.0 |
| ft.pass | count | 3 | 57 | 38 | 76 | 27.2 |
| ft.skipped | count | 3 | 18 | 12 | 24 | 27.2 |
| gpu.gpc | MHz | 3 | 1417 | 1417 | 1417 | 0.0 |
| gpu.limit_enf | mW | 3 | 115000 | 115000 | 115000 | 0.0 |
| gpu.power | mW | 3 | 17361 | 17330 | 17521 | 0.5 |
| gpu.temp | C | 3 | 66.72 | 66.69 | 66.75 | 0.0 |
| log.flipto | per_min | 3 | 2 | 2 | 2 | 0.0 |
| log.nvrm | per_min | 3 | 653 | 641 | 666 | 1.6 |
| log.other | per_min | 3 | 651 | 639 | 664 | 1.6 |
| log.present | per_min | 3 | 0 | 0 | 0 | 0.0 |
| panes.cpu | s | 9 | 1.7 | 1.67 | 1.74 | 1.3 |
| pipe.ms_each | ms | 3 | 0.4 | 0.4 | 0.4 | 0.0 |
| pipe.speedup | x | 3 | 7.29 | 7.07 | 7.32 | 1.5 |
| present.failed | count | 3 | 1 | 1 | 1 | 0.0 |
| samp.draws | per_s | 3 | 397470 | 396106 | 405398 | 1.0 |
| sched.b_scheduled | ms | 3 | 0.085 | 0.08 | 0.09 | 4.8 |
| selftest.failed | count | 3 | 0 | 0 | 0 | 0.0 |
| selftest.ran | count | 3 | 16 | 16 | 16 | 0.0 |
| surfin.bad | cells | 3 | 0 | 0 | 0 | 0.0 |
| surfin.fps | frames/s | 3 | 539 | 500 | 553 | 4.2 |

Noisy (CV > 15 %): drag.early, ft.degraded, ft.pass, ft.skipped
