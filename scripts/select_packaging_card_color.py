#!/usr/bin/env python3
"""Select a source-derived backing-card color for a sticker package."""

from __future__ import annotations

import argparse
import colorsys
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image


SUPPORTED_SUFFIXES = {".png", ".webp", ".tif", ".tiff"}


@dataclass(frozen=True)
class PaletteColor:
    rgb: tuple[int, int, int]
    weight: float


def parse_hex(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("colors must use six-digit hex notation")
    try:
        return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("colors must use six-digit hex notation") from exc


def as_hex(rgb: Sequence[int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def srgb_channel(value: int) -> float:
    channel = value / 255.0
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: Sequence[int]) -> float:
    red, green, blue = (srgb_channel(value) for value in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: Sequence[int], second: Sequence[int]) -> float:
    light, dark = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def rgb_to_lab(rgb: Sequence[int]) -> tuple[float, float, float]:
    red, green, blue = (srgb_channel(value) for value in rgb)
    x = (red * 0.4124 + green * 0.3576 + blue * 0.1805) / 0.95047
    y = red * 0.2126 + green * 0.7152 + blue * 0.0722
    z = (red * 0.0193 + green * 0.1192 + blue * 0.9505) / 1.08883

    def pivot(value: float) -> float:
        return value ** (1.0 / 3.0) if value > 0.008856 else 7.787 * value + 16.0 / 116.0

    fx, fy, fz = pivot(x), pivot(y), pivot(z)
    return 116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz)


def delta_e(first: Sequence[int], second: Sequence[int]) -> float:
    lab_a = rgb_to_lab(first)
    lab_b = rgb_to_lab(second)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab_a, lab_b)))


def hue_distance(first: float, second: float) -> float:
    distance = abs(first - second) % 1.0
    return min(distance, 1.0 - distance) * 360.0


def collect_pixels(paths: Iterable[Path], stickers: bool) -> list[tuple[int, int, int]]:
    pixels: list[tuple[int, int, int]] = []
    for path in paths:
        with Image.open(path) as opened:
            image = opened.convert("RGBA")
            image.thumbnail((320, 320), Image.Resampling.LANCZOS)
            for red, green, blue, alpha in image.getdata():
                if alpha < 128:
                    continue
                hue, lightness, saturation = colorsys.rgb_to_hls(red / 255, green / 255, blue / 255)
                if stickers and lightness > 0.84 and saturation < 0.22:
                    continue
                if stickers and lightness < 0.12:
                    continue
                pixels.append((red, green, blue))
    if not pixels:
        raise ValueError("no usable pixels found")
    return pixels


def resolve_sticker_paths(value: Path) -> list[Path]:
    if value.is_dir():
        paths = sorted(
            (path for path in value.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES),
            key=lambda path: path.name,
        )
    elif value.is_file():
        paths = [value]
    else:
        raise FileNotFoundError(f"sticker path does not exist: {value}")
    if not paths:
        raise ValueError(f"no transparent sticker files found in {value}")
    return paths


def quantized_palette(paths: Iterable[Path], stickers: bool, colors: int = 24) -> list[PaletteColor]:
    pixels = collect_pixels(paths, stickers)
    stride = max(1, len(pixels) // 180_000)
    sampled = pixels[::stride]
    strip = Image.new("RGB", (len(sampled), 1))
    strip.putdata(sampled)
    quantized = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    total = len(sampled)
    result: list[PaletteColor] = []
    for count, index in quantized.getcolors(colors) or []:
        offset = index * 3
        rgb = tuple(palette[offset : offset + 3])
        result.append(PaletteColor(rgb=rgb, weight=count / total))  # type: ignore[arg-type]
    return sorted(result, key=lambda item: item.weight, reverse=True)


def card_variants(source: PaletteColor) -> Iterable[tuple[int, int, int]]:
    red, green, blue = (value / 255.0 for value in source.rgb)
    hue, _lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    muted_saturation = min(0.56, max(0.28, saturation * 0.72))
    for lightness in (0.22, 0.26, 0.30, 0.34):
        candidate = colorsys.hls_to_rgb(hue, lightness, muted_saturation)
        yield tuple(round(channel * 255) for channel in candidate)  # type: ignore[misc]


def choose_color(
    photo_palette: list[PaletteColor],
    sticker_palette: list[PaletteColor],
    text_color: tuple[int, int, int],
    min_contrast: float,
    min_sticker_distance: float,
) -> list[dict[str, object]]:
    chromatic_sources = []
    for item in photo_palette[:16]:
        _hue, lightness, saturation = colorsys.rgb_to_hls(*(value / 255.0 for value in item.rgb))
        if saturation >= 0.12 and 0.08 < lightness < 0.92:
            chromatic_sources.append(item)
    sources = chromatic_sources or photo_palette[:8]
    max_weight = max(item.weight for item in sources)

    sticker_entries = []
    for item in sticker_palette[:16]:
        hue, lightness, saturation = colorsys.rgb_to_hls(*(value / 255.0 for value in item.rgb))
        if saturation >= 0.14 and 0.12 < lightness < 0.88:
            sticker_entries.append((item, hue, saturation))

    ranked: list[dict[str, object]] = []
    seen: set[tuple[int, int, int]] = set()
    for source in sources:
        source_hue, _source_lightness, _source_saturation = colorsys.rgb_to_hls(
            *(value / 255.0 for value in source.rgb)
        )
        prominence = source.weight / max_weight
        overlap = sum(
            item.weight
            for item, sticker_hue, _sticker_saturation in sticker_entries
            if hue_distance(source_hue, sticker_hue) <= 18.0
        )
        for candidate in card_variants(source):
            if candidate in seen:
                continue
            seen.add(candidate)
            contrast = contrast_ratio(candidate, text_color)
            if contrast < min_contrast:
                continue
            nearest = min((delta_e(candidate, item.rgb) for item, _hue, _sat in sticker_entries), default=100.0)
            if nearest < min_sticker_distance:
                continue
            distance_quality = min(nearest / 45.0, 1.0)
            contrast_quality = min(max(contrast - min_contrast, 0.0) / 4.0, 1.0)
            score = 2.2 * (1.0 - min(overlap, 1.0)) + 0.9 * prominence + 0.8 * distance_quality + 0.2 * contrast_quality
            ranked.append(
                {
                    "hex": as_hex(candidate),
                    "rgb": list(candidate),
                    "source_hex": as_hex(source.rgb),
                    "source_prominence": round(prominence, 4),
                    "sticker_hue_overlap": round(overlap, 4),
                    "nearest_sticker_delta_e": round(nearest, 2),
                    "cream_text_contrast": round(contrast, 2),
                    "score": round(score, 4),
                }
            )
    if not ranked:
        raise ValueError("no candidate met the contrast and sticker-separation thresholds")
    return sorted(ranked, key=lambda item: float(item["score"]), reverse=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--photos", nargs="+", type=Path, required=True, help="one or more source photos")
    parser.add_argument(
        "--stickers",
        type=Path,
        nargs="+",
        required=True,
        help="validated transparent sticker files or directories",
    )
    parser.add_argument("--text-color", type=parse_hex, default=parse_hex("#F4E7C8"))
    parser.add_argument("--min-contrast", type=float, default=4.5)
    parser.add_argument("--min-sticker-distance", type=float, default=18.0)
    parser.add_argument("--out", type=Path, help="optional JSON output path")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    photo_palette = quantized_palette(args.photos, stickers=False)
    sticker_paths: list[Path] = []
    for value in args.stickers:
        sticker_paths.extend(resolve_sticker_paths(value))
    sticker_palette = quantized_palette(sticker_paths, stickers=True)
    ranked = choose_color(
        photo_palette,
        sticker_palette,
        args.text_color,
        args.min_contrast,
        args.min_sticker_distance,
    )
    payload = {
        "selected": ranked[0],
        "text_hex": as_hex(args.text_color),
        "minimum_contrast": args.min_contrast,
        "minimum_sticker_delta_e": args.min_sticker_distance,
        "alternates": ranked[1:5],
    }
    output = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
