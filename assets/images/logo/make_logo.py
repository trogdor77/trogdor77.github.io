#!/usr/bin/env python3
"""Builds the Rohr Software logo (a dragon eye) as logo.svg and every favicon PNG from one set of fibers.

Run from anywhere: python3 make_logo.py. Needs Pillow. Output goes to the repo root and this folder.
"""
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent

STOPS = [(0.0, "#ffb020"), (0.30, "#f4601a"), (0.60, "#bd1f0e"), (0.84, "#5e0e06"), (1.0, "#2a0805")]
PUPIL = "#0a0504"
PUPIL_PATH = "M32 11.5C38.5 22 38.5 42 32 52.5C25.5 42 25.5 22 32 11.5Z"
CX = CY = 32.0
R = 31.0
LENS_RX, LENS_RY = 4.6, 20.0

REDS = ["#e8341c", "#d92b17", "#c62412", "#f04a1c"]
DARK = ["#a31a0c", "#8c150a", "#b81e0e", "#c62412"]
ORANGES = ["#ff8a1f", "#ff7a1a", "#f9661a", "#ff9a24"]
YELLOWS = ["#ffd23a", "#ffc02a", "#ffb020", "#ffe066"]


def fibers(count=470):
    rng = random.Random(11)
    out = []
    for _ in range(count):
        theta = rng.uniform(0, math.tau)
        c, s = math.cos(theta), math.sin(theta)
        r_end = 9 + 18 * rng.random() ** 0.8
        twist = rng.uniform(-0.3, 0.3)
        p0 = (CX + LENS_RX * c, CY + LENS_RY * s)
        p3 = (CX + r_end * math.cos(theta + twist), CY + r_end * math.sin(theta + twist))
        dx, dy = p3[0] - p0[0], p3[1] - p0[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length, dx / length
        amp = rng.uniform(1.0, 3.6) * (length / 18) * rng.choice((-1, 1))
        c1 = (p0[0] + dx * 0.33 + nx * amp, p0[1] + dy * 0.33 + ny * amp)
        c2 = (p0[0] + dx * 0.66 - nx * amp, p0[1] + dy * 0.66 - ny * amp)
        h = abs(c)
        t = (r_end - 9) / 18 * (1.2 - 0.5 * h) + rng.uniform(-0.12, 0.12)
        if t < 0.22:
            palette = YELLOWS
        elif t < 0.45:
            palette = ORANGES
        elif t < 0.75:
            palette = REDS
        else:
            palette = DARK
        width = round(rng.uniform(0.3, 0.75), 2)
        out.append((r_end, (p0, c1, c2, p3, width, rng.choice(palette))))
    out.sort(key=lambda item: -item[0])
    return [item for _, item in out]


def hex_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def gradient_at(t):
    t = min(max(t, 0.0), 1.0)
    for (a, ca), (b, cb) in zip(STOPS, STOPS[1:]):
        if t <= b:
            f = (t - a) / (b - a)
            return tuple(round(x + (y - x) * f) for x, y in zip(hex_rgb(ca), hex_rgb(cb)))
    return hex_rgb(STOPS[-1][1])


def cubic(p0, p1, p2, p3, steps=16):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        pts.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return pts


def write_svg(path, items):
    f = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in STOPS)
    paths = "".join(
        f'<path d="M{f(a[0])} {f(a[1])}C{f(b[0])} {f(b[1])} {f(c[0])} {f(c[1])} {f(e[0])} {f(e[1])}" stroke="{col}" stroke-width="{w}"/>'
        for a, b, c, e, w, col in items)
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img">'
        '<title>Rohr Software</title>'
        f'<defs><radialGradient id="iris" gradientUnits="userSpaceOnUse" cx="32" cy="32" r="31">{stops}</radialGradient></defs>'
        '<circle cx="32" cy="32" r="31" fill="url(#iris)"/>'
        f'<g fill="none" stroke-linecap="round">{paths}</g>'
        f'<path d="{PUPIL_PATH}" fill="{PUPIL}"/>'
        '<ellipse cx="39.6" cy="19" rx="2.3" ry="2.5" fill="#fff"/>'
        '</svg>\n')


def render(items, size, square=False, ss=8):
    S = size * ss
    k = S / 64
    bg = hex_rgb(STOPS[-1][1])
    img = Image.new("RGBA", (S, S), bg + ((255,) if square else (0,)))
    d = int(round(2 * R * k))
    gray = Image.radial_gradient("L").resize((d, d), Image.BICUBIC)
    luts = [[gradient_at(i / 180)[ch] for i in range(256)] for ch in range(3)]
    disc = Image.merge("RGB", [gray.point(luts[ch]) for ch in range(3)])
    mask = Image.new("L", (d, d), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, d - 1, d - 1], fill=255)
    off = int(round((CX - R) * k))
    img.paste(disc, (off, off), mask)
    draw = ImageDraw.Draw(img)
    for a, b, c, e, w, col in items:
        pts = [(x * k, y * k) for x, y in cubic(a, b, c, e)]
        draw.line(pts, fill=hex_rgb(col), width=max(1, round(w * k)), joint="curve")
    lens = []
    for p0, p1, p2, p3 in [((32, 11.5), (38.5, 22), (38.5, 42), (32, 52.5)), ((32, 52.5), (25.5, 42), (25.5, 22), (32, 11.5))]:
        for i in range(41):
            t = i / 40
            u = 1 - t
            lens.append(((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]) * k,
                         (u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]) * k))
    draw.polygon(lens, fill=hex_rgb(PUPIL))
    hx, hy, rx, ry = 39.6 * k, 19 * k, 2.3 * k, 2.5 * k
    draw.ellipse([hx - rx, hy - ry, hx + rx, hy + ry], fill=(255, 255, 255))
    out = img.resize((size, size), Image.LANCZOS)
    return out.convert("RGB") if square else out


if __name__ == "__main__":
    items = fibers()
    write_svg(HERE / "logo.svg", items)
    write_svg(ROOT / "favicon.svg", items)
    render(items, 512).save(HERE / "logo-512.png")
    render(items, 16).save(ROOT / "favicon-16.png")
    render(items, 32).save(ROOT / "favicon-32.png")
    render(items, 180, square=True).save(ROOT / "apple-touch-icon.png")
    render(items, 256).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("ok", len(items), "fibers;", (HERE / "logo.svg").stat().st_size, "bytes svg")
