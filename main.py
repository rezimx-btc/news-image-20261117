#!/usr/bin/env python3
"""THE WORLD -- Tuesday, 17 November 2026. One day's world news in one page.

Stdlib-only Python 3.13. Draws a dense front-page newspaper (1024x1024 PNG)
to MAKEFUN_OUTPUT_DIR (or /output) as entry.png. No network, no time,
no randomness: running it twice produces byte-identical output.
"""
import binascii
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (245, 239, 224)
INK = (20, 20, 20)
RED = (163, 22, 33)
OCEAN = (216, 232, 236)
LAND = (198, 188, 158)
LAND_LINE = (90, 84, 66)
WHITE = (245, 239, 224)

# 5x7 bitmap font, uppercase only. Each glyph is 7 rows of 5 bits,
# bit 4 is the leftmost pixel. All text is uppercased before drawing.
FONT = {
    'A': (14, 17, 17, 31, 17, 17, 17),
    'B': (30, 17, 17, 30, 17, 17, 30),
    'C': (14, 17, 16, 16, 16, 17, 14),
    'D': (30, 17, 17, 17, 17, 17, 30),
    'E': (31, 16, 16, 30, 16, 16, 31),
    'F': (31, 16, 16, 30, 16, 16, 16),
    'G': (14, 17, 16, 23, 17, 17, 15),
    'H': (17, 17, 17, 31, 17, 17, 17),
    'I': (14, 4, 4, 4, 4, 4, 14),
    'J': (7, 2, 2, 2, 2, 18, 12),
    'K': (17, 18, 20, 24, 20, 18, 17),
    'L': (16, 16, 16, 16, 16, 16, 31),
    'M': (17, 27, 21, 21, 17, 17, 17),
    'N': (17, 25, 21, 19, 17, 17, 17),
    'O': (14, 17, 17, 17, 17, 17, 14),
    'P': (30, 17, 17, 30, 16, 16, 16),
    'Q': (14, 17, 17, 17, 21, 18, 13),
    'R': (30, 17, 17, 30, 20, 18, 17),
    'S': (15, 16, 16, 14, 1, 1, 30),
    'T': (31, 4, 4, 4, 4, 4, 4),
    'U': (17, 17, 17, 17, 17, 17, 14),
    'V': (17, 17, 17, 17, 17, 10, 4),
    'W': (17, 17, 17, 21, 21, 27, 17),
    'X': (17, 17, 10, 4, 10, 17, 17),
    'Y': (17, 17, 10, 4, 4, 4, 4),
    'Z': (31, 1, 2, 4, 8, 16, 31),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def rect(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

FONT.update({
    '0': (14, 17, 19, 21, 25, 17, 14),
    '1': (4, 12, 4, 4, 4, 4, 14),
    '2': (14, 17, 1, 2, 4, 8, 31),
    '3': (31, 2, 4, 2, 1, 17, 14),
    '4': (2, 6, 10, 18, 31, 2, 2),
    '5': (31, 16, 30, 1, 1, 17, 14),
    '6': (14, 16, 30, 17, 17, 17, 14),
    '7': (31, 1, 2, 4, 8, 8, 8),
    '8': (14, 17, 17, 14, 17, 17, 14),
    '9': (14, 17, 17, 15, 1, 2, 12),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 12, 12),
    ',': (0, 0, 0, 0, 12, 4, 8),
    ':': (0, 12, 12, 0, 12, 12, 0),
    ';': (0, 12, 12, 0, 12, 4, 8),
    '-': (0, 0, 0, 14, 0, 0, 0),
    '\u2014': (0, 0, 0, 31, 0, 0, 0),
    "'": (4, 4, 8, 0, 0, 0, 0),
    '\u2019': (4, 4, 8, 0, 0, 0, 0),
    '"': (10, 10, 10, 0, 0, 0, 0),
    '(': (2, 4, 8, 8, 8, 4, 2),
    ')': (8, 4, 2, 2, 2, 4, 8),
    '/': (1, 2, 2, 4, 8, 8, 16),
    '%': (25, 26, 2, 4, 8, 11, 19),
    '$': (4, 15, 20, 14, 5, 30, 4),
    '&': (12, 18, 20, 8, 21, 18, 13),
    '!': (4, 4, 4, 4, 4, 0, 4),
    '?': (14, 17, 1, 2, 4, 0, 4),
    '+': (0, 4, 4, 14, 4, 4, 0),
    '#': (10, 10, 31, 10, 31, 10, 10),
    '=': (0, 0, 31, 0, 31, 0, 0),
    '\u2022': (0, 0, 12, 12, 12, 0, 0),
})


def text_width(s, scale):
    return len(s) * 6 * scale


def draw_text(cv, s, x, y, scale=1, color=INK):
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            bits = g[r]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.fill(cx + col * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(cv, s, cx, y, scale=1, color=INK):
    draw_text(cv, s, cx - text_width(s, scale) // 2, y, scale, color)


def wrap(text, max_chars):
    words = text.split()
    lines = []
    cur = ''
    for wd in words:
        if cur and len(cur) + 1 + len(wd) > max_chars:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + ' ' + wd) if cur else wd
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, lines, x, y, scale=1, color=INK, leading=None):
    lh = leading if leading is not None else 9 * scale + 1
    for ln in lines:
        draw_text(cv, ln, x, y, scale, color)
        y += lh
    return y


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        c += struct.pack('>I', binascii.crc32(typ + data) & 0xffffffff)
        return c

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(data)


# ---- world map: simplified continent outlines in (lon, lat) ----
MAP_X, MAP_Y, MAP_W, MAP_H = 648, 186, 340, 216
NORTH_AMERICA = [(-168, 66), (-140, 70), (-110, 72), (-95, 80), (-80, 73),
                 (-65, 60), (-55, 52), (-65, 45), (-75, 35), (-81, 26),
                 (-90, 21), (-97, 16), (-86, 12), (-79, 9), (-92, 15),
                 (-105, 20), (-114, 29), (-124, 40), (-130, 55),
                 (-155, 58), (-168, 66)]
GREENLAND = [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-22, 70),
             (-25, 76), (-40, 80), (-58, 76), (-58, 64)]
SOUTH_AMERICA = [(-79, 9), (-72, 11), (-62, 10), (-52, 5), (-50, 0),
                 (-44, -3), (-35, -8), (-40, -20), (-48, -28), (-58, -38),
                 (-65, -45), (-68, -52), (-71, -54), (-73, -37),
                 (-70, -20), (-77, -12), (-81, -6), (-80, 1), (-79, 9)]
AFRICA = [(-17, 15), (-10, 5), (-8, -2), (9, -1), (12, 5), (9, 14),
          (11, 19), (20, 22), (30, 31), (32, 31), (35, 28), (40, 15),
          (43, 11), (51, 10), (48, 0), (40, -10), (35, -18), (32, -26),
          (26, -34), (19, -35), (15, -27), (12, -18), (13, -12),
          (9, -1), (-8, -2), (-17, 15)]
EUROPE = [(-10, 37), (-9, 43), (-2, 44), (-1, 46), (0, 50), (3, 53),
          (8, 55), (10, 57), (18, 56), (21, 55), (24, 58), (28, 60),
          (30, 62), (25, 65), (20, 68), (15, 70), (10, 68), (5, 62),
          (5, 58), (-2, 57), (-5, 50), (-9, 48), (-10, 43), (-10, 37)]
ASIA = [(30, 62), (40, 68), (60, 70), (70, 72), (90, 75), (110, 77),
        (130, 72), (150, 70), (160, 66), (170, 66), (162, 60), (156, 52),
        (142, 50), (140, 40), (135, 35), (127, 33), (120, 30), (110, 20),
        (108, 12), (105, 9), (100, 7), (98, 12), (92, 16), (88, 22),
        (80, 13), (77, 8), (73, 20), (66, 25), (60, 25), (55, 26),
        (50, 29), (48, 30), (44, 29), (40, 31), (36, 36), (30, 36),
        (28, 41), (30, 46), (30, 62)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
             (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
             (153, -32), (150, -22), (146, -19), (142, -15), (142, -11),
             (137, -12), (135, -15), (132, -12), (130, -13), (126, -14),
             (122, -17), (118, -20), (113, -22)]
BORNEO = [(109, 1), (113, 4), (117, 2), (119, -2), (116, -4), (110, -3),
          (109, 1)]
SUMATRA = [(95, 5), (100, 0), (104, -3), (106, -6), (102, -5), (97, 2),
           (95, 5)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -4), (146, -6), (150, -9),
              (146, -8), (141, -8), (136, -4), (131, -1)]
JAPAN = [(130, 31), (132, 33), (134, 34), (137, 35), (140, 36), (141, 39),
         (142, 42), (144, 44), (141, 45), (139, 41), (137, 37), (134, 34),
         (130, 31)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EUROPE,
              ASIA, AUSTRALIA, BORNEO, SUMATRA, NEW_GUINEA, JAPAN]
# numbered story markers: (lon, lat, number)
MARKERS = [(56, 26, '1'), (33, 45, '2'), (114, 22, '3'), (121, 15, '4'),
           (31, 37, '5'), (107, 48, '6'), (-77, 39, '7'), (34, 31, '8')]


def project(lon, lat):
    x = MAP_X + int((lon + 180.0) / 360.0 * MAP_W)
    y = MAP_Y + int((75.0 - lat) / 130.0 * MAP_H)
    return (x, y)


def fill_poly(cv, pts, color):
    if len(pts) < 3:
        return
    ys = [p[1] for p in pts]
    y0 = max(0, min(ys))
    y1 = min(cv.h - 1, max(ys))
    n = len(pts)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, y1p = pts[i]
            x2, y2p = pts[(i + 1) % n]
            if (y1p <= y < y2p) or (y2p <= y < y1p):
                xs.append(x1 + (y - y1p) * (x2 - x1) / (y2p - y1p))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa = int(xs[i] + 0.5)
            xb = int(xs[i + 1] + 0.5)
            if xb > xa:
                cv.fill(xa, y, xb - xa, 1, color)


def draw_map(cv):
    cv.fill(MAP_X, MAP_Y, MAP_W, MAP_H, OCEAN)
    for lon in range(-180, 181, 30):
        x, _ = project(lon, 0)
        for yy in range(MAP_Y, MAP_Y + MAP_H, 4):
            cv.set(x, yy, (190, 205, 210))
    for lat in (-30, 0, 30, 60):
        _, y = project(0, lat)
        for xx in range(MAP_X, MAP_X + MAP_W, 4):
            cv.set(xx, y, (190, 205, 210))
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        fill_poly(cv, pts, LAND)
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            cv.line(x1, y1, x2, y2, LAND_LINE)
    for lon, lat, num in MARKERS:
        x, y = project(lon, lat)
        cv.fill(x - 4, y - 4, 9, 9, RED)
        cv.rect(x - 4, y - 4, 9, 9, WHITE)
        draw_text(cv, num, x + 7, y - 4, 1, INK)
    cv.rect(MAP_X, MAP_Y, MAP_W, MAP_H, INK, 2)


def kicker(cv, x, y, s):
    draw_text(cv, s, x, y, 1, RED)
    return y + 11


def headline(cv, lines, x, y, scale=2):
    for ln in lines:
        draw_text(cv, ln, x, y, scale, INK)
        y += 7 * scale + 2
    return y + 2


def body(cv, text, x, y, w, scale=1):
    max_chars = max(1, w // (6 * scale))
    lines = wrap(text, max_chars)
    return draw_block(cv, lines, x, y, scale, INK, leading=9 * scale + 1)


def story(cv, x, y, w, kick, head_lines, body_text, hscale=2):
    y = kicker(cv, x, y, kick)
    y = headline(cv, head_lines, x, y, hscale)
    return body(cv, body_text, x, y + 2, w)


def main():
    cv = Canvas(W, H, PAPER)
    # top bar
    cv.fill(0, 0, W, 26, INK)
    draw_text(cv, 'EST. 2026', 28, 9, 1, WHITE)
    draw_centered(cv, "THE WORLD'S NEWS \u2014 IN ONE PAGE", 512, 9, 1, WHITE)
    draw_text(cv, 'TUESDAY', 1024 - 28 - text_width('TUESDAY', 1), 9, 1, WHITE)
    # masthead
    draw_centered(cv, 'THE WORLD', 512, 36, 9, INK)
    cv.fill(28, 106, 968, 2, INK)
    draw_centered(cv, 'TUESDAY, 17 NOVEMBER 2026', 512, 116, 2, INK)
    draw_text(cv, 'VOL. I \u2014 NO. 321', 28, 120, 1, INK)
    draw_text(cv, 'PRICE: ONE READ', 1024 - 28 - text_width('PRICE: ONE READ', 1),
              120, 1, INK)
    cv.fill(28, 140, 968, 2, INK)
    # lead story: Hormuz
    y = kicker(cv, 28, 152, 'MIDDLE EAST \u2014 WAR AT SEA')
    y = headline(cv, ['FOURTH TANKER HIT IN HORMUZ',
                      'AS U.S.-IRAN WAR ESCALATES'], 28, y, 3)
    y = body(cv, 'A FOURTH OIL TANKER CAUGHT FIRE IN THE STRAIT OF HORMUZ AFTER '
                 'STRIKING A NAVAL MINE IN 24 HOURS, IRAN SAID, AS ITS '
                 'REVOLUTIONARY GUARDS SEIZED A U.S. MQ-170 DRONE NEAR QESHM '
                 'ISLAND. THE U.S. STRUCK AN IRANIAN MISSILE SITE ON QESHM, '
                 'AND CONDEMNED IRANIAN DRONE ATTACKS ON ITS FACILITY IN '
                 'BAHRAIN \u2014 THE THIRD IN FIVE DAYS.', 28, y + 2, 600)
    cv.fill(28, y + 12, 4, 22, RED)
    draw_text(cv, 'BY THE NUMBERS: 4 TANKERS HIT IN 24 HOURS', 40, y + 12, 1, INK)
    draw_text(cv, '1 U.S. DRONE SEIZED \u2022 3 DRONE STRIKES ON BAHRAIN IN 5 DAYS',
              40, y + 23, 1, INK)
    y2 = kicker(cv, 28, y + 48, 'WASHINGTON')
    y2 = headline(cv, ["U.S. CONDEMNS IRAN'S", 'BAHRAIN STRIKES'], 28, y2, 2)
    body(cv, "WASHINGTON CONDEMNED IRAN'S ATTACKS AND REAFFIRMED ITS SECURITY "
             'COMMITMENT TO BAHRAIN AFTER THE THIRD DRONE STRIKE IN FIVE DAYS.',
         28, y2 + 2, 600)
    y3 = kicker(cv, 28, y2 + 32, 'THE STRAIT')
    y3 = headline(cv, ['STRAIT STAYS CLOSED TO SHIPPING'], 28, y3, 2)
    body(cv, 'IRAN KEPT THE STRAIT CLOSED TO SHIPPING AS THE U.S. NAVAL '
             'BLOCKADE TIGHTENED.', 28, y3 + 2, 600)
    # map panel
    draw_centered(cv, 'THE WORLD AT A GLANCE', 818, 164, 1, INK)
    draw_map(cv)
    draw_centered(cv, '1 HORMUZ  2 CRIMEA  3 SHENZHEN  4 MANILA', 818, 410, 1, INK)
    draw_centered(cv, '5 ANTALYA  6 ULAANBAATAR  7 WASHINGTON  8 JERICHO', 818, 422,
                  1, INK)
    cv.fill(28, 436, 968, 2, INK)
    # row 2: Ukraine | APEC summit
    story(cv, 28, 446, 472, 'EUROPE \u2014 WAR',
          ['UKRAINE HITS KERCH BRIDGE;',
           "ZELENSKY HAILS 'UNPRECEDENTED'", 'ATTACK'],
          'UKRAINE SAID ITS MISSILE AND DRONE ATTACK PARTLY COLLAPSED THE '
          'BRIDGE LINKING RUSSIA TO OCCUPIED CRIMEA. KYIV ALSO REPORTED DRONE '
          'STRIKES IN CRIMEA, AS A RUSSIAN STRIKE ON ZAPORIZHZHIA KILLED 40 '
          'AND AN ATTACK ON AN AID CENTRE KILLED 26.')
    story(cv, 524, 446, 472, 'ASIA \u2014 DIPLOMACY',
          ['XI, TRUMP AND PUTIN TO MEET', 'IN SHENZHEN ON THURSDAY'],
          'THE FIRST-EVER TRILATERAL SUMMIT OF THE LEADERS OF CHINA, RUSSIA '
          'AND THE UNITED STATES IS SET FOR THURSDAY AT THE APEC MEETING IN '
          'SHENZHEN. PUTIN ARRIVED EARLY; TRUMP LEFT MANILA, WHERE QUAD '
          'LEADERS REAFFIRMED THEIR INDO-PACIFIC PACT.')
    cv.fill(28, 568, 968, 2, INK)
    # row 3: COP31 | Mongolia | Markets
    story(cv, 28, 578, 314, 'CLIMATE \u2014 COP31, ANTALYA',
          ['COP31 DRAFT: FASTER', 'FOSSIL-FUEL EXIT, $120BN',
           'CLIMATE FINANCE'],
          'NEGOTIATORS IN ANTALYA PUBLISHED AN 18-PAGE DRAFT DEAL CALLING FOR '
          'A FASTER PHASE-OUT OF FOSSIL FUELS AND AT LEAST $120 BILLION A YEAR '
          'IN CLIMATE ADAPTATION FINANCE FOR DEVELOPING COUNTRIES BY 2035.')
    story(cv, 354, 578, 314, 'ASIA',
          ["MONGOLIA'S PRESIDENT", 'QUITS AMID CORRUPTION', 'SCANDAL'],
          'PRESIDENT UKHNAAGIIN KHURELSUKH ANNOUNCED HIS RESIGNATION ON '
          'TUESDAY AS A CORRUPTION SCANDAL ENGULFED HIS GOVERNMENT IN '
          'ULAANBAATAR.')
    story(cv, 680, 578, 314, 'MARKETS',
          ['BITCOIN STALLS BELOW', '$65,000; NVIDIA FACES', 'EARNINGS TEST'],
          'BITCOIN STALLED BELOW $65,000 AFTER A SELLOFF THAT HAS CUT MORE '
          'THAN 15% THIS MONTH. NVIDIA FACES ITS EARNINGS TEST AMID A CEO SPY '
          'SCANDAL, AS WASHINGTON TIGHTENS GLOBAL AI CHIP CONTROLS ON CHINA.')
    cv.fill(28, 708, 968, 2, INK)
    # row 4: U.S. | West Bank | Sport
    story(cv, 28, 718, 314, 'AMERICAS',
          ['PENTAGON FAILS AUDIT FOR', 'NINTH YEAR; U.S. LOSES',
           'MEASLES-FREE STATUS'],
          'THE DEFENSE DEPARTMENT FAILED ITS ANNUAL AUDIT FOR THE NINTH YEAR '
          'IN A ROW. THE U.S. LOST ITS MEASLES ELIMINATION STATUS AFTER 26 '
          'YEARS, WITH MORE THAN 5,400 CASES AND 10 DEATHS REPORTED.')
    story(cv, 354, 718, 314, 'MIDDLE EAST',
          ['SETTLERS SHOOT DEAD', 'PALESTINIAN WOMAN, 72,', 'NEAR JERICHO'],
          'ISRAELI SETTLERS SHOT DEAD A 72-YEAR-OLD PALESTINIAN WOMAN OUTSIDE '
          "HER HOME, THE HEALTH MINISTRY SAID. ISRAEL'S ATTORNEY GENERAL "
          'SUSPENDED THE TENDER FOR THE E1 SETTLEMENT NEAR JERUSALEM.')
    story(cv, 680, 718, 314, 'SPORT',
          ['INDIA EDGE PAKISTAN IN', 'U19 ASIA CUP THRILLER'],
          'INDIA BEAT PAKISTAN BY ONE WICKET IN A LAST-BALL THRILLER TO WIN '
          'THE UNDER-19 ASIA CUP FINAL IN OMAN, CHASING 338. GERMANY THRASHED '
          'THE NETHERLANDS 5-0.')
    cv.fill(28, 848, 968, 2, INK)
    # also today
    kicker(cv, 28, 858, 'ALSO TODAY')
    minis = ['RUSSIA: MILITARY PLANE CRASH KILLS ALL 19 ON BOARD IN KEMEROVO',
             'THAILAND: 11 DEAD IN FIRE ON PHUKET ISLAND',
             'SOUTH AFRICA: 17 KILLED IN TWO MASS SHOOTINGS',
             'PAKISTAN: PETROL AND DIESEL CUT BY RS2 A LITRE']
    for i, m in enumerate(minis):
        body(cv, m, 28 + i * 240, 874, 230)
    cv.fill(28, 906, 968, 2, INK)
    draw_centered(cv, 'THE WORLD \u2022 TUESDAY, 17 NOVEMBER 2026 \u2022 ONE DAY, '
                      'ONE PAGE', 512, 920, 1, INK)
    draw_centered(cv, 'COMPILED FROM REPORTS FILED AROUND THE WORLD ON '
                      '17 NOVEMBER 2026', 512, 934, 1, INK)
    cv.fill(28, 956, 968, 1, INK)
    cv.fill(0, 972, W, 52, INK)
    draw_centered(cv, 'THE WORLD', 512, 980, 2, WHITE)
    draw_centered(cv, 'ONE DAY \u2022 ONE PAGE', 512, 1000, 1, WHITE)
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    write_png(cv, os.path.join(out_dir, 'entry.png'))


if __name__ == '__main__':
    main()
