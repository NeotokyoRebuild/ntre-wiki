---
description: "The palette and typefaces of the wiki's dark and light themes"
---

# Colours & type

The wiki's **palette** follows the NEOTOKYO;REBUILD branding: neutral black, white and a red dot. One cool accent is added for link underlines.

Red is kept to small marks. It never colours link text, because on a wiki red text means a page that doesn't exist yet.

## Palette

{{table:palette}}

!!! note ""
    Dark is the default. The sun/moon button in the header switches to the light palette. That palette is in the same stylesheet, under `[data-md-color-scheme="default"]`.

## Reds

The brand assets use three different reds:

| Red | Where |
| --- | --- |
| <span class="swatch" style="background:#ff0000"></span>`#ff0000` | Wordmark dots; the site's dot marks (`--ntre-red`) |
| <span class="swatch" style="background:#d1482e"></span>`#d1482e` | Wireframe NT;RE mark dot and app icon |
| <span class="swatch" style="background:#c62a1d"></span>`#c62a1d` | Open Collective badge dot (`--ntre-red-soft`) |

## Typefaces

| Face | Used for | Weights |
| --- | --- | ---: |
| <span style="font-family: var(--md-text-font-family); font-size: 1.05em">Inter</span> | Headings and body text | 400 · 500 · 600 · 650 · 700 |
| <span style="font-family: var(--md-code-font-family); font-size: 1em">IBM Plex Mono</span> | Numbers in infoboxes and tables, code, citation markers | 400 · 500 |

Both load from Google Fonts, through the theme's `font` setting in `mkdocs.yml`. The wordmark's lettering is part of the image, not a font.
{ .table-caption }

## Marks

- **Red dot after page titles**, raised like the dot in the wordmark
- **Red dot beside the current page** in the sidebar
- **Links** in white, with a faint, muted cyan underline. On hover the underline fills from left to right, snaps, pulses once and settles.
- **Hairline borders**, with no shadows or gradients
- **Rounded blocks**: 8-pixel corners on tables, callouts, cards, code and the search box, and 6-pixel corners on navigation items

See [[logos|Logos]] for the images themselves.
