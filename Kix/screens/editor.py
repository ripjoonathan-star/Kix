"""EditorScreen — tela do projeto estilo Pocket Code (M7).

Layout (sem tab bar inferior — navegação real por telas):
- App bar: ← / título / cast (↗) / kebab (⋮)
- "Fundo" row (card cinza placeholder → tap abre ObjectScreen do fundo)
- Section header "Atores e objetos"
- Lista de objetos (▶ + nome + kebab) → tap abre ObjectScreen
- FAB ▶ (play) lavanda canto inferior direito
- FAB + (lavanda) canto inferior direito abaixo do play

Navega para:
- ScreenManager.OBJECT (abrir objeto/fundo)
- ScreenManager.CATEGORIAS (futuro M8)
- ScreenManager.FORMULA (input numérico)
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from Kix.core.theme import (
    FONT_SIZE_HEADING,
    LAVANDA,
    PADDING,
    SURFACE_1,
    SURFACE_2,
    SURFACE_3,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
)
from Kix.projects.manager import ProjectManager
from Kix.projects.model import KixObject, KixProject
from Kix.ui.app_bar import KixAppBar
from Kix.ui.button import IconButton

Builder.load_string("""
<EditorScreen>:
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
                    padding: [dp(16), dp(16), dp(16), dp(120)]
                    spacing: dp(12)
        IconButton:
            id: fab_play
            glyph: '▶'
            primary: True
            size_hint: (None, None)
            size: dp(56), dp(56)
            x: root.width - dp(72)
            y: dp(104)
            on_release: root._run_program()
        IconButton:
            id: fab_add
            glyph: '+'
            primary: True
            size_hint: (None, None)
            size: dp(56), dp(56)
            x: root.width - dp(72)
            y: dp(32)
            on_release: root._show_add_object()
""")


class EditorScreen(Screen):
    """Tela do projeto (Pocket Code style)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project: KixProject | None = None
        self.project_name: str = ""

    # --- API pública ------------------------------------------------------
    def load_project(self, name: str) -> None:
        """Carrega projeto do disco e popula conteúdo."""
        self.project_name = name
        manager = ProjectManager()
        try:
            self.project = manager.load(name)
        except FileNotFoundError:
            self.project = None
        self._apply_fab_color()
        self._render_topbar()
        self._render_content()

    def refresh(self) -> None:
        """Recarrega conteúdo (após add/delete/rename)."""
        self._render_content()

    # --- render ------------------------------------------------------------
    def _apply_fab_color(self) -> None:
        """FABs da tela do projeto são LAVANDA, não emerald."""
        lav = LAVANDA
        for fab_id in ("fab_play", "fab_add"):
            fab = self.ids.get(fab_id)
            if fab is None:
                continue
            # troca a cor de fundo (canvas.before) para lavanda
            if hasattr(fab, "_bg_color"):
                fab._bg_color.rgba = lav

    def _render_topbar(self) -> None:
        title = self.project_name or "Projeto"
        self.ids.topbar.set_title(title)
        # botões direitos: cast + kebab
        self.ids.topbar.set_actions([
            ("cast", "↗", lambda *_: self._broadcast()),
            ("kebab", "⋮", lambda *_: self._show_kebab()),
        ])

    def _render_content(self) -> None:
        content = self.ids.content
        content.clear_widgets()

        if self.project is None:
            content.add_widget(self._empty())
            return

        # 1. Fundo
        content.add_widget(self._fundo_row())

        # 2. Section header
        content.add_widget(self._section_label("Atores e objetos"))

        # 3. Objetos
        if not self.project.objects:
            content.add_widget(self._empty_objetos())
        else:
            for obj in self.project.objects:
                content.add_widget(self._object_row(obj))

    # --- helpers ----------------------------------------------------------
    def _fundo_row(self) -> BoxLayout:
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(72),
            padding=[dp(8), dp(8), dp(8), dp(8)],
            spacing=dp(12),
        )
        with row.canvas.before:
            row._bg_color = Color(*SURFACE_3)
            row._bg_rect = RoundedRectangle(
                pos=row.pos, size=row.size, radius=[dp(8)]
            )
        row.bind(pos=lambda i, _: self._sync_bg(i), size=lambda i, _: self._sync_bg(i))

        thumb = BoxLayout(size_hint=(None, None), size=(dp(56), dp(56)))
        with thumb.canvas.before:
            Color(*SURFACE_4)
            thumb._bg_rect = RoundedRectangle(pos=thumb.pos, size=thumb.size, radius=[dp(8)])
        thumb.bind(
            pos=lambda i, _: setattr(i._bg_rect, "pos", i.pos),
            size=lambda i, _: setattr(i._bg_rect, "size", i.size),
        )
        row.add_widget(thumb)

        name_lbl = Label(
            text="Fundo",
            color=TEXT_HIGH,
            font_size="16sp",
            halign="left",
            valign="middle",
        )
        name_lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        row.add_widget(name_lbl)

        # tap no row abre ObjectScreen com kind=background (se houver) ou cria
        row.bind(on_touch_down=lambda w, t: self._row_tap(w, t, kind="background"))
        return row

    def _object_row(self, obj: KixObject) -> BoxLayout:
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=[dp(8), dp(8), dp(8), dp(8)],
            spacing=dp(10),
        )
        with row.canvas.before:
            row._bg_color = Color(*SURFACE_2)
            row._bg_rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(8)])
        row.bind(pos=lambda i, _: self._sync_bg(i), size=lambda i, _: self._sync_bg(i))

        play = IconButton(glyph="▶", primary=True)
        play.size_hint = (None, None)
        play.size = (dp(44), dp(44))
        play.bind(on_release=lambda *_: self._run_object(obj))
        row.add_widget(play)
        self._tint_lavanda(play)

        name_lbl = Label(
            text=obj.name,
            color=TEXT_HIGH,
            font_size="15sp",
            halign="left",
            valign="middle",
        )
        name_lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        row.add_widget(name_lbl)

        kebab = IconButton(glyph="⋮", primary=False)
        kebab.size_hint = (None, None)
        kebab.size = (dp(44), dp(44))
        kebab.bind(on_release=lambda *_: self._show_object_menu(obj, kebab))
        row.add_widget(kebab)

        # tap em qualquer lugar fora dos botões abre ObjectScreen
        row.bind(on_touch_down=lambda w, t: self._row_tap(w, t, obj=obj))
        return row

    def _tint_lavanda(self, btn: IconButton) -> None:
        if hasattr(btn, "_bg_color"):
            btn._bg_color.rgba = LAVANDA

    def _row_tap(self, row: BoxLayout, touch, obj: KixObject | None = None,
                  kind: str | None = None) -> bool:
        if not row.collide_point(*touch.pos):
            return False
        # ignora se tocou num filho que já consome (botões)
        for child in row.children:
            if child is row:
                continue
            if child.collide_point(*touch.pos):
                return False
        if obj is not None:
            self._open_object(obj)
        elif kind == "background":
            self._open_background()
        return True

    def _sync_bg(self, widget) -> None:
        widget._bg_rect.pos = widget.pos
        widget._bg_rect.size = widget.size

    def _section_label(self, text: str) -> Label:
        lbl = Label(
            text=text,
            font_size=f"{FONT_SIZE_HEADING}sp",
            color=TEXT_MED,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(32),
        )
        lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        return lbl

    def _empty(self) -> BoxLayout:
        box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(120),
                        padding=[dp(16), dp(32), dp(16), dp(32)])
        msg = Label(text="Projeto não encontrado", color=TEXT_MED,
                    halign="center", valign="middle")
        msg.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        box.add_widget(msg)
        return box

    def _empty_objetos(self) -> BoxLayout:
        box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(80),
                        padding=[dp(16), dp(24), dp(16), dp(24)])
        msg = Label(
            text='Toque em "+" para adicionar',
            color=TEXT_LOW,
            font_size="13sp",
            halign="center", valign="middle",
        )
        msg.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        box.add_widget(msg)
        return box

    # --- navegação --------------------------------------------------------
    def _open_object(self, obj: KixObject) -> None:
        from Kix.core.app import KixApp
        from Kix.core.screen_manager import ScreenManager

        app = KixApp.get_running_app()
        sm = app.root
        if isinstance(sm, ScreenManager):
            sm.go(ScreenManager.OBJECT, object_id=obj.id)

    def _open_background(self) -> None:
        from Kix.core.app import KixApp
        from Kix.core.screen_manager import ScreenManager

        app = KixApp.get_running_app()
        sm = app.root
        if isinstance(sm, ScreenManager):
            # abre ObjectScreen com flag background
            obj_screen = sm.get_screen(ScreenManager.OBJECT)
            if obj_screen is not None and hasattr(obj_screen, "set_background"):
                obj_screen.set_background()
            sm.go(ScreenManager.OBJECT)

    def _run_object(self, obj: KixObject) -> None:
        # TODO M8: executar scripts do objeto
        pass

    def _run_program(self) -> None:
        # TODO M8: executar programa do projeto (todos os scripts)
        pass

    def _show_kebab(self) -> None:
        """Menu kebab do app bar."""
        from Kix.ui.menu import DropdownMenu

        items = [
            {"key": "options", "label": "Opções do projeto", "glyph": "⚙",
             "on_select": lambda s: self._toast("Opções do projeto — em breve")},
            {"key": "files", "label": "Arquivos do projeto", "glyph": "📁",
             "on_select": lambda s: self._toast("Arquivos — em breve")},
            {"key": "libs", "label": "Bibliotecas do projeto", "glyph": "</>",
             "on_select": lambda s: self._toast("Bibliotecas — em breve")},
            {"key": "share", "label": "Compartilhar", "glyph": "↗",
             "on_select": lambda s: self._toast("Compartilhar — em breve")},
            {"key": "rename", "label": "Mudar nome do projeto", "glyph": "✎",
             "on_select": lambda s: self._rename_project()},
        ]
        kebab = self.ids.topbar.ids.get("kebab") if hasattr(self.ids.topbar, "ids") else None
        menu = DropdownMenu(items=items, anchor_widget=self.ids.topbar)
        self.add_widget(menu)

    def _show_object_menu(self, obj: KixObject, anchor) -> None:
        """Dropdown menu do objeto (linha kebab)."""
        from Kix.ui.menu import DropdownMenu

        items = [
            {"key": "backpack", "label": "Mochila", "glyph": "🎒",
             "on_select": lambda s: self._toast("Mochila — em breve")},
            {"key": "copy", "label": "Copiar", "glyph": "⎘",
             "on_select": lambda s: self._copy_object(obj)},
            {"key": "delete", "label": "Apagar", "glyph": "🗑",
             "on_select": lambda s: self._delete_object(obj)},
            {"key": "rename", "label": "Mudar nome", "glyph": "✎",
             "on_select": lambda s: self._rename_object(obj)},
            {"key": "new_group", "label": "Novo grupo", "glyph": "➕",
             "on_select": lambda s: self._toast("Novo grupo — em breve")},
            {"key": "new_scene", "label": "Nova cena", "glyph": "∿",
             "on_select": lambda s: self._toast("Nova cena — em breve")},
            {"key": "details", "label": "Mostrar detalhes", "glyph": "⋮",
             "on_select": lambda s: self._toast(f"{obj.name}: {obj.kind}")},
            {"key": "project_opts", "label": "Opções do projeto", "glyph": "⚙",
             "on_select": lambda s: self._toast("Opções — em breve")},
        ]
        menu = DropdownMenu(items=items, anchor_widget=anchor)
        self.add_widget(menu)

    def _show_add_object(self) -> None:
        """FAB + → AddObjectDialog."""
        from Kix.screens.add_object import AddObjectDialog

        def _on_select(key: str, kind: str) -> None:
            self._add_object(key, kind)

        dlg = AddObjectDialog(on_select=_on_select)
        self.add_widget(dlg)

    def _add_object(self, key: str, kind: str) -> None:
        if self.project is None:
            return
        idx = len(self.project.objects) + 1
        obj = KixObject(name=f"Ator {idx}", kind=kind)
        self.project.objects.append(obj)
        ProjectManager().save(self.project)
        self.refresh()

    def _copy_object(self, obj: KixObject) -> None:
        if self.project is None:
            return
        clone = KixObject(
            name=obj.name + " (cópia)",
            kind=obj.kind,
            image=obj.image,
        )
        self.project.objects.append(clone)
        ProjectManager().save(self.project)
        self.refresh()

    def _delete_object(self, obj: KixObject) -> None:
        if self.project is None:
            return
        self.project.objects = [o for o in self.project.objects if o.id != obj.id]
        ProjectManager().save(self.project)
        self.refresh()

    def _rename_object(self, obj: KixObject) -> None:
        from Kix.screens.rename_object import RenameObjectDialog
        dlg = RenameObjectDialog(
            current=obj.name,
            on_done=lambda new_name: self._apply_rename(obj, new_name),
        )
        self.add_widget(dlg)

    def _apply_rename(self, obj: KixObject, new_name: str) -> None:
        if not new_name or self.project is None:
            return
        obj.name = new_name
        ProjectManager().save(self.project)
        self.refresh()

    def _rename_project(self) -> None:
        from Kix.screens.rename_object import RenameObjectDialog
        dlg = RenameObjectDialog(
            current=self.project_name,
            on_done=lambda new_name: self._apply_project_rename(new_name),
        )
        self.add_widget(dlg)

    def _apply_project_rename(self, new_name: str) -> None:
        if not new_name or self.project is None:
            return
        old = self.project_name
        if new_name == old:
            return
        mgr = ProjectManager()
        mgr.rename(old, new_name)
        self.project_name = new_name
        self.project.name = new_name
        self._render_topbar()

    def _broadcast(self) -> None:
        # botão cast no app bar
        self._toast("Transmitir — em breve")

    def _toast(self, msg: str) -> None:
        # toast simples como popup modal centrado
        from Kix.ui.toast import Toast
        Toast(msg).show(self)


__all__ = ["EditorScreen"]
