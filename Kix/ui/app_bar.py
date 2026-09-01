"""TopBar custom — título 'Kix' centralizado, fundo grafite."""

from __future__ import annotations

from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from Kix.core.theme import FONT_SIZE_TITLE, SURFACE_1, TEXT_HIGH

Builder.load_string(
    """
<KixAppBar>:
    size_hint_y: None
    height: dp(56)
    padding: [dp(16), 0, dp(16), 0]
""")


class KixAppBar(BoxLayout):
    """Barra superior fixa (56dp) com título centralizado."""

    def __init__(self, title: str = "Kix", **kwargs):
        super().__init__(orientation="horizontal", **kwargs)
        with self.canvas.before:
            self._bg = Color(*SURFACE_1)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda i, _: setattr(i._rect, "pos", i.pos),
            size=lambda i, _: setattr(i._rect, "size", i.size),
        )
        label = Label(
            text=title,
            font_size=f"{FONT_SIZE_TITLE}sp",
            color=TEXT_HIGH,
            bold=True,
            halign="center",
            valign="middle",
        )
        label.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(label)