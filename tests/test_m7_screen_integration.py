"""Testes M7 — Integração das telas no ScreenManager.

Valida que Dashboard + Editor + Object + Formula estão registradas
no KixApp, e que o editor navega para o ObjectScreen ao tocar num objeto.
"""

from __future__ import annotations

import ast
from pathlib import Path


# --- ScreenManager constants ---------------------------------------------

def test_screen_manager_has_object_and_formula_constants():
    from Kix.core.screen_manager import ScreenManager

    assert ScreenManager.DASHBOARD == "dashboard"
    assert ScreenManager.EDITOR == "editor"
    assert ScreenManager.OBJECT == "object"
    assert ScreenManager.FORMULA == "formula"


# --- App registra todas as telas ------------------------------------------

def test_app_registers_all_screens():
    """KixApp.build() adiciona Dashboard + Editor + Object + Formula."""
    text = (Path(__file__).parent.parent / "Kix/core/app.py").read_text()
    assert "DashboardScreen" in text
    assert "EditorScreen" in text
    assert "ObjectScreen" in text
    assert "FormulaEditorScreen" in text
    assert "ScreenManager.DASHBOARD" in text
    assert "ScreenManager.EDITOR" in text
    assert "ScreenManager.OBJECT" in text
    assert "ScreenManager.FORMULA" in text


# --- ObjectScreen + FormulaEditorScreen + RenameObjectDialog -----------

def test_object_screen_has_on_back_on_play():
    """ObjectScreen aceita on_back e on_play no construtor."""
    text = (Path(__file__).parent.parent / "Kix/screens/object_screen.py").read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ObjectScreen":
            init = next(
                (n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"),
                None,
            )
            assert init is not None
            args = [a.arg for a in init.args.args]
            assert "on_back" in args
            assert "on_play" in args


def test_formula_editor_has_on_done():
    """FormulaEditorScreen aceita on_done no construtor."""
    text = (Path(__file__).parent.parent / "Kix/screens/formula_editor.py").read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "FormulaEditorScreen":
            init = next(
                (n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"),
                None,
            )
            assert init is not None
            args = [a.arg for a in init.args.args]
            assert "on_done" in args


def test_rename_object_dialog_module():
    """RenameObjectDialog existe como classe."""
    text = (Path(__file__).parent.parent / "Kix/screens/rename_object.py").read_text()
    tree = ast.parse(text)
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert "RenameObjectDialog" in classes


# --- ObjetosTab substituiu SimplesTab ------------------------------------

def test_objetos_tab_module():
    text = (Path(__file__).parent.parent / "Kix/screens/tabs/objetos.py").read_text()
    tree = ast.parse(text)
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert "ObjetosTab" in classes
    assert "_ObjectRow" in classes


def test_editor_uses_objetos_tab_not_simples_for_objetos():
    """EditorScreen usa ObjetosTab para a aba 'objetos' (não mais SimplesTab)."""
    text = (Path(__file__).parent.parent / "Kix/screens/editor.py").read_text()
    # importa ObjetosTab
    assert "tabs.objetos" in text
    # E o branch elif name == "objetos" usa ObjetosTab
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test_src = ast.unparse(node.test).strip()
            if test_src == "'objetos'":
                body_src = ast.unparse(node)
                assert "ObjetosTab" in body_src
                assert "SimplesTab" not in body_src


def test_editor_exposes_sm_helper():
    """EditorScreen tem método _sm() que retorna ScreenManager."""
    text = (Path(__file__).parent.parent / "Kix/screens/editor.py").read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "EditorScreen":
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            assert "_sm" in methods


# --- Fluxo end-to-end: criar objeto + mochila -----------------------------

def test_end_to_end_create_object_then_share(tmp_path):
    """Fluxo: cria projeto → adiciona objeto → gera URL share."""
    from Kix.projects.backpack import Backpack
    from Kix.projects.manager import ProjectManager
    from Kix.projects.model import KixObject, KixScene, ProjectSettings
    from Kix.projects.share import decode_share_url, encode_share_url, is_shareable_url

    mgr = ProjectManager(base_dir=tmp_path)
    settings = ProjectSettings(share_link=True, version="1.0.0", orientation="landscape")
    proj = mgr.create("Demo", settings=settings)

    # adiciona 2 objetos
    proj.objects.append(KixObject(name="Ator 1", kind="sprite"))
    proj.objects.append(KixObject(name="Ator 2", kind="background"))
    proj.scenes.append(KixScene(name="Cena 1"))
    mgr.save(proj)

    # mochila
    bp = Backpack(base_dir=tmp_path / "backpack.json")
    proj.blocks.append({"id": "m1", "name": "Mover 10", "category": "motion"})
    mgr.save(proj)
    bp.import_from_project("Demo", ["m1"], base_dir=tmp_path)
    assert len(bp.list()) == 1

    # share link
    url = encode_share_url(proj.to_dict())
    assert is_shareable_url(url)
    decoded = decode_share_url(url)
    assert len(decoded["objects"]) == 2
    assert decoded["settings"]["share_link"] is True
    assert decoded["settings"]["orientation"] == "landscape"