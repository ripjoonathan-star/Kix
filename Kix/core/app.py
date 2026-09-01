"""KixApp — entry point do app.

Configura tamanho padrão (mobile-first, mas roda em desktop), monta
ScreenManager com DashboardScreen + EditorScreen.
"""

from __future__ import annotations

from kivy.app import App
from kivy.core.window import Window

from Kix.core import theme as _theme
from Kix.core.screen_manager import ScreenManager
from Kix.screens.dashboard import DashboardScreen
from Kix.screens.editor import EditorScreen
from Kix.screens.formula_editor import FormulaEditorScreen
from Kix.screens.object_screen import ObjectScreen


class KixApp(App):
    """App Kivy principal."""

    title = "Kix"

    def build(self) -> ScreenManager:
        sm = ScreenManager(transition=None)  # sem animação — sensação app nativa
        sm.add_widget(DashboardScreen(name=ScreenManager.DASHBOARD))
        editor = EditorScreen(name=ScreenManager.EDITOR)

        def _object_back():
            sm.go(ScreenManager.EDITOR)

        def _object_play():
            sm.go(ScreenManager.EDITOR)

        object_screen = ObjectScreen(
            name=ScreenManager.OBJECT,
            on_back=_object_back,
            on_play=_object_play,
        )

        def _formula_done(_value):
            sm.go(ScreenManager.EDITOR)

        formula = FormulaEditorScreen(
            name=ScreenManager.FORMULA,
            on_done=_formula_done,
        )

        sm.add_widget(editor)
        sm.add_widget(object_screen)
        sm.add_widget(formula)
        return sm

    def on_start(self) -> None:
        """Configura a janela quando o display está pronto."""
        try:
            Window.clearcolor = _theme.BG
            Window.size = (390, 844)  # iPhone 14 — mobile-first, desktop-friendly
        except Exception:
            # Sem display provider (headless/test) — sem janela para configurar.
            pass