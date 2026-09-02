"""Cards de projeto: ProjectCard (lista) e RecentProjectCard (destaque)."""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from Kix.core.theme import (
    CARD_BG,
    FONT_SIZE_HEADING,
    FONT_SIZE_META,
    PADDING,
    RADIUS,
    SURFACE_2,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
)
from Kix.ui.button import IconButton

Builder.load_string(
    """
<ProjectCard>:
    padding: dp(16)
    spacing: dp(8)
    size_hint_y: None
    height: dp(72)

<RecentProjectCard>:
    padding: dp(16)
    spacing: dp(12)
    size_hint_y: None
    height: dp(140)
"""
)


def _rounded_bg(widget, color):
    with widget.canvas.before:
        widget._bg_color = Color(*color)
        widget._rect = RoundedRectangle(
            radius=[dp(RADIUS)], pos=widget.pos, size=widget.size
        )

    def _update(_, __):
        widget._rect.pos = widget.pos
        widget._rect.size = widget.size

    widget.bind(pos=_update, size=_update)
    return widget


class ProjectCard(BoxLayout):
    """Card compacto da lista 'Projetos'."""

    def __init__(self, name: str, modified: str, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        _rounded_bg(self, CARD_BG)
        title = Label(
            text=name, font_size=f"{FONT_SIZE_HEADING}sp",
            color=TEXT_HIGH, halign="left", valign="bottom",
        )
        title.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        sub = Label(
            text=modified, font_size=f"{FONT_SIZE_META}sp",
            color=TEXT_LOW, halign="left", valign="top",
        )
        sub.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(title)
        self.add_widget(sub)


class RecentProjectCard(BoxLayout):
    """Card grande do 'Projeto mais recente' com thumb e botão lápis."""

    def __init__(self, name: str, modified: str, **kwargs):
        super().__init__(orientation="horizontal", **kwargs)
        _rounded_bg(self, SURFACE_2)

        self.thumb = BoxLayout(size_hint=(None, 1), width=dp(108))
        with self.thumb.canvas.before:
            Color(*CARD_BG)
            self.thumb._bg_color = Color(*CARD_BG)
            from kivy.graphics import RoundedRectangle as _RR
            self.thumb._rect = _RR(
                radius=[dp(RADIUS)], pos=self.thumb.pos, size=self.thumb.size
            )
            self.thumb.bind(
                pos=lambda i, _: setattr(i._rect, "pos", i.pos),
                size=lambda i, _: setattr(i._rect, "size", i.size),
            )
        self.add_widget(self.thumb)

        info = BoxLayout(orientation="vertical", spacing=dp(4), padding=[dp(8), 0, 0, 0])
        title = Label(
            text=name, font_size=f"{FONT_SIZE_HEADING + 2}sp",
            color=TEXT_HIGH, halign="left", valign="bottom", bold=True,
        )
        title.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        sub = Label(
            text=modified, font_size=f"{FONT_SIZE_META}sp",
            color=TEXT_MED, halign="left", valign="top",
        )
        sub.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        info.add_widget(title)
        info.add_widget(sub)
        self.add_widget(info)

        # botão lápis verde, canto direito
        self.edit_btn = IconButton(glyph="✎", primary=True)
        self.edit_btn.size_hint = (None, None)
        self.edit_btn.size = (dp(48), dp(48))
        # alinha verticalmente ao centro via BoxLayout outer
        spacer_top = BoxLayout(size_hint_y=0.25)
        spacer_bottom = BoxLayout(size_hint_y=0.25)
        right_col = BoxLayout(orientation="vertical", size_hint_x=None, width=dp(56))
        right_col.add_widget(spacer_top)
        right_col.add_widget(self.edit_btn)
        right_col.add_widget(spacer_bottom)
        self.add_widget(right_col)