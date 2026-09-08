#!/usr/bin/env python3
"""Compose nine transparent black-ink stickers into a fixed-size package preview.

The input stickers remain untouched.  A narrow white backing is derived from
each alpha mask and added only to the opaque packaging composite.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageFilter


SUPPORTED_SUFFIXES = {".png", ".webp", ".tif", ".tiff"}
DEFAULT_WIDTH = 1086
DEFAULT_HEIGHT = 1448


def natural_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def resolve_sticker_paths(values: Iterable[Path]) -> list[Path]:
    resolved: list[Path] = []
    seen: set[Path] = set()
    for value in values:
        if value.is_dir():
            candidates = sorted(
                (path for path in value.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES),
                key=natural_key,
            )
        elif value.is_file():
            candidates = [value]
        else:
            raise FileNotFoundError(f"sticker path does not exist: {value}")
        for candidate in candidates:
            absolute = candidate.resolve()
            if absolute not in seen:
                seen.add(absolute)
                resolved.append(absolute)
    if not resolved:
        raise ValueError("at least one sticker PNG or WebP is required")
    return resolved


def load_sticker(path: Path, padding: int = 2) -> Image.Image:
    with Image.open(path) as opened:
        if "A" not in opened.getbands():
            raise ValueError(f"{path} has no alpha channel; provide a transparent cut-out")
        sticker = opened.convert("RGBA")

    alpha = sticker.getchannel("A")
    if alpha.getbbox() is None:
        raise ValueError(f"{path} contains no visible sticker pixels")
    corners = (
        alpha.getpixel((0, 0)),
        alpha.getpixel((sticker.width - 1, 0)),
        alpha.getpixel((0, sticker.height - 1)),
        alpha.getpixel((sticker.width - 1, sticker.height - 1)),
    )
    if any(corners):
        raise ValueError(f"{path} has opaque corners; remove its rectangular background first")

    bbox = alpha.getbbox()
    assert bbox is not None
    cropped = sticker.crop(bbox)
    padded = Image.new("RGBA", (cropped.width + padding * 2, cropped.height + padding * 2), (0, 0, 0, 0))
    padded.alpha_composite(cropped, (padding, padding))
    return padded


def choose_columns(count: int, requested: int | None, maximum: int) -> int:
    if count < 1:
        raise ValueError("at least one sticker is required")
    if requested is not None:
        if requested < 1 or requested > min(maximum, count):
            raise ValueError(f"columns must be between 1 and {min(maximum, count)}")
        return requested
    if count <= 3:
        return count
    if count == 4:
        return 2
    return min(maximum, count)


def fit(image: Image.Image, max_width: int, max_height: int, occupancy: float) -> Image.Image:
    if max_width < 1 or max_height < 1:
        raise ValueError("the grid has no usable sticker cell; reduce the sticker count or increase the canvas")
    scale = min(max_width * occupancy / image.width, max_height * occupancy / image.height)
    if scale <= 0:
        raise ValueError("sticker scale is not positive")
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)


def make_packaging_layers(sticker: Image.Image, backing_px: int) -> tuple[Image.Image, Image.Image]:
    """Return a final-size white backing layer and a padded art layer."""
    if backing_px < 1:
        raise ValueError("backing-px must be at least 1")
    alpha = sticker.getchannel("A")
    expanded_canvas = Image.new("L", (sticker.width + backing_px * 2, sticker.height + backing_px * 2), 0)
    expanded_canvas.paste(alpha, (backing_px, backing_px))
    expanded = expanded_canvas.filter(ImageFilter.MaxFilter(backing_px * 2 + 1))
    backing = Image.new("RGBA", expanded.size, (255, 255, 255, 0))
    backing.putalpha(expanded)
    art = Image.new("RGBA", expanded.size, (0, 0, 0, 0))
    art.alpha_composite(sticker, (backing_px, backing_px))
    return backing, art


def add_sticker(canvas: Image.Image, sticker: Image.Image, x: int, y: int, backing_px: int) -> None:
    backing, art = make_packaging_layers(sticker, backing_px)
    shadow_alpha = backing.getchannel("A").filter(ImageFilter.GaussianBlur(5)).point(lambda value: round(value * 0.16))
    shadow = Image.new("RGBA", backing.size, (73, 65, 51, 0))
    shadow.putalpha(shadow_alpha)
    canvas.alpha_composite(shadow, (x, y + 3))
    canvas.alpha_composite(backing, (x, y))
    canvas.alpha_composite(art, (x, y))


def compose(
    background_path: Path,
    sticker_paths: list[Path],
    output_path: Path,
    card_bottom: int,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    requested_columns: int | None = None,
    maximum_columns: int = 3,
    occupancy: float = 0.95,
    backing_px: int = 4,
    expected_count: int | None = 9,
    title: str = "",
    layout_json: Path | None = None,
) -> dict[str, object]:
    if width != DEFAULT_WIDTH or height != DEFAULT_HEIGHT:
        raise ValueError(f"this skill uses a fixed {DEFAULT_WIDTH}x{DEFAULT_HEIGHT} output")
    if not 0 < occupancy <= 1:
        raise ValueError("occupancy must be greater than 0 and no more than 1")
    minimum_card_bottom = round(height * 0.15)
    maximum_card_bottom = round(height * 0.18)
    if card_bottom < minimum_card_bottom or card_bottom > maximum_card_bottom:
        raise ValueError(
            f"card-bottom must keep the top card between 15% and 18% of the canvas "
            f"({minimum_card_bottom}–{maximum_card_bottom}px)"
        )
    if backing_px < 1 or backing_px > 12:
        raise ValueError("backing-px must be between 1 and 12")
    if expected_count is not None and expected_count < 1:
        raise ValueError("expected-count must be positive or omitted")
    if not title.strip():
        raise ValueError("title is required so the packaging card cannot lose its theme name")

    background = Image.open(background_path).convert("RGBA")
    if background.size != (width, height):
        raise ValueError(f"background must be exactly {width}x{height}, got {background.size}")

    stickers = [load_sticker(path) for path in sticker_paths]
    count = len(stickers)
    if expected_count is not None and count != expected_count:
        raise ValueError(f"expected {expected_count} stickers, found {count}")
    columns = choose_columns(count, requested_columns, maximum_columns)
    rows = math.ceil(count / columns)

    side_margin = round(width * 0.05)
    column_gap = round(width * 0.025)
    top_bottom_margin = round(height * 0.025)
    row_gap = round(height * 0.018)
    available_width = width - 2 * side_margin - (columns - 1) * column_gap
    available_height = height - card_bottom - 2 * top_bottom_margin - (rows - 1) * row_gap
    cell_width = available_width // columns
    cell_height = available_height // rows
    fitted = [
        fit(
            sticker,
            max(1, cell_width - backing_px * 2),
            max(1, cell_height - backing_px * 2),
            occupancy,
        )
        for sticker in stickers
    ]

    grid_top = card_bottom + top_bottom_margin
    placements: list[dict[str, object]] = []
    for index, sticker in enumerate(fitted):
        row, column = divmod(index, columns)
        row_count = min(columns, count - row * columns)
        slot_offset = (columns - row_count) / 2 if row == rows - 1 and row_count < columns else 0
        packaged_width = sticker.width + backing_px * 2
        packaged_height = sticker.height + backing_px * 2
        x = round(side_margin + (slot_offset + column) * (cell_width + column_gap) + (cell_width - packaged_width) / 2)
        y = round(grid_top + row * (cell_height + row_gap) + (cell_height - packaged_height) / 2)
        add_sticker(background, sticker, x, y, backing_px)
        placements.append(
            {
                "index": index + 1,
                "source": str(sticker_paths[index]),
                "x": x,
                "y": y,
                "width": packaged_width,
                "height": packaged_height,
                "row": row + 1,
                "column": column + 1,
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    background.convert("RGB").save(output_path, "PNG")
    payload: dict[str, object] = {
        "canvas": {"width": width, "height": height, "format": "RGB PNG"},
        "sticker_count": count,
        "title": title.strip(),
        "count_label": f"{count} PIECES",
        "columns": columns,
        "rows": rows,
        "card_bottom": card_bottom,
        "side_margin": side_margin,
        "column_gap": column_gap,
        "row_gap": row_gap,
        "top_bottom_margin": top_bottom_margin,
        "occupancy": occupancy,
        "packaging_backing_px": backing_px,
        "placements": placements,
    }
    json_path = layout_json or output_path.with_suffix(".layout.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {output_path} | {width}x{height} | stickers={count} "
        f"grid={columns}x{rows} side={side_margin}px column_gap={column_gap}px "
        f"row_gap={row_gap}px"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--background", type=Path, required=True, help="Blank 1086x1448 packaging background")
    parser.add_argument("--stickers", type=Path, nargs="+", required=True, help="Transparent sticker files or directories")
    parser.add_argument("--card-bottom", type=int, required=True, help="Visible lower edge of the backing card in pixels")
    parser.add_argument("--out", type=Path, required=True, help="Opaque RGB PNG output")
    parser.add_argument("--columns", type=int, help="Explicit column count; otherwise choose automatically")
    parser.add_argument("--max-columns", type=int, default=3, help="Maximum automatic column count (default: 3)")
    parser.add_argument("--occupancy", type=float, default=0.95, help="Sticker occupancy within each grid cell")
    parser.add_argument("--backing-px", type=int, default=4, help="Packaging-only white backing expansion in pixels (default: 4)")
    parser.add_argument("--expected-count", type=int, default=9, help="Expected sticker count; use 0 to disable (default: 9)")
    parser.add_argument(
        "--title",
        required=True,
        help="Theme title already rendered on the blank card; recorded as a required metadata guard",
    )
    parser.add_argument("--layout-json", type=Path, help="Optional sidecar JSON path")
    args = parser.parse_args()
    if args.max_columns < 1:
        parser.error("--max-columns must be at least 1")
    paths = resolve_sticker_paths(args.stickers)
    compose(
        args.background,
        paths,
        args.out,
        args.card_bottom,
        requested_columns=args.columns,
        maximum_columns=args.max_columns,
        occupancy=args.occupancy,
        backing_px=args.backing_px,
        expected_count=None if args.expected_count == 0 else args.expected_count,
        title=args.title,
        layout_json=args.layout_json,
    )


if __name__ == "__main__":
    main()
