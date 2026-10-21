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
