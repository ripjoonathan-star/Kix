"""KixApp — entry point do app.

Configura tamanho padrão (mobile-first, mas roda em desktop), monta
ScreenManager com DashboardScreen + EditorScreen.
"""

from __future__ import annotations

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.popup import Popup

from Kix.core import theme as _theme
from Kix.core.screen_manager import ScreenManager
from Kix.screens.dashboard import DashboardScreen
from Kix.screens.editor import EditorScreen


class KixApp(App):
    """App Kivy principal."""

    title = "Kix"

    def build(self) -> ScreenManager:
        sm = ScreenManager(transition=None)  # sem animação — sensação app nativa
        sm.add_widget(DashboardScreen(name=ScreenManager.DASHBOARD))
        sm.add_widget(EditorScreen(name=ScreenManager.EDITOR))
        return sm

    def on_start(self) -> None:
        """Configura a janela quando o display está pronto."""
        try:
            Window.clearcolor = _theme.BG
            Window.size = (390, 844)  # iPhone 14 — mobile-first, desktop-friendly
            # No celular, teclado virtual sobrepõe inputs por padrão. 'below_target'
            # faz o Kivy rolar o TextInput ativo para uma posição visível quando o
            # softinput abrir (vs 'pan' que move a janela inteira ou 'resize' que
            # reduz a área — quebraria o layout fixo).
            Window.softinput_mode = "below_target"
            # Back button (Android) / ESC (desktop): dismiss popup aberto → voltar
            # editor→dashboard → deixa fechar app (comportamento padrão).
            Window.bind(on_keyboard=self._on_android_back)
        except Exception:
            # Sem display provider (headless/test) — sem janela para configurar.
            pass

    def _on_android_back(self, _window, key: int, _scancode: int, _text: str,
                          _modifiers: list[str]) -> bool:
        """Handler do botão de voltar do sistema.

        Kivy envia key=27 com key=='back' no Android; no desktop, o usuário
        também usa ESC (mesmo keycode). Devolvemos ``True`` para indicar
        que consumimos o evento.
        """
        # 1) Popup aberto: fecha o topo
        open_popups = Popup.get_open_popups()
        if open_popups:
            open_popups[-1].dismiss()
            return True
        # 2) Tela de editor aberta → volta para dashboard
        sm = self.root
        if sm is not None and getattr(sm, "current", None) == ScreenManager.EDITOR:
            sm.go(ScreenManager.DASHBOARD)
            return True
        # 3) Senão, deixa o sistema fechar o app
        return False