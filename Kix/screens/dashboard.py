"""DashboardScreen — primeira tela do app.

Layout Pocket Code:
- KixAppBar ("Kix") com kebab menu (⋮) canto direito
- ScrollView com:
    * label "Projetos"
    * lista de ProjectCards (sem "Projeto mais recente" — match Pocket Code)
- FAB "+" canto inferior direito (cria projeto → NewProjectDialog)

Dados vêm do `ProjectManager`. Tap em um card abre o `EditorScreen`
carregando o projeto correspondente.
"""

from __future__ import annotations

from datetime import datetime

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from Kix.core.theme import (
    EMERALD,
    FONT_SIZE_BODY,
    SURFACE_2,
    SURFACE_3,
    TEXT_LOW,
    TEXT_MED,
)
from Kix.projects.manager import ProjectManager
from Kix.screens.new_project import NewProjectDialog
from Kix.ui.app_bar import KixAppBar
from Kix.ui.button import IconButton
from Kix.ui.card import ProjectCard

Builder.load_string("""
<DashboardScreen>:
    FloatLayout:
        BoxLayout:
            orientation: 'vertical'
            KixAppBar:
                id: topbar
            ScrollView:
                do_scroll_x: False
                bar_width: 0
                BoxLayout:
                    id: content
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(24), dp(24), dp(24), dp(96)]
                    spacing: dp(16)
        IconButton:
            id: fab
            glyph: '+'
            primary: True
            size_hint: (None, None)
            size: dp(56), dp(56)
            x: root.width - dp(72)
            y: dp(32)
            on_release: root._show_new_project_popup()
""")


def _humanize_modified(iso: str) -> str:
    """Formata '2026-09-01T12:34:56+00:00' → '01/09 12:34'."""
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%d/%m %H:%M")
    except (ValueError, TypeError):
        return iso or ""


class DashboardScreen(Screen):
    """Lista projetos do usuário + ação de criar novo."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._manager = ProjectManager()

    def on_enter(self, *_):
        self.refresh()

    # --- público ----------------------------------------------------------
    def refresh(self) -> None:
        """Recarrega a lista de projetos do disco."""
        content = self.ids.content
        content.clear_widgets()
        infos = self._manager.list()
        infos.sort(key=lambda i: i.modified_at, reverse=True)

        if not infos:
            content.add_widget(self._empty_state())
            return

        # Pocket Code: só lista "Projetos", sem "Projeto mais recente".
        content.add_widget(self._section_label("Projetos"))
        for info in infos:
            card = ProjectCard(
                name=info.name,
                modified=_humanize_modified(info.modified_at),
            )
            card.bind(on_touch_down=self._make_touch_open(card, info.name))
            content.add_widget(card)

    # --- criação ----------------------------------------------------------
    def _show_new_project_popup(self) -> None:
        """Abre o diálogo "Criar Jogo" (estilo Pocket Code)."""

        def _on_create(name: str, settings) -> None:
            try:
                self._manager.create(name, settings=settings)
            except FileExistsError:
                # Mantém o popup aberto em caso de duplicidade
                return
            if self._dlg is not None and self._dlg.parent is not None:
                self._dlg.parent.remove_widget(self._dlg)
            self._dlg = None
            self.refresh()

        def _on_cancel() -> None:
            if self._dlg is not None and self._dlg.parent is not None:
                self._dlg.parent.remove_widget(self._dlg)
            self._dlg = None

        self._dlg = NewProjectDialog(on_create=_on_create, on_cancel=_on_cancel)
        # Anexa como overlay por cima de tudo no Screen.
        self.add_widget(self._dlg)

    # --- helpers ----------------------------------------------------------
    def _empty_state(self) -> BoxLayout:
        box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(180),
            padding=[dp(24), dp(40), dp(24), dp(40)],
            spacing=dp(8),
        )
        msg = Label(
            text="Sem projetos ainda",
            font_size="18sp",
            color=TEXT_MED,
            halign="center",
            valign="middle",
        )
        msg.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        sub = Label(
            text='Toque no "+" para começar',
            font_size="14sp",
            color=TEXT_LOW,
            halign="center",
            valign="middle",
        )
        sub.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        box.add_widget(msg)
        box.add_widget(sub)
        return box

    @staticmethod
    def _section_label(text: str) -> Label:
        lbl = Label(
            text=text,
            font_size=f"{FONT_SIZE_BODY}sp",
            color=TEXT_MED,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(28),
        )
        lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        return lbl

    @staticmethod
    def _spacer() -> BoxLayout:
        return BoxLayout(size_hint_y=None, height=dp(8))

    @staticmethod
    def _make_touch_open(card, name: str):
        """Tap no card abre o editor."""
        def _on_touch(instance, touch):
            if card.collide_point(*touch.pos):
                DashboardScreen._open_editor(name)
                return True
            return False
        return _on_touch

    @staticmethod
    def _open_editor(name: str) -> None:
        from Kix.core.app import KixApp
        from Kix.core.screen_manager import ScreenManager

        app = KixApp.get_running_app()
        sm = app.root
        if isinstance(sm, ScreenManager):
            sm.go(ScreenManager.EDITOR, project_name=name)
