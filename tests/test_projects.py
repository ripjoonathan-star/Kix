"""Testes do sistema de projetos Kix: modelo + serializer + manager (.kix)."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from Kix.projects import (
    KIX_FORMAT,
    KIX_VERSION,
    KixFormatError,
    KixObject,
    KixProject,
    KixScene,
    KixScript,
    ProjectInfo,
    ProjectManager,
    ProjectSettings,
    from_dict,
    from_json,
    to_dict,
    to_json,
)


# ---------- fixtures -------------------------------------------------------
@pytest.fixture
def tmp_manager(tmp_path) -> ProjectManager:
    return ProjectManager(base_dir=tmp_path / "projects")


def _sample_project(name: str = "Meu Jogo") -> KixProject:
    """Projeto mínimo com 1 scene, 1 object, 1 script, 1 block custom."""
    from Kix.blocks.builtin import MOVE

    p = KixProject(name=name, description="Jogo de teste")
    p.scenes.append(KixScene(id="scn_a", name="Stage", background="#101010",
                              objects=["obj_a"]))
    p.objects.append(KixObject(id="obj_a", name="Player", kind="sprite",
                                image="assets/player.png", scripts=["scr_a"]))
    p.scripts.append(KixScript(id="scr_a", trigger="on_start", blocks=["blk_1"]))
    p.blocks.append(MOVE.to_dict())
    return p


# ---------- Serializer -----------------------------------------------------
def test_format_constants():
    assert KIX_FORMAT == "kix"
    assert KIX_VERSION == 1


def test_to_json_round_trip():
    p = _sample_project()
    text = to_json(p)
    assert isinstance(text, str)
    back = from_json(text)
    assert back.name == p.name
    assert back.description == p.description
    assert len(back.scenes) == 1 and back.scenes[0].name == "Stage"
    assert len(back.objects) == 1 and back.objects[0].name == "Player"
    assert len(back.scripts) == 1 and back.scripts[0].trigger == "on_start"
    assert len(back.blocks) == 1 and back.blocks[0]["id"] == "core.move"
    assert back.settings.orientation == "portrait"


def test_to_dict_has_required_keys():
    data = to_dict(_sample_project())
    for key in ("format", "version", "name", "created_at", "modified_at",
                "scenes", "objects", "scripts", "blocks", "settings"):
        assert key in data
    assert data["format"] == KIX_FORMAT
    assert data["version"] == KIX_VERSION


def test_invalid_format_raises():
    bad = json.dumps({"format": "other", "version": 1, "name": "x"})
    with pytest.raises(KixFormatError, match="format"):
        from_json(bad)


def test_invalid_version_raises():
    bad = json.dumps({"format": "kix", "version": 999, "name": "x"})
    with pytest.raises(KixFormatError, match="Versão"):
        from_json(bad)


def test_malformed_json_raises():
    with pytest.raises(KixFormatError, match="JSON inválido"):
        from_json("{not json")


def test_non_object_json_raises():
    with pytest.raises(KixFormatError):
        from_json("[1,2,3]")


def test_from_dict_generates_ids_when_missing():
    """Se um dict de scene/object/script vier sem id, geramos um."""
    data = {
        "format": "kix",
        "version": 1,
        "name": "x",
        "scenes": [{"name": "S"}],
        "objects": [{"name": "O"}],
        "scripts": [{"trigger": "on_start"}],
        "blocks": [],
    }
    p = from_dict(data)
    assert p.scenes[0].id.startswith("scn_")
    assert p.objects[0].id.startswith("obj_")
    assert p.scripts[0].id.startswith("scr_")


# ---------- Settings -------------------------------------------------------
def test_settings_round_trip():
    s = ProjectSettings(width=1920, height=1080, orientation="landscape")
    p = KixProject(name="x", settings=s)
    back = from_json(to_json(p))
    assert back.settings.width == 1920
    assert back.settings.height == 1080
    assert back.settings.orientation == "landscape"


# ---------- Manager: CRUD --------------------------------------------------
def test_create_save_load(tmp_manager):
    p = _sample_project("alpha")
    path = tmp_manager.save(p)
    assert path.exists()
    assert path.suffix == ".kix"

    loaded = tmp_manager.load("alpha")
    assert loaded.name == "alpha"
    assert loaded.scenes[0].name == "Stage"


def test_create_with_template(tmp_manager):
    p = _sample_project("template")
    new = tmp_manager.create("derived", template=p)
    assert new.name == "derived"
    loaded = tmp_manager.load("derived")
    assert loaded.description == p.description
    assert loaded.scenes[0].name == "Stage"


def test_create_without_template_creates_empty(tmp_manager):
    p = tmp_manager.create("empty")
    assert p.name == "empty"
    assert p.scenes == []
    assert p.objects == []
    assert p.scripts == []


def test_create_duplicate_raises(tmp_manager):
    tmp_manager.create("dupe")
    with pytest.raises(FileExistsError):
        tmp_manager.create("dupe")


def test_list_empty(tmp_manager):
    assert tmp_manager.list() == []


def test_list_returns_project_info(tmp_manager):
    tmp_manager.create("alpha")
    tmp_manager.create("beta")
    items = tmp_manager.list()
    names = {i.name for i in items}
    assert names == {"alpha", "beta"}
    assert all(isinstance(i, ProjectInfo) for i in items)
    assert all(i.size_bytes > 0 for i in items)


def test_exists(tmp_manager):
    assert not tmp_manager.exists("nope")
    tmp_manager.create("yes")
    assert tmp_manager.exists("yes")


def test_load_missing_raises(tmp_manager):
    with pytest.raises(FileNotFoundError):
        tmp_manager.load("missing")


def test_load_path_external(tmp_path, tmp_manager):
    """load_path deve aceitar qualquer .kix (mesmo fora do diretório gerenciado)."""
    external = tmp_path / "external.kix"
    external.write_text(to_json(_sample_project("ext")), encoding="utf-8")
    p = tmp_manager.load_path(external)
    assert p.name == "ext"


# ---------- Rename / Duplicate / Delete ------------------------------------
def test_rename(tmp_manager):
    tmp_manager.create("old")
    tmp_manager.rename("old", "new")
    assert not tmp_manager.exists("old")
    assert tmp_manager.exists("new")


def test_rename_to_existing_raises(tmp_manager):
    tmp_manager.create("a")
    tmp_manager.create("b")
    with pytest.raises(FileExistsError):
        tmp_manager.rename("a", "b")


def test_rename_missing_raises(tmp_manager):
    with pytest.raises(FileNotFoundError):
        tmp_manager.rename("nope", "new")


def test_duplicate_regenerates_ids(tmp_manager):
    """Após duplicar, IDs de scene/object/script devem ser NOVOS mas
    as referências internas entre eles devem continuar consistentes."""
    tmp_manager.create("orig", template=_sample_project("orig"))
    dup = tmp_manager.duplicate("orig", "copy")

    orig = tmp_manager.load("orig")
    # IDs diferentes
    assert orig.scenes[0].id != dup.scenes[0].id
    assert orig.objects[0].id != dup.objects[0].id
    assert orig.scripts[0].id != dup.scripts[0].id
    # referências internas intactas
    assert dup.scenes[0].objects[0] == dup.objects[0].id
    assert dup.objects[0].scripts[0] == dup.scripts[0].id


def test_delete(tmp_manager):
    tmp_manager.create("victim")
    tmp_manager.delete("victim")
    assert not tmp_manager.exists("victim")


def test_delete_missing_raises(tmp_manager):
    with pytest.raises(FileNotFoundError):
        tmp_manager.delete("nope")


# ---------- Import / Export ------------------------------------------------
def test_export(tmp_path, tmp_manager):
    tmp_manager.create("src")
    exported = tmp_manager.export("src", tmp_path / "out.kix")
    assert exported.exists()
    assert exported.read_text(encoding="utf-8") == (tmp_manager.base_dir / "src.kix").read_text(encoding="utf-8")


def test_export_creates_parent_dirs(tmp_path, tmp_manager):
    tmp_manager.create("src")
    nested = tmp_path / "deep" / "nested" / "out.kix"
    exported = tmp_manager.export("src", nested)
    assert exported.exists()


def test_export_missing_raises(tmp_manager, tmp_path):
    with pytest.raises(FileNotFoundError):
        tmp_manager.export("nope", tmp_path / "x.kix")


def test_import_project(tmp_path, tmp_manager):
    external = tmp_path / "outside.kix"
    external.write_text(to_json(_sample_project("imported")), encoding="utf-8")
    p = tmp_manager.import_project(external)
    assert p.name == "imported"
    assert tmp_manager.exists("imported")


def test_import_with_rename(tmp_path, tmp_manager):
    external = tmp_path / "outside.kix"
    external.write_text(to_json(_sample_project("orig")), encoding="utf-8")
    p = tmp_manager.import_project(external, new_name="renamed")
    assert p.name == "renamed"
    assert tmp_manager.exists("renamed")
    assert not tmp_manager.exists("orig")


def test_import_collision_raises(tmp_path, tmp_manager):
    external = tmp_path / "outside.kix"
    external.write_text(to_json(_sample_project("dup")), encoding="utf-8")
    tmp_manager.create("dup")
    with pytest.raises(FileExistsError):
        tmp_manager.import_project(external)


def test_import_missing_file_raises(tmp_path, tmp_manager):
    with pytest.raises(FileNotFoundError):
        tmp_manager.import_project(tmp_path / "nope.kix")


def test_import_invalid_format_raises(tmp_path, tmp_manager):
    bad = tmp_path / "bad.kix"
    bad.write_text('{"format":"x","version":1}', encoding="utf-8")
    with pytest.raises(KixFormatError):
        tmp_manager.import_project(bad)


# ---------- Round-trip end-to-end -----------------------------------------
def test_full_round_trip_via_disk(tmp_manager):
    """Projeto escrito em disco deve poder ser lido de volta idêntico."""
    p = _sample_project("full")
    p.settings.width = 1920
    p.settings.height = 1080
    p.settings.orientation = "landscape"
    tmp_manager.save(p)

    loaded = tmp_manager.load("full")
    assert loaded.name == "full"
    assert loaded.settings.width == 1920
    assert loaded.settings.height == 1080
    assert loaded.settings.orientation == "landscape"
    assert len(loaded.scenes) == 1
    assert loaded.scenes[0].background == "#101010"
    assert loaded.objects[0].image == "assets/player.png"


def test_export_then_import_round_trip(tmp_path, tmp_manager):
    """Exporta um projeto, depois importa de volta — deve sobreviver ao ciclo."""
    p = _sample_project("cycle")
    tmp_manager.save(p)

    # exporta
    dest = tmp_path / "exported.kix"
    tmp_manager.export("cycle", dest)
    # remove do gerenciado
    tmp_manager.delete("cycle")

    # importa de volta
    imported = tmp_manager.import_project(dest)
    assert imported.name == "cycle"
    assert imported.scenes[0].name == "Stage"
    assert imported.objects[0].name == "Player"