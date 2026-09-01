"""Mini-dialog para renomear objeto.

Reusa o estilo do NewProjectDialog mas mais simples: só nome.
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from Kix.core.theme import (
    PADDING_LG,
    RADIUS,
    SURFACE_2,
    SURFACE_3,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
)
from Kix.ui.button import KixButton


class RenameObjectDialog(FloatLayout):
    """Popup modal com campo de texto + botões Renomear/Cancelar."""

    def __init__(self, initial: str = "", on_done=None, on_cancel=None, **kwargs):
        super().__init__(**kwargs)
        self._on_done = on_done or (lambda name: None)
        self._on_cancel = on_cancel or (lambda: None)

        with self.canvas.before:
            Color(0, 0, 0, 0.55)
            self._overlay = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[0]
            )
        self.bind(pos=self._sync_overlay, size=self._sync_overlay)

        self._card = BoxLayout(
            orientation="vertical",
            padding=[PADDING_LG, PADDING_LG, PADDING_LG, PADDING_LG],
            spacing=dp(12),
            size_hint=(None, None),
            width=dp(320),
            height=dp(220),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        with self._card.canvas.before:
            Color(*SURFACE_2)
            self._card_bg = RoundedRectangle(
                radius=[RADIUS], pos=self._card.pos, size=self._card.size
            )
        self._card.bind(pos=self._sync_card_bg, size=self._sync_card_bg)
        self.add_widget(self._card)

        title = Label(
            text="Mudar nome",
            color=TEXT_HIGH,
            font_size="16sp",
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(28),
        )
        title.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self._card.add_widget(title)

        self._input = TextInput(
            text=initial,
            multiline=False,
            font_size="15sp",
            foreground_color=TEXT_HIGH,
            background_color=SURFACE_3,
            cursor_color=(1, 1, 1, 1),
            padding=[dp(10), dp(8), dp(10), dp(8)],
        )
        self._card.add_widget(self._input)

        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10),
        )
        cancel = KixButton(text="Cancelar")
        ok = KixButton(text="Renomear", primary=True)
        cancel.bind(on_release=lambda *_: self._cancel())
        ok.bind(on_release=lambda *_: self._done())
        row.add_widget(cancel)
        row.add_widget(ok)
        self._card.add_widget(row)

    def _sync_overlay(self, *_):
        if hasattr(self, "_overlay") and self._overlay is not None:
            self.canvas.before.remove(self._overlay)
        with self.canvas.before:
            Color(0, 0, 0, 0.55)
            from kivy.graphics import Rectangle
            self._overlay = Rectangle(pos=self.pos, size=self.size)
        if self._card in self.children:
            self.remove_widget(self._card)
            self.add_widget(self._card)

    def _sync_card_bg(self, *_):
        self._card_bg.pos = self._card.pos
        self._card_bg.size = self._card.size

    def _cancel(self):
        if self.parent is not None:
            self.parent.remove_widget(self)
        self._on_cancel()

    def _done(self):
        name = self._input.text.strip()
        if self.parent is not None:
            self.parent.remove_widget(self)
        self._on_done(name)


__all__ = ["RenameObjectDialog"]