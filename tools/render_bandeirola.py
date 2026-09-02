"""Renderiza a silhueta bandeirola via Pillow (verificação visual headless).

Não usa Kivy Window (não inicializa sem display). Replica a geometria de
``Kix.ui.block_render.bandeirola_mesh`` e desenha polígonos diretamente
com PIL — mesmo padrão de ``Kix/render/png.py``.

Uso:
    python3 -m tools.render_bandeirola /tmp/bandeirola.png
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

from Kix.core import theme
from Kix.core.theme import (
    BLOCK_CORNER_RADIUS,
    BLOCK_ICON_OUTLINE,
    BLOCK_MIN_HEIGHT,
    BLOCK_PADDING_LEFT,
    BLOCK_TEXT_START_X,
    BLOCK_WAVE_AMPLITUDE,
    SURFACE_1,
    TEXT_HIGH,
    BG,
    cat_color,
)


DEMO = [
    ("event.when_started",   "Quando o jogo começa"),
    ("motion.move",          "Mover 10 passos"),
    ("looks.say",            "Dizer Olá! por 2s"),
    ("control.wait",         "Esperar 1 segundo"),
    ("sound.play",           "Tocar som Pop"),
    ("physics.gravity",      "Definir gravidade 9.8"),
]


def _wave_polygon(width: float, height: float, amplitude: float,
                  corner_radius: float = BLOCK_CORNER_RADIUS,
                  segments: int = 24) -> list[tuple[float, float]]:
    """Bordeirola como polígono fechado (sentido horário a partir do canto sup-esq)."""
    r = min(corner_radius, width / 2, height / 2)
    pts: list[tuple[float, float]] = []

    # Top wave (esq → dir)
    for i in range(segments + 1):
        t = i / segments
        x = r + (width - 2 * r) * t
        y = -4 * amplitude * t * (1 - t)
        pts.append((x, y))

    # Right side (top → bottom)
    pts.append((width, height - r))

    # Bottom wave (dir → esq, espelhado)
    for i in range(segments, -1, -1):
        t = i / segments
        x = r + (width - 2 * r) * t
        y = height + 4 * amplitude * t * (1 - t)
        pts.append((x, y))

    # Left side (bottom → top)
    pts.append((0.0, r))

    return pts


def _rgba_to_int(rgba: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    r, g, b, a = rgba
    return (int(r * 255), int(g * 255), int(b * 255), int(a * 255))


def _render_block(
    draw: ImageDraw.ImageDraw, x: float, y: float,
    width: float, height: float, label_text: str, color,
) -> None:
    """Desenha 1 bloco no canvas."""
    amp = BLOCK_WAVE_AMPLITUDE
    poly_local = _wave_polygon(width, height, amp)
    poly = [(p[0] + x, p[1] + y) for p in poly_local]
    draw.polygon(poly, fill=_rgba_to_int(color))

    # Ícone (canto esq)
    icon_size = 32
    icon_x = x + BLOCK_PADDING_LEFT
    icon_y = y + (height - icon_size) / 2
    fold = icon_size * 0.25
    # contorno da página
    page = [
        (icon_x + fold, icon_y),
        (icon_x + icon_size, icon_y),
        (icon_x + icon_size, icon_y + icon_size),
        (icon_x, icon_y + icon_size),
        (icon_x, icon_y + fold),
        (icon_x + fold, icon_y),
    ]
    draw.line(page, fill=_rgba_to_int(BLOCK_ICON_OUTLINE), width=2, joint="curve")
    # dobra
    draw.line(
        [(icon_x, icon_y + fold), (icon_x + fold, icon_y + fold),
         (icon_x + fold, icon_y)],
        fill=_rgba_to_int(BLOCK_ICON_OUTLINE), width=1,
    )
    # 3 linhas de roteiro
    m = icon_size * 0.18
    top_pad = icon_size * 0.42
    line_gap = icon_size * 0.16
    for i in range(3):
        line_y = icon_y + top_pad + i * line_gap
        draw.line(
            [(icon_x + m, line_y), (icon_x + icon_size - m, line_y)],
            fill=_rgba_to_int(BLOCK_ICON_OUTLINE), width=1,
        )

    # label do bloco — esquerda, branco, x=BLOCK_TEXT_START_X
    text_x = x + BLOCK_TEXT_START_X
    text_y = y + (height - 20) / 2  # fonte 18sp ≈ 24px; centro vertical
    draw.text(
        (text_x, text_y),
        label_text, fill=_rgba_to_int(TEXT_HIGH),
    )


def render(out_path: Path) -> None:
    img_w, img_h = 360, 720
    img = Image.new("RGBA", (img_w, img_h), _rgba_to_int(BG))
    draw = ImageDraw.Draw(img, "RGBA")

    block_w = img_w - 32  # margem lateral 16px
    block_h = BLOCK_MIN_HEIGHT
    gap = 0
    x0 = 16
    y0 = 60  # abaixo do título

    # título
    draw.text((16, 24), "Kix — silhueta bandeirola (spec 2.2)",
              fill=_rgba_to_int((0.62, 0.62, 0.62, 1)))

    for i, (_id, label) in enumerate(DEMO):
        category = _id.split(".")[0]
        color = cat_color(category, "base") if category in {
            "motion", "looks", "sound", "control", "event", "data",
            "device", "files", "pen",
        } else SURFACE_1
        bx = x0
        by = y0 + i * (block_h + gap)
        _render_block(draw, bx, by, block_w, block_h, label, color)

    img.save(out_path)
    print(f"saved → {out_path}")


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/bandeirola.png")
    render(out)