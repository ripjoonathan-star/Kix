"""Wrapper fino sobre kivy.uix.screenmanager.ScreenManager.

Mantém nomes canônicos para as telas, permitindo `go("editor")` em vez
de manipular o `current` diretamente.
"""

from __future__ import annotations

from kivy.uix.screenmanager import ScreenManager as _KivySM


class ScreenManager(_KivySM):
    """Adiciona transições nomeadas para as telas canônicas do Kix."""

    DASHBOARD = "dashboard"
    EDITOR = "editor"
    OBJECT = "object"
    FORMULA = "formula"

    def go(self, name: str, **options) -> None:
        """Transiciona para a tela nomeada."""
        if name not in self.screen_names:
            raise KeyError(f"Tela desconhecida: {name!r}. Disponíveis: {self.screen_names}")
        self.current = name
        for k, v in options.items():
            screen = self.get_screen(name)
            if hasattr(screen, k):
                setattr(screen, k, v)