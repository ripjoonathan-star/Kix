"""KixAppBar — barra superior (mobile-first).

Layout (Pocket Code):
[ ← (opcional) ]   Título centralizado   [ ações à direita ]

`set_title(text)` atualiza o título.
`set_actions([(key, glyph, callback), ...])` define botões à direita.
Se o primeiro glyph for '←', vira botão de back (canto esquerdo).
"""

from __future__ import annotations

from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label

from Kix.core.theme import FONT_SIZE_TITLE, SURFACE_1, TEXT_HIGH, TEXT_MED
from Kix.ui.button import IconButton


class _TitleLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = "center"
        self.valign = "middle"
        self.bind(size=lambda i, _: setattr(i, "text_size", i.size))


class KixAppBar(BoxLayout):
    """Barra superior fixa (56dp) com título centralizado + ações."""

    def __init__(self, title: str = "Kix", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(56)
        self.padding = [dp(8), 0, dp(8), 0]
        with self.canvas.before:
            self._bg = Color(*SURFACE_1)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda i, _: setattr(i._rect, "pos", i.pos),
            size=lambda i, _: setattr(i._rect, "size", i.size),
        )

        self._back = None       # botão voltar (canto esquerdo)
        self._title_lbl = _TitleLabel(text=title)
        self._actions = {}      # key → IconButton

        self.add_widget(self._title_lbl)

    # --- API --------------------------------------------------------------
    def set_title(self, text: str) -> None:
        self._title_lbl.text = text

    def set_back(self, on_back) -> None:
        """Botão ← canto esquerdo."""
        if self._back is None:
            self._back = IconButton(glyph="←", primary=False)
            self._back.size_hint = (None, None)
            self._back.size = (dp(40), dp(40))
            # insere como primeiro widget
            self.remove_widget(self._title_lbl)
            self.add_widget(self._back)
            self.add_widget(self._title_lbl)
        self._back.bind(on_release=lambda *_: on_back())

    def set_actions(self, actions: list[tuple]) -> None:
        """Define botões à direita.

        `actions`: lista de `(key, glyph, callback)`.
        """
        # remove actions antigas
        for btn in self._actions.values():
            if btn.parent is self:
                self.remove_widget(btn)
        self._actions.clear()

        # título cresce; actions à direita
        for key, glyph, cb in actions:
            btn = IconButton(glyph=glyph, primary=False)
            btn.size_hint = (None, None)
            btn.size = (dp(40), dp(40))
            btn.bind(on_release=lambda *_, c=cb: c())
            self._actions[key] = btn
            self.add_widget(btn)


__all__ = ["KixAppBar"]
