---
name: stable-black-ink-doodle
description: Generate or transform provided images into a consistent hand-drawn black-ink doodle illustration style based on the bundled IMG_3762 master reference. Use when the user asks for small object illustrations, food illustrations, stationery, daily-life items, sticker assets, or photo-to-illustration conversion in this specific monochrome ink style.
---

# Stable Black Ink Doodle

Use this skill to create a coherent family of small black-and-white object illustrations for electronic journals, stickers, icon sheets, and printable assets. Keep the subject variable while keeping the visual language fixed to the bundled master reference.

## Style master

Use `assets/style-master-sheet.png` as the primary style reference for every generated or edited image when the image-generation tool supports reference images. `assets/style-master-img-3762.png` is the wider cropped photo reference and is useful only when the page context needs to be inspected.

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
- Default to a clean white background. Use a transparent background when the asset is intended for app placement or stickers and the user has not requested a paper page.
- Exclude captions, logos, watermarks, UI elements, borders, frames, and decorative scenery by default.

## Workflow

### 1. Classify the input

Determine whether the user wants:

1. a single object extracted or reimagined from a provided image;
2. a set of separate objects;
3. a 3x3 or similar reference-sheet layout; or
4. a page mockup with paper and hand lettering.

Keep the first two modes as isolated assets. Use the sheet or page modes only when explicitly requested.

For a provided photograph, preserve the requested subject and its recognizable pose or silhouette, but remove the photographic setting and convert the subject into the master style.

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

For a source-image conversion, instruct the model to preserve the subject's identity, silhouette, and key features while redrawing it in the master style. Do not ask for an exact pixel trace; the target is a simplified hand-drawn reinterpretation.

For a batch, keep the same output aspect ratio, canvas padding, background choice, and generation/editing mode for all items. Do not switch between unrelated image workflows within one batch.

### 4. Handle labels separately

Do not rely on image generation for readable labels. Omit labels unless the user explicitly requests them. If labels are required, generate the illustration first, then add the text in a separate editing or layout step using a consistent hand-lettering treatment.

### 5. Review and regenerate

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

If one criterion fails, regenerate with one focused correction while keeping the rest of the recipe unchanged. Do not rewrite the whole style prompt between iterations.

## Controlled variants

Treat these as explicit variants, not spontaneous changes:

- `single-object`: one centered object, clean white or transparent background, no label;
- `object-pair`: two related objects with balanced spacing and shared scale;
- `object-sheet`: a user-requested grid, with equal cells, consistent scale, and optional labels added afterward;
- `page-mockup`: only when the user wants the photographed paper presentation, including a controlled paper background and layout.

The default is `single-object`.

## Output defaults

- Prefer PNG for app assets and previews.
- Prefer transparent PNG for stickers or direct placement in the electronic-journal app.
- Prefer white-background PNG when the asset is intended to look like ink on paper.
- Keep the artwork isolated and padded; do not crop into the contour.
- Produce SVG only when the user explicitly needs vector output. A vector conversion may remove the organic ink variation, so preserve the raster PNG as the visual source of truth.
