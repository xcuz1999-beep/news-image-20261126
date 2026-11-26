#!/usr/bin/env python3
"""THE THURSDAY GLOBE - one front page for Thursday 26 November 2026.

Pure standard library. The program reads nothing and writes a single
1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png (falling back to
/output/entry.png). Every run produces the same bytes: fixed layout,
fixed text, no clocks, no randomness, no network.

The stories are the day's real reporting of 26 November 2026, kept short
and factual: North Korea's call for wider deployment of tactical nuclear
weapons leads, with Ukraine's strike on a Russian air base, the new US
tariff proposals, Nvidia's slide, BepiColombo's arrival at Mercury, the
World Chess Championship and a full Champions League night inside.
Thirty-five news items plus a dotted world map, a markets strip and an
in-brief ticker fill the page, broadsheet style.
"""

import os
import struct
import zlib

# ------------------------------------------------------------ palette ----
SIZE = 1024
PAPER = (248, 244, 233)
INK = (18, 16, 14)
ACCENT = (158, 24, 30)
FAINT = (110, 104, 94)
RULE = (196, 189, 170)
SEA = (58, 98, 128)
LIGHT = (232, 226, 210)
GOLD = (176, 132, 40)

canvas = bytearray(bytes(PAPER) * (SIZE * SIZE))


def plot(x, y, rgb):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        i = (y * SIZE + x) * 3
        canvas[i] = rgb[0]
        canvas[i + 1] = rgb[1]
        canvas[i + 2] = rgb[2]


def rect(x, y, w, h, rgb):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(SIZE, x + w), min(SIZE, y + h)
    for yy in range(y0, y1):
        base = (yy * SIZE + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            canvas[i] = rgb[0]
            canvas[i + 1] = rgb[1]
            canvas[i + 2] = rgb[2]


def hline(x, y, w, rgb=INK, t=1):
    rect(x, y, w, t, rgb)


def vline(x, y, h, rgb=INK, t=1):
    rect(x, y, t, h, rgb)


def circle(cx, cy, r, rgb):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                plot(xx, yy, rgb)


def disc(cx, cy, r, rgb):
    circle(cx, cy, r, rgb)

# ------------------------------------------------------------ 5x7 font ----
# Each glyph is 7 rows of 5 bits, written '1' for ink and '0' for paper.
FONT = {
    'A': '01110/10001/10001/11111/10001/10001/10001',
    'B': '11110/10001/10001/11110/10001/10001/11110',
    'C': '01110/10001/10000/10000/10000/10001/01110',
    'D': '11110/10001/10001/10001/10001/10001/11110',
    'E': '11111/10000/10000/11110/10000/10000/11111',
    'F': '11111/10000/10000/11110/10000/10000/10000',
    'G': '01110/10001/10000/10111/10001/10001/01111',
    'H': '10001/10001/10001/11111/10001/10001/10001',
    'I': '01110/00100/00100/00100/00100/00100/01110',
    'J': '00111/00010/00010/00010/00010/10010/01100',
    'K': '10001/10010/10100/11000/10100/10010/10001',
    'L': '10000/10000/10000/10000/10000/10000/11111',
    'M': '10001/11011/10101/10101/10001/10001/10001',
    'N': '10001/11001/10101/10011/10001/10001/10001',
    'O': '01110/10001/10001/10001/10001/10001/01110',
    'P': '11110/10001/10001/11110/10000/10000/10000',
    'Q': '01110/10001/10001/10001/10101/10010/01101',
    'R': '11110/10001/10001/11110/10100/10010/10001',
    'S': '01111/10000/10000/01110/00001/00001/11110',
    'T': '11111/00100/00100/00100/00100/00100/00100',
    'U': '10001/10001/10001/10001/10001/10001/01110',
    'V': '10001/10001/10001/10001/10001/01010/00100',
    'W': '10001/10001/10001/10101/10101/11011/10001',
    'X': '10001/10001/01010/00100/01010/10001/10001',
    'Y': '10001/10001/01010/00100/00100/00100/00100',
    'Z': '11111/00001/00010/00100/01000/10000/11111',
    'a': '00000/00000/01110/00001/01111/10001/01111',
    'b': '10000/10000/11110/10001/10001/10001/11110',
    'c': '00000/00000/01110/10000/10000/10001/01110',
    'd': '00001/00001/01111/10001/10001/10001/01111',
    'e': '00000/00000/01110/10001/11111/10000/01110',
    'f': '00110/01001/01000/11110/01000/01000/01000',
    'g': '00000/01111/10001/10001/01111/00001/01110',
    'h': '10000/10000/11110/10001/10001/10001/10001',
    'i': '00100/00000/01100/00100/00100/00100/01110',
    'j': '00010/00000/00110/00010/00010/10010/01100',
    'k': '10000/10000/10010/10100/11000/10100/10010',
    'l': '01100/00100/00100/00100/00100/00100/01110',
    'm': '00000/00000/11010/10101/10101/10101/10101',
    'n': '00000/00000/11110/10001/10001/10001/10001',
    'o': '00000/00000/01110/10001/10001/10001/01110',
    'p': '00000/00000/11110/10001/10001/11110/10000/10000',
    'q': '00000/00000/01111/10001/10001/01111/00001/00001',
    'r': '00000/00000/10110/11001/10000/10000/10000',
    's': '00000/00000/01111/10000/01110/00001/11110',
    't': '01000/01000/11110/01000/01000/01001/00110',
    'u': '00000/00000/10001/10001/10001/10011/01101',
    'v': '00000/00000/10001/10001/10001/01010/00100',
    'w': '00000/00000/10001/10101/10101/10101/01010',
    'x': '00000/00000/10001/01010/00100/01010/10001',
    'y': '00000/00000/10001/10001/01111/00001/01110',
    'z': '00000/00000/11111/00010/00100/01000/11111',
    '0': '01110/10001/10011/10101/11001/10001/01110',
    '1': '00100/01100/00100/00100/00100/00100/01110',
    '2': '01110/10001/00001/00110/01000/10000/11111',
    '3': '11111/00010/00100/00010/00001/10001/01110',
    '4': '00010/00110/01010/10010/11111/00010/00010',
    '5': '11111/10000/11110/00001/00001/10001/01110',
    '6': '01110/10000/10000/11110/10001/10001/01110',
    '7': '11111/00001/00010/00100/01000/01000/01000',
    '8': '01110/10001/10001/01110/10001/10001/01110',
    '9': '01110/10001/10001/01111/00001/00001/01110',
    ' ': '00000/00000/00000/00000/00000/00000/00000',
    '.': '00000/00000/00000/00000/00000/01100/01100',
    ',': '00000/00000/00000/00000/01100/00100/01000',
    ':': '00000/01100/01100/00000/01100/01100/00000',
    ';': '00000/01100/01100/00000/01100/00100/01000',
    '!': '00100/00100/00100/00100/00100/00000/00100',
    '?': '01110/10001/00001/00110/00100/00000/00100',
    "'": '00100/00100/01000/00000/00000/00000/00000',
    '"': '01010/01010/00000/00000/00000/00000/00000',
    '-': '00000/00000/00000/01110/00000/00000/00000',
    '(': '00010/00100/01000/01000/01000/00100/00010',
    ')': '01000/00100/00010/00010/00010/00100/01000',
    '/': '00001/00010/00010/00100/01000/01000/10000',
    '%': '11001/11010/00010/00100/01000/01011/10011',
    '$': '00100/01111/10100/01110/00101/11110/00100',
    '&': '01100/10010/10100/01000/10101/10010/01101',
    '+': '00000/00100/00100/01110/00100/00100/00000',
    '=': '00000/00000/11111/00000/11111/00000/00000',
    '#': '01010/01010/11111/01010/11111/01010/01010',
    '@': '01110/10001/10111/10101/10110/10000/01110',
    '*': '00000/10101/01110/11111/01110/10101/00000',
    '_': '00000/00000/00000/00000/00000/00000/11111',
    '[': '01110/01000/01000/01000/01000/01000/01110',
    ']': '01110/00010/00010/00010/00010/00010/01110',
    '<': '00010/00100/01000/10000/01000/00100/00010',
    '>': '01000/00100/00010/00001/00010/00100/01000',
}

# 'p' and 'q' carry an 8th row (descender); trim to 7 for uniform height.
for _k in ('p', 'q'):
    FONT[_k] = '/'.join(FONT[_k].split('/')[:7])


def glyph_rows(ch):
    return FONT.get(ch, FONT['?']).split('/')


def text_w(text, scale=1):
    return len(text) * 6 * scale - (1 * scale if text else 0)


def draw_text(x, y, text, scale=1, rgb=INK):
    cx = x
    for ch in text:
        rows = glyph_rows(ch)
        for ry in range(7):
            row = rows[ry]
            for rx in range(5):
                if row[rx] == '1':
                    if scale == 1:
                        plot(cx + rx, y + ry, rgb)
                    else:
                        rect(cx + rx * scale, y + ry * scale, scale, scale, rgb)
        cx += 6 * scale
    return cx - x


def draw_centred(cx, y, text, scale=1, rgb=INK):
    w = text_w(text, scale)
    draw_text(cx - w // 2, y, text, scale, rgb)
    return w


def wrap_text(text, max_chars):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, text, scale, max_w_px, line_h, rgb=INK):
    max_chars = max(1, max_w_px // (6 * scale))
    lines = wrap_text(text, max_chars)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * line_h, ln, scale, rgb)
    return y + len(lines) * line_h

# ------------------------------------------------------------ world map ----
# Coarse dotted world map, 64 x 32 cells, equirectangular.
# '#' is land. Drawn as dots; red markers flag the day's hot spots.
WORLD_MAP = [
    '................................................................',
    '......#####..........#####......##########....############.......',
    '....##########......#######..##########################..###....',
    '...############....########.#############################.##....',
    '...###########......######...##############################.....',
    '....#########........####.....########.##################......',
    '.....#######.........#####.....######....###############........',
    '.....######...........###......#####.....#############..........',
    '......####............###......####.......##########............',
    '......###.............##........###.......########..............',
    '......###.............###.......####.......######...............',
    '.....####............####........###.......#####................',
    '.....#####...........#####.......###.......####.................',
    '....######............####........##........##..................',
    '....#####.............####........##............................',
    '....####..............###......................................',
    '....###...............###......................................',
    '....###................#.......................................',
    '....##.................#.....................###...............',
    '...###................#.....................#####..............',
    '...##......................................#######.............',
    '............................................########...........',
    '.............................................######............',
    '..............................................####.............',
    '...............................................##..............',
    '............................................................##..',
    '...........................................................###..',
    '................................................................',
    '................................................................',
    '................................................................',
    '................................................................',
    '................................................................',
]

# (col, row) hot spots on the 64x32 grid: Pyongyang, Kyiv, Moscow,
# Washington, London, Beijing, Delhi, Cairo, Geneva, Mercury (off-map).
MAP_SPOTS = [
    (55, 8), (38, 6), (41, 5), (9, 9), (30, 6),
    (51, 9), (45, 10), (37, 11), (33, 7), (58, 12),
]


def draw_map(x, y, cell=7):
    for r, row in enumerate(WORLD_MAP):
        for c, ch in enumerate(row):
            if ch == '#':
                disc(x + c * cell + cell // 2, y + r * cell + cell // 2, 2, SEA)
    for (c, r) in MAP_SPOTS:
        mx = x + c * cell + cell // 2
        my = y + r * cell + cell // 2
        circle(mx, my, 5, ACCENT)
        disc(mx, my, 2, ACCENT)


# ------------------------------------------------------------ furniture ----
def section_head(x, y, w, label, rgb=INK):
    rect(x, y, w, 13, rgb)
    draw_text(x + 4, y + 3, label, 1, PAPER)
    return y + 16


def headline(x, y, text, scale, max_w, rgb=INK):
    max_chars = max(1, max_w // (6 * scale))
    lines = wrap_text(text, max_chars)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * (7 * scale + 2), ln, scale, rgb)
    return y + len(lines) * (7 * scale + 2)


def kicker(x, y, text, rgb=ACCENT):
    draw_text(x, y, text, 1, rgb)
    return y + 9


def story(x, y, w, kick, head, body, head_scale=2):
    y = kicker(x, y, kick)
    y = headline(x, y, head, head_scale, w)
    y = draw_para(x, y + 2, body, 1, w, 9)
    return y

# ------------------------------------------------------------ content ------
LEAD_HEAD = "KIM ORDERS WIDER NUCLEAR BUILD-UP"
LEAD_BODY = (
    "North Korean leader Kim Jong Un said his country should focus on deploying "
    "tactical nuclear weapons across multiple domains and systematically expand "
    "its nuclear material production, state media KCNA reported on Thursday. "
    "The call came as dozens of countries pressed Russia over the alleged use "
    "of a riot agent in Ukraine, and Kyiv said it had struck a major Russian "
    "air base, damaging five planes."
)

TICKER = ("KIM ORDERS NUCLEAR BUILD-UP  -  UKRAINE HITS RUSSIAN AIR BASE  -  "
          "US TARIFFS FOR 14 PARTNERS  -  NVIDIA -3.9%  -  BEPICOLOMBO AT MERCURY")

MARKETS = [
    ("S&P 500", "7,182.78  -0.3%"),
    ("Nasdaq", "23,585.80  -0.6%"),
    ("Dow Jones", "50,182.95  +0.3%"),
    ("Nikkei 225", "+1.6%"),
    ("Kospi", "+1.9%"),
    ("Brent crude", "$94.81 / bbl"),
    ("WTI crude", "$84.24 / bbl"),
    ("Gold", "$3,566 / oz"),
    ("EUR / USD", "1.0973"),
    ("USD / JPY", "159.14"),
    ("US 10-year yield", "4.848%"),
    ("US core inflation", "3.3%"),
]

WEATHER = ("London 4-6C overcast - Paris 4-7C light rain - Berlin -1-2C partly "
           "cloudy - Madrid 3-11C sunny - Riga -1-3C light snow")

WORLD = [
    ("UKRAINE", "UKRAINE HITS AIR BASE",
     "Kyiv says its forces struck a major Russian air base, damaging five planes."),
    ("UKRAINE", "WAR DEAD NEAR 500,000",
     "Russia's own figures show it has lost nearly 500,000 people in the war in Ukraine."),
    ("UKRAINE", "RIOT AGENT PROTEST",
     "Dozens of countries call on Russia to halt the alleged use of a riot agent in the war."),
    ("RUSSIA", "MURMANSK GOVERNOR HELD",
     "The head of Russia's Murmansk region is placed in pre-trial detention in a corruption inquiry."),
    ("UNITED STATES", "BIRTHRIGHT ORDER BLOCKED",
     "A second judge blocks Trump's newest order curtailing birthright citizenship."),
    ("LEBANON", "SECOND AIRPORT TO OPEN",
     "Lebanon plans a second international airport next month, a sign of Hezbollah's waning sway."),
    ("COLOMBIA", "HOSTAGES FREED IN RAID",
     "Police storm a supermarket and free 20 people held hostage for 17 hours."),
    ("INDIA", "CONSTITUTION DAY",
     "India marks Samvidhan Divas; a Rs 15,000-crore package for Nepal is announced."),
]

BUSINESS = [
    ("TRADE", "TARIFFS AIMED AT 14 PARTNERS",
     "The US proposes new duties on China, Japan, the EU and others, up to 25% on Indian goods."),
    ("MARKETS", "NVIDIA SLIDES AGAIN",
     "Down 3.9% to $149.30, $2.3 trillion below its October peak; S&P puts its rating on watch."),
    ("ECONOMY", "US GROWTH 4.3%",
     "Third-quarter GDP is revised sharply up; core inflation is 3.3%."),
    ("INDIA", "FLIPKART CHIEF TO GO",
     "Kalyan Krishnamurthy, chief executive of Walmart-owned Flipkart, steps down in December."),
]

TECH = [
    ("SPACE", "BEPICOLOMBO REACHES MERCURY",
     "After an eight-year journey; a glitch cut the burn to 77%. Its orbiters part on 9 December; science starts in April 2027."),
    ("SPACE", "RECORD QUASAR FOUND",
     "Euclid spots a quasar at redshift 8.13, 'Dun Aonghasa', seen 630m years after the Big Bang."),
    ("SPACE", "CHINA EYES CALLISTO",
     "China plans humanity's first landing on a moon of Jupiter, targeting the ice world Callisto."),
    ("TECHNOLOGY", "CRYPTO WARNING",
     "Scott Aaronson warns AI labs may hold undisclosed cryptography breakthroughs."),
]

SPORT = [
    ("CHESS", "GUKESH DRAWS GAME 2",
     "A 20-move draw with Sindarov leaves the World Championship match level at 1-1 in Geneva."),
    ("FOOTBALL", "CHAMPIONS LEAGUE NIGHT",
     "Isak scores twice as Liverpool beat Club Brugge; Manchester United are held 2-2 at Sporting; Bayern fall at Lille."),
    ("CRICKET", "SOORYAVANSHI 204 OFF 53",
     "Fifteen-year-old Vaibhav Sooryavanshi hits a record double century against UAE, with 28 sixes."),
    ("CRICKET", "IPL 2027: 1,220 REGISTER",
     "Players sign up for the auction, with 66 slots on offer across the franchises."),
    ("CRICKET", "BUMRAH NEARS NO. 1",
     "Jasprit Bumrah climbs to joint second in the ICC Test bowling rankings."),
    ("FOOTBALL", "STERLING SENTENCED",
     "Raheem Sterling is handed a suspended prison sentence after crashing his Lamborghini while inhaling laughing gas."),
    ("MUSIC", "ANDY TAYLOR DIES AT 65",
     "The guitarist of new wave icons Duran Duran dies at 65."),
]

BRIEFS = [
    "Thanksgiving Day in the United States.",
    "Australia capex jumps 12.2%, most since 2011.",
    "Kenya's last Ebola patient discharged.",
    "EU hunts a new ECB chief as Lagarde quits.",
    "North Korea tells Switzerland to shut its office.",
    "Six die in a plane crash off Mississippi.",
    "Hasina seeks a return to Bangladesh on 16 Dec.",
    "Bangladesh garment minimum wage up 36%.",
    "Norway court voids disputed oil licences.",
    "Cairo tanker fire kills at least 30.",
]

# ------------------------------------------------------------ layout -------
def draw_column(x, y, w, sections):
    for label, stories in sections:
        y = section_head(x, y, w, label)
        for kick, head, body in stories:
            y = story(x, y, w, kick, head, body, head_scale=2)
            y += 6
    return y


def build():
    # ---- masthead ----
    draw_centred(512, 16, "THE THURSDAY GLOBE", 6, INK)
    draw_text(24, 66, "VOL. I - No. 330", 1, FAINT)
    draw_centred(512, 66, "THURSDAY, 26 NOVEMBER 2026", 1, INK)
    draw_text(1000 - text_w("WORLD EDITION", 1), 66, "WORLD EDITION", 1, FAINT)
    hline(24, 80, 976, INK, 2)
    hline(24, 83, 976, INK, 1)
    draw_centred(512, 90, TICKER, 1, ACCENT)
    hline(24, 104, 976, RULE, 1)

    # ---- lead story ----
    y = 112
    y = kicker(24, y, "NORTH KOREA - NUCLEAR")
    y = headline(24, y, LEAD_HEAD, 3, 976)
    y = draw_para(24, y + 2, LEAD_BODY, 1, 976, 9)
    hline(24, 202, 976, INK, 2)

    # ---- map (left) ----
    y = 210
    section_head(24, y, 460, "THE WORLD IN ONE MAP")
    draw_map(24, y + 18, cell=7)
    draw_text(24, y + 246, "Red dots mark the day's flashpoints - from Pyongyang to Geneva.", 1, FAINT)

    # ---- markets (right) ----
    section_head(508, y, 492, "MARKETS - THE DAY IN NUMBERS")
    my = y + 20
    for name, val in MARKETS:
        draw_text(508, my, name, 1, INK)
        draw_text(1000 - text_w(val, 1), my, val, 1, INK)
        hline(508, my + 9, 492, RULE, 1)
        my += 14
    my += 4
    rect(508, my, 492, 1, INK)
    draw_text(508, my + 6, "WEATHER", 1, ACCENT)
    draw_para(508, my + 16, WEATHER, 1, 492, 9)

    hline(24, 472, 976, INK, 2)

    # ---- three columns ----
    col_y = 480
    draw_column(24, col_y, 313, [("WORLD", WORLD)])
    draw_column(349, col_y, 313, [("BUSINESS", BUSINESS), ("TECH & SCIENCE", TECH)])
    sport_end = draw_column(674, col_y, 300, [("SPORT", SPORT)])
    # briefs fill the rest of the sport column
    by = section_head(674, sport_end + 4, 300, "IN BRIEF")
    for b in BRIEFS:
        by = draw_para(674, by, "- " + b, 1, 300, 9)

    # ---- footer ----
    hline(24, 988, 976, INK, 1)
    draw_centred(512, 996, "THE THURSDAY GLOBE  -  THURSDAY, 26 NOVEMBER 2026  -  34 STORIES, ONE DAY", 1, FAINT)


# ------------------------------------------------------------ PNG writer ---
def write_png(path):
    raw = bytearray()
    for yy in range(SIZE):
        raw.append(0)
        base = yy * SIZE * 3
        raw += canvas[base:base + SIZE * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        c += struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack('>IIBBBBB', SIZE, SIZE, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


def main():
    build()
    out = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, 'entry.png')
    n = write_png(path)
    print('wrote %s (%d bytes)' % (path, n))


if __name__ == '__main__':
    main()
