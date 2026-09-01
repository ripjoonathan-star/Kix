"""CategoriasScreen — lista full-width de categorias (Pocket Code).

11+ linhas coloridas (Evento, Controle, Movimento, Som, Aparências,
Caneta, Dados, Dispositivo, Arquivos, Seus blocos, Bibliotecas).

Tap em categoria → lista de blocos daquela categoria (CategoriaScreen).

Screenshots Pocket Code de referência:
- Header: ← / "Categorias" / 🔍 / kebab
- Linhas: 60dp de altura, fundo cor da categoria, label BRANCO bold
  esquerda-aligned, padding generoso.
- FAB play + FAB +: cor LARANJA (não emerald/lavanda)
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
    BG,
    CAT_CONTROL, CAT_DATA, CAT_DEVICE, CAT_EVENT, CAT_FILES,
    CAT_LOOKS, CAT_MOTION, CAT_PEN, CAT_SOUND, CAT_USER, CAT_LIBS,
    LARANJA, LARANJA_PRESSED,
    PADDING, PADDING_SM, RADIUS_SM,
    SURFACE_1, SURFACE_2, SURFACE_3,
    TEXT_HIGH, TEXT_LOW, TEXT_MED,
)
from Kix.ui.app_bar import KixAppBar
from Kix.ui.button import IconButton
from Kix.ui.toast import Toast

Builder.load_string("""
<CategoriasScreen>:
    FloatLayout:
        BoxLayout:
            orientation: 'vertical'
            KixAppBar:
                id: topbar
            ScrollView:
                do_scroll_x: False
                bar_width: 0
                BoxLayout:
                    id: list_box
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(0), dp(0), dp(0), dp(120)]
                    spacing: dp(2)
        IconButton:
            id: fab_play
            glyph: '▶'
            primary: True
            size_hint: (None, None)
            size: dp(56), dp(56)
            x: root.width - dp(72)
            y: dp(104)
            on_release: root._run()
        IconButton:
            id: fab_add
            glyph: '+'
            primary: True
            size_hint: (None, None)
            size: dp(56), dp(56)
            x: root.width - dp(72)
            y: dp(32)
            on_release: root._add()
""")


# (label, cor, key interno)
_CATEGORIES = [
    ("Evento", CAT_EVENT, "event"),
    ("Controle", CAT_CONTROL, "control"),
    ("Movimento", CAT_MOTION, "motion"),
    ("Som", CAT_SOUND, "sound"),
    ("Aparências", CAT_LOOKS, "looks"),
    ("Caneta", CAT_PEN, "pen"),
    ("Dados", CAT_DATA, "data"),
    ("Dispositivo", CAT_DEVICE, "device"),
    ("Arquivos", CAT_FILES, "files"),
    ("Seus blocos", CAT_USER, "user"),
    ("Bibliotecas", CAT_LIBS, "libs"),
]


class _CategoryRow(BoxLayout):
    """Linha colorida full-width da lista de Categorias."""

    def __init__(self, label: str, color: tuple, on_select, **kwargs):
        super().__init__(**kwargs)
        self._on_select = on_select
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(20), dp(8), dp(20), dp(8)]

        with self.canvas.before:
            self._bg_color = Color(*color)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[0]
            )
        self.bind(pos=self._sync, size=self._sync, on_touch_down=self._on_touch)

        lbl = Label(
            text=label,
            color=(1, 1, 1, 1),
            font_size="18sp",
            bold=True,
            halign="left",
            valign="middle",
        )
        lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(lbl)

    def _sync(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _on_touch(self, _w, touch):
        if not self.collide_point(*touch.pos):
            return False
        # escurece brevemente
        from kivy.clock import Clock
        c = self._bg_color.rgba
        self._bg_color.rgba = (c[0]*0.8, c[1]*0.8, c[2]*0.8, c[3])
        Clock.schedule_once(lambda *_: setattr(self._bg_color, "rgba", c), 120)
        self._on_select()
        return True


class CategoriasScreen(Screen):
    """Lista full-width de categorias (Pocket Code)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self, *_):
        self._render_topbar()
        self._render_list()
        self._apply_fab_color()

    def _render_topbar(self) -> None:
        self.ids.topbar.set_title("Categorias")
        self.ids.topbar.set_back(lambda: self._back())
        self.ids.topbar.set_actions([
            ("search", "🔍", lambda *_: self._search()),
            ("kebab", "⋮", lambda *_: self._kebab()),
        ])

    def _render_list(self) -> None:
        box = self.ids.list_box
        box.clear_widgets()
        for label, color, key in _CATEGORIES:
            row = _CategoryRow(
                label=label, color=color,
                on_select=lambda k=key: self._open_category(k),
            )
            box.add_widget(row)

    def _apply_fab_color(self) -> None:
        # FABs da tela Categorias são LARANJA (Pocket Code)
        for fab_id in ("fab_play", "fab_add"):
            fab = self.ids.get(fab_id)
            if fab is not None and hasattr(fab, "_bg_color"):
                fab._bg_color.rgba = LARANJA

    # --- handlers --------------------------------------------------------
    def _open_category(self, key: str) -> None:
        from Kix.core.app import KixApp
        from Kix.core.screen_manager import ScreenManager

        app = KixApp.get_running_app()
        sm = app.root
        if isinstance(sm, ScreenManager):
            sm.go(ScreenManager.CATEGORIA, category=key)

    def _back(self) -> None:
        from Kix.core.app import KixApp
        from Kix.core.screen_manager import ScreenManager

        app = KixApp.get_running_app()
        sm = app.root
        if isinstance(sm, ScreenManager):
            sm.go(ScreenManager.OBJECT)

    def _search(self) -> None:
        Toast("Buscar — em breve").show(self)

    def _kebab(self) -> None:
        from Kix.ui.menu import DropdownMenu
        items = [
            {"key": "help", "label": "Ajuda", "glyph": "?",
             "on_select": lambda s: Toast("Ajuda — em breve").show(self)},
            {"key": "about", "label": "Sobre", "glyph": "i",
             "on_select": lambda s: Toast("Kix M7 — Paridade Pocket Code").show(self)},
        ]
        menu = DropdownMenu(items=items, anchor_widget=self.ids.topbar)
        self.add_widget(menu)

    def _run(self) -> None:
        Toast("Executar — em breve").show(self)

    def _add(self) -> None:
        Toast("Adicionar bloco — em breve").show(self)


__all__ = ["CategoriasScreen", "_CATEGORIES"]
