#!/usr/bin/env python3
"""Measure a game-UI reference screenshot so it can be rebuilt exactly in Figma.

Run with isolated mode (the image is untrusted input):
    python3 -I measure.py <command> <image> [args]

Commands
  info    <img>                          size
  crops   <img> <outdir> [scale]         zoomed crops: grid of 3x2 tiles, for visual inspection
  crop    <img> <out.png> x0 y0 x1 y1 scale
  edges   <img> [dark_threshold] [step]  left/right edge of the dark window per row,
                                         top/bottom edge per column  -> slanted window geometry
  bbox    <img> x0 y0 x1 y1 <mask>       tight bbox of pixels matching a mask inside a box
  colors  <img> x,y [x,y ...]            hex colours at points
  line    <img> h|v <fixed> <from> <to> [step]   hex colours along a horizontal/vertical line
  runs    <img> h|v <fixed> <from> <to> [min_sat]  runs of saturated pixels (card borders)
  bggrid  <img> <cell> <poly_json>       average colour per cell, ignoring covered polygons,
                                         holes filled by diffusion -> hex rows for a blurred backdrop

Masks for `bbox`: white, dark, gray, gold, lime, red, green, pink, blue, sat, or
  "rgb:R,G,B,tol"  (euclidean-ish per channel tolerance).
"""
import json
import math
import sys
from PIL import Image

MASKS = {
    "white": lambda p: min(p) > 232,
    "dark": lambda p: max(p) < 60,
    "gray": lambda p: abs(p[0] - p[1]) < 8 and abs(p[1] - p[2]) < 8 and 140 < p[0] < 190,
    "gold": lambda p: p[0] > 235 and 165 < p[1] < 230 and p[2] < 90,
    "lime": lambda p: p[1] > 215 and p[0] < 190 and p[2] < 90,
    "red": lambda p: p[0] > 190 and p[1] < 60 and p[2] < 60,
    "green": lambda p: p[1] > 170 and p[0] < 120 and p[2] < 60,
    "pink": lambda p: p[0] > 230 and p[2] > 200 and p[1] < 190,
    "blue": lambda p: p[2] > 190 and p[0] < 80 and 90 < p[1] < 190,
    "sat": lambda p: max(p) - min(p) > 90,
}


def load(path):
    return Image.open(path).convert("RGB")


def hx(p):
    return "#%02x%02x%02x" % p


def mask_fn(spec):
    if spec.startswith("rgb:"):
        r, g, b, tol = [int(v) for v in spec[4:].split(",")]
        return lambda p: abs(p[0] - r) <= tol and abs(p[1] - g) <= tol and abs(p[2] - b) <= tol
    return MASKS[spec]


def cmd_info(im):
    print(im.size)


def cmd_crops(im, outdir, scale=2):
    import os
    os.makedirs(outdir, exist_ok=True)
    W, H = im.size
    tw, th = math.ceil(W / 3), math.ceil(H / 2)
    for r in range(2):
        for c in range(3):
            box = (c * tw, r * th, min(W, (c + 1) * tw), min(H, (r + 1) * th))
            t = im.crop(box)
            t = t.resize((t.width * scale, t.height * scale), Image.LANCZOS)
            t.save(f"{outdir}/tile_r{r}c{c}.png")
            print(f"tile_r{r}c{c}.png  box={box}")


def cmd_crop(im, out, x0, y0, x1, y1, scale):
    t = im.crop((x0, y0, x1, y1))
    t.resize((t.width * scale, t.height * scale), Image.LANCZOS).save(out)


def cmd_edges(im, thr=75, step=20):
    px = im.load()
    W, H = im.size
    dark = lambda p: p[0] < thr and p[1] < thr and p[2] < thr
    print("row  left_edge  right_edge   (first dark pixel scanning inward)")
    for y in range(0, H, step):
        l = next((x for x in range(0, W) if dark(px[x, y])), None)
        r = next((x for x in range(W - 1, -1, -1) if dark(px[x, y])), None)
        print(y, l, r)
    print("col  top_edge  bottom_edge")
    for x in range(0, W, step * 3):
        ys = [y for y in range(H) if dark(px[x, y])]
        print(x, (min(ys), max(ys)) if ys else None)
    print("Fit lines: slope = dx/dy per side; corners = line intersections with the top/bottom y.")


def cmd_bbox(im, x0, y0, x1, y1, mask):
    px = im.load()
    f = mask_fn(mask)
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if f(px[x, y]):
                xs.append(x)
                ys.append(y)
    print((min(xs), min(ys), max(xs), max(ys)) if xs else None)


def cmd_colors(im, pts):
    px = im.load()
    for p in pts:
        x, y = [int(v) for v in p.split(",")]
        print(p, hx(px[x, y]))


def cmd_line(im, axis, fixed, a, b, step=4):
    px = im.load()
    for t in range(a, b, step):
        p = px[t, fixed] if axis == "h" else px[fixed, t]
        print(t, hx(p))


def cmd_runs(im, axis, fixed, a, b, min_sat=90):
    px = im.load()
    pts = [t for t in range(a, b) if max(px[t, fixed] if axis == "h" else px[fixed, t]) - min(px[t, fixed] if axis == "h" else px[fixed, t]) > min_sat]
    runs, s, prev = [], None, None
    for t in pts:
        if s is None:
            s = t
        elif t - prev > 3:
            runs.append((s, prev))
            s = t
        prev = t
    if s is not None:
        runs.append((s, prev))
    print(runs)


def _inpoly(x, y, poly):
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def cmd_bggrid(im, cell, polys):
    """polys: JSON list of polygons (list of [x,y]) and/or {"rect":[x0,y0,x1,y1]} / {"circle":[cx,cy,r]}."""
    px = im.load()
    W, H = im.size
    shapes = json.loads(polys)

    def covered(x, y):
        for s in shapes:
            if isinstance(s, list) and _inpoly(x, y, s):
                return True
            if isinstance(s, dict):
                if "rect" in s and s["rect"][0] <= x <= s["rect"][2] and s["rect"][1] <= y <= s["rect"][3]:
                    return True
                if "circle" in s and (x - s["circle"][0]) ** 2 + (y - s["circle"][1]) ** 2 <= s["circle"][2] ** 2:
                    return True
        return False

    cols, rows = math.ceil(W / cell), math.ceil(H / cell)
    grid = [[None] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            rs = gs = bs = n = 0
            for y in range(r * cell, min(H, (r + 1) * cell), 3):
                for x in range(c * cell, min(W, (c + 1) * cell), 3):
                    if not covered(x, y):
                        p = px[x, y]
                        rs += p[0]; gs += p[1]; bs += p[2]; n += 1
            if n > 40:
                grid[r][c] = (rs // n, gs // n, bs // n)
    for _ in range(40):  # diffuse known colours into covered cells
        new = [row[:] for row in grid]
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] is None:
                    nb = [grid[rr][cc] for rr, cc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1))
                          if 0 <= rr < rows and 0 <= cc < cols and grid[rr][cc]]
                    if nb:
                        new[r][c] = tuple(sum(v[i] for v in nb) // len(nb) for i in range(3))
        grid = new
    print(json.dumps(["".join(("%02x%02x%02x" % g) if g else "808080" for g in row) for row in grid]))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    cmd, path = argv[1], argv[2]
    a = argv[3:]
    im = load(path)
    if cmd == "info": cmd_info(im)
    elif cmd == "crops": cmd_crops(im, a[0], int(a[1]) if len(a) > 1 else 2)
    elif cmd == "crop": cmd_crop(im, a[0], *[int(v) for v in a[1:5]], int(a[5]))
    elif cmd == "edges": cmd_edges(im, int(a[0]) if a else 75, int(a[1]) if len(a) > 1 else 20)
    elif cmd == "bbox": cmd_bbox(im, *[int(v) for v in a[:4]], a[4])
    elif cmd == "colors": cmd_colors(im, a)
    elif cmd == "line": cmd_line(im, a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4]) if len(a) > 4 else 4)
    elif cmd == "runs": cmd_runs(im, a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4]) if len(a) > 4 else 90)
    elif cmd == "bggrid": cmd_bggrid(im, int(a[0]), a[1])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
