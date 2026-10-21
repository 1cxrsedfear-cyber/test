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
| bg/navy-950 | #020F2A |
| bg/navy-900 | #041535 |
| card/fill | #07204A |
| card/border | #14407F |
| text/primary | #FFFFFF |
| text/secondary | #9DB4DA |
| text/muted | #6F8BB8 |
| accent/cyan | #1FD1FF |
| accent/blue | #0A8BFF |
| accent/blue-dark | #0A5FD6 |
| accent/green | #22D6A3 |

Gradients: primary button `#05B4FF → #0A74F6` (horizontal); card `#0B2B5E → #061A41` (vertical), border `#174684`.

## Shape and spacing
Screen padding 32 px · card radius 16 px · pills and buttons are fully rounded · list row ≈ 52 px · tab bar 91 px ·
icons on a 24 px grid, stroke 1.6–2.4.

## Components (frame `Components`)
Status Bar · App Header · Bottom Nav (variant `Active` = Home | Subscription | Referral | News | Support) ·
Button / Primary (text property `Label`) · Brand / Logo.

## Images
News 1–5, the home hero and the referral gift are AI-generated raster image fills (soft-masked rectangles).
Logo, icons and flags are vectors. The logo mark has an SVG export preset.
