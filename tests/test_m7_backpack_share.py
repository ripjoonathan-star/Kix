"""Testes M7 — Backpack + Share link.

Foco em estrutura de dados e roundtrip. UI drag-and-drop real fica
para M8 (Kivy DragBehavior); UI de share dialog é stub.
"""

from __future__ import annotations

import base64
import json
import zlib


# --- Backpack --------------------------------------------------------------

def test_backpack_module_imports():
    import ast
    from pathlib import Path
    p = Path("Kix/projects/backpack.py")
    assert p.exists()
    tree = ast.parse(p.read_text())
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert "Backpack" in classes
    assert "BackpackBlock" in classes


def test_backpack_add_and_list(tmp_path):
    from Kix.projects.backpack import Backpack

    bp = Backpack(base_dir=tmp_path / "backpack.json")
    assert bp.list() == []

    bp.add({"id": "b1", "name": "Mover 10", "category": "motion"}, origin="Projeto A")
    bp.add({"id": "b2", "name": "Esperar 1s", "category": "control"}, origin="Projeto A")

    items = bp.list()
    assert len(items) == 2
    assert items[0].block["id"] == "b1"
    assert items[1].origin == "Projeto A"


def test_backpack_remove(tmp_path):
    from Kix.projects.backpack import Backpack

    bp = Backpack(base_dir=tmp_path / "backpack.json")
    bp.add({"id": "b1", "name": "X", "category": "motion"}, origin="A")
    bp.add({"id": "b2", "name": "Y", "category": "motion"}, origin="A")
    assert len(bp.list()) == 2

    target = bp.list()[0]
    assert bp.remove(target.id)
    assert len(bp.list()) == 1
    assert not bp.remove("nonexistent")


def test_backpack_persistence(tmp_path):
    from Kix.projects.backpack import Backpack

    path = tmp_path / "backpack.json"
    bp1 = Backpack(base_dir=path)
    bp1.add({"id": "x", "name": "Hello", "category": "motion"}, origin="P1")

    bp2 = Backpack(base_dir=path)
    items = bp2.list()
    assert len(items) == 1
    assert items[0].block["name"] == "Hello"


def test_backpack_export_to_project(tmp_path):
    from Kix.projects.backpack import Backpack
    from Kix.projects.manager import ProjectManager

    mgr = ProjectManager(base_dir=tmp_path)
    mgr.create("Origem")

    bp = Backpack(base_dir=tmp_path / "backpack.json")
    bp.add({"id": "bloco_a", "name": "A", "category": "motion"}, origin="Origem")
    bp.add({"id": "bloco_b", "name": "B", "category": "motion"}, origin="Origem")

    mgr.create("Destino")
    added = bp.export_to_project("Destino", base_dir=tmp_path)
    assert added == 2

    proj = mgr.load("Destino")
    block_ids = {b["id"] for b in proj.blocks}
    assert "bloco_a" in block_ids
    assert "bloco_b" in block_ids


def test_backpack_export_renames_on_collision(tmp_path):
    """Se o projeto destino já tem um bloco com mesmo id, gera novo id."""
    from Kix.projects.backpack import Backpack
    from Kix.projects.manager import ProjectManager

    mgr = ProjectManager(base_dir=tmp_path)
    mgr.create("Destino")
    dest = mgr.load("Destino")
    dest.blocks.append({"id": "bloco_a", "name": "A", "category": "motion"})
    mgr.save(dest)

    bp = Backpack(base_dir=tmp_path / "backpack.json")
    bp.add({"id": "bloco_a", "name": "A2", "category": "motion"}, origin="Origem")

    added = bp.export_to_project("Destino", base_dir=tmp_path)
    assert added == 1

    proj = mgr.load("Destino")
    ids = [b["id"] for b in proj.blocks]
    # temos 2 entradas com mesmo id-base mas uma delas foi renomeada
    assert any(i.startswith("bloco_a_") for i in ids)


def test_backpack_import_from_project(tmp_path):
    from Kix.projects.backpack import Backpack
    from Kix.projects.manager import ProjectManager

    mgr = ProjectManager(base_dir=tmp_path)
    mgr.create("Origem")
    proj = mgr.load("Origem")
    proj.blocks.append({"id": "x", "name": "X", "category": "motion"})
    proj.blocks.append({"id": "y", "name": "Y", "category": "motion"})
    mgr.save(proj)

    bp = Backpack(base_dir=tmp_path / "backpack.json")
    added = bp.import_from_project("Origem", ["x", "y"], base_dir=tmp_path)
    assert added == 2
    assert len(bp.list()) == 2


def test_backpack_clear(tmp_path):
    from Kix.projects.backpack import Backpack

    bp = Backpack(base_dir=tmp_path / "backpack.json")
    bp.add({"id": "a", "name": "A", "category": "motion"}, origin="X")
    bp.add({"id": "b", "name": "B", "category": "motion"}, origin="X")
    assert len(bp.list()) == 2

    bp.clear()
    assert len(bp.list()) == 0


# --- Share link ------------------------------------------------------------

def test_share_module_imports():
    import ast
    from pathlib import Path
    p = Path("Kix/projects/share.py")
    assert p.exists()
    tree = ast.parse(p.read_text())
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "encode_share_payload" in funcs
    assert "decode_share_payload" in funcs
    assert "encode_share_url" in funcs
    assert "decode_share_url" in funcs


def test_share_payload_round_trip():
    from Kix.projects.share import decode_share_payload, encode_share_payload

    original = {
        "name": "Meu Jogo",
        "version": "1.2.3",
        "blocks": [{"id": "a", "name": "X", "category": "motion"}],
    }
    payload = encode_share_payload(original)
    assert isinstance(payload, str)
    assert len(payload) > 0
    decoded = decode_share_payload(payload)
    assert decoded == original


def test_share_payload_is_compact():
    """Payload usa zlib — tamanho razoável para um projeto grande."""
    from Kix.projects.share import encode_share_payload

    big = {"blocks": [{"id": f"b{i}", "name": f"Bloco {i}", "category": "motion"} for i in range(100)]}
    payload = encode_share_payload(big)
    # JSON cru seria ~5kb; comprimido deve ser menor
    raw_json = json.dumps(big)
    assert len(payload) < len(raw_json)


def test_share_url_format():
    from Kix.projects.share import SHARE_PREFIX, encode_share_url

    url = encode_share_url({"name": "X"})
    assert url.startswith(SHARE_PREFIX)


def test_share_url_round_trip():
    from Kix.projects.share import decode_share_url, encode_share_url

    project = {"name": "Jogo", "version": "1.0", "blocks": [{"id": "1", "name": "A", "category": "motion"}]}
    url = encode_share_url(project)
    decoded = decode_share_url(url)
    assert decoded == project


def test_share_url_with_query_string():
    """Aceita URL HTTP com ?p=<payload> (compatível com share.catrob.at)."""
    from Kix.projects.share import decode_share_payload, decode_share_url, encode_share_payload

    project = {"name": "Test"}
    payload = encode_share_payload(project)
    url = f"https://share.kixapp.local/?p={payload}"
    assert decode_share_url(url) == project


def test_share_link_includes_name():
    """share_link_for_project embute o nome no path."""
    from Kix.projects.share import SHARE_HOST, decode_share_url, share_link_for_project

    project = {"name": "Demo", "version": "1.0"}
    url = share_link_for_project("Demo", project)
    assert "Demo" in url
    assert SHARE_HOST in url
    decoded = decode_share_url(url)
    assert decoded == project


def test_is_shareable_url_detects_format():
    from Kix.projects.share import SHARE_PREFIX, is_shareable_url

    assert is_shareable_url("kix://share/foo/bar")
    assert is_shareable_url(f"https://share.kixapp.local/?p=abc")
    assert not is_shareable_url("https://example.com/foo")
    assert not is_shareable_url("http://malicious.example/")


def test_share_invalid_url_raises():
    import pytest
    from Kix.projects.share import decode_share_url

    with pytest.raises(ValueError):
        decode_share_url("not-a-share-url")


# --- Integração ProjectSettings.share_link -------------------------------

def test_new_project_with_share_link_marks_flag(tmp_path):
    from Kix.projects.manager import ProjectManager
    from Kix.projects.model import ProjectSettings

    mgr = ProjectManager(base_dir=tmp_path)
    settings = ProjectSettings(share_link=True, version="1.0.0")
    proj = mgr.create("Linkable", settings=settings)
    assert proj.settings.share_link is True

    # Ao reabrir, mantém a flag
    proj2 = mgr.load("Linkable")
    assert proj2.settings.share_link is True