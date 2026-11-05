#!/usr/bin/env python3
"""Generate stand-in ink-wash paintings, one SVG per chapter.

They exist so the scroll, camera moves and ink transitions can be built and
tested before the real artwork is made. Each one leaves the chapter's copy side
quiet, like the real paintings must, and is clearly labeled as a placeholder.

    python3 scripts/make_placeholders.py
"""

import math
import random
from pathlib import Path

W, H = 1920, 1080
OUT = Path(__file__).resolve().parent.parent / "assets" / "art" / "placeholder"

PAPER = "#efe7d6"
PAPER_DEEP = "#e2d6bd"
INK = "#1d2320"
GOLD = "#d6a24a"
RED = "#a8322a"
TEAL = "#5f8582"

# file, year, label, copy side, motif
SCENES = [
    ("01-divide", "1832", "Wetland on the divide", "left", "reeds"),
    ("02-clearing", "1833", "Log hut in the clearing", "right", "hut"),
    ("03-canal", "1845", "Canal boat at Lock One", "left", "canal"),
    ("04-boomtown", "1850", "Canal-side street", "right", "town"),
    ("05-rails", "1871", "Train beyond the canal", "left", "rail"),
    ("06-two-towns", "1876", "Two towns across the canal", "bottom", "roofs"),
    ("07-gaslight", "1888", "Gaslight and the opera house", "right", "lamps"),
    ("08-interurban", "1902", "Interurban on Main Street", "left", "street"),
    ("09-centennial", "1933", "Centennial parade", "right", "flags"),
    ("10-today", "Today", "Lock One today", "bottom", "lock"),
]


def ridge(rng, base, amp, color, opacity):
    pts = []
    phase = rng.uniform(0, 6.28)
    for i in range(0, W + 80, 60):
        y = base + amp * (0.6 * math.sin(i / 310 + phase) + 0.4 * math.sin(i / 97 + phase * 2)) + rng.uniform(-8, 8)
        pts.append(f"{i},{y:.0f}")
    d = "M-40," + str(H + 40) + " L" + " L".join(pts) + f" L{W + 40},{H + 40} Z"
    return f'<path d="{d}" fill="{color}" opacity="{opacity}" filter="url(#wash)"/>'


def water(y, h):
    out = [f'<rect x="-40" y="{y}" width="{W + 80}" height="{h}" fill="#c6cec2" opacity=".75" filter="url(#wash)"/>']
    for k in range(7):
        yy = y + 12 + k * (h - 20) / 7
        out.append(
            f'<path d="M{80 + k * 170},{yy:.0f} h{220 + (k % 3) * 90}" stroke="{INK}" stroke-width="2" opacity=".18" filter="url(#brush)"/>'
        )
    return "".join(out)


def house(x, base, w, h, opacity, windows=True):
    roof = h * 0.35
    s = (
        f'<path d="M{x},{base} v{-h} l{w / 2},{-roof} l{w / 2},{roof} v{h} Z" fill="{INK}" opacity="{opacity}" filter="url(#brush)"/>'
    )
    if windows and w > 40:
        for wx in range(int(x + w * 0.2), int(x + w * 0.8), max(18, int(w / 4))):
            s += f'<rect x="{wx}" y="{base - h * 0.75:.0f}" width="9" height="15" fill="{PAPER}" opacity=".55"/>'
    return s


def motif(kind, rng, cx, cy):
    s = []
    if kind == "reeds":
        for _ in range(46):
            x = cx + rng.uniform(-340, 340)
            y = H * rng.uniform(0.86, 0.99)
            h = rng.uniform(80, 240)
            dx = rng.uniform(-40, 40)
            s.append(
                f'<path d="M{x:.0f},{y:.0f} q{dx / 2:.0f},{-h / 2:.0f} {dx:.0f},{-h:.0f}" stroke="{INK}" stroke-width="{rng.uniform(1.5, 4):.1f}" fill="none" opacity="{rng.uniform(.35, .75):.2f}" filter="url(#brush)"/>'
            )
        s.append(f'<path d="M{cx},{H * .76:.0f} c-120,20 -260,10 -520,60" stroke="{TEAL}" stroke-width="7" fill="none" opacity=".45" filter="url(#wash)"/>')
        s.append(f'<path d="M{cx},{H * .76:.0f} c120,25 300,15 560,70" stroke="{TEAL}" stroke-width="7" fill="none" opacity=".45" filter="url(#wash)"/>')
    elif kind == "hut":
        for k in range(6):
            tx = cx + (-420 if k < 3 else 300) + k * 40
            s.append(f'<ellipse cx="{tx}" cy="{H * .42:.0f}" rx="{rng.uniform(70, 120):.0f}" ry="{rng.uniform(140, 220):.0f}" fill="{INK}" opacity=".22" filter="url(#wash)"/>')
        s.append(house(cx - 100, H * 0.72, 200, 110, 0.78, windows=False))
        s.append(f'<rect x="{cx - 18}" y="{H * .72 - 60:.0f}" width="34" height="60" fill="{PAPER}" opacity=".5"/>')
        s.append(f'<path d="M{cx + 60},{H * .58:.0f} c30,-60 -40,-90 10,-160 s-30,-90 20,-150" stroke="{INK}" stroke-width="16" fill="none" opacity=".2" filter="url(#wash)"/>')
        s.append(f'<path d="M{cx + 160},{H * .76:.0f} h130 v-50 q-65,-55 -130,0 Z" fill="{INK}" opacity=".5" filter="url(#brush)"/>')
        s.append(f'<circle cx="{cx + 185}" cy="{H * .77:.0f}" r="20" stroke="{INK}" stroke-width="4" fill="none" opacity=".6"/>')
        s.append(f'<circle cx="{cx + 270}" cy="{H * .77:.0f}" r="20" stroke="{INK}" stroke-width="4" fill="none" opacity=".6"/>')
        for k in range(5):
            s.append(f'<path d="M{cx - 300 + k * 60},{H * .82:.0f} v-26" stroke="{INK}" stroke-width="4" opacity=".55"/>')
    elif kind == "canal":
        s.append(water(H * 0.68, H * 0.14))
        s.append(f'<path d="M-40,{H * .67:.0f} H{W + 40}" stroke="{INK}" stroke-width="3" opacity=".35" filter="url(#brush)"/>')
        s.append(f'<path d="M{cx - 40},{H * .72:.0f} h300 l-30,34 h-250 Z" fill="{INK}" opacity=".72" filter="url(#brush)"/>')
        s.append(f'<rect x="{cx + 60}" y="{H * .72 - 34:.0f}" width="110" height="34" fill="{INK}" opacity=".6" filter="url(#brush)"/>')
        for k in range(3):
            mx = cx - 330 + k * 70
            s.append(f'<ellipse cx="{mx}" cy="{H * .64:.0f}" rx="28" ry="14" fill="{INK}" opacity=".7" filter="url(#brush)"/>')
            s.append(f'<path d="M{mx - 14},{H * .64 + 10:.0f} v22 M{mx + 14},{H * .64 + 10:.0f} v22" stroke="{INK}" stroke-width="4" opacity=".7"/>')
        s.append(f'<path d="M{cx - 40},{H * .72:.0f} L{cx - 190},{H * .64:.0f}" stroke="{INK}" stroke-width="2" opacity=".5"/>')
        gx = cx + 420
        s.append(f'<rect x="{gx}" y="{H * .6:.0f}" width="26" height="{H * .22:.0f}" fill="{INK}" opacity=".75" filter="url(#brush)"/>')
        s.append(f'<path d="M{gx + 13},{H * .61:.0f} l170,-40" stroke="{INK}" stroke-width="12" opacity=".7" filter="url(#brush)"/>')
    elif kind == "town":
        x = cx - 380
        for k in range(7):
            w = rng.uniform(90, 140)
            s.append(house(x, H * 0.7, w, rng.uniform(130, 230), rng.uniform(.5, .78)))
            x += w + rng.uniform(6, 20)
        s.append(water(H * 0.74, H * 0.12))
        for k in range(9):
            bx = cx - 200 + (k % 3) * 34
            by = H * 0.72 - (k // 3) * 30
            s.append(f'<ellipse cx="{bx}" cy="{by:.0f}" rx="15" ry="14" fill="{INK}" opacity=".6" filter="url(#brush)"/>')
        s.append(f'<path d="M{cx + 40},{H * .79:.0f} h260 l-26,30 h-210 Z" fill="{INK}" opacity=".6" filter="url(#brush)"/>')
    elif kind == "rail":
        s.append(water(H * 0.74, H * 0.16))
        s.append(f'<path d="M-40,{H * .57:.0f} H{W + 40}" stroke="{INK}" stroke-width="6" opacity=".3" filter="url(#wash)"/>')
        tx = cx - 40
        s.append(f'<rect x="{tx}" y="{H * .535:.0f}" width="70" height="30" fill="{INK}" opacity=".8" filter="url(#brush)"/>')
        s.append(f'<rect x="{tx + 12}" y="{H * .535 - 24:.0f}" width="12" height="24" fill="{INK}" opacity=".8"/>')
        for k in range(4):
            s.append(f'<rect x="{tx + 78 + k * 64}" y="{H * .54:.0f}" width="58" height="24" fill="{INK}" opacity=".6" filter="url(#brush)"/>')
        s.append(f'<path d="M{tx + 18},{H * .5:.0f} c-80,-50 -200,-30 -320,-70 s-200,-10 -320,-40" stroke="{INK}" stroke-width="22" fill="none" opacity=".16" filter="url(#wash)"/>')
    elif kind == "roofs":
        vx, vy = cx, H * 0.36
        s.append(f'<path d="M{vx - 14},{vy:.0f} L{vx + 14},{vy:.0f} L{vx + 260},{H * .7:.0f} L{vx - 260},{H * .7:.0f} Z" fill="#c6cec2" opacity=".85" filter="url(#wash)"/>')
        for side in (-1, 1):
            for k in range(9):
                t = k / 8
                size = 120 - 90 * t
                x = vx + side * (300 - 250 * t) - (size if side < 0 else 0) + side * rng.uniform(0, 40)
                base = H * 0.68 - (H * 0.3) * t
                s.append(house(x, base, size, size * 0.8, 0.45 + 0.25 * (1 - t), windows=size > 70))
            sx = vx + side * 330
            s.append(f'<path d="M{sx - 18},{H * .52:.0f} l18,-170 l18,170 Z" fill="{INK}" opacity=".6" filter="url(#brush)"/>')
        s.append(f'<path d="M{vx - 150},{H * .56:.0f} q150,-50 300,0" stroke="{INK}" stroke-width="8" fill="none" opacity=".65" filter="url(#brush)"/>')
    elif kind == "lamps":
        s.append(f'<rect x="{cx - 230}" y="{H * .3:.0f}" width="400" height="{H * .42:.0f}" fill="{INK}" opacity=".72" filter="url(#brush)"/>')
        s.append(f'<path d="M{cx - 250},{H * .3:.0f} h440 l-30,-40 h-380 Z" fill="{INK}" opacity=".8" filter="url(#brush)"/>')
        for r in range(2):
            for c in range(5):
                wx = cx - 200 + c * 76
                wy = H * 0.38 + r * 130
                s.append(f'<rect x="{wx}" y="{wy:.0f}" width="34" height="62" fill="{GOLD}" opacity=".85"/>')
                s.append(f'<circle cx="{wx + 17}" cy="{wy + 30:.0f}" r="42" fill="{GOLD}" opacity=".25" filter="url(#glow)"/>')
        for k in range(3):
            lx = cx - 420 + k * 90 if k < 2 else cx + 300
            s.append(f'<path d="M{lx},{H * .86:.0f} V{H * .55:.0f}" stroke="{INK}" stroke-width="6" opacity=".8"/>')
            s.append(f'<circle cx="{lx}" cy="{H * .54:.0f}" r="10" fill="{GOLD}"/>')
            s.append(f'<circle cx="{lx}" cy="{H * .54:.0f}" r="70" fill="{GOLD}" opacity=".35" filter="url(#glow)"/>')
        for _ in range(30):
            s.append(f'<ellipse cx="{cx + rng.uniform(-300, 260):.0f}" cy="{H * rng.uniform(.8, .86):.0f}" rx="9" ry="16" fill="{INK}" opacity=".7"/>')
    elif kind in ("street", "flags"):
        vx, vy = cx + 60, H * 0.48
        s.append(f'<path d="M{vx - 6},{vy:.0f} L{vx + 6},{vy:.0f} L{vx + 420},{H + 20} L{vx - 420},{H + 20} Z" fill="#d4d6c8" opacity=".7" filter="url(#wash)"/>')
        for side in (-1, 1):
            for k in range(6):
                t = k / 6
                w = 170 - 120 * t
                h = 300 - 200 * t
                x = vx + side * (440 - 380 * t) - (w if side < 0 else 0)
                base = H * 0.86 - (H * 0.36) * t
                s.append(f'<rect x="{x:.0f}" y="{base - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{INK}" opacity="{.42 + .3 * (1 - t):.2f}" filter="url(#brush)"/>')
        if kind == "street":
            s.append(f'<path d="M{vx - 600},{H * .3:.0f} L{vx},{vy - 60:.0f}" stroke="{INK}" stroke-width="2" opacity=".6"/>')
            s.append(f'<rect x="{vx - 150}" y="{H * .56:.0f}" width="250" height="120" rx="18" fill="{INK}" opacity=".82" filter="url(#brush)"/>')
            for k in range(5):
                s.append(f'<rect x="{vx - 132 + k * 46}" y="{H * .58:.0f}" width="30" height="34" fill="{PAPER}" opacity=".6"/>')
            s.append(f'<path d="M{vx - 40},{H * .56:.0f} L{vx - 160},{H * .41:.0f}" stroke="{INK}" stroke-width="3" opacity=".7"/>')
        else:
            colors = [RED, TEAL, PAPER, RED, GOLD]
            for row in range(3):
                y0 = H * (0.36 + row * 0.08)
                spread = 420 - row * 110
                n = 12 - row * 3
                for k in range(n):
                    x = vx - spread + k * (2 * spread / n)
                    s.append(f'<path d="M{x:.0f},{y0:.0f} l{spread / n:.0f},0 l{-spread / n / 2:.0f},{30 - row * 6} Z" fill="{colors[k % len(colors)]}" opacity=".7" filter="url(#brush)"/>')
            for _ in range(60):
                s.append(f'<ellipse cx="{vx + rng.uniform(-380, 380):.0f}" cy="{H * rng.uniform(.84, .92):.0f}" rx="8" ry="15" fill="{INK}" opacity=".65"/>')
    elif kind == "lock":
        for k in range(5):
            s.append(f'<ellipse cx="{cx - 520 + k * 260}" cy="{H * .36:.0f}" rx="{rng.uniform(150, 220):.0f}" ry="{rng.uniform(150, 210):.0f}" fill="{INK}" opacity=".18" filter="url(#wash)"/>')
        s.append(water(H * 0.62, H * 0.12))
        s.append(f'<rect x="{cx - 330}" y="{H * .6:.0f}" width="660" height="18" fill="{INK}" opacity=".5" filter="url(#brush)"/>')
        s.append(f'<rect x="{cx - 330}" y="{H * .74:.0f}" width="660" height="18" fill="{INK}" opacity=".5" filter="url(#brush)"/>')
        for gx in (cx - 300, cx + 280):
            s.append(f'<rect x="{gx}" y="{H * .6:.0f}" width="22" height="{H * .15:.0f}" fill="{INK}" opacity=".75"/>')
            s.append(f'<path d="M{gx + 11},{H * .6:.0f} l150,-36" stroke="{INK}" stroke-width="10" opacity=".7" filter="url(#brush)"/>')
        s.append(f'<path d="M-40,{H * .8:.0f} H{W + 40}" stroke="{INK}" stroke-width="4" opacity=".3" filter="url(#brush)"/>')
        bx = cx + 120
        s.append(f'<circle cx="{bx}" cy="{H * .78:.0f}" r="18" stroke="{INK}" stroke-width="3" fill="none" opacity=".75"/>')
        s.append(f'<circle cx="{bx + 50}" cy="{H * .78:.0f}" r="18" stroke="{INK}" stroke-width="3" fill="none" opacity=".75"/>')
        s.append(f'<path d="M{bx},{H * .78:.0f} l20,-24 h24 l6,24 M{bx + 22},{H * .78 - 24:.0f} l-4,-30" stroke="{INK}" stroke-width="3" fill="none" opacity=".75"/>')
        s.append(f'<circle cx="{bx + 18}" cy="{H * .78 - 62:.0f}" r="7" fill="{INK}" opacity=".75"/>')
        for _ in range(18):
            x = cx + rng.uniform(-600, 600)
            y = H * rng.uniform(.5, .56)
            s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3" fill="{GOLD}"/><circle cx="{x:.0f}" cy="{y:.0f}" r="14" fill="{GOLD}" opacity=".3" filter="url(#glow)"/>')
    return "".join(s)


def scene_svg(index, file, year, label, side, kind):
    rng = random.Random(index * 9973 + 17)
    seed = index * 11 + 3
    if side == "left":
        cx, quiet = W * 0.66, (W * 0.12, H * 0.48)
    elif side == "right":
        cx, quiet = W * 0.34, (W * 0.86, H * 0.48)
    else:
        cx, quiet = W * 0.5, (W * 0.5, H * 0.95)
    cy = H * 0.5

    dusk = kind == "lamps"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        "<defs>",
        f'<filter id="wash" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.006 0.012" numOctaves="3" seed="{seed}"/><feDisplacementMap in="SourceGraphic" scale="70"/><feGaussianBlur stdDeviation="5"/></filter>',
        f'<filter id="brush" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="{seed + 1}"/><feDisplacementMap in="SourceGraphic" scale="6"/><feGaussianBlur stdDeviation="0.6"/></filter>',
        '<filter id="mist" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="50"/></filter>',
        '<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="16"/></filter>',
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PAPER_DEEP}"/><stop offset=".65" stop-color="{PAPER}"/></linearGradient>',
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
    ]
    if dusk:
        parts.append(f'<rect width="{W}" height="{H}" fill="#39404a" opacity=".32"/>')
    parts.append(ridge(rng, H * 0.5, 60, "#aab3a6", 0.55))
    parts.append(ridge(rng, H * 0.63, 45, "#7e8a7f", 0.45))
    parts.append(ridge(rng, H * 0.82, 18, "#5c675f", 0.3))
    lift = -H * 0.12 if side == "bottom" else 0  # keep the bottom third quiet for copy
    parts.append(f'<g transform="translate(0 {lift:.0f})">{motif(kind, rng, cx, cy)}</g>')

    # Mist, heaviest over the copy side so text has a quiet field.
    parts.append(f'<ellipse cx="{quiet[0]:.0f}" cy="{quiet[1]:.0f}" rx="{W * .3:.0f}" ry="{H * .42:.0f}" fill="{PAPER}" opacity=".8" filter="url(#mist)"/>')
    for _ in range(4):
        parts.append(
            f'<ellipse cx="{rng.uniform(0, W):.0f}" cy="{rng.uniform(H * .35, H * .8):.0f}" rx="{rng.uniform(240, 480):.0f}" ry="{rng.uniform(40, 90):.0f}" fill="#ffffff" opacity=".45" filter="url(#mist)"/>'
        )

    font = "font-family=\"Georgia, 'Times New Roman', serif\""
    parts.append(f'<text x="{cx:.0f}" y="{H * .3:.0f}" {font} font-style="italic" font-size="220" text-anchor="middle" fill="{INK}" opacity=".1">{year}</text>')
    parts.append(f'<rect x="{cx - 13:.0f}" y="{H - 104}" width="26" height="26" rx="2" fill="{RED}" opacity=".85"/>')
    parts.append(
        f'<text x="{cx:.0f}" y="{H - 48}" {font} font-size="19" letter-spacing="5" text-anchor="middle" fill="{INK}" opacity=".55">PLACEHOLDER · {label.upper()}</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for i, (file, year, label, side, kind) in enumerate(SCENES):
        (OUT / f"{file}.svg").write_text(scene_svg(i, file, year, label, side, kind), encoding="utf-8")
        print(f"wrote {OUT / (file + '.svg')}")


if __name__ == "__main__":
    main()
