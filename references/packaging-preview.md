# Nine-piece packaging preview

Use this procedure for the `nine-piece-sticker` variant. It is a deterministic
retail-package presentation built from the nine transparent line-art assets;
the image model may create the blank package background, but it must not
redraw, recolor, or rearrange the stickers.

## Output contract

- Final file: opaque RGB PNG, exactly `1086x1448` pixels, portrait `3:4`.
- The top backing card is full-bleed from `x=0`, `y=0`, with no top or side
  gutter. Its visible height should be about 15–17% of the canvas; the
  compositor accepts a small tolerance up to 18%.
- The card has a centered hang hole, a centered uppercase serif theme title,
  and the exact dynamic count label `9 PIECES`. The title is required; never
  deliver a card with an empty or omitted theme name.
- The lower field is warm ivory/cream paper with restrained grain and soft
  diffuse light. Do not add travel props, extra scenery, a checkerboard, UI,
  watermark, or decorative text.
- Save the compositor sidecar JSON next to the PNG. It records the title,
  count, card boundary, grid, spacing, and packaging-only white backing width.

The nine source files remain the visual master. They must stay RGBA and
transparent, with no white sticker base, drop shadow, paper texture, or card
color. White backing is generated only while composing the opaque preview.

## Procedure

1. Resolve the nine files from `stickers/01.png` through `stickers/09.png`.
   Reject files with opaque corners or no alpha. Keep natural numeric order.
2. Select a muted card color from the supplied reference photos, rather than
   using a fixed blue-gray. The selector checks cream-text contrast and keeps
   the card visually separate from colored sticker content:

   ```bash
   python scripts/select_packaging_card_color.py \
     --photos /path/to/reference-1.jpg /path/to/reference-2.jpg \
     --stickers /path/to/stickers \
     --out /path/to/packaging/packaging-card-color.json
   ```

   Use `selected.hex` from this JSON when creating the blank background.
3. Create or generate a blank `1086x1448` background using the selected card
   color. Put the title and `9 PIECES` on the card during this step. Keep the
   lower field warm cream. Do not place any sticker artwork in this background.
   Measure the visible lower edge of the card (`card_bottom`) after generation;
   it should fall between roughly 217 and 246 pixels.
4. Composite the unchanged transparent stickers. The script crops only
   transparent padding, fits the visible bounds into a strict 3x3 grid, adds
   a narrow white backing derived from each alpha mask, then adds a faint
   external shadow. The backing is not written back to any source file:

   ```bash
   python scripts/compose_packaging_preview.py \
     --background /path/to/packaging/blank-background.png \
     --stickers /path/to/stickers \
     --card-bottom 232 \
     --title "CAFÉ DAYS" \
     --backing-px 4 \
     --out /path/to/packaging/packaging-preview.png
   ```

   `--title` is both a required metadata guard and the title used in the
   background-generation prompt. The compositor does not paint text into the
   background, because generated typography should be reviewed before the
   stickers are placed. If an open line drawing produces a weak backing from
   its alpha mask, create a closed silhouette for packaging use only and keep
   it out of `stickers/`.
5. Inspect the final PNG at its exact size. Confirm the card is flush to the
   top and full width, the title and count are legible, the nine stickers form
   an even 3x3 grid, and the lower field does not contain an oversized blank
   band. Confirm each source PNG still has real transparency and no white matte.

## Layout rules

Use 5% side margins, 2.5% column gaps, 1.8% row gaps, and 2.5% top/bottom
margins within the area below the card. Fit by visible alpha bounds with about
95% cell occupancy. Keep sticker order stable and center an incomplete final
row for variants that contain fewer than nine items; the black-ink preset must
contain exactly nine and therefore uses a strict 3x3 grid.

The compositor intentionally does not use a hand-authored PIL collage or ask
the image model to draw the final arrangement. This keeps the package card,
theme label, count, spacing, and white backing reproducible across runs.
