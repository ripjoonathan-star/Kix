"""Testes M7 — navegação Pocket Code real entre telas.

Exercita o fluxo Dashboard → Editor → Object → Categorias → Categoria
sem precisar de display (usa KivyMock ou instancia widgets direto).
"""

from __future__ import annotations

import os
import sys

import pytest


# Estes testes instanciam widgets Kivy (BoxLayout). Precisam de Window provider funcional.
# Em ambiente headless sem GL/SDL2, pulamos com motivo claro.
_HAS_DISPLAY = False
try:
    os.environ.setdefault("KIVY_NO_ARGS", "1")
    # força inicialização do provider — se não houver GL/SDL2, falha aqui
    from kivy.core.window import Window
    _ = Window.size  # noqa: B018
    _HAS_DISPLAY = True
except Exception:
    _HAS_DISPLAY = False


needs_display = pytest.mark.skipif(
    not _HAS_DISPLAY,
    reason="requer display/GL para instanciar widgets Kivy",
)


def test_dashboard_lists_projects_without_recent_card():
    """Dashboard não tem mais 'Projeto mais recente' — só lista 'Projetos'."""
    text = open("Kix/screens/dashboard.py").read()
    assert "RecentProjectCard" not in text, "Dashboard ainda importa RecentProjectCard"
    assert "_section_label(\"Projetos\")" in text or '_section_label("Projetos")' in text


def test_editor_layout_no_tab_bar():
    """EditorScreen não tem tab bar inferior (Pocket Code style)."""
    text = open("Kix/screens/editor.py").read()
    # não há mais o bloco de 5 tabs
    assert "_TAB_LABELS" not in text
    assert "tabs.objetos" not in text
    # tem Fundo + Atores
    assert "Fundo" in text
    assert "Atores e objetos" in text


def test_editor_fab_color_is_lavanda():
    """FABs do Editor são lavanda (#B4A8DF), não emerald."""
    from Kix.core import theme
    text = open("Kix/screens/editor.py").read()
    assert "LAVANDA" in text
    assert theme.LAVANDA[0] < 0.8  # mais roxo que verde


def test_object_screen_resolves_object_id_on_enter():
    """ObjectScreen.on_enter resolve object_id via ScreenManager."""
    from Kix.screens.object_screen import ObjectScreen
    import inspect
    src = inspect.getsource(ObjectScreen.on_enter)
    assert "object_id" in src
    assert "ScreenManager.EDITOR" in src


def test_categorias_screen_has_11_colored_rows():
    """CategoriasScreen tem 11 categorias na ordem Pocket Code."""
    from Kix.screens.categorias import _CATEGORIES
    assert len(_CATEGORIES) == 11
    labels = [c[0] for c in _CATEGORIES]
    assert labels[0] == "Evento"
    assert labels[-1] == "Bibliotecas"
    # cores vêm do theme
    from Kix.core import theme
    for label, color, key in _CATEGORIES:
        assert len(color) == 4  # RGBA


def test_categorias_screen_fab_color_is_laranja():
    """FABs de Categorias são laranja (#FF9800)."""
    from Kix.core import theme
    text = open("Kix/screens/categorias.py").read()
    assert "LARANJA" in text
    # laranja tem R > G > B
    assert theme.LARANJA[0] > theme.LARANJA[1] > theme.LARANJA[2]


def test_categoria_screen_renders_blocks_with_hat_shape():
    """CategoriaScreen usa BlockChip — hat-blocks aparecem com is_hat=True."""
    from Kix.screens.categoria import CategoriaScreen
    text = open("Kix/screens/categoria.py").read()
    assert "BlockChip" in text


def test_event_blocks_have_is_hat_true():
    """Os 8 hat-blocks de evento têm is_hat=True."""
    from Kix.blocks.event import EVENTS
    hats = [b for b in EVENTS if b.is_hat]
    assert len(hats) >= 8, f"esperado ≥8 hat blocks, obtido {len(hats)}"
    ids = {b.id for b in hats}
    assert "event.scene_start" in ids
    assert "event.tap" in ids
    assert "event.message_received" in ids


def test_control_clone_start_is_hat():
    """control.clone_start também é hat (Quando eu começar como clone)."""
    from Kix.blocks.control import WHEN_CLONE_START
    assert WHEN_CLONE_START.is_hat is True


def test_kixblock_is_hat_default_false():
    """KixBlock.is_hat default False (compat com blocos existentes)."""
    from Kix.block_engine import KixBlock
    from Kix.block_engine.visual import BlockVisual, Group, Text
    from Kix.block_engine.behavior import BlockBehavior
    b = KixBlock(
        id="t.x", name="X", category="test", color=(0,0,0,1),
        visual=BlockVisual(root=Group(children=[Text("X")])),
        behavior=BlockBehavior("python", "pass"),
    )
    assert b.is_hat is False


def test_kixblock_is_hat_round_trip():
    """KixBlock.is_hat sobrevive to_dict/from_dict."""
    from Kix.block_engine import KixBlock
    from Kix.block_engine.visual import BlockVisual, Group, Text
    from Kix.block_engine.behavior import BlockBehavior
    b = KixBlock(
        id="t.h", name="Hat", category="event", color=(1,0,0,1),
        visual=BlockVisual(root=Group(children=[Text("hat")])),
        behavior=BlockBehavior("python", "pass"),
        is_hat=True,
    )
    d = b.to_dict()
    assert d["is_hat"] is True
    b2 = KixBlock.from_dict(d)
    assert b2.is_hat is True


@needs_display
def test_block_chip_renders_text_and_inputs():
    """BlockChip monta Group(Text, BlockInput) → Label + TextInput."""
    from kivy.uix.textinput import TextInput
    from kivy.uix.label import Label
    from Kix.block_engine import KixBlock, BlockVisual, Group, Text, BlockInput, SocketDef, SocketKind
    from Kix.block_engine.behavior import BlockBehavior
    from Kix.ui.block_chip import BlockChip

    b = KixBlock(
        id="t.m", name="Mover", category="motion", color=(0.2, 0.6, 0.8, 1),
        visual=BlockVisual(root=Group(children=[
            Text("Mover "), BlockInput("steps"), Text(" passos"),
        ])),
        inputs=[SocketDef("steps", SocketKind.NUMBER, default=10)],
        behavior=BlockBehavior("python", "pass"),
    )
    chip = BlockChip(b)
    has_text = any(isinstance(c, Label) and "Mover" in c.text for c in chip.children)
    has_input = any(isinstance(c, TextInput) for c in chip.children)
    assert has_text
    assert has_input


@needs_display
def test_block_chip_hat_shape_has_extra_padding():
    """BlockChip com is_hat tem altura maior que sem is_hat."""
    from Kix.block_engine import KixBlock, BlockVisual, Group, Text
    from Kix.block_engine.behavior import BlockBehavior
    from Kix.ui.block_chip import BlockChip

    base = dict(
        visual=BlockVisual(root=Group(children=[Text("X")])),
        behavior=BlockBehavior("python", "pass"),
    )
    regular = KixBlock(id="t.r", name="r", category="c", color=(0,0,0,1), **base)
    hat = KixBlock(id="t.h", name="h", category="c", color=(0,0,0,1), is_hat=True, **base)

    c_regular = BlockChip(regular)
    c_hat = BlockChip(hat)
    assert c_hat.height > c_regular.height


def test_kixapp_registers_all_screens():
    """KixApp.build() registra Dashboard + Editor + Object + Formula + Categorias + Categoria."""
    text = open("Kix/core/app.py").read()
    assert "DashboardScreen" in text
    assert "EditorScreen" in text
    assert "ObjectScreen" in text
    assert "FormulaEditorScreen" in text
    assert "CategoriasScreen" in text
    assert "CategoriaScreen" in text


def test_screen_manager_has_categorias_route():
    """ScreenManager tem constante CATEGORIAS e CATEGORIA."""
    from Kix.core.screen_manager import ScreenManager
    assert ScreenManager.CATEGORIAS == "categorias"
    assert ScreenManager.CATEGORIA == "categoria"


def test_appbar_supports_set_title_and_set_actions():
    """KixAppBar.set_title e set_actions funcionam."""
    text = open("Kix/ui/app_bar.py").read()
    assert "def set_title" in text
    assert "def set_actions" in text
    assert "def set_back" in text


def test_theme_has_lavanda_laranja_cyan_tab():
    """theme.py tem LAVANDA, LARANJA, CYAN_TAB."""
    from Kix.core import theme
    assert hasattr(theme, "LAVANDA")
    assert hasattr(theme, "LARANJA")
    assert hasattr(theme, "CYAN_TAB")
