# LLM Handoff

Use this repository to create embroidery thread-layout YAML files, substitute colors into generic templates, and render preview PNGs.

## Core files

- `templates/*.yaml`
  Template thread layouts. These usually contain placeholder colors like `__COLOR1__` and `__COLOR2__`.
- `create_mesh.py`
  Renders a YAML thread file into a PNG grid preview.
- `Makefile`
  Convenience wrapper for substituting `__COLORn__` placeholders and calling `create_mesh.py`.
- `generate_grid.py`
  Example script that programmatically generates a repeated unit grid. It is useful as a pattern reference, not as the full source of truth for every template in this repo.

## YAML format

Thread files look like this:

```yaml
colors:
  color11: &color11 __COLOR1__
  color12: &color12 __COLOR1__

threads:
  - color: *color11
    paths:
      - start: [0, 1]
        end: [1, 0]
      - start: [0, 2]
        end: [2, 0]
```

Rules:

- Top-level keys are usually `colors:` and `threads:`.
- A thread block has a `color` and a `paths` list.
- Each path has `start: [x, y]` and `end: [x, y]`.
- Coordinates may be integers or floats.
- Floats are valid and are used for shortened whip-stitch rows.
- `skip` is a special color value that erases a rectangular region during rendering.
- Color anchors like `&color11` and references like `*color11` are plain YAML anchors.

## Placeholder colors

Generic templates often use placeholders:

- `__COLOR1__`
- `__COLOR2__`
- etc.

The `Makefile` replaces these placeholders from environment variables:

- `COLOR1=...`
- `COLOR2=...`

Example:

```sh
make mesh GENERIC=templates/large-side.yaml OUTPUT=large-side.png COLOR1=black COLOR2=red
```

## Makefile targets

Run `make help` for the summary.

### `make temp`

Expands a generic YAML template into a temporary resolved YAML file.

Example:

```sh
make temp GENERIC=templates/large-side.yaml COLOR1=black COLOR2=red
```

Use this when you want to inspect the final YAML after placeholder substitution.

### `make mesh`

Expands placeholders and renders a PNG preview.

Example:

```sh
make mesh GENERIC=templates/large-side.yaml OUTPUT=large-side.png COLOR1=black COLOR2=red
```

Important:

- Do not rely on the default `GENERIC`.
- The current default in `Makefile` is `rainbow/top.generic.yaml`, which may not exist in another checkout.
- Always pass `GENERIC=...` explicitly unless you have confirmed the default file exists.

## Direct script usage

If you already have a fully resolved YAML file with real colors, render it directly:

```sh
python3 create_mesh.py --threads resolved.yaml --output preview.png
```

Useful options:

```sh
python3 create_mesh.py \
  --threads resolved.yaml \
  --output preview.png \
  --cell-size 20 \
  --thread-width 7 \
  --debug-overlay
```

Notes:

- Grid size is auto-detected from the maximum coordinates in the thread file.
- Fractional coordinates are supported.
- The output mesh may be rectangular, not only square.

## Recommended LLM workflow

When asked to create a new template:

1. Open a nearby template in `templates/` that already has the closest structure.
2. Reuse the existing YAML style, comments, anchors, and coordinate conventions.
3. If the request is patterned or repetitive, generate the content programmatically, then write the final YAML file.
4. Render a preview with `make mesh GENERIC=... COLOR1=... COLOR2=...` or `python3 create_mesh.py`.
5. Check the preview bounds and confirm no rows or columns are unintentionally clipped.

When asked to modify an existing template:

1. Preserve the overall structure unless the user explicitly wants a redesign.
2. Treat whip-stitch rows and regular unit grids as separate sections.
3. If moving a repeated grid, shift all affected coordinates consistently.
4. If cropping units, also crop or move the matching whip-stitch rows.
5. Re-render after every structural change.

## Practical conventions in this repo

- “Regular units” are the repeated interior grid blocks.
- “Whip-stitch rows” are standalone border rows or columns outside the regular units.
- Unit size is determined by the path pattern:
  - 9-thread units use a `5x5` cell footprint.
  - 11-thread units use a `6x6` cell footprint.
- Some templates intentionally use shortened border stitches with fractional coordinates.

## Common pitfalls

- Forgetting to pass `GENERIC=...` to `make mesh`.
- Leaving unresolved `__COLORn__` placeholders in a file.
- Moving a unit grid without moving its matching border whip-stitch rows.
- Cropping the regular units but forgetting to shorten the side or bottom border rows.
- Assuming coordinates must be integers. They do not.

## Good commands to use

Inspect a template:

```sh
sed -n '1,220p' templates/large-side.yaml
tail -n 80 templates/large-side.yaml
```

Find templates:

```sh
rg --files templates
```

Render a template:

```sh
make mesh GENERIC=templates/large-side.yaml OUTPUT=out.png COLOR1=black COLOR2=red
```

Render without the Makefile:

```sh
python3 create_mesh.py --threads some-file.yaml --output out.png
```

## What another LLM should do by default

- Prefer editing or copying an existing template over inventing a format.
- Use explicit `GENERIC=...` arguments in `make`.
- Re-render after structural YAML edits.
- Keep comments and anchor naming consistent with nearby files.
- If a change is very repetitive, generate the coordinates with a script, then save the final YAML.
