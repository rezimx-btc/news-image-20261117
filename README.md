# THE WORLD — Tuesday, 17 November 2026

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
