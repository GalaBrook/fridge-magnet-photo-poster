#!/usr/bin/env python3
"""Compose a deterministic 3:4 magnet/photo travel poster."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--photo", required=True, type=Path)
    parser.add_argument("--magnet", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--background", required=True)
    parser.add_argument("--key-color", default="#00ff00")
    parser.add_argument("--width", type=int, default=1536)
    parser.add_argument("--height", type=int, default=2048)
    parser.add_argument("--font", type=Path)
    return parser.parse_args()


def cover_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def corner_key(image: Image.Image) -> tuple[int, int, int]:
    rgb = image.convert("RGB")
    sample = max(4, min(rgb.size) // 80)
    points = [
        (sample, sample),
        (rgb.width - sample - 1, sample),
        (sample, rgb.height - sample - 1),
        (rgb.width - sample - 1, rgb.height - sample - 1),
    ]
    values = [rgb.getpixel(point) for point in points]
    return tuple(round(sum(value[i] for value in values) / len(values)) for i in range(3))


def remove_key(image: Image.Image, key_spec: str) -> Image.Image:
    rgba = image.convert("RGBA")
    existing_alpha = rgba.getchannel("A")
    if existing_alpha.getextrema()[0] < 255:
        bbox = existing_alpha.getbbox()
        if bbox is None:
            raise RuntimeError("Transparent magnet image contains no visible pixels")
        padding = max(8, min(rgba.size) // 80)
        left = max(0, bbox[0] - padding)
        top = max(0, bbox[1] - padding)
        right = min(rgba.width, bbox[2] + padding)
        bottom = min(rgba.height, bbox[3] + padding)
        return rgba.crop((left, top, right, bottom))

    key = corner_key(rgba) if key_spec.lower() == "auto" else ImageColor.getrgb(key_spec)
    pixels = rgba.load()
    mask = Image.new("L", rgba.size, 0)
    alpha = mask.load()

    inner, outer = 42.0, 135.0
    for y in range(rgba.height):
        for x in range(rgba.width):
            red, green, blue, _ = pixels[x, y]
            distance = math.sqrt(
                (red - key[0]) ** 2 + (green - key[1]) ** 2 + (blue - key[2]) ** 2
            )
            if distance <= inner:
                value = 0
            elif distance >= outer:
                value = 255
            else:
                value = round(255 * (distance - inner) / (outer - inner))
            alpha[x, y] = value

    mask = mask.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(0.8))
    bbox = mask.getbbox()
    if bbox is None:
        raise RuntimeError("Could not isolate the magnet from its background")

    padding = max(8, min(rgba.size) // 80)
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(rgba.width, bbox[2] + padding)
    bottom = min(rgba.height, bbox[3] + padding)
    cutout = rgba.crop((left, top, right, bottom))
    cutout.putalpha(mask.crop((left, top, right, bottom)))
    return cutout


def find_font(explicit: Path | None) -> Path:
    candidates = [
        explicit,
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/System/Library/Fonts/HelveticaNeue.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    raise RuntimeError("No suitable Helvetica-style sans serif font found; pass --font with a local font path")


def fit_title(
    draw: ImageDraw.ImageDraw,
    title: str,
    font_path: Path,
    max_width: int,
) -> tuple[list[str], ImageFont.FreeTypeFont, int]:
    normalized = " ".join(title.strip().split())
    if not normalized:
        raise ValueError("Title cannot be empty")

    line_candidates = [[normalized]]
    words = normalized.split()
    if len(words) > 1:
        for index in range(1, len(words)):
            line_candidates.append([" ".join(words[:index]), " ".join(words[index:])])

    for size in range(50, 27, -1):
        font = ImageFont.truetype(str(font_path), size)
        spacing = max(1, round(size * 0.04))
        for lines in line_candidates:
            widths = [sum(draw.textlength(c, font=font) for c in line) + spacing * (len(line) - 1) for line in lines]
            if max(widths) <= max_width:
                return lines, font, spacing
    raise ValueError("Title is too long; use a concise one-to-three-word English title")


def draw_spaced_line(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    center_x: int,
    y: int,
    fill: tuple[int, int, int],
    spacing: int,
) -> None:
    widths = [draw.textlength(char, font=font) for char in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = center_x - total / 2
    for char, width in zip(text, widths):
        draw.text((round(x), y), char, font=font, fill=fill)
        x += width + spacing


def contrasting_text(background: tuple[int, int, int]) -> tuple[int, int, int]:
    luminance = 0.2126 * background[0] + 0.7152 * background[1] + 0.0722 * background[2]
    return (38, 42, 42) if luminance > 155 else (248, 246, 238)


def main() -> None:
    args = parse_args()
    if args.width <= 0 or args.height <= 0 or args.width * 4 != args.height * 3:
        raise ValueError("Canvas must use an exact 3:4 ratio")
    if args.height % 2:
        raise ValueError("Canvas height must be even for equal panels")
    if args.output.resolve() == args.photo.resolve():
        raise ValueError("Output must not overwrite the source photo")

    background = ImageColor.getrgb(args.background)
    panel_height = args.height // 2
    poster = Image.new("RGB", (args.width, args.height), background)

    magnet = remove_key(Image.open(args.magnet), args.key_color)
    max_magnet_w = round(args.width * 0.42)
    max_magnet_h = round(panel_height * 0.48)
    scale = min(max_magnet_w / magnet.width, max_magnet_h / magnet.height)
    magnet = magnet.resize(
        (round(magnet.width * scale), round(magnet.height * scale)),
        Image.Resampling.LANCZOS,
    )
    draw = ImageDraw.Draw(poster)
    font_path = find_font(args.font)
    lines, font, letter_spacing = fit_title(draw, args.title, font_path, round(args.width * 0.76))
    line_height = round(font.size * 1.25)
    title_block_h = line_height * len(lines)
    gap = round(panel_height * 0.045)
    group_height = magnet.height + gap + title_block_h
    group_center_y = round(panel_height * 0.52)
    magnet_x = (args.width - magnet.width) // 2
    magnet_y = group_center_y - group_height // 2
    title_y = magnet_y + magnet.height + gap
    poster.paste(magnet, (magnet_x, magnet_y), magnet)
    for index, line in enumerate(lines):
        draw_spaced_line(
            draw,
            line,
            font,
            args.width // 2,
            title_y + index * line_height,
            contrasting_text(background),
            letter_spacing,
        )

    photo = cover_crop(Image.open(args.photo).convert("RGB"), (args.width, panel_height))
    poster.paste(photo, (0, panel_height))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    poster.save(args.output, "PNG", optimize=True)
    print(
        {
            "path": str(args.output),
            "size": poster.size,
            "split_y": panel_height,
            "title": " ".join(args.title.strip().split()),
            "background": "#%02x%02x%02x" % background,
        }
    )


if __name__ == "__main__":
    main()
