# THE WORLD — Tuesday, 17 November 2026

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/rezimx-btc/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/rezimx-btc/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

[View the bounty on make.fun](https://make.fun/bounty/news-image-20261117)

A one-page front-page newspaper summing up the world's news of
Tuesday, 17 November 2026: the war at sea in the Strait of Hormuz,
Ukraine's strike on the Kerch Bridge, the Xi–Trump–Putin summit in
Shenzhen, COP31 in Antalya, and more — with a world map marking
where each story happened.

`main.py` (Python 3.13, standard library only) draws the whole page
and writes it to `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR`).

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Running it twice produces byte-identical output (no time, no
randomness, no network). The PNG is 1024x1024 and under 1 MiB.
