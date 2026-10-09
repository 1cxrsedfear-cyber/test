---
name: figma-game-ui
description: Build or recreate game UI (Roblox-style HUDs, menus, shops, inventories, collection windows, icon buttons) in Figma through the Figma MCP so it matches a reference image pixel-for-pixel. Use whenever the user asks for a game interface, HUD, "UI like in <game>/<mode>", or gives a screenshot of a game UI to copy. Always combine with game-ui-reference-measure (measure first) and roblox-ui-style-recipes (components).
---

# Figma game UI — workflow

Goal: the result must look like the reference, not "inspired by" it. Eyeballing failed
repeatedly; **measuring** the reference and then building from numbers is what worked.

## Prerequisites (do these once per session)
1. `mcp__Figma__whoami` → get `planKey`. Seat can be *View* and `use_figma` still works.
2. Read the MCP skills **before** the first call, via `ReadMcpResourceTool(server=Figma)`:
   `skill://figma/figma-use/SKILL.md`, `skill://figma/figma-generate-design/SKILL.md`,
   `skill://figma/figma-create-new-file/SKILL.md` (only when creating a file).
   Pass `skillNames: "resource:figma-use,resource:figma-generate-design"` on every `use_figma`.
3. Budget: the Starter plan has a hard **tool-call limit**. Plan for ~8-12 `use_figma`
   calls per UI. Batch aggressively (one call = backdrop + window + cards), and avoid
   cosmetic one-line follow-up calls — fold them into the next real change.

## Workflow
1. **Look at the reference** with `Read` on the image file. Zoom crops (PIL, 2x-6x) of
   header, one card, close button, text. Name every layer you see (see checklist below).
2. **Measure** (skill `game-ui-reference-measure`): silhouette edges, element bboxes,
   sampled colors, text glyph bboxes, backdrop color grid. Write the numbers down.
3. **Pick fonts** (see roblox-ui-style-recipes). Never default to Inter for game UI.
4. **Build in one big `use_figma` call** from `reference/helpers.js` + measured numbers.
   Page-level origin: `ox = max(child.x+child.width) + 200` so nothing overlaps.
5. **Verify numerically**: `node.absoluteRenderBounds` vs the reference bbox (return both).
   Then one inline `await root.screenshot({scale:1})` and compare with the reference by eye.
6. Fix only what differs, in as few calls as possible.

## Layer checklist for a game window
backdrop (blurred) · window silhouette (slanted polygons) · header bar + title · header
icons · search/filter controls · sub-header row (counters, tabs, buttons) · inner panel ·
grid of cards (component) · overlays (bottom fade, scrollbar) · close button · bottom CTA.
Cards: border colour per rarity, glow, level text, icon badge, check marks, price, name.

## Hard-won gotchas (Plugin API through MCP)
- A failed `use_figma` call **rolls back atomically** — nothing is created. Safe to retry
  with a fixed script; delete earlier attempts by id at the top of the script.
- `figma.createFrame()/createComponent()` default to a **white fill** → set `fills = []`.
- Children of an **instance can't be moved/appended** (`relative-transform` error). Put
  everything that varies (e.g. a small name vs. a big name, 3 level icons, 2 check marks)
  into the component as separate layers and toggle `.visible` per instance.
- Hidden layers are **skipped by `instance.findOne`**. Either look up all layers first and
  toggle visibility afterwards, or set `figma.skipInvisibleInstanceChildren = false`.
- Text: load the font first; `t.name = ...` after setting characters; add **strokes last**
  (`strokeAlign="OUTSIDE"`, `strokeJoin="ROUND"`) so `absoluteRenderBounds` is the glyph box.
- Fitting text to a measured width: set size 40 → read `absoluteRenderBounds.width` →
  scale size by `target/width` → repeat once (helpers.js `fitW`). Position by glyph box
  centre (`center`), never by the text node's x/y.
- Right-aligned labels in instances: fixed-width box + `textAlignHorizontal="RIGHT"`,
  and `textAlignVertical="CENTER"` in a fixed-height box when the label can wrap 1-2 lines.
- Gradients: vertical = `[[0,1,0],[-1,0,1]]`, horizontal = identity `[[1,0,0],[0,1,0]]`.
  Gradient stops need `a`; solid paints take `{r,g,b}` only (opacity on the paint).
- `createNodeFromSvg` is the reliable way to get slanted polygons, checks, funnels, crowns,
  skulls: give `width/height` + `viewBox`; `linearGradient` in `<defs>` works; use
  `stroke-linejoin="round"` for outlines. The returned frame scales its contents on `resize`.
- Layer blur: `{type:"LAYER_BLUR", radius, visible:true, blurType:"NORMAL"}` (wrap in try).
- Glow = `DROP_SHADOW` with offset 0,0 and the border colour at alpha .5-.7.
- `figma.screenshot` cannot be downloaded from the sandbox (proxy blocks figma.com);
  the **inline** `node.screenshot({scale})` image is the only visual feedback.
- `get_screenshot` returns a URL only — don't try to curl it.

## Output
Reply with: the Figma link, what was matched (with the measured numbers), and an honest
list of what could not be verified or differs. Never claim pixel-perfect without numbers.
