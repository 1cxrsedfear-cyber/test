// "Steal a Lucky Block" — HUD + Lucky Block Shop, for the Figma MCP `use_figma` tool.
// Body of the call (top-level await / return allowed). Pass skillNames:
//   "resource:figma-use,resource:figma-generate-design"
// Builds two 1280x720 frames to the right of existing page content:
//   "Steal a Lucky Block — HUD" and "Lucky Block Shop" (+ component "Shop/BlockCard").
// Style: chunky Roblox (see .claude/skills/roblox-ui-style-recipes). No reference image was given,
// so proportions come from the recipes; re-measure against a screenshot when one exists.

figma.skipInvisibleInstanceChildren = false;
await figma.loadFontAsync({ family: "Fredoka One", style: "Regular" });
await figma.loadFontAsync({ family: "Montserrat", style: "Bold" });
await figma.loadFontAsync({ family: "Montserrat", style: "ExtraBold" });

// ---------------- helpers (figma-game-ui/reference/helpers.js) ----------------
const hex = h => [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];
const S = h => { const c = hex(h); return { type: "SOLID", color: { r: c[0], g: c[1], b: c[2] } }; };
const G = (stops, vertical = true) => ({ type: "GRADIENT_LINEAR",
  gradientTransform: vertical ? [[0, 1, 0], [-1, 0, 1]] : [[1, 0, 0], [0, 1, 0]],
  gradientStops: stops.map(([p, h, a = 1]) => { const c = hex(h); return { position: p, color: { r: c[0], g: c[1], b: c[2], a } }; }) });
const outline = (t, w, col) => { try { t.strokes = [S(col)]; t.strokeWeight = w; t.strokeAlign = "OUTSIDE"; t.strokeJoin = "ROUND"; } catch (e) {} };
const FF = "Fredoka One", MB = "Montserrat";
const mkT = (str, fam, style, size, fill, name) => { const t = figma.createText(); t.fontName = { family: fam, style }; t.characters = str; t.fontSize = size; t.fills = [fill]; t.name = name; return t; };
const R = (o) => { const r = figma.createRectangle(); r.name = o.name || "rect"; r.resize(o.w, o.h); r.x = o.x; r.y = o.y; r.cornerRadius = o.r || 0; r.fills = o.fill ? [o.fill] : [];
  if (o.stroke) { r.strokes = [S(o.stroke)]; r.strokeWeight = o.sw || 2; r.strokeAlign = o.align || "INSIDE"; } return r; };
const E = (name, x, y, w, h, fill) => { const e = figma.createEllipse(); e.name = name; e.resize(w, h); e.x = x; e.y = y; e.fills = fill ? [fill] : []; return e; };
const svg = (w, h, inner, vb) => `<svg width="${w}" height="${h}" viewBox="${vb || `0 0 ${w} ${h}`}" xmlns="http://www.w3.org/2000/svg">${inner}</svg>`;
const fromSvg = (s, name) => { const n = figma.createNodeFromSvg(s); n.name = name; return n; };
const blur = (n, rad) => { try { n.effects = [{ type: "LAYER_BLUR", radius: rad, visible: true, blurType: "NORMAL" }]; } catch (e) {} };
const glow = (c, a, rad, spread = 0) => { const k = hex(c); return { type: "DROP_SHADOW", color: { r: k[0], g: k[1], b: k[2], a }, offset: { x: 0, y: 0 }, radius: rad, spread, visible: true, blendMode: "NORMAL" }; };
const rb = (t, host) => { const b = t.absoluteRenderBounds, h = host.absoluteBoundingBox; return { x: b.x - h.x, y: b.y - h.y, w: b.width, h: b.height }; };
const center = (t, host, cx, cy) => { const b = rb(t, host); t.x += cx - (b.x + b.w / 2); t.y += cy - (b.y + b.h / 2); };
// outlined label centred on (cx,cy) inside `host`
const label = (parent, host, str, fam, style, size, fill, cx, cy, sw, sc, name) => {
  const t = mkT(str, fam, style, size, fill, name || str); parent.appendChild(t); center(t, host, cx, cy); if (sw) outline(t, sw, sc); return t; };

let maxX = 0; for (const c of figma.currentPage.children) maxX = Math.max(maxX, c.x + c.width);
const ox = maxX + 200;
const made = [];

// ---------------- lucky block builder ----------------
const RAR = {
  LUCKY:     { front: "#ffc21a", top: "#ffe45a", right: "#d98a0a", edge: "#ffcd1f" },
  RARE:      { front: "#2f8cff", top: "#6cb4ff", right: "#1757c2", edge: "#2a9ff0" },
  EPIC:      { front: "#9a4dff", top: "#c493ff", right: "#6422c4", edge: "#8a2bff" },
  LEGENDARY: { front: "#ff6a1a", top: "#ff9a5a", right: "#c23c08", edge: "#ff7a1a" },
  MYTHIC:    { front: "#ff4fa8", top: "#ff8fcb", right: "#c01f74", edge: "#ff4fa8" },
  DIVINE:    { front: "#fff27a", top: "#ffffff", right: "#e0b800", edge: "#fff000" },
  SECRET:    { front: "#262630", top: "#4b4b5c", right: "#0b0b10", edge: "#a0a0b8" },
  RAINBOW:   { front: "#3dff9a", top: "#9affd0", right: "#14b36a", edge: "#19e6ff" },
};
const lucky = (size, c, name) => {
  const wrap = figma.createFrame(); wrap.name = name; wrap.resize(size, size); wrap.fills = []; wrap.clipsContent = false;
  const cube = fromSvg(svg(100, 100,
    `<polygon points="8,34 30,12 86,12 64,34" fill="${c.top}" stroke="#1a1000" stroke-width="5" stroke-linejoin="round"/>` +
    `<polygon points="64,34 86,12 86,68 64,90" fill="${c.right}" stroke="#1a1000" stroke-width="5" stroke-linejoin="round"/>` +
    `<polygon points="8,34 64,34 64,90 8,90" fill="${c.front}" stroke="#1a1000" stroke-width="5" stroke-linejoin="round"/>` +
    `<polygon points="14,40 58,40 58,84 14,84" fill="none" stroke="#ffffff" stroke-opacity="0.35" stroke-width="3"/>`).replace('width="100" height="100"', `width="${size}" height="${size}"`), "Cube");
  ["face-top", "face-right", "face-front", "bevel"].forEach((n, i) => { if (cube.children[i]) cube.children[i].name = n; });
  wrap.appendChild(cube); cube.x = 0; cube.y = 0;
  const q = mkT("?", FF, "Regular", 44 * size / 100, S("#ffffff"), "Q"); wrap.appendChild(q);
  center(q, wrap, 36 * size / 100, 63 * size / 100); outline(q, 4 * size / 100 + 0.5, "#6b3300");
  return wrap;
};

// ---------------- scene (sky, hills, grass, platform) ----------------
const scene = (root, W, H, blurAmt) => {
  const g = figma.createFrame(); g.name = "Scene"; g.resize(W + 160, H + 160); g.x = -80; g.y = -80; g.fills = []; g.clipsContent = false; root.appendChild(g);
  const sky = R({ name: "Sky", x: 0, y: 0, w: W + 160, h: H + 160, fill: G([[0, "#3aa6ff"], [0.5, "#9fe0ff"], [0.64, "#d6f6ff"]]) }); g.appendChild(sky);
  for (const [x, y, w, h, o] of [[120, 130, 300, 90, 0.95], [620, 60, 380, 110, 0.9], [1060, 150, 300, 90, 0.9], [-20, 250, 260, 70, 0.8]]) { const c = E("Cloud", x, y, w, h, S("#ffffff")); c.opacity = o; blur(c, 6); g.appendChild(c); }
  const h1 = E("Hill1", -120, 420, 760, 300, S("#59d65a")); const h2 = E("Hill2", 520, 400, 900, 340, S("#46c64a")); g.appendChild(h1); g.appendChild(h2);
  const ground = R({ name: "Ground", x: 0, y: 470, w: W + 160, h: H + 160 - 470, fill: G([[0, "#5bd64d"], [1, "#2f9e3a"]]) }); g.appendChild(ground);
  const stripes = [0, 1, 2, 3, 4, 5].map(i => R({ name: "GrassStripe", x: 0, y: 510 + i * 38, w: W + 160, h: 18, fill: S("#ffffff") })); stripes.forEach(s => { s.opacity = 0.05; g.appendChild(s); });
  const plat = E("Platform", W / 2 + 80 - 330, 500, 660, 170, S("#d9ccaa")); plat.strokes = [S("#8d7a4a")]; plat.strokeWeight = 5; plat.strokeAlign = "INSIDE"; g.appendChild(plat);
  const plat2 = E("PlatformInner", W / 2 + 80 - 270, 526, 540, 118, S("#eadfc2")); g.appendChild(plat2);
  if (blurAmt) blur(g, blurAmt);
  return g;
};

// ---------------- icon svgs for side buttons ----------------
const ICON = {
  shop: '<path d="M7 14 L29 14 L32 35 L4 35 Z" fill="#ffd21f" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/><path d="M12 14 C12 4 24 4 24 14" fill="none" stroke="#000" stroke-width="3" stroke-linecap="round"/>',
  index: '<rect x="6" y="5" width="24" height="29" rx="3" fill="#ff5a5a" stroke="#000" stroke-width="2.6"/><rect x="10" y="9" width="16" height="3" fill="#fff"/><rect x="10" y="16" width="16" height="3" fill="#fff"/><rect x="10" y="23" width="10" height="3" fill="#fff"/>',
  rebirth: '<polygon points="18,3 32,18 24,18 24,26 12,26 12,18 4,18" fill="#47e84f" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/><rect x="12" y="29" width="12" height="5" rx="1" fill="#47e84f" stroke="#000" stroke-width="2.4"/>',
  gift: '<rect x="5" y="15" width="26" height="19" rx="2" fill="#ff4fd8" stroke="#000" stroke-width="2.6"/><rect x="3" y="9" width="30" height="8" rx="2" fill="#ff7be5" stroke="#000" stroke-width="2.6"/><rect x="16" y="9" width="4" height="25" fill="#ffd21f"/>',
};
const iconBtn = (parent, x, y, labelStr, keyStr, icon) => {
  const f = figma.createFrame(); f.name = "Btn/" + labelStr; f.resize(92, 92); f.x = x; f.y = y; f.fills = []; f.clipsContent = false; parent.appendChild(f);
  const gold = R({ name: "GoldFrame", x: 0, y: 0, w: 92, h: 92, r: 8, fill: G([[0, "#fff000"], [0.5, "#ffc800"], [1, "#e8981a"]]) }); gold.effects = [glow("#ffcf00", 0.5, 6)]; f.appendChild(gold);
  f.appendChild(R({ name: "InnerLine", x: 5, y: 5, w: 82, h: 82, r: 4, fill: S("#000000") }));
  f.appendChild(R({ name: "Face", x: 6, y: 6, w: 80, h: 80, r: 3.5, fill: G([[0, "#2c3c96"], [1, "#0c1240"]]) }));
  const ic = fromSvg(svg(36, 36, icon).replace('width="36" height="36"', 'width="44" height="44"'), "Icon"); f.appendChild(ic); ic.x = 24; ic.y = 12;
  label(f, f, labelStr, FF, "Regular", 18, S("#ffffff"), 46, 70, 3, "#0a0f33", "Label");
  const k = mkT(keyStr, FF, "Regular", 22, S("#0a0a0a"), "Key"); f.appendChild(k); center(k, f, 80, 6); outline(k, 3, "#ffffff");
  return f;
};

// =====================================================================
//  SCREEN 1 — HUD  (1280 x 720)
// =====================================================================
const hud = figma.createFrame(); hud.name = "Steal a Lucky Block — HUD"; hud.resize(1280, 720); hud.x = ox; hud.y = 0; hud.fills = []; hud.clipsContent = true; made.push(hud.id);
scene(hud, 1280, 720, 0);

// big lucky block on the platform
const shadow = E("BlockShadow", 520, 560, 240, 56, S("#000000")); shadow.opacity = 0.28; blur(shadow, 10); hud.appendChild(shadow);
const big = lucky(230, RAR.LEGENDARY, "Lucky Block (Legendary)"); hud.appendChild(big); big.x = 525; big.y = 335; big.effects = [glow("#ff9a2a", 0.55, 28, 2)];
const spark = (x, y, s, o = 1) => { const n = fromSvg(svg(30, 30, '<polygon points="15,0 19,11 30,15 19,19 15,30 11,19 0,15 11,11" fill="#ffffff"/>').replace('width="30" height="30"', `width="${s}" height="${s}"`), "Sparkle"); hud.appendChild(n); n.x = x; n.y = y; n.opacity = o; n.effects = [glow("#fff6a0", 0.9, 8)]; return n; };
spark(480, 330, 34); spark(790, 300, 26, 0.9); spark(700, 270, 20, 0.8); spark(500, 440, 18, 0.8); spark(805, 430, 30);

// world billboard above the block
const bb = figma.createFrame(); bb.name = "Billboard"; bb.resize(270, 92); bb.x = 505; bb.y = 196; bb.fills = []; bb.clipsContent = false; hud.appendChild(bb);
bb.appendChild(R({ name: "Plate", x: 0, y: 0, w: 270, h: 92, r: 18, fill: G([[0, "#34344a"], [1, "#14141f"]]), stroke: "#000000", sw: 4 }));
bb.appendChild(R({ name: "RarityStrip", x: 4, y: 4, w: 262, h: 8, r: 4, fill: G([[0, "#ff6a1a"], [1, "#ffb21a"]], false) }));
label(bb, bb, "Legendary Lucky Block", FF, "Regular", 21, S("#ffffff"), 135, 38, 3, "#000000", "Name");
label(bb, bb, "$2.5K / sec", MB, "ExtraBold", 19, S("#5cff6a"), 135, 67, 3, "#06300c", "Income");
const tail = fromSvg(svg(30, 18, '<polygon points="0,0 30,0 15,16" fill="#14141f" stroke="#000" stroke-width="3" stroke-linejoin="round"/>'), "Tail"); bb.appendChild(tail); tail.x = 120; tail.y = 88;

// top-center cash pill
const cash = figma.createFrame(); cash.name = "Cash"; cash.resize(280, 60); cash.x = 500; cash.y = 16; cash.fills = []; cash.clipsContent = false; hud.appendChild(cash);
cash.appendChild(R({ name: "Pill", x: 0, y: 0, w: 280, h: 60, r: 30, fill: G([[0, "#30345c"], [1, "#12142c"]]), stroke: "#000000", sw: 4 }));
cash.appendChild(R({ name: "PillHi", x: 14, y: 6, w: 252, h: 3, r: 1.5, fill: S("#ffffff") })).opacity = 0.18;
const coin = E("Coin", 8, 8, 44, 44, G([[0, "#ffe45a"], [1, "#f0a000"]])); coin.strokes = [S("#7a4a00")]; coin.strokeWeight = 3; coin.strokeAlign = "INSIDE"; cash.appendChild(coin);
label(cash, cash, "$", FF, "Regular", 28, S("#8a5200"), 30, 31, 0, "#000000", "CoinGlyph");
label(cash, cash, "1.25M", FF, "Regular", 34, S("#ffffff"), 155, 30, 3.5, "#0a0c22", "Amount");
label(hud, hud, "+$850/s", MB, "ExtraBold", 17, S("#5cff6a"), 640, 92, 3, "#06300c", "Income/s");

// event banner (top-left)
const ev = figma.createFrame(); ev.name = "Event"; ev.resize(292, 62); ev.x = 24; ev.y = 18; ev.fills = []; ev.clipsContent = false; hud.appendChild(ev);
ev.appendChild(R({ name: "Plate", x: 0, y: 0, w: 292, h: 62, r: 16, fill: G([[0, "#ffb61a"], [1, "#ff8511"]]), stroke: "#000000", sw: 4 }));
ev.appendChild(R({ name: "PlateHi", x: 10, y: 6, w: 272, h: 3, r: 1.5, fill: S("#ffffff") })).opacity = 0.35;
const evb = lucky(46, RAR.LUCKY, "Icon"); ev.appendChild(evb); evb.x = 10; evb.y = 8;
label(ev, ev, "LUCKY EVENT", FF, "Regular", 20, S("#ffffff"), 150, 22, 3, "#5a2a00", "Title");
label(ev, ev, "x2 Luck  •  04:59", MB, "ExtraBold", 15, S("#ffffff"), 160, 44, 2.6, "#5a2a00", "Timer");

// top-right pills
const pill = (parent, x, y, w, txt, color) => { const p = R({ name: "Pill", x, y, w, h: 44, r: 22, fill: G([[0, "#30345c"], [1, "#12142c"]]), stroke: "#000000", sw: 4 }); parent.appendChild(p);
  label(parent, parent, txt, FF, "Regular", 21, S(color || "#ffffff"), x + w / 2, y + 22, 3, "#07091c", "PillText"); };
pill(hud, 1000, 20, 256, "Rebirths: 12");
pill(hud, 1000, 74, 256, "Stolen: 7 / 10", "#ffd21f");

// left icon buttons
[["Shop", "E", ICON.shop], ["Index", "I", ICON.index], ["Rebirth", "R", ICON.rebirth], ["Gifts", "G", ICON.gift]].forEach(([l, k, ic], i) => made.push(iconBtn(hud, 24, 112 + i * 104, l, k, ic).id));

// steal prompt + progress
label(hud, hud, "Hold [E] to STEAL", FF, "Regular", 30, S("#ffffff"), 640, 566, 4, "#000000", "Prompt");
hud.appendChild(R({ name: "StealBar/Back", x: 480, y: 592, w: 320, h: 22, r: 11, fill: S("#0c0c14"), stroke: "#000000", sw: 4 }));
hud.appendChild(R({ name: "StealBar/Fill", x: 484, y: 596, w: 200, h: 14, r: 7, fill: G([[0, "#7dff3a"], [1, "#20b82a"]]) }));
hud.appendChild(R({ name: "StealBar/Hi", x: 490, y: 598, w: 188, h: 3, r: 1.5, fill: S("#ffffff") })).opacity = 0.45;

// hotbar
const slots = [["LUCKY", "3"], ["RARE", "1"], ["EPIC", "2"], ["LEGENDARY", "1"], ["MYTHIC", "1"]];
slots.forEach(([rk, cnt], i) => {
  const sel = i === 2, x = 430 + i * 86, y = sel ? 626 : 634;
  const s = figma.createFrame(); s.name = "Slot/" + (i + 1); s.resize(76, 76); s.x = x; s.y = y; s.fills = []; s.clipsContent = false; hud.appendChild(s);
  const body = R({ name: "Body", x: 0, y: 0, w: 76, h: 76, r: 12, fill: G([[0, "#262c55"], [1, "#0e1230"]]), stroke: sel ? "#ffd21f" : "#2f3b7a", sw: sel ? 4 : 3 });
  if (sel) body.effects = [glow("#ffd21f", 0.7, 12, 1)]; s.appendChild(body);
  const b = lucky(54, RAR[rk], "Block"); s.appendChild(b); b.x = 11; b.y = 9;
  label(s, s, String(i + 1), FF, "Regular", 18, S("#ffffff"), 13, 13, 3, "#000000", "Key");
  label(s, s, "x" + cnt, MB, "ExtraBold", 14, S("#ffd21f"), 60, 63, 2.6, "#000000", "Count");
});

// rebirth progress (bottom-left)
const rbf = figma.createFrame(); rbf.name = "RebirthProgress"; rbf.resize(330, 56); rbf.x = 24; rbf.y = 646; rbf.fills = []; rbf.clipsContent = false; hud.appendChild(rbf);
label(rbf, rbf, "REBIRTH 13  —  $1.25M / $5M", MB, "ExtraBold", 14, S("#ffffff"), 165, 9, 2.6, "#000000", "Label");
rbf.appendChild(R({ name: "Back", x: 0, y: 22, w: 330, h: 30, r: 15, fill: S("#0c0c14"), stroke: "#000000", sw: 4 }));
rbf.appendChild(R({ name: "Fill", x: 4, y: 26, w: 90, h: 22, r: 11, fill: G([[0, "#ffe45a"], [1, "#ff9a1a"]]) }));
rbf.appendChild(R({ name: "Hi", x: 10, y: 29, w: 76, h: 3, r: 1.5, fill: S("#ffffff") })).opacity = 0.5;

// lock base button (bottom-right)
const lk = figma.createFrame(); lk.name = "LockBase"; lk.resize(226, 64); lk.x = 1030; lk.y = 636; lk.fills = []; lk.clipsContent = false; hud.appendChild(lk);
lk.appendChild(R({ name: "Btn", x: 0, y: 0, w: 226, h: 64, r: 10, fill: G([[0, "#fa0000"], [1, "#af0000"]]), stroke: "#2b0c0b", sw: 3.5 }));
lk.appendChild(R({ name: "Hi", x: 4, y: 4, w: 218, h: 3, r: 1.5, fill: S("#ff6a6a") }));
const lockIc = fromSvg(svg(30, 34, '<path d="M8 15 V10 C8 3 22 3 22 10 V15" fill="none" stroke="#000" stroke-width="5" stroke-linecap="round"/><path d="M8 15 V10 C8 3 22 3 22 10 V15" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-linecap="round"/><rect x="3" y="15" width="24" height="17" rx="3" fill="#ffd21f" stroke="#000" stroke-width="2.6"/>'), "LockIcon"); lk.appendChild(lockIc); lockIc.x = 14; lockIc.y = 14;
label(lk, lk, "LOCK BASE", FF, "Regular", 24, S("#ffffff"), 132, 26, 3.4, "#3a0505", "Label");
label(lk, lk, "Ready in 23s", MB, "ExtraBold", 13, S("#ffe0e0"), 132, 48, 2.2, "#3a0505", "Sub");

// =====================================================================
//  SCREEN 2 — LUCKY BLOCK SHOP (1280 x 720)
// =====================================================================
const shop = figma.createFrame(); shop.name = "Lucky Block Shop"; shop.resize(1280, 720); shop.x = ox + 1480; shop.y = 0; shop.fills = []; shop.clipsContent = true; made.push(shop.id);
scene(shop, 1280, 720, 22);
const dim = R({ name: "Dim", x: 0, y: 0, w: 1280, h: 720, fill: S("#0a1030") }); dim.opacity = 0.35; shop.appendChild(dim);

// window body + stripes
const stripes = [-5, -4, -3, -2, -1, 0, 1, 2, 3].map(k => { const xc = 760 + 100 * k, a = xc + 25, b = xc - 24; return `<polygon points="${a - 11},124 ${a + 11},124 ${b + 11},172 ${b - 11},172" fill="#151515"/>`; }).join("");
const body = fromSvg(svg(1160, 560, '<polygon points="152,126 1190,126 1158,628 92,644" fill="#080808" stroke="#000" stroke-width="5" stroke-linejoin="round"/>' + stripes, "80 100 1160 560"), "Window/Body");
body.x = 80; body.y = 100; shop.appendChild(body);
const header = fromSvg(svg(1160, 90,
  '<defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff8511"/><stop offset="0.37" stop-color="#ff8511"/><stop offset="1" stop-color="#ffd60e"/></linearGradient>' +
  '<linearGradient id="v" x1="0" y1="0" x2="0" y2="1"><stop offset="0.55" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0.1"/></linearGradient></defs>' +
  '<polygon points="112,50 1170,50 1214,126 138,126" fill="#000"/>' +
  '<polygon points="122,58 1160,58 1200,118 150,118" fill="url(#h)"/><polygon points="122,58 1160,58 1200,118 150,118" fill="url(#v)"/>', "80 40 1160 90"), "Window/Header");
header.x = 80; header.y = 40; shop.appendChild(header);
shop.appendChild(R({ name: "Panel", x: 172, y: 170, w: 968, h: 392, r: 10, fill: S("#111111"), stroke: "#1d1d1d", sw: 2 }));

label(shop, shop, "Lucky Block Shop", FF, "Regular", 44, S("#ffffff"), 372, 86, 4, "#2a1405", "Title");
const chip = (x, w, txt, col, icFill) => { const f = figma.createFrame(); f.name = "Chip"; f.resize(w, 42); f.x = x; f.y = 66; f.fills = []; f.clipsContent = false; shop.appendChild(f);
  f.appendChild(R({ name: "Pill", x: 0, y: 0, w, h: 42, r: 21, fill: G([[0, "#2c2f55"], [1, "#101228"]]), stroke: "#000000", sw: 3.5 }));
  const c = E("Icon", 6, 5, 32, 32, G([[0, icFill[0]], [1, icFill[1]]])); c.strokes = [S("#000000")]; c.strokeWeight = 2.5; c.strokeAlign = "INSIDE"; f.appendChild(c);
  label(f, f, txt, FF, "Regular", 22, S(col), 44 + (w - 44) / 2, 21, 3, "#07091c", "Amount"); };
chip(690, 200, "1.25M", "#ffffff", ["#ffe45a", "#f0a000"]);
chip(910, 190, "R$ 320", "#ffffff", ["#7dffb4", "#14b36a"]);

// sub row
label(shop, shop, "Luck Boost x3  •  04:59", MB, "ExtraBold", 17, S("#e1e1e1"), 330, 150, 0, "#000000", "LuckBoost");
const tabBtn = (x, txt, c1, c2, edge, tcol) => { shop.appendChild(R({ name: "Tab/" + txt, x, y: 134, w: 140, h: 32, r: 6, fill: G([[0, c1], [1, c2]]), stroke: edge, sw: 2.5 }));
  label(shop, shop, txt, FF, "Regular", 18, S("#ffffff"), x + 70, 150, 3, tcol, "TabText/" + txt); };
tabBtn(640, "Blocks", "#4dfa01", "#02b301", "#002900", "#063300");
tabBtn(796, "Boosts", "#ffb0f6", "#fb39f3", "#370136", "#4a174a");
tabBtn(952, "Passes", "#ffb0f6", "#fb39f3", "#370136", "#4a174a");

// ---- card component ----
const card = figma.createComponent(); card.name = "Shop/BlockCard"; card.resize(218, 176); card.cornerRadius = 10; card.clipsContent = false;
card.fills = [G([[0, "#1c1a24"], [1, "#0b0b10"]])]; card.strokes = [S("#ffcd1f")]; card.strokeWeight = 4; card.strokeAlign = "INSIDE"; card.x = ox; card.y = 800; made.push(card.id);
{ const t = mkT("LUCKY", MB, "ExtraBold", 12, S("#ffcd1f"), "Rarity"); card.appendChild(t); t.x = 14; t.y = 10; outline(t, 2, "#000000"); }
const cb = lucky(86, RAR.LUCKY, "Block"); card.appendChild(cb); cb.x = 66; cb.y = 8;
const boxText = (str, fam, style, size, fill, y, h, name, sw, sc) => { const t = mkT(str, fam, style, size, fill, name); card.appendChild(t); t.textAutoResize = "NONE"; t.resize(200, h); t.textAlignHorizontal = "CENTER"; t.textAlignVertical = "CENTER"; t.x = 9; t.y = y; if (sw) outline(t, sw, sc); return t; };
boxText("Lucky Block", FF, "Regular", 21, S("#ffffff"), 94, 28, "Name", 3, "#000000");
boxText("Luck x1", MB, "Bold", 13, S("#b8c0e8"), 120, 18, "Luck", 0);
card.appendChild(R({ name: "BuyBtn", x: 19, y: 141, w: 180, h: 28, r: 9, fill: G([[0, "#4dfa01"], [1, "#02b301"]]), stroke: "#002900", sw: 2.5 }));
boxText("$500", FF, "Regular", 19, S("#ffffff"), 141, 28, "Price", 3, "#063300");

const items = [
  ["LUCKY", "Lucky Block", "Luck x1", "$500", 0], ["RARE", "Rare Block", "Luck x2", "$2.5K", 0], ["EPIC", "Epic Block", "Luck x4", "$12K", 0], ["LEGENDARY", "Legendary Block", "Luck x8", "$75K", 0],
  ["MYTHIC", "Mythic Block", "Luck x16", "$400K", 0], ["DIVINE", "Divine Block", "Luck x32", "$2.5M", 0], ["SECRET", "Secret Block", "Luck x100", "R$ 199", 1], ["RAINBOW", "Rainbow Block", "Luck x250", "R$ 399", 1],
];
const grid = figma.createFrame(); grid.name = "Grid"; grid.resize(968, 392); grid.x = 172; grid.y = 170; grid.fills = []; grid.clipsContent = true; grid.cornerRadius = 10; shop.appendChild(grid);
const cardIds = [];
items.forEach(([rk, nm, luck, price, rbx], i) => {
  const inst = card.createInstance(); inst.name = "Card/" + nm; grid.appendChild(inst);
  inst.x = 12 + (i % 4) * 242; inst.y = 13 + Math.floor(i / 4) * 190;
  const c = RAR[rk];
  inst.strokes = [S(c.edge)]; inst.effects = [glow(c.edge, 0.55, 9, 1)];
  const q = (n) => inst.findOne(x => x.name === n);
  const tag = q("Rarity"), nmN = q("Name"), lu = q("Luck"), pr = q("Price"), buy = q("BuyBtn");
  const ft = q("face-top"), fr = q("face-right"), ff = q("face-front");
  tag.characters = rk; tag.fills = [S(c.edge)]; nmN.characters = nm; lu.characters = luck; pr.characters = price;
  ft.fills = [S(c.top)]; fr.fills = [S(c.right)];
  ff.fills = rk === "RAINBOW" ? [G([[0, "#ff4f4f"], [0.25, "#ffd21f"], [0.5, "#3dff6a"], [0.75, "#2f8cff"], [1, "#b04dff"]])] : [S(c.front)];
  if (rbx) { buy.fills = [G([[0, "#ffb0f6"], [1, "#fb39f3"]])]; buy.strokes = [S("#370136")]; }
  cardIds.push(inst.id);
});
// fade + scrollbar
shop.appendChild(R({ name: "Grid/Fade", x: 172, y: 536, w: 968, h: 26, r: 0, fill: G([[0, "#111111", 0], [1, "#111111", 0.55]]) }));
shop.appendChild(R({ name: "Scrollbar", x: 1128, y: 180, w: 3, h: 70, r: 1.5, fill: S("#c8c8c8") }));

// close
const c0 = E("Close/Base", 1144, 50, 84, 84, G([[0, "#ff2a2c"], [0.55, "#e11416"], [1, "#a90204"]])); c0.strokes = [S("#4a0000")]; c0.strokeWeight = 2.2; c0.strokeAlign = "INSIDE";
const c1 = E("Close/InnerRing", 1154, 60, 64, 64, null); c1.strokes = [S("#ffffff")]; c1.strokeWeight = 1.5; c1.strokeAlign = "INSIDE"; c1.opacity = 0.14;
const c3 = E("Close/Gloss", 1160, 55, 52, 24, G([[0, "#ffffff", 0.3], [1, "#ffffff", 0]]));
const cx = fromSvg(svg(60, 64, '<path d="M18 17 L42 47 M42 17 L18 47" stroke="#4a0a0a" stroke-width="16" stroke-linecap="round"/><path d="M18 17 L42 47 M42 17 L18 47" stroke="#f3f3f3" stroke-width="11.5" stroke-linecap="round"/>'), "Close/X"); cx.x = 1156; cx.y = 60;
for (const n of [c0, c1, c3, cx]) shop.appendChild(n);

// bottom CTA
shop.appendChild(R({ name: "CTA/Button", x: 470, y: 612, w: 340, h: 74, r: 8, fill: G([[0, "#4dfa01"], [1, "#02b301"]]), stroke: "#002900", sw: 3.5 }));
shop.appendChild(R({ name: "CTA/Highlight", x: 476, y: 617, w: 328, h: 3, r: 1.5, fill: S("#c8ff9a") }));
label(shop, shop, "Open x10", FF, "Regular", 34, S("#ffffff"), 640, 640, 4.5, "#063300", "CTA/Label");
label(shop, shop, "R$ 399  •  Luck x2", MB, "ExtraBold", 15, S("#eaffd8"), 640, 670, 2.6, "#063300", "CTA/Sub");

await hud.screenshot({ scale: 1 });
await shop.screenshot({ scale: 1 });
return { hud: hud.id, shop: shop.id, cards: cardIds.length, made };
