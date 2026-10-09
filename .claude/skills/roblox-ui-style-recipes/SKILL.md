---
name: roblox-ui-style-recipes
description: Recipes, fonts, palettes and Figma Plugin-API snippets for the look of popular Roblox game UIs (anime tower-defence collections, shops, inventories, HUD icon buttons) and the dark ink-stamp survival style. Use when building game UI components in Figma (outlined text, bevelled gradient buttons, rarity-glow cards, slanted windows, check marks, close buttons, tabs, currency chips, bars).
---

# Roblox-style UI recipes (for use with figma-game-ui)

Two house styles seen so far. Identify which one the reference is before building.

## A. "Chunky Roblox" (anime TD / simulator games)
- **Fonts**: titles/buttons/labels = `Fredoka One` (Regular, Roblox "FredokaOne"); numbers,
  prices, names, counters = `Montserrat` ExtraBold/Bold. Both exist in Figma by default.
- **Outlined text**: white fill + OUTSIDE stroke, 2-3.5px (title/buttons 3-3.5, small
  labels 1.8-2.4). Stroke colour is *tinted*, not always black: title `#2a1405`, green button
  `#063300`, pink button `#4a174a`, red button `#3a0505`, price `#1d0a00`.
- **Gold price text**: gradient `#f4d746 → #f9ba19` + dark stroke. **Level text**: horizontal
  gradient `#f2ffa8 → #7dffc2`, stroke black 2.2.
- **Window**: black polygon outline + near-black body `#080808` + panel `#111`; faint
  diagonal stripes `#151515` (22px wide, 45° "/", pitch ~90). Header = trapezoid leaning "\"
  with horizontal gradient `#ff8511 → #ffd60e` (flat orange for the first ~37 %), +10 % white
  overlay toward the bottom, black outline 6-8px.
- **Gradient buttons** (green `#4dfa01→#02b301`, red `#fa0000→#af0000`, pink `#ffb0f6→#fb39f3`,
  filter `#58f800→#3aa803`): 2-3px dark outline (INSIDE), 1-2px lighter highlight line on top.
- **Search bar**: outer `#fcb426` with `#4c2a00` 2.5px outline, inner field darker
  `#e59c2c→#e4a61c` (darker than the bar, not lighter).
- **Close button**: circle r≈42 vertical gradient `#ff2a2c→#a90204`, 2px `#4a0000` edge, faint
  inner ring (white 14 % opacity), top gloss ellipse, white X (`#f3f3f3`) with `#4a0a0a`
  outline (svg path, round caps, 11.5px over 16px). **No white ring.**
- **Rarity/colour borders (4px INSIDE + glow)**: red `#fb211f`, lime `#b6fa34` (glow `#fff000`),
  violet `#6a1cff`, yellow `#ffcd1f`, blue `#1a6fe8`, purple `#7a05f0`, sky `#1a9ffa`.
  Glow = DROP_SHADOW 0,0 radius 9 spread 1 alpha .55. Card fill `#18151a → #0b0b0d`.
- **Cards**: 122×120, radius 8, pitch 133×134. Level top-left (16,12). Badge icon (crown, skull
  outline, sparkle) at (≈9,38). Price right edge at x=113, name right-aligned at x=112,
  vertically centred at y=107.5 (1-2 lines). Big names ≈17.4px, small ≈11.1px (autoscaled).
- **Check mark**: 3D stroke path (face `#1cf03a`, extrusion `#139a37` offset 4px down, outline
  `#0b3d12`), miter joins, butt caps; a second **blue** one (`#34aaf0/#1a6fb5`) 13-14px lower
  for "owned+equipped" cards. Sits top-right, overlapping the card edge by ~6px.
- **List fade**: last 35px of the scroll panel fades to the panel colour (gradient 0→.92).
- **Backdrop**: blurred game screenshot → 60px colour grid + layer blur 34.

## B. Dark ink-stamp survival HUD
- Fonts: `EB Garamond` Medium (labels/titles), Regular (small). White `#F4F4F4`.
- Slots: near-black `#0b0b0b` rough-edged polygons (jittered edges ±1.6-3px, step 4-8px) over a
  `#2c2c2c` fringe; thin inner outline `#303030`; chalk wear specks (short white lines, 30 %).
- Selected = rough white ring (`fill-rule="evenodd"` path), 6px gap. Tooltip = arrow-shaped
  rough polygon with serif label. Icons = white woodcut polygons with black cuts.
- Needs a seeded PRNG (mulberry32) so edges are reproducible.

## C. Icon buttons with a key badge (e.g. "Units" + K)
- Canvas ≈104×107 on a dark game backdrop (navy→purple, neon streak, neighbour icon sliver).
- Button 80×80: gold frame 5px (`#fff000→#ffc800→#e8981a`, gold glow), 1px black line, face
  gradient `#130c00→#4a2c08`. Flat star (no stroke) `#ffee00→#fdb300`, cornerRadius 5, 52×49.
- Label Fredoka white→`#c6cace` + `#161616` 2.6px stroke. Key badge = **black letter with white
  3px outline**, no plate.

## Snippets
Outline text, gradient fill on text, fit-to-width, glow, svg check/funnel/crown/skull: see
`../figma-game-ui/reference/helpers.js` and the svg strings below.

```js
// 3D check (face, side, outline) — 46x38 canvas
const mkCheck = (face, side, line) => svg(46, 38,
  `<path d="M6 14 L16 24 L38 4" transform="translate(0,3)" fill="none" stroke="${line}" stroke-width="14" stroke-linejoin="miter" stroke-linecap="butt"/>` +
  `<path d="M6 14 L16 24 L38 4" transform="translate(0,4)" fill="none" stroke="${side}" stroke-width="10" stroke-linejoin="miter" stroke-linecap="butt"/>` +
  `<path d="M6 14 L16 24 L38 4" fill="none" stroke="${face}" stroke-width="10" stroke-linejoin="miter" stroke-linecap="butt"/>`);
// funnel (filter) 28x26
svg(28, 26, '<polygon points="0,0 28,0 17.5,13 17.5,22.5 13.5,25.5 10.5,24 10.5,13" fill="#000"/>')
// slanted window pieces: draw as svg <polygon> with stroke-linejoin="round"; place with the viewBox offset trick:
// svg(w, h, inner, "x y w h") placed at (x, y) keeps absolute coordinates identical to the reference.
```

## Anti-patterns that were rejected
- Light-grey window body (it is near-black), purple icon backdrop for a dark-navy scene,
  white ring on the close button, white plate behind the key letter, check marks half the
  real size, one-weight text outlines, Inter anywhere, "approximately" placed elements.
