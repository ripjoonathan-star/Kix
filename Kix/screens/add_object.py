"""Diálogo "Meu ator ou objeto" — grid 2 colunas com 9 opções.

Replica o grid Pocket Code:
- Desenhar / Biblioteca de mídia
- Selecionar Imagem / Biblioteca
- Tirar foto / Mochila
- Da biblioteca / Objeto vazio
- Projetos locais (linha cheia)
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from Kix.core.theme import (
    EMERALD,
    PADDING,
    PADDING_SM,
    RADIUS,
    RADIUS_SM,
    SURFACE_2,
    SURFACE_3,
    SURFACE_4,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
)
from Kix.projects.model import KixObject


_OPTIONS = [
    {"key": "draw", "label": "Desenhar", "glyph": "✏", "kind": "sprite"},
    {"key": "media", "label": "Biblioteca de mídia", "glyph": "🎞", "kind": "sprite"},
    {"key": "image", "label": "Selecionar Imagem", "glyph": "🖼", "kind": "sprite"},
    {"key": "library", "label": "Biblioteca", "glyph": "📚", "kind": "sprite"},
    {"key": "photo", "label": "Tirar foto", "glyph": "📷", "kind": "sprite"},
    {"key": "backpack", "label": "Mochila", "glyph": "🎒", "kind": "sprite"},
    {"key": "from_lib", "label": "Da biblioteca", "glyph": "📦", "kind": "sprite"},
    {"key": "empty", "label": "Objeto vazio", "glyph": "⭕", "kind": "sprite"},
    {"key": "local", "label": "Projetos locais", "glyph": "💾", "kind": "background", "full": True},
]


class _GridItem(BoxLayout):
    """Item do grid 2×4 — ícone + label, com hover."""

    def __init__(self, glyph: str, label: str, on_select, **kwargs):
        super().__init__(**kwargs)
        self._on_select = on_select
        self.orientation = "vertical"
        self.padding = [dp(8), dp(10), dp(8), dp(10)]
        self.spacing = dp(4)
        with self.canvas.before:
            self._bg_color = Color(*SURFACE_3)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[RADIUS_SM]
            )
        self.bind(pos=self._sync_bg, size=self._sync_bg, on_touch_down=self._on_touch)

        icon = Label(
            text=glyph,
            font_size="22sp",
            color=TEXT_HIGH,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(40),
        )
        icon.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(icon)

        text = Label(
            text=label,
            font_size="11sp",
            color=TEXT_MED,
            halign="center",
            valign="middle",
        )
        text.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(text)

    def _sync_bg(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _on_touch(self, _w, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._bg_color.rgba = SURFACE_4
        from kivy.clock import Clock
        Clock.schedule_once(lambda *_: setattr(self._bg_color, "rgba", SURFACE_3), 100)
        self._on_select()
        return True


class AddObjectDialog(FloatLayout):
    """Popup modal para adicionar objeto (Pocket Code).

    Callback:
        on_select(key: str) — usuário escolheu uma opção.
            "backpack" / "draw" / "library" / "local" → stubs (toast "em breve")
            "image" / "media" / "from_lib" / "photo" → criam KixObject real
            "empty" → cria KixObject vazio
    """

    def __init__(self, on_select, on_cancel=None, **kwargs):
        super().__init__(**kwargs)
        self._on_select = on_select
        self._on_cancel = on_cancel or (lambda: None)

        with self.canvas.before:
            Color(0, 0, 0, 0.55)
            self._overlay = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[0]
            )
        self.bind(pos=self._sync_overlay, size=self._sync_overlay)

        # Card
        self._card = BoxLayout(
            orientation="vertical",
            padding=[PADDING, PADDING, PADDING, PADDING],
            spacing=dp(12),
            size_hint=(None, None),
            width=dp(360),
            height=dp(540),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        with self._card.canvas.before:
            Color(*SURFACE_2)
            self._card_bg = RoundedRectangle(
                radius=[RADIUS], pos=self._card.pos, size=self._card.size
            )
        self._card.bind(pos=self._sync_card_bg, size=self._sync_card_bg)
        self.add_widget(self._card)

        self._build_header()
        self._build_grid()

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

    def _build_header(self):
        title = Label(
            text="Meu ator ou objeto",
            color=TEXT_HIGH,
            font_size="16sp",
            bold=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(28),
        )
        title.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self._card.add_widget(title)

        sub = Label(
            text="Como adicionar um novo objeto?",
            color=TEXT_LOW,
            font_size="12sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(20),
        )
        sub.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self._card.add_widget(sub)

    def _build_grid(self):
        grid = GridLayout(
            cols=2,
            spacing=dp(8),
            padding=[0, dp(4), 0, dp(4)],
            size_hint_y=None,
            height=dp(440),
        )
        for spec in _OPTIONS:
            item = _GridItem(
                glyph=spec["glyph"],
                label=spec["label"],
                on_select=lambda s=spec: self._select(s),
            )
            if spec.get("full"):
                # "Projetos locais" ocupa linha cheia
                from kivy.metrics import dp as _dp
                grid._rows = grid.rows  # placeholder
                # Trick: insere um widget "vazio" ao lado
                grid.add_widget(item)
                # Espaço para a próxima linha começar
                empty = BoxLayout(size_hint_x=None, width=0)
                grid.add_widget(empty)
            else:
                grid.add_widget(item)
        self._card.add_widget(grid)

    def _select(self, spec: dict):
        if self.parent is not None:
            self.parent.remove_widget(self)
        self._on_select(spec["key"], spec.get("kind", "sprite"))


__all__ = ["AddObjectDialog", "KixObject"]