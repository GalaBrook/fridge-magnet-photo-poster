---
name: fridge-magnet-photo-poster
description: Create a vertical 3:4 travel photography poster from a user-supplied real photo, with a prominent source-derived refrigerator-magnet icon and compact Helvetica-style English title on a clean solid-color field above, plus the unchanged real photograph below. Use for 建筑冰箱贴摄影海报、小红书城市打卡、酒店门头、地标建筑、人物或动物旅行纪念卡片、极简旅行卡片、上下分区摄影拼贴, or requests combining a generated souvenir icon with an authentic photo.
---

# Fridge Magnet Photo Poster

Create exactly one polished poster. Use image generation only for the magnet icon and deterministic local composition for the final poster.

## Fixed Output Contract

- Use a vertical 3:4 canvas, `1536 x 2048` by default.
- Give the upper and lower panels exactly 50% of the canvas each.
- Keep the upper panel minimal: one flat source-derived color, one prominent centered magnet, and one English title.
- Put the supplied real photo in the lower panel. Permit only proportional resize and center crop.
- Never generate, redraw, retouch, recolor, stylize, or reconstruct the lower photo.
- Save a new PNG; never overwrite the source photo.

## Workflow

### 1. Inspect the source

Identify:

- the single most recognizable building, landmark, facade, entrance, or scene subject;
- three to five defining features such as roof, doorway, arches, windows, balcony, sign shape, people, or animals;
- one clean saturated color derived from a prominent sky, wall, door, environment, or architectural surface;
- a dynamic English title for this image.

### 2. Resolve the dynamic title

Choose a new title for every photograph. Never reuse an earlier title by habit.

Use this priority:

1. Use a clearly readable proper building or place name when reliable.
2. Otherwise use a concise architectural or location identity.
3. Otherwise use a short travel-oriented feeling grounded in the visible scene.

Title rules:

- Use one to three English words.
- Prefer 18 characters or fewer when practical.
- Use natural, correctly spelled English.
- Prefer natural title case. Preserve exact user-supplied capitalization.
- Do not invent a specific place name without evidence.
- Do not transliterate uncertain source text.
- Respect exact user-supplied wording when provided.
- Do not include title text in the image-generation prompt.
- Pass the resolved title to `scripts/compose_poster.py --title` for local rendering.

### 3. Resolve the background

- Select one exact hexadecimal RGB color from the source's strongest useful color memory.
- Prefer a bright, saturated, clean travel-postcard color with adequate contrast for the magnet and title.
- Use one solid color only. No gradient, pattern, texture, border, or decorative shapes.
- Pass it to the composition script with `--background`.

### 4. Generate only the magnet

Use the available image-generation capability once to create a landscape magnet source image.

Require:

- one centered refrigerator-magnet interpretation derived from the source;
- preserved defining architecture with moderately simplified detail;
- a thin warm-white or light-cream outer rim;
- shallow molded relief and a restrained compact shadow;
- a refined souvenir scale that remains prominent while preserving generous empty space;
- a perfectly flat solid `#00ff00` chroma-key background;
- no text, letters, labels, logos, captions, watermark, gradients, scenery, or extra decoration;
- no `#00ff00` inside the magnet.

Do not ask the generator to create the final poster. Do not ask it to reproduce the lower photo.

### 5. Compose deterministically

Locate a Python interpreter with Pillow. Run the bundled script relative to this file:

```text
<python> scripts/compose_poster.py \
  --photo <source-photo> \
  --magnet <generated-magnet> \
  --output <final-poster.png> \
  --title <resolved-title> \
  --background <resolved-hex> \
  --key-color '#00ff00'
```

Use `--key-color auto` only when continuing from an existing generated magnet whose corner background is a uniform non-green color.

The composition script enforces the reference-led upper-panel relationship:

- scale the magnet up to about 42% of the canvas width or 48% of the upper-panel height;
- treat the magnet and title as one vertically centered group;
- keep a compact gap of about 4.5% of the upper-panel height between them;
- use Helvetica first, with Arial or another metric-compatible sans serif as fallback;
- preserve title capitalization instead of forcing all caps.

### 6. Verify once

Inspect the final PNG and confirm:

- exact 3:4 dimensions and equal panels;
- one flat upper background color;
- a prominent icon and title forming one compact, visually centered group with ample outer whitespace;
- correctly spelled title below the icon with no overlap;
- authentic lower photo content with no stretch or model reconstruction;
- recognizable building crop;
- no garbled text, gradient, extra decoration, or watermark.

If the magnet itself is unusable, make at most one targeted image-generation correction. Fix deterministic layout problems by rerunning the script, not by regenerating the whole poster.

## Delivery

Return the final PNG and one brief sentence naming the dynamic title and source-derived background choice. Do not expose the full image-generation prompt unless requested.
