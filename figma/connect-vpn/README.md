# Connect VPN — mobile UI (Figma)

Figma file: https://www.figma.com/design/iTqOpRhVugz6jh07ra7giM

Five screens rebuilt from the reference mock-up as editable layers (uniform scale ×1.75 of the reference; each
`Screen / …` frame is 390 × 1122 px). Page `Connect VPN`.

| Screen | Frame | Node id |
| --- | --- | --- |
| Home | `Screen / Home` | 10:184 |
| Tariffs | `Screen / Tariffs` | 5:3 |
| Referral | `Screen / Referral` | 6:49 |
| Support | `Screen / Support` | 8:94 |
| News | `Screen / News` | 9:139 |

Every `Screen / …` and `Mockup / …` frame has a PNG @2x export preset. The `Handoff / Spec` card above the mockups repeats
this page inside the file.

## Fonts
- Inter — Regular, Medium, Semi Bold, Bold (all UI text)
- Montserrat — Bold, Medium (logo wordmark only)

## Colour variables (collection `Connect VPN / Colors`)
| Variable | Value |
| --- | --- |
| bg/navy-950 | #010F29 |
| bg/navy-900 | #041535 |
| card/fill | #01193F |
| card/border | #14407F |
| text/primary | #FFFFFF |
| text/secondary | #8CA8D6 |
| text/muted | #6F8BB8 |
| accent/cyan | #1FD1FF |
| accent/blue | #0A8BFF |
| accent/blue-dark | #0A5FD6 |
| accent/green | #22D6A3 |

Gradients: primary button `#05B4FF → #0A74F6` (horizontal); card `#02204C → #01173F` (vertical), border `#16508F` at 55%.

## Shape and spacing
Screen padding 32 px · card radius 16 px · pills and buttons are fully rounded · list row ≈ 52 px · tab bar 91 px ·
icons on a 24 px grid, stroke 1.6–2.4.

## Components (frame `Components`)
Status Bar · App Header · Bottom Nav (variant `Active` = Home | Subscription | Referral | News | Support) ·
Button / Primary (text property `Label`) · Brand / Logo.

## Images
News 1–5, the home hero and the referral gift are AI-generated raster image fills (soft-masked rectangles).
Logo, icons and flags are vectors. The logo mark has an SVG export preset.

## App flow v2 (second reference — 8 screens)
Frames `Screen v2 / …` (390 × 867 px, reference scaled ×1.5), placed below the first set (y ≈ 2200):

| Screen | Node id |
| --- | --- |
| Splash | 45:314 |
| Home | 45:317 |
| Servers | 45:320 |
| Connected | 45:323 |
| Subscription | 45:326 |
| Profile | 45:329 |
| Referral | 45:332 |
| Settings | 45:335 |

Components: `Brand / Logo mark v2` (vector, SVG export), `App Header v2`, `Bottom Nav v2` (variant `Active` = Home | Servers | Subscription | Profile).
Extra colour variables: v2/bg-deep #000E26, v2/bg-nav #000B1D, v2/card-glass #06183F, v2/azure #0A84FF, v2/azure-light #38A8FF, v2/text-dim #8EA2C6.
Only the referral gift is a raster (AI-generated, soft-masked); logo, icons, flags, power ring and glass cards are vectors.
Screenshots: `figma-overview-full.png` (whole page), `figma-overview-v2.png` (v2 section).

## Style v3 — HUD / terminal (third reference)
Frames `Screen v3 / …` and `Mockup v3 / …` (390 × 867), y ≈ 4500 — the same 8 screens and tabs as v2, restyled:
gradient background with vector contour lines and circuit traces, dashed colour-coded panels, `// <tag>` labels, JetBrains Mono.

| Screen | Node id |
| --- | --- |
| Splash | 74:1052 |
| Home | 74:1598 |
| Servers | 74:2144 |
| Connected | 74:2690 |
| Subscription | 74:3236 |
| Profile | 74:3782 |
| Referral | 74:4328 |
| Settings | 74:4874 |

Components (frame `HUD Components`): HUD / Background (instance on every screen — edit once to restyle all), HUD Panel (Style = Solid | Green | Red | Blue, dashed variants),
HUD / Tag, HUD / Chip, HUD / Badge, HUD / Button Primary, HUD / Button Dashed, HUD / Header, HUD Bottom Nav (Active = Home | Servers | Subscription | Profile).
Tokens: collection `Connect VPN HUD / Colors` (hud/bg-0 #050E24, bg-1 #0B1A4D, panel #1F232D, panel-border #343B4C, tag-accent #7C9BFF, tag #5A6378, text #E6EAF5, text-dim #8E97AD, green #8BC57F, red #F07E6E, violet #B993FF, orange #F0A06A).
Screenshot: `figma-overview-v3.png`.

### v3 background update (gray)
`HUD / Background` is neutral graphite (#262626 → #171718) with topographic contour lines generated from a height field (marching squares),
faint circuit traces and corner marks. Panels are graphite frosted glass, phone frames metallic gray. Decorative ghost icons only appear on
Splash (rings) and Settings (gear) where there is free space.

## Style v4 — gray HUD restyle of the first 5-screen set (in progress)
Frames `Screen v4 / …` / `Mockup v4 / …` (390 × 867), y ≈ 7900 on the Figma page. Gray graphite background (`HUD / Background`),
frosted panels, `// <tag>` labels, JetBrains Mono, silver buttons, minimal nav `HUD Bottom Nav 5`
(variant `Active` = Home | Tariffs | Referral | News | Support).

| Screen | Status |
| --- | --- |
| Home | done |
| Tariffs | done |
| Referral | done; TODO: button icon should be "copy" (currently power), move caption `// больше друзей…` ~6 px up from the button |
| Support | TODO: search, FAQ list (6 rows), operator panel (green dashed), Telegram + Instructions rows |
| News | TODO: filter chips (Все / Обновления / Акции), 5 news cards (78×78 image, title, 2-line text, date) |

Icon components `HUD Icon / <name>` (power, arrow, copy, logout, crown, globe, gear) sit in `HUD Components`; the button has `Icon` (swap) and `Show icon` properties.
Figma file used last: `hP0t2XArWCBEJn2gB2vusf` (copy). The Figma connector must be authorised in a new session before editing.
