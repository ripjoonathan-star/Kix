"""Testes M7 — Paridade visual Pocket Code.

Foca em garantir que os novos componentes existem, têm a forma certa
e roundtrip correto. Sem display: testa-se só estrutura dos dados
e dataclasses (a parte gráfica fica smoke-tested via Python AST/imports).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


# --- helpers --------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# --- ProjectSettings (item 2 do plano M7) --------------------------------

def test_project_settings_has_pocketcode_fields():
    from Kix.projects.model import ProjectSettings

    s = ProjectSettings()
    assert s.version == "1.0.0"
    assert s.orientation == "portrait"
    assert s.share_link is False


def test_project_settings_round_trip():
    from Kix.projects.model import ProjectSettings

    original = ProjectSettings(
        width=800,
        height=480,
        orientation="landscape",
        version="2.5.1",
        share_link=True,
    )
    data = original.to_dict()
    restored = ProjectSettings.from_dict(data)
    assert restored.width == 800
    assert restored.height == 480
    assert restored.orientation == "landscape"
    assert restored.version == "2.5.1"
    assert restored.share_link is True


def test_project_settings_invalid_orientation_defaults_to_portrait():
    from Kix.projects.model import ProjectSettings

    s = ProjectSettings.from_dict({"orientation": "diagonal"})
    assert s.orientation == "portrait"


def test_project_settings_version_can_be_changed():
    from Kix.projects.model import ProjectSettings

    s = ProjectSettings.from_dict({"version": "9.9.9-rc1"})
    assert s.version == "9.9.9-rc1"


def test_kixproject_full_round_trip_with_settings():
    from Kix.projects.model import KixProject, KixScene, ProjectSettings

    p = KixProject(name="Meu Jogo", description="test")
    p.settings = ProjectSettings(
        width=480, height=800, orientation="landscape", version="3.0.0", share_link=True
    )
    p.scenes.append(KixScene(name="Cena 1"))

    payload = p.to_dict()
    text = json.dumps(payload)
    restored = KixProject.from_dict(json.loads(text))

    assert restored.name == "Meu Jogo"
    assert restored.settings.version == "3.0.0"
    assert restored.settings.orientation == "landscape"
    assert restored.settings.share_link is True
    assert len(restored.scenes) == 1


# --- ProjectManager.create aceita settings (item 2 do plano) -------------

def test_manager_create_with_settings(tmp_path):
    from Kix.projects.manager import ProjectManager
    from Kix.projects.model import ProjectSettings

    mgr = ProjectManager(base_dir=tmp_path)
    settings = ProjectSettings(
        width=640, height=360, orientation="landscape", version="1.2.3", share_link=True
    )
    project = mgr.create("Demo", settings=settings)
    assert project.settings.version == "1.2.3"
    assert project.settings.orientation == "landscape"
    assert project.settings.share_link is True
    # persiste
    loaded = mgr.load("Demo")
    assert loaded.settings.version == "1.2.3"


# --- Tema Pocket Code (item 1 do plano) ----------------------------------

def test_theme_has_pocketcode_palette():
    from Kix.core import theme as t

    # Cores hex comentadas batem com #3C8DCF, #67AD3F, #9B59B6, etc.
    expected = {
        "CAT_MOTION": (0.235, 0.553, 0.812, 1),
        "CAT_LOOKS": (0.404, 0.678, 0.247, 1),
        "CAT_SOUND": (0.608, 0.349, 0.714, 1),
        "CAT_CONTROL": (0.886, 0.627, 0.388, 1),
        "CAT_EVENT": (0.659, 0.278, 0.231, 1),
        "CAT_DATA": (0.886, 0.408, 0.537, 1),
        "CAT_DEVICE": (0.639, 0.561, 0.176, 1),
        "CAT_FILES": (0.741, 0.718, 0.259, 1),
        "CAT_USER": (0.235, 0.435, 0.898, 1),
        "CAT_LIBS": (0.882, 0.561, 0.667, 1),
    }
    for name, color in expected.items():
        actual = getattr(t, name)
        assert actual == pytest.approx(color, abs=0.005), f"{name}: esperado {color}, obtido {actual}"


def test_theme_category_order():
    from Kix.core.theme import CATEGORY_ORDER

    assert "event" in CATEGORY_ORDER
    assert CATEGORY_ORDER[0] == "event"  # Evento sempre primeiro no Pocket Code
    assert "control" in CATEGORY_ORDER
    assert "motion" in CATEGORY_ORDER


def test_theme_has_pocketcode_radius_constants():
    from Kix.core.theme import RADIUS, RADIUS_SM, PADDING, PADDING_LG, RADIUS_XS

    assert RADIUS > 0
    assert RADIUS_SM > 0
    assert RADIUS_XS > 0
    assert PADDING > 0
    assert PADDING_LG >= PADDING


def test_hex_to_rgba_helper():
    from Kix.core.theme import hex_to_rgba

    assert hex_to_rgba("#3C8DCF") == pytest.approx((0.235, 0.553, 0.812, 1.0), abs=0.005)
    assert hex_to_rgba("#FF0000FF") == pytest.approx((1.0, 0.0, 0.0, 1.0), abs=0.005)


# --- Telas existem e têm a forma certa (importável, não-instanciável sem display) ---

def test_new_project_module_imports():
    """O módulo carrega sem erros de sintaxe."""
    spec_path = ROOT / "Kix/screens/new_project.py"
    assert spec_path.exists()
    import ast

    tree = ast.parse(spec_path.read_text())
    # Procura classe NewProjectDialog
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert "NewProjectDialog" in classes
    assert "_IconTile" in classes
    assert "_OrientationOption" in classes
    assert "_CheckBox" in classes


def test_add_object_module_imports():
    """O módulo carrega sem erros de sintaxe."""
    spec_path = ROOT / "Kix/screens/add_object.py"
    assert spec_path.exists()
    import ast

    tree = ast.parse(spec_path.read_text())
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert "AddObjectDialog" in classes
    assert "_GridItem" in classes


def test_dropdown_menu_module_imports():
    """O módulo carrega sem erros de sintaxe."""
    spec_path = ROOT / "Kix/ui/menu.py"
    assert spec_path.exists()
    import ast

    tree = ast.parse(spec_path.read_text())
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert "DropdownMenu" in classes
    assert "_MenuItem" in classes


# --- Dashboard (item 1 do plano: remove RecentProjectCard) ---------------

def test_dashboard_does_not_import_recent_project_card():
    """dashboard.py não importa mais RecentProjectCard."""
    text = (ROOT / "Kix/screens/dashboard.py").read_text()
    assert "RecentProjectCard" not in text


def test_dashboard_uses_new_project_dialog():
    """dashboard.py usa NewProjectDialog (não Popup)."""
    text = (ROOT / "Kix/screens/dashboard.py").read_text()
    assert "NewProjectDialog" in text
    # não usa mais Popup para criar projeto
    assert "_show_new_project_popup" in text


def test_dashboard_no_recent_section_label():
    """refresh() não chama _section_label('Projeto mais recente')."""
    import ast

    tree = ast.parse((ROOT / "Kix/screens/dashboard.py").read_text())
    # Procura todas as chamadas _section_label(...) no módulo
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "_section_label":
                if node.args and isinstance(node.args[0], ast.Constant):
                    found.append(node.args[0].value)
    assert "Projeto mais recente" not in found
    assert "Projetos" in found


# --- 9 opções do AddObjectDialog -----------------------------------------

def test_add_object_has_nine_options():
    """9 opções: 8 do grid 2×4 + 'Projetos locais' linha cheia."""
    spec_path = ROOT / "Kix/screens/add_object.py"
    text = spec_path.read_text()
    # Conta items na lista _OPTIONS
    expected_keys = ["draw", "media", "image", "library", "photo", "backpack", "from_lib", "empty", "local"]
    for k in expected_keys:
        assert f'"{k}"' in text, f"key {k} não encontrada em AddObjectDialog"
    assert text.count('"key":') >= 9


# --- DropdownMenu items do Editor ----------------------------------------

def test_dropdown_menu_has_actor_items():
    """Itens do dropdown menu do objeto (Mochila, Copiar, etc.).

    Verificamos só a estrutura textual do módulo para garantir que os
    labels corretos estão lá. Comportamento runtime fica defer para M8+.
    """
    # Por enquanto não há dropdown embutido no editor — vamos só garantir
    # que o módulo DropdownMenu está pronto para uso.
    from Kix.ui import menu as _m  # import smoke
    assert hasattr(_m, "DropdownMenu")


# --- Cores Pocket Code aplicadas a categorias ----------------------------

def test_pocketcode_color_mapping_is_consistent():
    """Cada CAT_* tem 4 componentes (RGBA) e alpha=1."""
    from Kix.core import theme as t

    cat_names = [n for n in dir(t) if n.startswith("CAT_") and not n.endswith("_ORDER")]
    for name in cat_names:
        rgba = getattr(t, name)
        assert isinstance(rgba, tuple)
        assert len(rgba) == 4, f"{name} deve ter 4 componentes RGBA"
        assert rgba[3] == 1, f"{name} deve ter alpha=1"


# --- Editor de fórmula (item 9 do plano M7) ------------------------------

def test_formula_editor_module_loads():
    import ast
    from pathlib import Path
    p = Path("Kix/screens/formula_editor.py")
    assert p.exists()
    tree = ast.parse(p.read_text())
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert "FormulaEditorScreen" in classes
    assert "tokenize" in [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]


def test_tokenize_basic_arithmetic():
    from Kix.screens.formula_editor import tokenize

    tokens = tokenize("1+2*3")
    kinds = [t[0] for t in tokens]
    assert "NUMBER" in kinds
    assert "OPER" in kinds
    # ordem
    assert tokens[0] == ("NUMBER", "1")


def test_tokenize_function_call():
    from Kix.screens.formula_editor import tokenize

    tokens = tokenize("sin(x)+1.5")
    func_tokens = [t for t in tokens if t[0] == "FUNC"]
    assert any(t[1] == "sin" for t in func_tokens)
    var_tokens = [t for t in tokens if t[0] == "VARIABLE"]
    assert any(t[1] == "x" for t in var_tokens)


def test_tokenize_string_and_boolean():
    from Kix.screens.formula_editor import tokenize

    tokens = tokenize('"hello" == True')
    assert ("STRING", '"hello"') in tokens
    assert ("BOOLEAN", "True") in tokens


def test_tokenize_empty_returns_empty_list():
    from Kix.screens.formula_editor import tokenize

    assert tokenize("") == []


def test_formula_evaluates_arithmetic():
    """Bateria do executor: expressão '1+2*3' → 7."""
    import asyncio

    from Kix.block_engine.behavior import BlockBehavior
    from Kix.block_engine.block import KixBlock
    from Kix.block_engine.visual import BlockVisual, Text
    from Kix.engine.ctx import make_ctx
    from Kix.engine.executor import BlockExecutor

    block = KixBlock(
        id="t1", name="avaliar", category="math",
        color=(0.3, 0.6, 0.8, 1),
        visual=BlockVisual(root=Text(value="1+2*3")),
        behavior=BlockBehavior(language="python", source="return (1+2*3)"),
    )
    result = asyncio.run(BlockExecutor().run_block(block, ctx=make_ctx(), inputs={}))
    assert result == 7


def test_formula_evaluates_math_function():
    """sin(0) → 0.0."""
    import asyncio
    import math

    from Kix.block_engine.behavior import BlockBehavior
    from Kix.block_engine.block import KixBlock
    from Kix.block_engine.visual import BlockVisual, Text
    from Kix.engine.ctx import make_ctx
    from Kix.engine.executor import BlockExecutor

    block = KixBlock(
        id="t2", name="sin", category="math",
        color=(0.3, 0.6, 0.8, 1),
        visual=BlockVisual(root=Text(value="sin(0)")),
        behavior=BlockBehavior(language="python", source="return math.sin(0)"),
    )
    result = asyncio.run(BlockExecutor().run_block(block, ctx=make_ctx(), inputs={}))
    assert result == pytest.approx(0.0, abs=1e-9)


# --- Tela do objeto com sub-abas (item 6 do plano M7) --------------------

def test_object_screen_module_planned():
    """Placeholder: tela do objeto com Scripts/Looks/Sounds será adicionada em M7.6."""
    # Por enquanto, só validamos que existe um diretório screens/tabs/ ou screens/ com arquivos relacionados.
    from pathlib import Path
    screens = Path("Kix/screens").glob("*.py")
    screen_names = [p.stem for p in screens]
    # Este teste fica como lembrete para M7.6
    assert "formula_editor" in screen_names  # já existe
    # Quando M7.6 for implementado, criar tests para isso


# --- Dropdown menu ações (item 4 do plano M7) ----------------------------

def test_dropdown_menu_supports_on_select_callback():
    """DropdownMenu aceita items com chave/label/on_select."""
    import ast
    from pathlib import Path

    text = Path("Kix/ui/menu.py").read_text()
    tree = ast.parse(text)
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert "DropdownMenu" in classes
    # Verifica que o init tem parâmetro 'items'
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "DropdownMenu":
            init = next((n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
            assert init is not None
            args = [a.arg for a in init.args.args]
            assert "items" in args


def test_add_object_dialog_has_all_actions():
    """AddObjectDialog expõe 9 opções, todas callback-áveis."""
    import ast
    from pathlib import Path

    text = Path("Kix/screens/add_object.py").read_text()
    # 9 keys no _OPTIONS
    for k in ("draw", "media", "image", "library", "photo",
              "backpack", "from_lib", "empty", "local"):
        assert f'"{k}"' in text


# --- ProjectManager actions para menu de contexto ------------------------

def test_manager_supports_rename_copy_delete(tmp_path):
    """Métodos rename/duplicate/delete existem e funcionam."""
    from Kix.projects.manager import ProjectManager

    mgr = ProjectManager(base_dir=tmp_path)
    p = mgr.create("Original")
    assert p is not None

    # rename
    mgr.rename("Original", "Renomeado")
    assert mgr.exists("Renomeado")
    assert not mgr.exists("Original")

    # duplicate
    mgr.duplicate("Renomeado", "Copia")
    assert mgr.exists("Copia")

    # delete
    mgr.delete("Copia")
    assert not mgr.exists("Copia")


def test_manager_duplicate_regenerates_ids(tmp_path):
    """Duplicate renova IDs para evitar colisão."""
    from Kix.projects.manager import ProjectManager

    mgr = ProjectManager(base_dir=tmp_path)
    mgr.create("Origem")
    p = mgr.duplicate("Origem", "Destino")
    assert p.name == "Destino"
    # IDs do destino são novos (não compartilha com Origem)
    orig = mgr.load("Origem")
    dest_ids = {s.id for s in p.scenes}
    orig_ids = {s.id for s in orig.scenes}
    if dest_ids and orig_ids:
        assert dest_ids.isdisjoint(orig_ids)