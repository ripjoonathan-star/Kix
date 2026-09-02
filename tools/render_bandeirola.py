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
    BLOCK_HEIGHT_2_LINES,
    BLOCK_ICON_OUTLINE,
    BLOCK_MIN_HEIGHT,
    BLOCK_PADDING_LEFT,
    BLOCK_PARAM_UNDERLINE,
    BLOCK_TEXT_START_X,
    BLOCK_WAVE_AMPLITUDE,
    SURFACE_1,
    TEXT_HIGH,
    BG,
    cat_color,
)


DEMO = [
    # (block_id, label_linha1, params_linha2_ou_None)
    ("event.when_started",   "Quando o jogo começa", None),
    ("motion.move",          "Mover passos",         "steps=10"),
    ("looks.say",            "Dizer por segundos",   "texto=Olá!, secs=2"),
    ("control.wait",         "Esperar segundos",     "secs=1"),
    ("sound.play",           "Tocar som",            "som=Pop"),
    ("physics.gravity",      "Definir gravidade",    "valor=9.8"),
    ("physics.add_wall",     "Adicionar parede",     None),
    ("network.connect",      "Conectar servidor",    "host=localhost"),
    ("storage.save",         "Salvar progresso",     "slot=1"),
    ("ai.pathfind",          "Pathfinding para",     "alvo=Player"),
    ("particles.emit",       "Emitir partículas",    "qtd=20, tipo=fogo"),
    ("tilemap.tile_at",      "Tile em linha/col",    "linha=0, col=0"),
    ("motion.move_xy",       "Mover x/y",            "dx=10, dy=0"),
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
    width: float, label_text: str, params_text: str | None, color,
) -> None:
    """Desenha 1 bloco no canvas (1 linha se params_text=None, 2 linhas caso contrário)."""
    has_params = params_text is not None
    height = BLOCK_HEIGHT_2_LINES if has_params else BLOCK_MIN_HEIGHT

    amp = BLOCK_WAVE_AMPLITUDE
    poly_local = _wave_polygon(width, height, amp)
    poly = [(p[0] + x, p[1] + y) for p in poly_local]
    draw.polygon(poly, fill=_rgba_to_int(color))

    # Ícone (canto esq, centralizado vertical)
    icon_size = 32
    icon_x = x + BLOCK_PADDING_LEFT
    icon_y = y + (height - icon_size) / 2
    fold = icon_size * 0.25
    page = [
        (icon_x + fold, icon_y),
        (icon_x + icon_size, icon_y),
        (icon_x + icon_size, icon_y + icon_size),
        (icon_x, icon_y + icon_size),
        (icon_x, icon_y + fold),
        (icon_x + fold, icon_y),
    ]
    draw.line(page, fill=_rgba_to_int(BLOCK_ICON_OUTLINE), width=2, joint="curve")
    draw.line(
        [(icon_x, icon_y + fold), (icon_x + fold, icon_y + fold),
         (icon_x + fold, icon_y)],
        fill=_rgba_to_int(BLOCK_ICON_OUTLINE), width=1,
    )
    m = icon_size * 0.18
    top_pad = icon_size * 0.42
    line_gap = icon_size * 0.16
    for i in range(3):
        line_y = icon_y + top_pad + i * line_gap
        draw.line(
            [(icon_x + m, line_y), (icon_x + icon_size - m, line_y)],
            fill=_rgba_to_int(BLOCK_ICON_OUTLINE), width=1,
        )

    # Linha 1 — rótulo do bloco (label do nó), x = BLOCK_TEXT_START_X.
    # Spec 2.2: 1 linha = vertical centro; 2 linhas = rótulo @28px do topo.
    text_x = x + BLOCK_TEXT_START_X
    if has_params:
        line1_y = y + 28 - 18  # baseline (top + 28) - ascent ≈ 18sp
    else:
        line1_y = y + (height - 20) / 2
    draw.text((text_x, line1_y), label_text, fill=_rgba_to_int(TEXT_HIGH))

    # Linha 2 — params com underline 1.5px (spec 2.2)
    if has_params:
        line2_y = y + 72 - 14
        draw.text((text_x + 4, line2_y), params_text, fill=_rgba_to_int(TEXT_HIGH))
        # underline 1.5px — cobre todo o texto da linha 2
        text_w = int(len(params_text) * 7.2)  # ~7.2 px/char @14sp
        draw.line(
            [(text_x + 4, line2_y + 18), (text_x + 4 + text_w, line2_y + 18)],
            fill=_rgba_to_int((1, 1, 1, 0.6)), width=2,
        )


def render(out_path: Path) -> None:
    img_w, img_h = 360, 1100
    img = Image.new("RGBA", (img_w, img_h), _rgba_to_int(BG))
    draw = ImageDraw.Draw(img, "RGBA")

    block_w = img_w - 32  # margem lateral 16px
    gap = 0
    x0 = 16
    y0 = 60  # abaixo do título

    # título
    draw.text((16, 24), "Kix — silhueta bandeirola (spec 2.2)",
              fill=_rgba_to_int((0.62, 0.62, 0.62, 1)))

    cursor_y = y0
    for _id, label, params in DEMO:
        category = _id.split(".")[0]
        # Tenta via cat_color() (Pocket Code + spec 3.1). Fallback SURFACE_1
        # para categorias sem two-tone canônico.
        try:
            color = cat_color(category, "base")
            # cat_color devolve SURFACE_3 (0.051,0.051,0.051,1) p/ cat. desconhecida
            if color == (0.051, 0.051, 0.051, 1) and category not in {
                "layers", "shaders", "ui", "spritesheet", "joystick", "math",
                "strings", "audio_advanced", "scenes", "notifications", "arvr",
                "user", "libs", "camera", "sensing",
            }:
                color = SURFACE_1
        except Exception:
            color = SURFACE_1
        block_h = BLOCK_HEIGHT_2_LINES if params else BLOCK_MIN_HEIGHT
        _render_block(draw, x0, cursor_y, block_w, label, params, color)
        cursor_y += block_h + gap

    img.save(out_path)
    print(f"saved → {out_path}")


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/bandeirola.png")
    render(out)