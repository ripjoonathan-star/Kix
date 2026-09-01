"""Botões custom do Kix: KixButton (rounded, grafite) e IconButton (circular).

Touch-first: alvos >= TOUCH_MIN dp. Estados visuais discretos via background_color.
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from Kix.core.theme import (
    EMERALD,
    EMERALD_PRESSED,
    PADDING_SM,
    RADIUS,
    RADIUS_SM,
    SURFACE_3,
    SURFACE_4,
    TEXT_HIGH,
    TOUCH_MIN,
)

Builder.load_string(
    """
<KixButton>:
    font_size: '14sp'
    color: 0.93, 0.93, 0.95, 1
    halign: 'center'
    valign: 'middle'
    text_size: self.size
"""
)


class KixButton(ButtonBehavior, Label):
    """Botão arredondado. `primary=True` usa emerald; default é grafite."""

    def __init__(self, text: str = "", primary: bool = False, **kwargs):
        super().__init__(text=text, **kwargs)
        self._primary = primary
        self._build_graphics()

    def _build_graphics(self) -> None:
        with self.canvas.before:
            base = EMERALD if self._primary else SURFACE_3
            self._bg_color = Color(*base)
            self._rect = RoundedRectangle(
                radius=[dp(RADIUS_SM)], pos=self.pos, size=self.size
            )
        self.bind(pos=self._update_rect, size=self._update_rect, state=self._on_state)

    def _update_rect(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _on_state(self, *_):
        if self._primary:
            self._bg_color.rgba = EMERALD_PRESSED if self.state == "down" else EMERALD
        else:
            self._bg_color.rgba = SURFACE_4 if self.state == "down" else SURFACE_3


class IconButton(ButtonBehavior, BoxLayout):
    """Botão circular pequeno — primário (esmeralda) por padrão."""

    def __init__(self, glyph: str = "✎", primary: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(TOUCH_MIN), dp(TOUCH_MIN))
        self.padding = dp(PADDING_SM)
        self._label = Label(text=glyph, font_size="18sp", color=TEXT_HIGH)
        self._label.halign = "center"
        self._label.valign = "middle"
        self._label.bind(size=lambda inst, _: setattr(inst, "text_size", inst.size))
        self.add_widget(self._label)
        self._build_graphics(primary)
        self.bind(pos=self._update_rect, size=self._update_rect, state=self._on_state)

    def _build_graphics(self, primary: bool) -> None:
        with self.canvas.before:
            base = EMERALD if primary else SURFACE_3
            self._bg_color = Color(*base)
            self._rect = RoundedRectangle(
                radius=[dp(RADIUS)], pos=self.pos, size=self.size
            )

    def _update_rect(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _on_state(self, *_):
        if self.state == "down":
            self._bg_color.rgba = EMERALD_PRESSED if self._bg_color.rgba == EMERALD else SURFACE_4
        else:
            self._bg_color.rgba = EMERALD if self._bg_color.rgba in (EMERALD_PRESSED,) else SURFACE_3