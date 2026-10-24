# i915 rebind register trace summary

Source: 20261024-005758-i915-trace/trace.txt (i915:i915_reg_rw).

## pre: 5205 accesses, 7 distinct registers, 0.0 ms

| block | reads | writes |
|---|---|---|
| pipe/plane | 5024 | 13 |
| de irq | 52 | 103 |
| other | 0 | 13 |

## unbind: 802 accesses, 219 distinct registers, 919.2 ms

| block | reads | writes |
|---|---|---|
| ddi/aux A | 166 | 130 |
| pipe/plane | 54 | 91 |
| de irq | 35 | 78 |
| other | 16 | 52 |
| de power | 31 | 11 |
| panel power | 38 | 3 |
| transcoder | 8 | 17 |
| cdclk/dbuf | 10 | 9 |
| ddi/aux | 1 | 15 |
| sgunit/pcode | 10 | 2 |
| pch/hpd | 2 | 6 |
| guc | 6 | 0 |
| c10/c20 phy | 2 | 4 |
| de straps | 2 | 0 |
| bcs ring | 0 | 1 |
| media gt | 0 | 1 |
| rcs ring | 0 | 1 |

## bind: 66500 accesses, 13244 distinct registers, 12829.4 ms

| block | reads | writes |
|---|---|---|
| pipe/plane | 46711 | 328 |
| dmc program upload | 5 | 11516 |
| de irq | 935 | 1734 |
| ddi/aux A | 1214 | 947 |
| other | 153 | 1859 |
| panel power | 324 | 10 |
| transcoder | 108 | 63 |
| de power | 130 | 31 |
| guc | 48 | 46 |
| c10/c20 phy | 42 | 11 |
| cdclk/dbuf | 29 | 20 |
| sgunit/pcode | 40 | 8 |
| pch/hpd | 28 | 14 |
| dmc | 10 | 21 |
| gt pm/rc6 | 21 | 8 |
| ddi/aux | 5 | 23 |
| rcs ring | 2 | 20 |
| gt misc | 16 | 0 |
| gt pm/fw | 0 | 10 |
| de straps | 6 | 0 |
| bcs ring | 0 | 2 |
| media gt | 0 | 1 |
| phy/pll | 1 | 0 |

## modeset: 17158 accesses, 79 distinct registers, 5591.6 ms

| block | reads | writes |
|---|---|---|
| pipe/plane | 15687 | 136 |
| de irq | 365 | 683 |
| other | 7 | 86 |
| ddi/aux A | 20 | 28 |
| ddi/aux | 0 | 36 |
| panel power | 26 | 2 |
| transcoder | 18 | 8 |
| de power | 18 | 2 |
| cdclk/dbuf | 9 | 6 |
| pch/hpd | 6 | 0 |
| c10/c20 phy | 6 | 0 |
| dmc | 5 | 0 |
| sgunit/pcode | 2 | 0 |
| dmc program upload | 1 | 0 |
| de straps | 1 | 0 |

