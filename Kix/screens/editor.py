"""EditorScreen — editor de projeto com 5 abas estilo Catroid.

Layout:
- App bar (título do projeto + ▶ Play + ⏹ Stop + Voltar)
- Conteúdo da aba ativa
- Tab bar inferior: Programação | Palco | Objetos | Recursos | Cenário

A aba ativa é trocada via `set_tab(name)`. O carregamento do projeto
acontece em `on_enter` (carrega via ProjectManager).
"""

from __future__ import annotations

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from Kix.core.theme import (
    EMERALD,
    FONT_SIZE_HEADING,
    PADDING,
    SURFACE_1,
    SURFACE_2,
    SURFACE_3,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
)
from Kix.projects.manager import ProjectManager
from Kix.projects.model import KixProject
from Kix.ui.app_bar import KixAppBar
from Kix.ui.button import IconButton

Builder.load_string("""
<EditorScreen>:
    FloatLayout:
        BoxLayout:
            orientation: 'vertical'
            KixAppBar:
                id: topbar
            BoxLayout:
                id: tab_content
                orientation: 'vertical'
            BoxLayout:
                id: tabbar
                size_hint_y: None
                height: dp(56)
                padding: [dp(8), dp(6), dp(8), dp(6)]
                spacing: dp(4)
                canvas.before:
                    Color:
                        rgba: 0.071, 0.071, 0.078, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
""")


_TAB_LABELS = ["Programação", "Palco", "Objetos", "Recursos", "Cenário"]


class EditorScreen(Screen):
    """Tela de edição do projeto carregado."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project: KixProject | None = None
        self.project_name: str = ""
        self._tab_buttons: dict[str, IconButton] = {}
        self._current_tab: str = "programacao"
        self._tabs: dict[str, BoxLayout] = {}

    # --- API pública ------------------------------------------------------
    def load_project(self, name: str) -> None:
        """Carrega projeto do disco e troca o título."""
        self.project_name = name
        manager = ProjectManager()
        try:
            self.project = manager.load(name)
        except FileNotFoundError:
            self.project = None
        self._render_topbar()
        self._rebuild_tabs()

    def set_tab(self, name: str) -> None:
        """Troca a aba ativa. Recarrega o conteúdo se ainda não foi criado."""
        if name not in self._tabs:
            self._tabs[name] = self._build_tab(name)
            self.ids.tab_content.clear_widgets()
            self.ids.tab_content.add_widget(self._tabs[name])
        else:
            self.ids.tab_content.clear_widgets()
            self.ids.tab_content.add_widget(self._tabs[name])
        self._current_tab = name
        self._highlight_tab(name)

    def save(self) -> None:
        """Persiste o projeto atual no disco."""
        if self.project is None:
            return
        manager = ProjectManager()
        manager.save(self.project)

    # --- ciclo de vida ----------------------------------------------------
    def on_enter(self, *_):
        # primeira entrada sem projeto carregado → mostra estado vazio
        if not self._tab_buttons:
            self._render_topbar()
            self._rebuild_tabs()

    # --- topbar -----------------------------------------------------------
    def _render_topbar(self) -> None:
        title = self.project.name if self.project else (self.project_name or "Sem nome")
        bar = self.ids.topbar
        bar.clear_widgets()
        # Botão voltar
        back = IconButton(glyph="‹", primary=False)
        back.size_hint = (None, None)
        back.size = (dp(40), dp(40))
        back.bind(on_release=self._go_back)

        # título centralizado (BoxLayout horizontal: back | title | spacer para alinhar)
        title_label = Label(
            text=title,
            font_size="18sp",
            bold=True,
            color=TEXT_HIGH,
            halign="center",
            valign="middle",
        )
        title_label.bind(size=lambda i, _: setattr(i, "text_size", i.size))

        # botões play/stop
        play = IconButton(glyph="▶", primary=True)
        play.size_hint = (None, None)
        play.size = (dp(40), dp(40))
        play.bind(on_release=lambda *_: self._run_script())

        stop = IconButton(glyph="⏹", primary=False)
        stop.size_hint = (None, None)
        stop.size = (dp(40), dp(40))
        stop.bind(on_release=lambda *_: self._stop_script())

        reset = IconButton(glyph="↺", primary=False)
        reset.size_hint = (None, None)
        reset.size = (dp(40), dp(40))
        reset.bind(on_release=lambda *_: self._reset_sprite())

        bar.add_widget(back)
        bar.add_widget(title_label)
        bar.add_widget(play)
        bar.add_widget(stop)
        bar.add_widget(reset)

    # --- tab bar ----------------------------------------------------------
    def _rebuild_tabs(self) -> None:
        bar = self.ids.tabbar
        bar.clear_widgets()
        self._tab_buttons.clear()
        # mapa nome-canônico → rótulo
        keys = ["programacao", "palco", "objetos", "recursos", "cenario"]
        for key, label in zip(keys, _TAB_LABELS):
            btn = self._make_tab_button(key, label)
            self._tab_buttons[key] = btn
            bar.add_widget(btn)
        # ativa "programacao" por padrão
        self.set_tab("programacao")

    def _make_tab_button(self, key: str, label: str) -> IconButton:
        # Botão de aba é só um rótulo com cor que muda; usamos KixButton-like
        from Kix.ui.button import KixButton
        btn = KixButton(text=label)
        btn.primary = False
        btn._primary = False
        btn.font_size = "13sp"
        btn.bind(on_release=lambda *_: self.set_tab(key))
        btn._tab_key = key
        return btn

    def _highlight_tab(self, key: str) -> None:
        for k, btn in self._tab_buttons.items():
            if k == key:
                # usa emerald via atributo _bg_color
                if hasattr(btn, "_bg_color"):
                    btn._bg_color.rgba = EMERALD
            else:
                if hasattr(btn, "_bg_color"):
                    btn._bg_color.rgba = SURFACE_3

    # --- tabs (lazy) ------------------------------------------------------
    def _build_tab(self, name: str) -> BoxLayout:
        if name == "programacao":
            from Kix.screens.tabs.programacao import ProgramacaoTab
            tab = ProgramacaoTab(screen=self)
        elif name == "palco":
            from Kix.screens.tabs.palco import PalcoTab
            tab = PalcoTab(screen=self)
        elif name == "objetos":
            from Kix.screens.tabs.simples import SimplesTab
            tab = SimplesTab(
                screen=self,
                title="Objetos",
                subtitle="Lista de objetos do projeto (em breve).",
            )
        elif name == "recursos":
            from Kix.screens.tabs.simples import SimplesTab
            tab = SimplesTab(
                screen=self,
                title="Recursos",
                subtitle="Imagens, sons e fontes (em breve).",
            )
        elif name == "cenario":
            from Kix.screens.tabs.simples import SimplesTab
            tab = SimplesTab(
                screen=self,
                title="Cenário",
                subtitle="Cenas e fundo (em breve).",
            )
        else:
            tab = Label(text=f"Aba '{name}' não encontrada")
        return tab

    # --- ações ------------------------------------------------------------
    def _go_back(self, *_):
        from Kix.core.app import KixApp
        from Kix.core.screen_manager import ScreenManager

        app = KixApp.get_running_app()
        sm = app.root
        if isinstance(sm, ScreenManager):
            sm.go(ScreenManager.DASHBOARD)

    def _run_script(self) -> None:
        """Dispara a execução do programa na aba Palco."""
        palco_tab = self._tabs.get("palco")
        if palco_tab is not None and hasattr(palco_tab, "run"):
            palco_tab.run()

    def _stop_script(self) -> None:
        """Para o programa em execução."""
        palco_tab = self._tabs.get("palco")
        if palco_tab is not None and hasattr(palco_tab, "stop"):
            palco_tab.stop()

    def _reset_sprite(self) -> None:
        """Reseta o estado do sprite no projeto (e na Palco)."""
        palco_tab = self._tabs.get("palco")
        if palco_tab is not None and hasattr(palco_tab, "reset"):
            palco_tab.reset()
