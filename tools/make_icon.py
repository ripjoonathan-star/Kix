#!/usr/bin/env python3
"""Generate the Kix launcher icon (512×512 PNG) from `Kix/core/theme.py` tokens.

Idempotent: by default exits 0 silently if the icon already exists.
Usage:  python3 tools/make_icon.py [--force]
Output: Kix/assets/icons/kix.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from Kix.core import theme as _t  # noqa: E402  (sys.path manipulation above)

OUT = REPO / "Kix" / "assets" / "icons" / "kix.png"
SIZE = 512


def _rgba_to_byte(color: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    """Convert Kivy's 0.0–1.0 RGBA tuple into PIL's 0–255 RGBA tuple."""
    r, g, b, a = color
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), int(round(a * 255)))


def render() -> Image.Image:
    bg = _rgba_to_byte(_t.CAT_USER)  # deep indigo/purple
    fg = _rgba_to_byte(_t.WHITE)

    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Filled circle background.
    d.ellipse((0, 0, SIZE - 1, SIZE - 1), fill=bg)

    # Stylised "K" — vertical stem + upper/lower diagonals, no font dep.
    cx, cy = SIZE // 2, SIZE // 2
    bar_w = 56
    stem_x0 = cx - 96
    stem_x1 = stem_x0 + bar_w
    bar_half = 156

    d.rectangle(
        (stem_x0, cy - bar_half, stem_x1, cy + bar_half),
        fill=fg,
    )

    # Upper diagonal: from top of stem out to the right.
    diag_w = 56
    arm_inner_y = cy - 8
    arm_outer_y = cy - 60
    d.polygon(
        [
            (stem_x1, cy - bar_half),
            (stem_x1 + diag_w, cy - bar_half),
            (cx + 120, arm_inner_y),
            (cx + 120 - diag_w, arm_outer_y),
        ],
        fill=fg,
    )

    # Lower diagonal: from bottom of stem out to the right.
    arm_inner_y2 = cy + 8
    arm_outer_y2 = cy + 60
    d.polygon(
        [
            (stem_x1, cy + bar_half),
            (stem_x1 + diag_w, cy + bar_half),
            (cx + 120, arm_inner_y2),
            (cx + 120 - diag_w, arm_outer_y2),
        ],
        fill=fg,
    )

    return img


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force",
        action="store_true",
        help="regenerate even if the icon already exists",
    )
    args = parser.parse_args()

    if OUT.exists() and not args.force:
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    render().save(OUT, format="PNG", optimize=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())