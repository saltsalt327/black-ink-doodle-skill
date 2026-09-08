---
name: stable-black-ink-doodle
description: Generate or transform small-object illustrations into a consistent hand-drawn black-ink doodle style based on the bundled IMG_3762 master reference. Use for text-to-image generation, photo-to-illustration conversion, nine-piece sticker sets from one to five references, transparent line-art assets, low-size previews, icon sheets, and deterministic 3:4 packaging previews involving food, stationery, or daily-life objects.
---

# Stable Black Ink Doodle

Use this skill to create a coherent family of small black-and-white object illustrations for electronic journals, stickers, icon sheets, and printable assets. Keep the subject variable while keeping the visual language fixed to the bundled master reference.

## Style master

Use `assets/style-master-sheet.png` as the primary style reference for every generated or edited image when the image-generation tool supports reference images. Resolve this path relative to the directory containing this `SKILL.md`; pass the resolved local path to the image tool rather than hardcoding a machine-specific absolute path. `assets/style-master-img-3762.png` is the wider cropped photo reference and is useful only when the page context needs to be inspected.

Treat the master sheet as a style reference, not a composition reference. Prefer a clean object crop or style-only sheet if one is available in the future; do not let the photographed page, labels, or 3x3 arrangement leak into a normal asset.

Read the reference as a photographed sample sheet, not as the requested composition. Copy only its illustration language:

- handmade black ink on white paper;
- slightly uneven, pressure-sensitive contours with rounded organic turns;
- simplified, recognizable objects with a naive and charming proportion;
- selective solid-black areas for deep shadows, dark materials, fruit skins, cups, trays, or accents;
- sparse dots, short hatching, and small interior marks instead of gray shading;
- generous white space and quiet, isolated object placement;
- occasional grounding plates, trays, saucers, or short shadows when they help the object read;
- restrained detail: enough to identify the object, never photorealistic rendering.

Ignore the reference image's desk, fabric, paper edges, photography shadows, watermark, and labels unless the user explicitly asks for a page mockup or lettering. Never reproduce the reference sheet's 3x3 grid for a single-object request.

## Non-negotiable constraints

Keep these constraints unchanged unless the user explicitly requests a different version of the style:

- Use black ink and white only for the artwork. Do not introduce color, pastel accents, gray gradients, or colored paper.
- Prefer imperfect hand-drawn contours over clean vector geometry. Do not make lines mechanically uniform.
- Use a thin-to-medium contour with controlled local thickening; reserve heavy black fill for selected areas rather than filling every surface.
- Use sparse texture marks: small dots, short strokes, or simple hatching. Do not use photorealistic texture, painterly brushwork, or dense crosshatching.
- Simplify the object into a readable doodle. Preserve its defining silhouette and one or two characteristic details, not every photographic detail.
- Keep the composition calm, centered, and surrounded by generous negative space. For a single asset, use one primary object unless the user asks for a group.
- Default to a clean white background for an unspecified use case. Use a transparent background only when the asset is intended for app placement or stickers and the user has not requested a paper page. Transparency is an export choice; it must not introduce a checkerboard, gray matte, or colored halo.
- For the `nine-piece-sticker` variant, keep every individual line-art master, preview, and sticker asset transparent. Do not bake a white sticker base, white matte, drop shadow, or paper texture into those individual files.
- Exclude captions, logos, watermarks, UI elements, borders, frames, and decorative scenery by default.

## Workflow

### 1. Classify the input

Determine whether the user wants:

1. a single object extracted or reimagined from a provided image;
2. a single object generated from a text description;
3. a set of separate objects;
4. a 3x3 or similar reference-sheet layout; or
5. a page mockup with paper and hand lettering.

Keep the first two modes as isolated assets. Use the sheet or page modes only when explicitly requested.

For a provided photograph, preserve the requested subject and its recognizable pose or silhouette, but remove the photographic setting and convert the subject into the master style.

If the request does not specify a mode, use `single-object` with the `journal` output preset. Infer `sticker` only from an explicit sticker, cutout, transparent, app-placement, or direct-placement request.

### 2. Lock the visual recipe

Use the same style instructions and the bundled master reference for every item in a batch. Change only the subject, requested arrangement, and any explicitly requested accessory.

Use this internal prompt structure:

```text
Create [SUBJECT] as a small hand-drawn black-ink doodle illustration.
Follow the bundled IMG_3762 style master: handmade pen contours, slight line wobble,
subtle pressure variation, simplified naive proportions, selective solid-black fills,
sparse dots and short hatching, organic imperfect symmetry, and generous white space.
Keep the subject clearly recognizable and isolated.
Use black ink and white only, no gray, no color, no gradients, no photorealism,
no polished vector finish, no decorative background, no text, no logo, and no watermark.
Output a clean [WHITE OR TRANSPARENT] background.
```

Do not replace this recipe with a generic style label such as “cartoon,” “comic,” “anime,” “vector,” or “coloring book”; those labels cause unwanted drift.

### 3. Use reference-aware generation or editing

When `image_gen` is available, include the bundled master image as a style reference on every call. If the user supplies a source image, include that image as the content reference as well, while keeping the master image as the style reference.

Use this reference protocol:

1. Resolve the style reference from `<skill-root>/assets/style-master-sheet.png`.
2. If the source image has a local path, pass both the source image and the style reference as local references. State in the prompt that the first is the content source and the second is the style source; never ask for a pixel trace.
3. If the source image exists only as a recent conversation attachment, use the tool's recent-image mechanism and include the smallest set of recent images that contains both the source image and the inspected style master. Do not pass mutually exclusive local-reference and recent-image parameters together.
4. If the tool cannot include both references, keep the full textual visual recipe, do not claim that the master image was supplied, and use a conservative single-object composition. Ask the user to reattach the missing source only when the subject cannot be identified without it.

When editing a supplied image, assign roles explicitly: preserve the source subject's identity, pose, silhouette, and defining details; borrow only the line, fill, texture, and composition language from the master. The source image must not contribute its background, UI, watermark, or photographic lighting.

For a source-image conversion, instruct the model to preserve the subject's identity, silhouette, and key features while redrawing it in the master style. Do not ask for an exact pixel trace; the target is a simplified hand-drawn reinterpretation.

For a batch, keep the same output aspect ratio, canvas padding, background choice, and generation/editing mode for all items. Do not switch between unrelated image workflows within one batch.

### 4. Handle labels separately

Do not rely on image generation for readable labels. Omit labels unless the user explicitly requests them. If labels are required, generate the illustration first, then add the text in a separate editing or layout step using a consistent hand-lettering treatment.

### 5. Review and regenerate

After each generation or edit, inspect the actual output image before delivering it. Run the acceptance list below in order: silhouette and recognizability first, then style, then background/export cleanliness. If one criterion fails, regenerate with one focused correction while keeping the rest of the recipe unchanged. Limit corrective iterations to two focused passes unless the user asks for more exploration.

Check every output against the following acceptance list:

- Is the main subject immediately recognizable?
- Does the image look hand-drawn rather than vector-clean or photorealistic?
- Are the lines black, organic, and mildly pressure-varied?
- Are black fills selective and intentional?
- Are dots and hatching sparse rather than noisy?
- Is the background only white or transparent as requested?
- Are the photographed setting, UI bars, watermark, frame, and unintended text absent?
- Does the object have enough empty space around it to work as an electronic-journal asset?
- Does it look like it belongs beside the IMG_3762 reference?

Do not rewrite the whole style prompt between iterations. Change only the failed dimension, such as `remove the copied grid and label`, `increase empty margin`, or `reduce interior hatching`.

### 6. Run the nine-piece sticker pipeline

Use this variant when the user provides one to five reference images and requests nine related black-and-white line-art assets, their previews, separate transparent stickers, and a packaging preview.

#### A. Plan the nine contents

Create an ordered nine-item manifest before generation. Record each item's number, short name, source reference(s), defining silhouette, and one or two required details. Treat the user's one to five images as content references unless the user explicitly assigns a different role; keep the bundled IMG_3762 image as the style reference. If the source images are only recent attachments, consolidate them into a reference board when needed so the style reference can still be included within the image tool's input limit.

#### B. Generate canonical line-art masters

Generate nine separate high-resolution images using the same style recipe, canvas ratio, padding, and transparent-background requirement. Each master must contain one clearly isolated object or scene, black ink artwork only, and no white sticker base. Do not use an AI-generated 3x3 sheet as the source of truth for the nine assets; create any contact sheet later by compositing the nine masters.

Use the canonical masters as the only source for all later derivatives. Do not regenerate the same content to make previews, stickers, or the packaging mockup.

#### C. Derive the low-size previews

Create one small preview for each canonical master by deterministic resizing and compression. Preserve the transparent background and the exact content, pose, and crop. Use a compact PNG or alpha-capable WebP when supported; do not ask the image model to redraw the previews. Keep the same numbering as the masters.

#### D. Export individual transparent stickers

Normalize each master to an RGBA sticker asset with black linework and transparent surroundings. Remove the white canvas or paper matte without removing required black marks. Do not add a white outline, white fill, sticker backing, shadow, or packaging background to these files. If the linework contains white negative space, keep that space transparent unless the user explicitly requests white interior fills.

#### E. Compose the packaging preview

Read `references/packaging-preview.md` before composing. Build the packaging preview from the nine transparent sticker assets using the dedicated scripts, not by asking the image model to draw the final arrangement:

1. Run `scripts/select_packaging_card_color.py` against the one to five source references and the transparent sticker directory. Use the selected muted source-derived color and the returned JSON as the card-color record.
2. Create a blank `1086x1448` background with the full-width top card, centered hang hole, warm cream lower field, the explicit theme title, and the exact `9 PIECES` label. Generate or edit only this blank background; keep all sticker artwork out of it. The title is mandatory. If the user has not supplied one, derive a short uppercase theme name from the nine-item manifest before proceeding; never omit the title.
3. Measure the visible card bottom and run `scripts/compose_packaging_preview.py` with the blank background, the nine-sticker directory, `--card-bottom`, and `--title`. The script enforces the fixed `1086x1448` canvas, 15–18% card height tolerance, exact nine-item count, and strict 3x3 layout. It writes the opaque RGB PNG and a `.layout.json` sidecar.
4. The compositor adds a narrow white sticker backing only inside the packaging composite, derived from each alpha mask, then adds a subtle external shadow. Use the default 4 px backing unless the reference requires a small adjustment. Never write the backing, shadow, card color, or paper texture back into `stickers/`, `masters/`, or `previews/`.

If an open line drawing cannot produce a reliable solid backing from its alpha mask, create a closed white silhouette layer for packaging use only. Do not export that silhouette as part of the standalone sticker. The packaging reference controls the product-card layout, typography placement, count label, and grid; the black-ink master controls the sticker artwork style.

#### F. Deliver and verify the set

Keep the nine item numbers consistent across masters, previews, stickers, and the packaging layout. Prefer the following output contract: `masters/01.png`–`09.png` for high-resolution transparent masters, `previews/01.webp`–`09.webp` or compact PNGs for transparent previews, `stickers/01.png`–`09.png` for standalone transparent assets, `packaging/packaging-preview.png` for the opaque `1086x1448` RGB composite, `packaging/packaging-preview.layout.json` for placement metadata, and `packaging/packaging-card-color.json` for the source-derived card color. Verify that there are exactly nine of each, that every individual file has real transparency and no white matte, that the packaging card is full-width at the top with a legible theme title and exact `9 PIECES` label, and that every packaged sticker has the intended white backing. Optionally create a manifest with item names, source references, dimensions, formats, and output paths.

## Controlled variants

Treat these as explicit variants, not spontaneous changes:

- `single-object`: one centered object, clean white or transparent background, no label;
- `object-pair`: two related objects with balanced spacing and shared scale;
- `object-sheet`: a user-requested grid, with equal cells, consistent scale, and optional labels added afterward;
- `nine-piece-sticker`: one to five content references expanded into nine canonical transparent line-art masters, nine derived low-size previews, nine standalone transparent sticker assets without white backing, and one fixed `1086x1448` packaging preview with a titled full-width backing card, exact count label, strict 3x3 grid, layout JSON, and white backing applied only during composition;
- `page-mockup`: only when the user wants the photographed paper presentation, including a controlled paper background and layout.

The default is `single-object`.

## Output presets

Choose the smallest preset that satisfies the request, and keep the preset fixed across a batch:

- `journal`: one centered object, square canvas when no ratio is requested, white background, generous padding, PNG;
- `sticker`: one isolated object, transparent PNG, clean alpha edge, no white sticker base, shadow, or paper texture unless requested;
- `nine-piece-sticker`: nine transparent black-and-white line-art masters, nine derived transparent previews, nine transparent standalone sticker PNGs, and one opaque `1086x1448` packaging preview with a titled card, exact `9 PIECES` label, strict 3x3 grid, sidecar layout JSON, and per-sticker white backing;
- `print`: white background, highest practical raster size, no compression artifacts, and 300 DPI metadata added during final packaging when a print workflow is available;
- `object-sheet`: user-requested grid only, equal cells and consistent scale, with labels added after illustration generation;
- `page-mockup`: photographed paper, desk, lettering, or layout only when explicitly requested.

If the user specifies a canvas ratio, size, or background, it overrides the preset. Keep at least 8–12% empty margin around the outermost contour unless the user asks for a tight crop.

For transparent output, verify that the artwork has real alpha transparency rather than a white matte, and that no gray or colored fringe remains around the contour. For white-background output, verify that the background is clean white rather than paper texture or a generated checkerboard.

## Output defaults

- Prefer PNG for app assets and previews.
- Prefer transparent PNG for stickers or direct placement in the electronic-journal app.
- Prefer white-background PNG when the asset is intended to look like ink on paper.
- Keep the artwork isolated and padded; do not crop into the contour.
- Produce SVG only when the user explicitly needs vector output. A vector conversion may remove the organic ink variation, so preserve the raster PNG as the visual source of truth.
