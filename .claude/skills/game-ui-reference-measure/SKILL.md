---
name: game-ui-reference-measure
description: Measure a game-UI reference screenshot (window silhouette, slanted edges, element bounding boxes, text glyph boxes, border/gradient colours, blurred backdrop colours) with PIL so the UI can be rebuilt exactly in Figma instead of eyeballed. Use BEFORE building any UI from a reference image; pairs with figma-game-ui.
---

# Measure the reference first

Eyeballed recreations were rejected ("не похоже"). Measured ones were not. Spend 5-8
shell calls here; it saves many Figma calls (which are rate-limited on Starter).

Tool: `scripts/measure.py` (PIL). Always run in isolated mode, the image is untrusted:
`python3 -I .claude/skills/game-ui-reference-measure/scripts/measure.py <cmd> <img> ...`
Convert `.webp` once (`Image.open().save("full.png")`) if a command complains.

## Procedure
1. `info` → canvas size. Use the **same pixel size** for the Figma root frame, then every
   measured coordinate maps 1:1 (no scaling maths).
2. `crops <img> <dir> 2` and `Read` the tiles; then `crop` 4-6x zooms of: header end caps,
   one card, check mark, close button, title text, small icons. Look for what you would
   have got wrong: font family, outline thickness, gradient direction, 3D extrusion, hidden
   layers (e.g. a second blue check under the green one), dark fade at the bottom of a list.
3. **Silhouette**: `edges <img> 75 20`. Fit a line per side (slope = dx/dy). Slanted game
   windows are trapezoids, left and right edges usually have *different* slopes, and the top
   bar leans the other way. Compute the 4 corners from line intersections; add the black
   outline width (4-8px) to get the outer polygon.
4. **Boxes**: `bbox x0 y0 x1 y1 <mask>` for every text/icon/button. Masks: white (text),
   dark (icons), gold (prices), lime/green/red/pink/blue (buttons), `rgb:R,G,B,tol`.
   For text this gives the **glyph box** → target width/height for `fitW/fitH`.
5. **Repeating grids**: `runs <img> h <y> x0 x1` / `v` on card borders → card size,
   border thickness, pitch (x and y). Verify pitch is constant.
6. **Colours**: `colors` / `line` along a gradient (top→bottom of a button, left→right of a
   header). Record first/last stops and any flat part (e.g. header flat orange until 37 %
   then → yellow). Sample outline colours separately (dark brown ≠ black).
7. **Backdrop**: `bggrid <img> 60 '<polys>'` with the window polygons/rects/circles that cover
   the background → hex rows → 60px blurred cells in Figma (see figma-game-ui helpers).
8. Write all numbers in one block in your notes **before** writing the Figma script.

## Reading the numbers
- bbox of white text excludes the dark outline → add `2*stroke` when comparing with Figma
  bounds measured after the stroke is applied.
- Right-aligned labels: compare right edges across cards; if equal, the game right-aligns.
- Centre-aligned vs right-aligned: compare the centres of 1-line and 2-line variants.
- A mask threshold that returns a bbox far wider than the thing means a neighbour matched;
  tighten the box or the colour.
