"""Renderização headless do palco → PNG via Pillow.

O renderer desenha:
- fundo da cena (cor sólida ou listrada de fallback);
- sprite ativo centralizado (rotacionado, com opacidade/tint aplicados);
- fallback visual quando o sprite está invisível (X tracejado).

Coordenadas:
- O `Stage` tem largura × altura em "pixels lógicos" do projeto.
- A origem (0,0) é o centro do palco (convenção Scratch).
- (x positivo, y positivo) → direita e cima.

O PNG resultante tem tamanho `width × height` (1 pixel = 1 unidade lógica).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw

if TYPE_CHECKING:
    from Kix.engine.ctx import RuntimeContext, SpriteProxy


# --- helpers ---------------------------------------------------------------
def _parse_hex_color(value: str, default: tuple[int, int, int] = (255, 255, 255)) -> tuple[int, int, int]:
    """Converte '#RRGGBB' ou '#AARRGGBB' → (R,G,B). Fallback se inválido."""
    if not isinstance(value, str):
        return default
    s = value.strip().lstrip("#")
    if len(s) == 6:
        try:
            return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
        except ValueError:
            return default
    if len(s) == 8:
        try:
            return (int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16))
        except ValueError:
            return default
    return default


def _apply_alpha(rgb: tuple[int, int, int], alpha: float) -> tuple[int, int, int, int]:
    a = max(0, min(255, int(round(alpha * 255))))
    return (rgb[0], rgb[1], rgb[2], a)


def _sprite_fill_color(sprite: "SpriteProxy") -> tuple[int, int, int]:
    """Cor base do sprite: usa tint (RGB 0..1) → 0..255."""
    t = sprite.tint
    r = max(0, min(255, int(round(t[0] * 255))))
    g = max(0, min(255, int(round(t[1] * 255))))
    b = max(0, min(255, int(round(t[2] * 255))))
    return (r, g, b)


def _draw_background(img: Image.Image, draw: ImageDraw.ImageDraw, bg: str) -> None:
    color = _parse_hex_color(bg, default=(255, 255, 255))
    draw.rectangle([(0, 0), img.size], fill=color)


def _draw_sprite(img: Image.Image, draw: ImageDraw.ImageDraw, sprite: "SpriteProxy") -> None:
    """Desenha o sprite centralizado em sprite.position, com rotação/opacidade/tint."""
    w, h = img.size
    cx, cy = w / 2 + sprite.position[0], h / 2 - sprite.position[1]   # y cresce para baixo na imagem

    # Tamanho efetivo: fw × fh escalado por sprite.scale
    fw = max(1.0, sprite.fw * sprite.scale)
    fh = max(1.0, sprite.fh * sprite.scale)

    # Cantos do retângulo não-rotacionado (centralizado na origem).
    half_w, half_h = fw / 2.0, fh / 2.0
    corners = [(-half_w, -half_h), (half_w, -half_h), (half_w, half_h), (-half_w, half_h)]

    # Aplica rotação (em graus; convenção Kivy/Sprite: positivo = anti-horário).
    import math
    rad = math.radians(sprite.rotation)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    rotated = [(cx + x * cos_a - y * sin_a, cy + x * sin_a + y * cos_a) for x, y in corners]

    if not sprite.visible:
        # X tracejado no lugar do sprite
        outline = (200, 200, 200, 200)
        draw.line([rotated[0], rotated[2]], fill=outline, width=2)
        draw.line([rotated[1], rotated[3]], fill=outline, width=2)
        return

    fill = _apply_alpha(_sprite_fill_color(sprite), sprite.opacity)
    draw.polygon(rotated, fill=fill, outline=(0, 0, 0, 220))


# --- API pública -----------------------------------------------------------
def render_sprite_to_image(sprite: "SpriteProxy", *, width: int = 390, height: int = 844,
                            background: str = "#FFFFFF") -> Image.Image:
    """Renderiza um sprite isolado (palco centrado) em uma Image Pillow."""
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_background(img, draw, background)
    _draw_sprite(img, draw, sprite)
    return img


def render_ctx_to_png(ctx: "RuntimeContext", out_path: str | Path) -> Path:
    """Renderiza o `RuntimeContext` (palco + sprite ativo) para um PNG em `out_path`."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    w = int(ctx.stage.width)
    h = int(ctx.stage.height)
    bg_rgba = ctx.stage.background  # tuple[float,float,float,float]
    bg = "#{:02X}{:02X}{:02X}".format(
        int(round(bg_rgba[0] * 255)),
        int(round(bg_rgba[1] * 255)),
        int(round(bg_rgba[2] * 255)),
    )

    sprite = ctx.stage.active
    if sprite is None:
        # sem sprite ativo: só fundo
        img = Image.new("RGBA", (w, h), _parse_hex_color(bg) + (255,))
    else:
        img = render_sprite_to_image(sprite, width=w, height=h, background=bg)

    img.save(out, format="PNG")
    return out


__all__ = ["render_ctx_to_png", "render_sprite_to_image"]
