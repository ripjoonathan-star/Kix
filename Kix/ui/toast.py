"""Toast — popup efêmero no centro inferior da tela.

Uso: Toast("Mensagem").show(parent)
Auto-remove após 2s via Clock.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from Kix.core.theme import RADIUS_SM, SURFACE_3, TEXT_HIGH


class Toast(FloatLayout):
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        # sem overlay (toast não bloqueia)
        self.size_hint = (None, None)
        self.size = (dp(280), dp(56))
        self._label = Label(
            text=text, color=TEXT_HIGH, font_size="13sp",
            halign="center", valign="middle",
            padding=[dp(12), dp(8)],
        )
        self._label.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        with self.canvas.before:
            Color(*SURFACE_3)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[RADIUS_SM])
        self.bind(pos=self._sync, size=self._sync)
        self.add_widget(self._label)

    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def show(self, parent) -> None:
        if parent is None:
            return
        parent.add_widget(self)
        # posição: centro inferior
        Clock.schedule_once(lambda *_: self._place(parent), 0)
        # auto-remove
        Clock.schedule_once(lambda *_: self._dismiss(parent), 2.0)

    def _place(self, parent) -> None:
        self.x = parent.width / 2 - self.width / 2
        self.y = dp(120)

    def _dismiss(self, parent) -> None:
        if self.parent is parent:
            parent.remove_widget(self)


__all__ = ["Toast"]
