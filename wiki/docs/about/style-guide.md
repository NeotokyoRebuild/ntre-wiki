---
description: "How this wiki is written and laid out"
---

# Style guide

The rules every page on this wiki follows. The writing rules live in `WRITING-STYLE.md` at the top of the repository and are included here, so this page always matches them.

--8<-- "WRITING-STYLE.md:guide"

## Visual

- Dark by default, minimal, neutral, with a light theme one click away. Hairline borders; no shadows, gradients or emoji.
- Blocks are rounded: 8px on tables, callouts, cards, infoboxes, code and the search box; 6px on navigation items.
- Text uses four sizes, set as tokens in `ntre.css` (in rem, so they follow Material's scaling and the reader's browser settings). At the default size:
    - **Prose**, 13px: body text, lists, card titles
    - **Secondary**, 12px: callouts and Technical details, card text, the menu and contents, search, references, footer, infobox titles
    - **Data**, 10.8px: tables and their captions, stat strips, infobox rows, tags, keys
    - **Marks**, 9px at least: citation markers, so they stay clickable in tables

    Headings scale from the prose size.
- Tables never sit beside an infobox: they start below it and take the full width, so they're never squeezed or cut off. Prose still flows beside it.
- In numeric table columns, citation markers come before the value, so the numbers line up on their right edge. Text cells and infoboxes keep them after the text. The build moves them; write citations after the value as usual.
- Red is for the brand dot only: after page titles and beside the current page. Never for link text, because red text means a missing page.
- Link underlines are a cool, desaturated cyan. On hover the line fills left to right, snaps into place, pulses once and settles. Cards lift to a lighter surface on hover instead.
- Icon buttons, like "Edit this page", are small: the icon at 60% of the theme's size, in a circle with a hairline border. They stay muted until hovered.
- The NT;RE mark is the primary logo. The wordmark appears only on the main page.
- Image slots are grey placeholders labelled with what belongs there, until assets are licensed.

Details: [[colours-and-type|Colours & type]] and [[logos|Logos]].
