"""DropdownMenu reutilizável.

Popup modal posicionado próximo a um botão âncora, com lista de
opções (ícone + label). Tap em uma opção chama o callback associado.

Usado para:
- Dropdown menu do objeto no Editor (Mochila, Copiar, Apagar, etc.)
- Kebab menu (⋮) nas app bars.

Cada item é um dict {"key": str, "label": str, "glyph": str, "on_select": callable}.
"""

from __future__ import annotations

from typing import Callable

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from Kix.core.theme import (
    RADIUS,
    RADIUS_SM,
    SURFACE_2,
    SURFACE_3,
    TEXT_HIGH,
    TEXT_MED,
)
from Kix.ui.button import IconButton


class _MenuItem(BoxLayout):
    """Linha de menu: ícone + label."""

    def __init__(self, glyph: str, label: str, on_select: Callable, **kwargs):
        super().__init__(**kwargs)
        self._on_select = on_select
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(44)
        self.padding = [dp(12), dp(8), dp(12), dp(8)]
        self.spacing = dp(12)

        # Background (transparente default).
        with self.canvas.before:
            self._bg_color = Color(*SURFACE_2)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[RADIUS_SM]
            )
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        icon = Label(
            text=glyph,
            color=TEXT_MED,
            font_size="16sp",
            size_hint_x=None,
            width=dp(24),
            halign="center",
            valign="middle",
        )
        icon.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(icon)

        text = Label(
            text=label,
            color=TEXT_HIGH,
            font_size="14sp",
            halign="left",
            valign="middle",
        )
        text.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(text)

        # Estado pressed/hover via on_touch_down.
        self.bind(on_touch_down=self._on_touch)

    def _sync_bg(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _on_touch(self, _w, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._bg_color.rgba = SURFACE_3
        from kivy.clock import Clock
        # restaura cor após 100ms (efeito ripple simples)
        Clock.schedule_once(lambda *_: setattr(self._bg_color, "rgba", SURFACE_2), 100)
        self._on_select()
        return True


class DropdownMenu(FloatLayout):
    """Popup dropdown com lista de opções.

    Items: lista de dicts {key, label, glyph, on_select}.
    """

    def __init__(self, items: list[dict], anchor_widget: Widget | None = None, **kwargs):
        super().__init__(**kwargs)
        self._items = items
        self._anchor = anchor_widget

        # Overlay escuro para fechar on touch fora.
        with self.canvas.before:
            Color(0, 0, 0, 0.30)
            self._overlay = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[0]
            )
        # usa Rectangle (RoundedRectangle com radius=[0] ainda funciona)
        self.bind(pos=self._sync_overlay, size=self._sync_overlay, on_touch_down=self._on_touch_out)

        # Card do menu.
        self._card = BoxLayout(
            orientation="vertical",
            padding=[dp(4), dp(4), dp(4), dp(4)],
            spacing=dp(2),
            size_hint=(None, None),
            width=dp(220),
            size_hint_min_y=dp(44),
        )
        # Calcula altura baseado nos itens.
        card_height = dp(8) + len(items) * dp(44) + dp(max(0, len(items) - 1)) * dp(2)
        self._card.height = card_height
        with self._card.canvas.before:
            Color(*SURFACE_2)
            self._card_bg = RoundedRectangle(
                radius=[RADIUS], pos=self._card.pos, size=self._card.size
            )
        self._card.bind(pos=self._sync_card_bg, size=self._sync_card_bg)

        for spec in items:
            item = _MenuItem(
                glyph=spec.get("glyph", "•"),
                label=spec.get("label", ""),
                on_select=lambda s=spec: self._select(s),
            )
            self._card.add_widget(item)

        # posiciona
        self._position_card()
        self.add_widget(self._card)

    def _sync_overlay(self, *_):
        # Overlay: usa Rectangle comum para simplicidade
        # (substitui o RoundedRectangle inicial por um Rectangle para garantir fullscreen)
        if hasattr(self, "_overlay") and self._overlay is not None:
            self.canvas.before.remove(self._overlay)
        with self.canvas.before:
            Color(0, 0, 0, 0.30)
            from kivy.graphics import Rectangle
            self._overlay = Rectangle(pos=self.pos, size=self.size)
        # Garante que fica atrás do card.
        if self._card in self.children:
            self.remove_widget(self._card)
            self.add_widget(self._card)

    def _sync_card_bg(self, *_):
        self._card_bg.pos = self._card.pos
        self._card_bg.size = self._card.size

    def _position_card(self) -> None:
        """Posiciona o card próximo ao anchor (canto direito/abaixo)."""
        # default: canto superior direito
        if self._anchor is None or self._anchor.parent is None:
            self._card.pos = (self.width - dp(232), self.height - dp(card_h := self._card.height + dp(16)))
            return
        ax, ay = self._anchor.to_window(*self._anchor.pos)
        aw, ah = self._anchor.size
        # canto direito do anchor → canto direito do card
        card_w = self._card.width
        x = ax + aw - card_w
        y = ay - self._card.height - dp(8)
        # clamp dentro do pai
        if y < 0:
            y = ay + ah + dp(8)  # abaixo se não couber acima
        if x < dp(8):
            x = dp(8)
        self._card.pos = (x, y)

    def _select(self, spec: dict) -> None:
        if self.parent is not None:
            self.parent.remove_widget(self)
        cb = spec.get("on_select")
        if cb:
            cb(spec)

    def _on_touch_out(self, _w, touch):
        if self._card.collide_point(*self.pos_for_card(touch)):
            return False
        # tocou fora do card → fecha
        if self.parent is not None:
            self.parent.remove_widget(self)
        return True

    def pos_for_card(self, touch):
        # converte touch pos para coordenadas do card
        return self.to_local(*touch.pos)


__all__ = ["DropdownMenu"]