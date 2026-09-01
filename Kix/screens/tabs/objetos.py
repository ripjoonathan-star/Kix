"""Aba Objetos — lista de KixObject do projeto.

Tap num objeto abre o ObjectScreen (sub-abas Scripts/Looks/Sounds).
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from Kix.core.screen_manager import ScreenManager
from Kix.core.theme import (
    EMERALD,
    PADDING,
    RADIUS,
    RADIUS_SM,
    SURFACE_2,
    SURFACE_3,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
)
from Kix.projects.model import KixObject
from Kix.ui.button import IconButton


class _ObjectRow(BoxLayout):
    """Linha de objeto na lista: ▶ (emerald) + nome + kebab."""

    def __init__(self, obj: KixObject, on_open, on_menu, **kwargs):
        super().__init__(**kwargs)
        self._obj = obj
        self._on_open = on_open
        self._on_menu = on_menu
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(64)
        self.padding = [dp(8), dp(8), dp(8), dp(8)]
        self.spacing = dp(10)

        with self.canvas.before:
            self._bg_color = Color(*SURFACE_2)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[RADIUS_SM]
            )
        self.bind(pos=self._sync, size=self._sync, on_touch_down=self._on_touch)

        play = IconButton(glyph="▶", primary=True)
        play.size_hint = (None, None)
        play.size = (dp(44), dp(44))
        play.bind(on_release=lambda *_: self._on_open(self._obj))
        self.add_widget(play)
        self._play = play

        name_lbl = Label(
            text=obj.name,
            color=TEXT_HIGH,
            font_size="15sp",
            halign="left",
            valign="middle",
        )
        name_lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(name_lbl)

        kebab = IconButton(glyph="⋮", primary=False)
        kebab.size_hint = (None, None)
        kebab.size = (dp(44), dp(44))
        kebab.bind(on_release=lambda *_: self._on_menu(self._obj, kebab))
        self.add_widget(kebab)
        self._kebab = kebab

    def _sync(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _on_touch(self, _w, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._bg_color.rgba = SURFACE_3
        from kivy.clock import Clock
        Clock.schedule_once(lambda *_: setattr(self._bg_color, "rgba", SURFACE_2), 100)
        return True


class ObjetosTab(BoxLayout):
    """Lista de objetos do projeto. Tap = abre ObjectScreen."""

    def __init__(self, screen, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self._screen = screen
        self._build()

    def _build(self) -> None:
        self.padding = [PADDING, PADDING, PADDING, PADDING]
        self.spacing = dp(8)

        head = Label(
            text="Atores e objetos",
            color=TEXT_MED,
            font_size="14sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(28),
        )
        head.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(head)

        self._list_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
        )
        self._list_box.bind(minimum_height=self._sync_list_height)
        self.add_widget(self._list_box)

        self.refresh()

    def _sync_list_height(self, _inst, h):
        self._list_box.height = h

    def refresh(self) -> None:
        self._list_box.clear_widgets()
        project = self._screen.project
        if project is None or not project.objects:
            empty = Label(
                text="Sem objetos ainda.\nToque em '+' para adicionar.",
                color=TEXT_LOW,
                font_size="13sp",
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(120),
            )
            empty.bind(size=lambda i, _: setattr(i, "text_size", i.size))
            self._list_box.add_widget(empty)
            return

        for obj in project.objects:
            row = _ObjectRow(
                obj=obj,
                on_open=self._open_object,
                on_menu=self._show_object_menu,
            )
            self._list_box.add_widget(row)

    # --- handlers ------------------------------------------------------
    def _open_object(self, obj: KixObject) -> None:
        sm = self._screen._sm()
        if sm is None:
            return
        # carrega o objeto no ObjectScreen e navega
        object_screen = sm.get_screen(ScreenManager.OBJECT)
        if hasattr(object_screen, "load_object"):
            object_screen.load_object(obj)
        sm.go(ScreenManager.OBJECT)

    def _show_object_menu(self, obj: KixObject, anchor) -> None:
        """Abre DropdownMenu com ações do objeto."""
        from Kix.ui.menu import DropdownMenu

        items = [
            {"key": "backpack", "label": "Mochila", "glyph": "🎒",
             "on_select": lambda *_: self._handle(obj, "backpack")},
            {"key": "copy", "label": "Copiar", "glyph": "⎘",
             "on_select": lambda *_: self._handle(obj, "copy")},
            {"key": "delete", "label": "Apagar", "glyph": "🗑",
             "on_select": lambda *_: self._handle(obj, "delete")},
            {"key": "rename", "label": "Mudar nome", "glyph": "✎",
             "on_select": lambda *_: self._handle(obj, "rename")},
            {"key": "new_group", "label": "Novo grupo", "glyph": "📁",
             "on_select": lambda *_: self._handle(obj, "new_group")},
            {"key": "new_scene", "label": "Nova cena", "glyph": "🎬",
             "on_select": lambda *_: self._handle(obj, "new_scene")},
        ]
        menu = DropdownMenu(items=items, anchor_widget=anchor)
        if self._screen.parent is not None:
            self._screen.parent.add_widget(menu)

    def _handle(self, obj: KixObject, key: str) -> None:
        from Kix.projects.manager import ProjectManager

        project = self._screen.project
        if project is None:
            return
        mgr = ProjectManager()
        if key == "delete":
            project.objects = [o for o in project.objects if o.id != obj.id]
            mgr.save(project)
            self.refresh()
        elif key == "rename":
            from Kix.screens.rename_object import RenameObjectDialog
            dlg = RenameObjectDialog(
                initial=obj.name,
                on_done=lambda new_name: self._apply_rename(obj, new_name),
            )
            if self._screen.parent is not None:
                self._screen.parent.add_widget(dlg)
        elif key == "copy":
            from copy import deepcopy
            clone = deepcopy(obj)
            clone.id = f"obj_{len(project.objects) + 1:03d}"
            clone.name = obj.name + " (cópia)"
            project.objects.append(clone)
            mgr.save(project)
            self.refresh()
        elif key == "new_group":
            # placeholder: cria um objeto "Grupo"
            from Kix.projects.model import KixObject
            new_obj = KixObject(name="Grupo")
            project.objects.append(new_obj)
            mgr.save(project)
            self.refresh()
        elif key == "new_scene":
            from Kix.projects.model import KixScene
            scene = KixScene(name="Cena")
            project.scenes.append(scene)
            mgr.save(project)

    def _apply_rename(self, obj: KixObject, new_name: str) -> None:
        if not new_name or not new_name.strip():
            return
        obj.name = new_name.strip()
        from Kix.projects.manager import ProjectManager
        ProjectManager().save(self._screen.project)
        self.refresh()

    def show_add_dialog(self) -> None:
        """Abre AddObjectDialog. Chamado pelo FAB + da aba Objetos."""
        from Kix.screens.add_object import AddObjectDialog

        def _on_select(key: str, kind: str) -> None:
            self._add_object(key, kind)

        dlg = AddObjectDialog(on_select=_on_select)
        if self._screen.parent is not None:
            self._screen.parent.add_widget(dlg)

    def _add_object(self, key: str, kind: str) -> None:
        from Kix.projects.manager import ProjectManager
        from Kix.projects.model import KixObject

        project = self._screen.project
        if project is None:
            return
        # Alguns são stubs (Mochila, Da biblioteca, etc.) — só placeholder
        stub_keys = {"backpack", "from_lib", "draw", "photo", "media"}
        if key in stub_keys:
            # cria objeto vazio como placeholder
            pass
        # cria objeto novo
        mgr = ProjectManager()
        idx = sum(1 for _ in project.objects) + 1
        new_obj = KixObject(
            name=("Ator " + str(idx)) if key in stub_keys else ("Ator " + str(idx)),
            kind=kind,
        )
        project.objects.append(new_obj)
        mgr.save(project)
        self.refresh()


__all__ = ["ObjetosTab"]