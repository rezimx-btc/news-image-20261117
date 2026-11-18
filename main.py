#!/usr/bin/env python3
"""THE WORLD -- front page summing up Tuesday 17 November 2026.

Stdlib only. Pure-Python PNG encoder (zlib + struct) and a hand-typed
5x7 bitmap font. Deterministic: two runs write byte-identical PNGs.
Run: python3 -P -s main.py ; writes $MAKEFUN_OUTPUT_DIR/entry.png
(or /output/entry.png when the variable is unset).
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# Each glyph: 7 rows of 5 cells, '#' = ink, '.' = blank.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}

# ---------------------------------------------------------------- canvas
PAPER = (245, 241, 232)
INK = (20, 20, 20)
RED = (178, 34, 34)
NAVY = (24, 48, 88)
SKY = (135, 180, 210)
SEA = (168, 205, 225)
LAND = (196, 178, 130)
LAND2 = (172, 190, 140)
GREY = (110, 110, 108)
LIGHT = (232, 226, 212)
GOLD = (196, 148, 44)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.set(cx + dx, cy + dy, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx - x

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def centred(self, y, s, scale, c, cx=512):
        w = self.text_w(s, scale)
        self.text(cx - w // 2, y, s, scale, c)

    def wrap(self, x, y, s, scale, c, max_w, lh=None):
        """Greedy word wrap; returns y just below the last line."""
        if lh is None:
            lh = 7 * scale + 4
        words = s.upper().split(' ')
        line = ''
        cy = y
        for wd in words:
            trial = wd if not line else line + ' ' + wd
            if self.text_w(trial, scale) <= max_w or not line:
                line = trial
            else:
                self.text(x, cy, line, scale, c)
                cy += lh
                line = wd
        if line:
            self.text(x, cy, line, scale, c)
            cy += lh
        return cy


# ---------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack('>I', len(data)) + kind + data
    out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', ihdr)
    png += _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += _chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def story_box(cv, x, y, w, h, tag, head, body):
    cv.rect(x, y, w, h, (255, 255, 255))
    cv.rect(x, y, w, 3, INK)
    cv.rect(x, y + h - 3, w, 3, INK)
    cv.rect(x, y, 3, h, INK)
    cv.rect(x + w - 3, y, 3, h, INK)
    cv.rect(x + 3, y + 3, w - 6, 24, RED)
    cv.text(x + 10, y + 8, tag, 2, (255, 255, 255))
    cy = cv.wrap(x + 10, y + 34, head, 2, INK, w - 20, lh=17)
    cv.wrap(x + 10, cy + 2, body, 2, (60, 60, 60), w - 20, lh=15)


def draw_scene(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 48, y + 34, 22, GOLD)
    cv.rect(x, y + h - 78, w, 78, (120, 120, 118))
    # skyline
    cv.rect(x + 12, y + 52, 44, 96, NAVY)
    cv.rect(x + 64, y + 30, 52, 118, (70, 90, 120))
    cv.rect(x + 124, y + 66, 40, 82, NAVY)
    cv.rect(x + 172, y + 44, 58, 104, (70, 90, 120))
    cv.rect(x + 238, y + 70, 46, 78, NAVY)
    for bx in (24, 80, 136, 188, 250):
        for by in (66, 88, 110):
            cv.rect(x + bx, y + by, 10, 8, GOLD)
    # plane: fuselage, wings, tail
    cv.rect(x + 30, y + 96, 200, 12, (255, 255, 255))
    cv.rect(x + 210, y + 92, 46, 10, (255, 255, 255))
    cv.rect(x + 90, y + 108, 60, 8, (230, 230, 230))
    cv.rect(x + 170, y + 108, 34, 8, (230, 230, 230))
    cv.rect(x + 40, y + 84, 10, 14, (255, 255, 255))
    cv.rect(x + 236, y + 100, 6, 6, RED)
    # runway
    cv.rect(x, y + h - 22, w, 22, (60, 60, 60))
    for dx in range(8, w - 10, 36):
        cv.rect(x + dx, y + h - 12, 20, 4, (255, 255, 255))
    cv.text(x + 10, y + h - 44, 'MANILA', 2, (255, 255, 255))


def draw_map(cv, x, y, w, h):
    cv.rect(x, y, w, h, SEA)
    cv.rect(x, y, w, 3, INK)
    cv.rect(x, y + h - 3, w, 3, INK)
    cv.rect(x, y, 3, h, INK)
    cv.rect(x + w - 3, y, 3, h, INK)
    # simplified continents
    cv.rect(x + 48, y + 12, 180, 36, LAND)    # N America
    cv.rect(x + 150, y + 54, 62, 36, LAND)    # S America
    cv.rect(x + 420, y + 8, 72, 24, LAND2)    # Europe
    cv.rect(x + 428, y + 36, 66, 44, LAND)    # Africa
    cv.rect(x + 510, y + 8, 260, 44, LAND2)   # Asia
    cv.rect(x + 736, y + 72, 78, 18, LAND)    # Australia
    dots = [
        (170, 32, 'NEW YORK'),
        (450, 18, 'LONDON'),
        (476, 24, 'PARIS'),
        (490, 20, 'KYIV'),
        (570, 44, 'BAHRAIN'),
        (736, 36, 'MANILA'),
        (786, 22, 'TOKYO'),
        (178, 74, 'S AMERICA'),
    ]
    for dx, dy, _lab in dots:
        cv.circle(x + dx, y + dy, 7, RED)
        cv.circle(x + dx, y + dy, 3, (255, 255, 255))
    cv.text(x + 12, y + h - 22, 'RED DOTS MARK THE STORIES', 2, NAVY)


def main():
    cv = Canvas(W, H, PAPER)
    # frame
    cv.rect(0, 0, W, 10, INK)
    cv.rect(0, H - 10, W, 10, INK)
    cv.rect(0, 0, 10, H, INK)
    cv.rect(W - 10, 0, 10, H, INK)
    # masthead
    cv.centred(26, 'THE WORLD', 10, INK)
    cv.hline(32, 104, 960, INK, 4)
    # dateline bar
    cv.rect(32, 114, 960, 34, NAVY)
    cv.text(44, 123, 'TUESDAY, 17 NOVEMBER 2026', 3, (255, 255, 255))
    cv.text(652, 123, 'ONE DAY - ONE PAGE', 3, (255, 255, 255))
    # ---- lead story
    cv.text(32, 162, 'ASIA - SUMMIT IN MANILA', 2, RED)
    cv.wrap(32, 188, 'TRUMP LANDS IN MANILA FOR QUAD SUMMIT', 4, INK, 610,
            lh=34)
    cv.wrap(32, 268, 'PRESIDENT TRUMP ARRIVES IN MANILA TO MEET QUAD '
            'LEADERS FROM THE US, JAPAN, INDIA AND AUSTRALIA. NEXT: '
            'TALKS WITH MARCOS, THEN SHENZHEN FOR A FIRST-EVER '
            'TRILATERAL WITH XI JINPING AND VLADIMIR PUTIN ON '
            'NUCLEAR ARMS.', 2, (60, 60, 60), 610, lh=18)
    draw_scene(cv, 672, 162, 320, 190)
    cv.hline(32, 364, 960, INK, 3)
    # ---- world map strip
    draw_map(cv, 32, 376, 960, 112)
    cv.hline(32, 496, 960, INK, 3)
    # ---- story grid: 3 columns x 3 rows
    boxes = [
        ('EUROPE', 'CRIMEA BRIDGE HIT',
         'A UKRAINE STRIKE DAMAGES THE KERCH BRIDGE. RUSSIA HITS KYIV '
         'BRIDGES, CUTTING HEAT, WATER AND POWER.'),
        ('MIDEAST', 'IRAN DRONES AT US BASE',
         'IRAN FIRES DRONES AT A US RADAR BASE IN BAHRAIN. '
         'INTERCEPTED, NO CASUALTIES. US WARNS OF A DIRTY-BOMB '
         'THREAT.'),
        ('MIDEAST', 'THIRD US CARRIER ARRIVES',
         'THE USS THEODORE ROOSEVELT ARRIVES IN THE MIDDLE EAST. A '
         'TANKER IS HIT NEAR THE STRAIT OF HORMUZ.'),
        ('BRITAIN', 'UK SANCTIONS SETTLERS',
         'THE UK SANCTIONS EIGHT ISRAELI SETTLEMENT FIRMS. SETTLERS '
         'KILL A 72-YEAR-OLD WOMAN IN JERICHO, WEST BANK.'),
        ('ASIA', 'XI AND CARNEY CUT TARIFFS',
         'XI JINPING AND CANADA PM MARK CARNEY AGREE TARIFF CUTS AND '
         'DEEPER TIES AHEAD OF APEC.'),
        ('ASIA', 'JAPAN SCRAMBLES JETS',
         'JAPAN SCRAMBLES FIGHTER JETS AFTER SUSPECTED RUSSIAN '
         'AIRCRAFT VIOLATE ITS AIRSPACE.'),
        ('USA', 'PENTAGON FAILS AUDIT',
         'THE PENTAGON FAILS ITS FINANCIAL AUDIT FOR A NINTH STRAIGHT '
         'YEAR. $4.8 TRILLION IN ASSETS UNVERIFIED.'),
        ('MARKETS', 'NVIDIA SLIDES, OIL UP',
         'NVIDIA UNDER PRESSURE AFTER JENSEN HUANG EXITS. MARKETS '
         'SLIDE. BRENT $92.76 AS OIL RISES.'),
        ('BRIEFS', 'IN BRIEF - 17 NOVEMBER',
         'PARIS G7: $250M FOR CHERNOBYL. DEPARDIEU GUILTY. 13 BABIES '
         'BORN WITH MEASLES. MAMDANI AXES POLICE UNIT. EU CHARGES '
         'TEMU.'),
    ]
    xs = (32, 352, 672)
    ys = (508, 664, 820)
    for i, (tag, head, body) in enumerate(boxes):
        story_box(cv, xs[i % 3], ys[i // 3], 304, 150, tag, head, body)
    # footer
    cv.hline(32, 980, 960, INK, 2)
    cv.centred(988, 'THE WORLD - TUESDAY 17 NOVEMBER 2026', 2, INK)
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(out_dir, exist_ok=True)
    write_png(cv, os.path.join(out_dir, 'entry.png'))


if __name__ == '__main__':
    main()
