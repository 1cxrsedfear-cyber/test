// Paste at the top of a use_figma script (plain JS, top-level await allowed).
// Fonts must be loaded first: await figma.loadFontAsync({family:"Fredoka One",style:"Regular"}) etc.

const hex = h => [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];
const S = h => { const c = hex(h); return { type: "SOLID", color: { r: c[0], g: c[1], b: c[2] } }; };
// vertical=true: top->bottom, false: left->right. stops: [[pos,"#hex",alpha?],...]
const G = (stops, vertical = true) => ({ type: "GRADIENT_LINEAR",
  gradientTransform: vertical ? [[0, 1, 0], [-1, 0, 1]] : [[1, 0, 0], [0, 1, 0]],
  gradientStops: stops.map(([p, h, a = 1]) => { const c = hex(h); return { position: p, color: { r: c[0], g: c[1], b: c[2], a } }; }) });

const outline = (t, w, col) => { try { t.strokes = [S(col)]; t.strokeWeight = w; t.strokeAlign = "OUTSIDE"; t.strokeJoin = "ROUND"; } catch (e) {} };
const mkT = (str, fam, style, size, fill, name) => { const t = figma.createText(); t.fontName = { family: fam, style }; t.characters = str; t.fontSize = size; t.fills = [fill]; t.name = name; return t; };
const R = (o) => { const r = figma.createRectangle(); r.name = o.name || "rect"; r.resize(o.w, o.h); r.x = o.x; r.y = o.y; r.cornerRadius = o.r || 0; r.fills = o.fill ? [o.fill] : [];
  if (o.stroke) { r.strokes = [S(o.stroke)]; r.strokeWeight = o.sw || 2; r.strokeAlign = o.align || "INSIDE"; } return r; };
const E = (name, x, y, w, h, fill) => { const e = figma.createEllipse(); e.name = name; e.resize(w, h); e.x = x; e.y = y; e.fills = fill ? [fill] : []; return e; };
const svg = (w, h, inner, vb) => `<svg width="${w}" height="${h}" viewBox="${vb || `0 0 ${w} ${h}`}" xmlns="http://www.w3.org/2000/svg">${inner}</svg>`;
const fromSvg = (s, name) => { const n = figma.createNodeFromSvg(s); n.name = name; return n; };
const blur = (n, rad) => { try { n.effects = [{ type: "LAYER_BLUR", radius: rad, visible: true, blurType: "NORMAL" }]; } catch (e) {} };
const glow = (c, a, rad, spread = 0) => { const k = hex(c); return { type: "DROP_SHADOW", color: { r: k[0], g: k[1], b: k[2], a }, offset: { x: 0, y: 0 }, radius: rad, spread, visible: true, blendMode: "NORMAL" }; };

// ---- glyph-box helpers (call BEFORE adding strokes) ----
// rb: render bounds of node relative to `host` (a top-level frame/component/instance)
const rb = (t, host) => { const b = t.absoluteRenderBounds, h = host.absoluteBoundingBox; return { x: b.x - h.x, y: b.y - h.y, w: b.width, h: b.height }; };
const fitW = (t, host, w) => { t.fontSize = 40; let b = rb(t, host); t.fontSize = 40 * w / b.w; b = rb(t, host); t.fontSize = t.fontSize * w / b.w; };
const fitH = (t, host, h) => { t.fontSize = 40; let b = rb(t, host); t.fontSize = 40 * h / b.h; b = rb(t, host); t.fontSize = t.fontSize * h / b.h; };
const center = (t, host, cx, cy) => { const b = rb(t, host); t.x += cx - (b.x + b.w / 2); t.y += cy - (b.y + b.h / 2); };

// ---- free space on the page ----
// let maxX = 0; for (const c of figma.currentPage.children) maxX = Math.max(maxX, c.x + c.width); const ox = maxX + 200;

// ---- blurred backdrop from a sampled colour grid (see game-ui-reference-measure `bggrid`) ----
// rows = array of strings, each cell = 6 hex chars. 60px cells; extend edge cells by 1 so blur has no transparent rim.
// const bgf = figma.createFrame(); bgf.fills = []; bgf.clipsContent = false; root.appendChild(bgf);
// for (let r=-1;r<=ROWS;r++) for (let c=-1;c<=COLS;c++) { const rr=Math.min(ROWS-1,Math.max(0,r)), cc=Math.min(COLS-1,Math.max(0,c));
//   bgf.appendChild(R({name:"cell",x:c*60-1,y:r*60-1,w:62,h:62,fill:S("#"+BG[rr].slice(cc*6,cc*6+6))})); }
// blur(bgf, 34);
