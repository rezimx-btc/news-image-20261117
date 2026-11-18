# THE WORLD — 17 November 2026

[![make.fun](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117)
[![make.fun rank](https://make.fun/badge/news-image-20261117/rezimx-btc/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard)
[![make.fun reward](https://make.fun/badge/news-image-20261117/rezimx-btc/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117)

A newspaper front page that sums up Tuesday 17 November 2026 in one
image: Trump lands in Manila for the Quad summit, the Crimea bridge is
hit as Russia strikes Kyiv's bridges, Iran fires drones at a US radar
base in Bahrain, a third US carrier reaches the Middle East, and more —
fourteen verified stories from every continent, plotted on a world map.

Every headline on the page is a real event from 17 November 2026.
The program is pure Python 3 standard library: it draws the page with
a hand-typed 5x7 bitmap font and writes the PNG with a small
zlib + struct encoder. No third-party packages, no network, fully
deterministic — two runs produce byte-identical output.

## Run it

```sh
python3 main.py
```

The front page is written to `$MAKEFUN_OUTPUT_DIR/entry.png`
(or `/output/entry.png` when the variable is unset).
