"""Tabs simples — placeholder para Objetos/Recursos/Cenário.

Cada uma é só um rótulo centralizado dizendo que a aba existe mas o
conteúdo ainda não foi construído. Mantém a navegação previsível
enquanto as outras abas evoluem.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from Kix.core.theme import TEXT_LOW, TEXT_MED


class SimplesTab(BoxLayout):
    def __init__(self, screen, title: str, subtitle: str, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.screen = screen
        self.padding = [dp(24), dp(40), dp(24), dp(40)]
        self.spacing = dp(8)

        head = Label(
            text=title,
            font_size="20sp",
            color=TEXT_MED,
            halign="center",
            valign="bottom",
            size_hint_y=None,
            height=dp(40),
        )
        head.bind(size=lambda i, _: setattr(i, "text_size", i.size))

        body = Label(
            text=subtitle,
            font_size="14sp",
            color=TEXT_LOW,
            halign="center",
            valign="top",
        )
        body.bind(size=lambda i, _: setattr(i, "text_size", i.size))

        self.add_widget(head)
        self.add_widget(body)
