"""Renderiza o ícone da cobra Python via Pillow (verificação headless).

Replica a geometria de ``Kix.ui.block_render.draw_python_cobra_icon``
sem precisar do Kivy Window (não inicializa sem display).

Uso:
    python3 -m tools.render_python_icon /tmp/python_icon.png
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

from Kix.core.theme import BLOCK_ICON_OUTLINE, CAT_PYTHON


def _cubic_bezier(p0, p1, p2, p3, n: int = 48) -> list[tuple[float, float]]:
    """Amostra cubic Bezier — espelha ``_cubic_bezier_points`` de block_render."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = (u**3 * p0[0] + 3 * u**2 * t * p1[0]
             + 3 * u * t**2 * p2[0] + t**3 * p3[0])
        y = (u**3 * p0[1] + 3 * u**2 * t * p1[1]
             + 3 * u * t**2 * p2[1] + t**3 * p3[1])
        pts.append((x, y))
    return pts


def _to_rgb_int(rgba, alpha_blend_on=(0, 0, 0)) -> tuple[int, int, int]:
    """Converte RGBA 0..1 → RGB 0..255 aplicando alpha sobre fundo."""
    r, g, b, a = rgba
    ar, ag, ab = alpha_blend_on
    rr = int(((1 - a) * ar + a * r) * 255)
    gg = int(((1 - a) * ag + a * g) * 255)
    bb = int(((1 - a) * ab + a * b) * 255)
    return (rr, gg, bb)


def render(out_path: Path) -> None:
    """Desenha o ícone em fundo transparente (PNG RGBA)."""
    s = 256
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # Bloco azul de fundo (CAT_PYTHON) — mostra contexto visual
    pad = 32
    draw.rectangle(
        [pad, pad, s - pad, s - pad],
        fill=_to_rgb_int(CAT_PYTHON),
    )
    # Inner border sutil
    draw.rectangle(
        [pad, pad, s - pad, s - pad],
        outline=(255, 255, 255, 60), width=2,
    )

    # Cobra — espelha draw_python_cobra_icon: size=s-padding*2 ~ 192
    icon_s = s - pad * 2
    ix, iy = pad, pad  # canto sup-esq da área do ícone

    # Cobra A: inf-esq → sup-dir
    snake_a = _cubic_bezier(
        p0=(ix + 3 * icon_s / 32,       iy + icon_s - 3 * icon_s / 32),
        p1=(ix + 3 * icon_s / 32,       iy + icon_s + 4 * icon_s / 32),
        p2=(ix + icon_s - 3 * icon_s / 32, iy - 4 * icon_s / 32),
        p3=(ix + icon_s - 3 * icon_s / 32, iy + 3 * icon_s / 32),
    )
    # Espelha coordenadas (block_render usa y crescente p/ cima)
    snake_a_img = [(x, iy + icon_s - (y - iy)) for x, y in snake_a]

    # Cobra B: sup-esq → inf-dir
    snake_b = _cubic_bezier(
        p0=(ix + 3 * icon_s / 32,       iy + 3 * icon_s / 32),
        p1=(ix + 3 * icon_s / 32,       iy - 4 * icon_s / 32),
        p2=(ix + icon_s - 3 * icon_s / 32, iy + icon_s + 4 * icon_s / 32),
        p3=(ix + icon_s - 3 * icon_s / 32, iy + icon_s - 3 * icon_s / 32),
    )
    snake_b_img = [(x, iy + icon_s - (y - iy)) for x, y in snake_b]

    stroke = _to_rgb_int(BLOCK_ICON_OUTLINE)
    draw.line(snake_a_img, fill=stroke, width=14, joint="curve")
    draw.line(snake_b_img, fill=stroke, width=14, joint="curve")

    # Olhos (cabeças)
    eye_r = max(4, int(icon_s * 0.08))
    eye_color = _to_rgb_int(BLOCK_ICON_OUTLINE)
    # Cobra A head no canto inf-dir do bloco
    draw.ellipse(
        [ix + icon_s - 8 - eye_r, iy + icon_s - 8 - eye_r,
         ix + icon_s - 8 + eye_r, iy + icon_s - 8 + eye_r],
        fill=eye_color,
    )
    # Cobra B head no canto sup-esq do bloco
    draw.ellipse(
        [ix + 6, iy + 6, ix + 6 + eye_r * 2, iy + 6 + eye_r * 2],
        fill=eye_color,
    )

    img.save(out_path)
    print(f"saved → {out_path}")


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/python_icon.png")
    render(out)
