#!/usr/bin/env python3
"""Builds the Rohr Software logo (a dragon eye) as logo.svg and every favicon.

Two drawings share one idea: the full eye (logo.svg, logo-512.png, apple-touch-icon.png) and a
bolder "small" eye with fewer, thicker fibers and a wider pupil that stays readable at tab size
(favicon.svg, favicon.ico, favicon-16/32.png).

Run from anywhere: python3 make_logo.py. Needs Pillow. Output goes to the repo root and this folder.
"""
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent

REDS = ["#e8341c", "#d92b17", "#c62412", "#f04a1c"]
DARK = ["#a31a0c", "#8c150a", "#b81e0e", "#c62412"]
ORANGES = ["#ff8a1f", "#ff7a1a", "#f9661a", "#ff9a24"]
YELLOWS = ["#ffd23a", "#ffc02a", "#ffb020", "#ffe066"]

FULL = dict(
    stops=[(0.0, "#ffb020"), (0.30, "#f4601a"), (0.60, "#bd1f0e"), (0.84, "#5e0e06"), (1.0, "#2a0805")],
    radius=31.0, pupil=((32, 11.5), (38.5, 22), (38.5, 42), (32, 52.5)), lens_rx=4.6, lens_ry=20.0,
    count=470, width=(0.3, 0.75), reach=(9, 27), glint=(39.6, 19, 2.3, 2.5), seed=11,
)
SMALL = dict(
    stops=[(0.0, "#ffc83d"), (0.35, "#f4601a"), (0.70, "#c42410"), (1.0, "#6a1208")],
    radius=32.0, pupil=((32, 9), (43, 21), (43, 43), (32, 55)), lens_rx=7.0, lens_ry=21.0,
    count=70, width=(1.0, 1.8), reach=(12, 28), glint=(40.5, 20, 3.2, 3.4), seed=5,
)
PUPIL = "#0a0504"
CX = CY = 32.0


def fibers(st):
    rng = random.Random(st["seed"])
    lo, hi = st["reach"]
    out = []
    for _ in range(st["count"]):
        theta = rng.uniform(0, math.tau)
        c, s = math.cos(theta), math.sin(theta)
        r_end = lo + (hi - lo) * rng.random() ** 0.8
        twist = rng.uniform(-0.3, 0.3)
        p0 = (CX + st["lens_rx"] * c, CY + st["lens_ry"] * s)
        p3 = (CX + r_end * math.cos(theta + twist), CY + r_end * math.sin(theta + twist))
        dx, dy = p3[0] - p0[0], p3[1] - p0[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length, dx / length
        amp = rng.uniform(1.0, 3.6) * (length / 18) * rng.choice((-1, 1))
        c1 = (p0[0] + dx * 0.33 + nx * amp, p0[1] + dy * 0.33 + ny * amp)
        c2 = (p0[0] + dx * 0.66 - nx * amp, p0[1] + dy * 0.66 - ny * amp)
        t = (r_end - lo) / (hi - lo) * (1.2 - 0.5 * abs(c)) + rng.uniform(-0.12, 0.12)
        palette = YELLOWS if t < 0.22 else ORANGES if t < 0.45 else REDS if t < 0.75 else DARK
        out.append((r_end, (p0, c1, c2, p3, round(rng.uniform(*st["width"]), 2), rng.choice(palette))))
    out.sort(key=lambda item: -item[0])
    return [item for _, item in out]


def hex_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def gradient_at(stops, t):
    t = min(max(t, 0.0), 1.0)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if t <= b:
            f = (t - a) / (b - a)
            return tuple(round(x + (y - x) * f) for x, y in zip(hex_rgb(ca), hex_rgb(cb)))
    return hex_rgb(stops[-1][1])


def cubic(p0, p1, p2, p3, steps=16):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        pts.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return pts


def pupil_outline(st):
    p0, p1, p2, p3 = st["pupil"]
    mirror = lambda p: (64 - p[0], p[1])
    return cubic(p0, p1, p2, p3, 40) + cubic(p3, mirror(p2), mirror(p1), p0, 40)


def write_svg(path, st, items):
    f = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in st["stops"])
    paths = "".join(
        f'<path d="M{f(a[0])} {f(a[1])}C{f(b[0])} {f(b[1])} {f(c[0])} {f(c[1])} {f(e[0])} {f(e[1])}" stroke="{col}" stroke-width="{w}"/>'
        for a, b, c, e, w, col in items)
    p0, p1, p2, p3 = st["pupil"]
    pupil = (f"M{f(p0[0])} {f(p0[1])}C{f(p1[0])} {f(p1[1])} {f(p2[0])} {f(p2[1])} {f(p3[0])} {f(p3[1])}"
             f"C{f(64 - p2[0])} {f(p2[1])} {f(64 - p1[0])} {f(p1[1])} {f(p0[0])} {f(p0[1])}Z")
    gx, gy, grx, gry = st["glint"]
    r = st["radius"]
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img">'
        '<title>Rohr Software</title>'
        f'<defs><radialGradient id="iris" gradientUnits="userSpaceOnUse" cx="32" cy="32" r="{f(r)}">{stops}</radialGradient></defs>'
        f'<circle cx="32" cy="32" r="{f(r)}" fill="url(#iris)"/>'
        f'<g fill="none" stroke-linecap="round">{paths}</g>'
        f'<path d="{pupil}" fill="{PUPIL}"/>'
        f'<ellipse cx="{f(gx)}" cy="{f(gy)}" rx="{f(grx)}" ry="{f(gry)}" fill="#fff"/>'
        '</svg>\n')


def render(st, items, size, square=False, ss=8):
    S = size * ss
    k = S / 64
    R = st["radius"]
    bg = hex_rgb(st["stops"][-1][1])
    img = Image.new("RGBA", (S, S), bg + ((255,) if square else (0,)))
    d = int(round(2 * R * k))
    gray = Image.radial_gradient("L").resize((d, d), Image.BICUBIC)
    # Pillow's radial gradient reaches 255 at the corner, so the circle's edge sits at gray 180
    luts = [[gradient_at(st["stops"], i / 180)[ch] for i in range(256)] for ch in range(3)]
    disc = Image.merge("RGB", [gray.point(luts[ch]) for ch in range(3)])
    mask = Image.new("L", (d, d), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, d - 1, d - 1], fill=255)
    off = int(round((CX - R) * k))
    img.paste(disc, (off, off), mask)
    draw = ImageDraw.Draw(img)
    for a, b, c, e, w, col in items:
        draw.line([(x * k, y * k) for x, y in cubic(a, b, c, e)], fill=hex_rgb(col),
                  width=max(1, round(w * k)), joint="curve")
    draw.polygon([(x * k, y * k) for x, y in pupil_outline(st)], fill=hex_rgb(PUPIL))
    gx, gy, grx, gry = st["glint"]
    draw.ellipse([(gx - grx) * k, (gy - gry) * k, (gx + grx) * k, (gy + gry) * k], fill=(255, 255, 255))
    out = img.resize((size, size), Image.LANCZOS)
    return out.convert("RGB") if square else out


if __name__ == "__main__":
    full, small = fibers(FULL), fibers(SMALL)
    write_svg(HERE / "logo.svg", FULL, full)
    write_svg(ROOT / "favicon.svg", SMALL, small)
    render(FULL, full, 512).save(HERE / "logo-512.png")
    render(FULL, full, 180, square=True).save(ROOT / "apple-touch-icon.png")
    render(SMALL, small, 16).save(ROOT / "favicon-16.png")
    render(SMALL, small, 32).save(ROOT / "favicon-32.png")
    render(SMALL, small, 256).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("ok:", len(full), "and", len(small), "fibers;", (HERE / "logo.svg").stat().st_size, "and",
          (ROOT / "favicon.svg").stat().st_size, "bytes")
