"""CategoriaScreen — lista vertical de blocos de uma categoria.

Tap em bloco com input → abre FormulaEditor.
Tap em bloco sem input → insere no canvas (M8).

Header:
- App bar com ← + nome da categoria
- Fundo da cor da categoria (full-width header band)
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from Kix.block_engine.block import KixBlock
from Kix.blocks.builtin import ALL as ALL_BLOCKS
from Kix.core.theme import (
    BG, PADDING, PADDING_SM, RADIUS_SM,
    SURFACE_1, SURFACE_2, SURFACE_3, SURFACE_4,
    TEXT_HIGH, TEXT_LOW, TEXT_MED,
)
from Kix.ui.app_bar import KixAppBar
from Kix.ui.block_chip import BlockChip
from Kix.ui.button import IconButton
from Kix.ui.toast import Toast
from Kix.screens.categorias import _CATEGORIES

Builder.load_string("""
<CategoriaScreen>:
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
                    padding: [dp(8), dp(8), dp(8), dp(96)]
                    spacing: dp(6)
""")


_CAT_LABELS = {key: label for label, _color, key in _CATEGORIES}
_CAT_COLORS = {key: color for label, color, key in _CATEGORIES}


class _BlockRow(BoxLayout):
    """Linha que mostra um BlockChip + tap handler."""

    def __init__(self, block: KixBlock, on_select, **kwargs):
        super().__init__(**kwargs)
        self._block = block
        self._on_select = on_select
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(48) if not block.is_hat else dp(54)
        self.padding = [dp(8), dp(2), dp(8), dp(2)]

        chip = BlockChip(block)
        self.add_widget(chip)

        self.bind(on_touch_down=self._on_touch)

    def _on_touch(self, _w, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._on_select(self._block)
        return True


class CategoriaScreen(Screen):
    """Lista vertical de blocos de uma categoria."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category: str = "motion"

    def on_enter(self, *_):
        self._render_topbar()
        self._render_list()

    def set_category(self, key: str) -> None:
        self.category = key

    def _render_topbar(self) -> None:
        title = _CAT_LABELS.get(self.category, self.category.title())
        self.ids.topbar.set_title(title)
        self.ids.topbar.set_back(lambda: self._back())

    def _render_list(self) -> None:
        box = self.ids.list_box
        box.clear_widgets()
        # filtra blocos da categoria
        blocks = [b for b in ALL_BLOCKS if b.category == self.category]
        if not blocks:
            box.add_widget(self._empty())
            return
        for b in blocks:
            row = _BlockRow(b, on_select=lambda blk: self._select_block(blk))
            box.add_widget(row)

    def _empty(self) -> BoxLayout:
        msg = Label(
            text="Nenhum bloco nesta categoria",
            color=TEXT_LOW, font_size="14sp",
            halign="center", valign="middle",
            size_hint_y=None, height=dp(80),
        )
        msg.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(80))
        box.add_widget(msg)
        return box

    def _select_block(self, block: KixBlock) -> None:
        # se tem inputs NUMBER, abre FormulaEditor; senão toast
        has_number_input = any(
            s.kind.value == "number" for s in block.inputs
        )
        if has_number_input and self.category in ("math", "looks", "motion",
                                                   "control", "event"):
            from Kix.core.app import KixApp
            from Kix.core.screen_manager import ScreenManager

            app = KixApp.get_running_app()
            sm = app.root
            if isinstance(sm, ScreenManager):
                sm.go(ScreenManager.FORMULA, block=block)
        else:
            Toast(f"{block.name} selecionado").show(self)

    def _back(self) -> None:
        from Kix.core.app import KixApp
        from Kix.core.screen_manager import ScreenManager

        app = KixApp.get_running_app()
        sm = app.root
        if isinstance(sm, ScreenManager):
            sm.go(ScreenManager.CATEGORIAS)


__all__ = ["CategoriaScreen"]
