"""Renderização headless do palco Kix.

Permite gerar PNGs do estado do `RuntimeContext` sem precisar do Kivy.
Usa Pillow (já vem como dependência transitiva do Kivy).
"""

from Kix.render.png import render_ctx_to_png, render_sprite_to_image

__all__ = ["render_ctx_to_png", "render_sprite_to_image"]
