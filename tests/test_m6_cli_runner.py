"""Testes para o CLI runner + PNG renderer (M6)."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from Kix.engine.ctx import make_ctx
from Kix.runner import (
    ProjectRunResult,
    run_project,
    run_project_dict,
    run_project_path,
)
from Kix.runner.demo import demo_project, write_demo, load_demo_json
from Kix.render import render_ctx_to_png, render_sprite_to_image
from PIL import Image


# --- Renderer --------------------------------------------------------------
def test_render_sprite_to_image_returns_rgba():
    ctx = make_ctx()
    sprite = ctx.stage.active
    sprite.position = (50, 30)
    img = render_sprite_to_image(sprite, width=200, height=200, background="#FF00FF")
    assert isinstance(img, Image.Image)
    assert img.mode == "RGBA"
    assert img.size == (200, 200)
    # O canto superior-esquerdo deve ser o background
    assert img.getpixel((2, 2))[:3] == (255, 0, 255)


def test_render_ctx_to_png_writes_file(tmp_path):
    ctx = make_ctx()
    out = tmp_path / "palco.png"
    p = render_ctx_to_png(ctx, out)
    assert p == out
    assert p.exists()
    assert p.stat().st_size > 0
    im = Image.open(p)
    assert im.size == (390, 844)


def test_render_with_sprite_moved(tmp_path):
    ctx = make_ctx()
    ctx.stage.active.position = (100, 50)
    out = tmp_path / "moved.png"
    render_ctx_to_png(ctx, out)
    assert out.exists()


def test_render_invisible_sprite_draws_x(tmp_path):
    ctx = make_ctx()
    ctx.stage.active.visible = False
    out = tmp_path / "hidden.png"
    render_ctx_to_png(ctx, out)
    assert out.exists()


def test_render_accepts_rgb_tuple_background():
    """Background como tupla RGBA deve funcionar via parser de hex."""
    from Kix.render.png import _parse_hex_color
    assert _parse_hex_color("#10B981") == (16, 185, 129)
    assert _parse_hex_color("#FF10B981") == (16, 185, 129)
    assert _parse_hex_color("invalid") == (255, 255, 255)


# --- Runner ----------------------------------------------------------------
def test_runner_runs_demo_project():
    """Roda o projeto demo e verifica que o sprite se moveu."""
    project = demo_project()
    result = asyncio.run(run_project(project))
    assert isinstance(result, ProjectRunResult)
    assert result.project_name == "Demo Mover"
    assert result.blocks_failed == 0, f"Erros: {result.errors}"
    assert result.blocks_run == 4
    # 2x MOVE (50 + 30 = 80px)
    assert result.sprite is not None
    assert result.sprite.position[0] == pytest.approx(80.0, abs=1e-6)
    assert result.sprite.position[1] == pytest.approx(0.0, abs=1e-6)


def test_runner_dict_path():
    """run_project_dict aceita um dict já desserializado."""
    text = load_demo_json()
    data = json.loads(text)
    result = run_project_dict(data)
    assert result.blocks_run == 4
    assert result.sprite.position[0] == pytest.approx(80.0)


def test_runner_file_path(tmp_path):
    """run_project_path lê .kix e roda."""
    p = write_demo(tmp_path / "demo.kix")
    result = run_project_path(p)
    assert result.blocks_run == 4


def test_runner_handles_invalid_block_gracefully(tmp_path):
    """Bloco com ID desconhecido vira falha contada, não exceção."""
    project = demo_project()
    # injeta um bloco malformado
    project.blocks.append({"id": "does.not.exist", "category": "x",
                            "name": "?", "color": [], "inputs": [], "outputs": []})
    result = asyncio.run(run_project(project))
    assert result.blocks_failed >= 1
    assert any("does.not.exist" in e for e in result.errors)


def test_runner_applies_persisted_state(tmp_path):
    """Se o projeto tem state persistido, ele é restaurado antes de rodar."""
    project = demo_project()
    project.state = {"position": [123.0, 45.0], "rotation": 90.0, "opacity": 0.5}
    result = asyncio.run(run_project(project))
    sprite = result.sprite
    # A restauração aplica ANTES dos blocos; depois os blocos movem +80 a partir de (123,45).
    assert sprite.position[0] == pytest.approx(123.0 + 80.0)
    assert sprite.position[1] == pytest.approx(45.0)
    assert sprite.rotation == pytest.approx(90.0)


def test_runner_summary_contains_sprite_state():
    project = demo_project()
    result = asyncio.run(run_project(project))
    s = result.summary()
    assert "Demo Mover" in s
    assert "Sprite1" in s
    assert "posição" in s
    assert "80" in s


# --- CLI (subprocess) -----------------------------------------------------
def test_cli_version():
    import subprocess
    out = subprocess.run(
        [sys.executable, "-m", "Kix.cli", "--version"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert out.returncode == 0
    assert "0.1.0" in out.stdout


def test_cli_list_blocks():
    import subprocess
    out = subprocess.run(
        [sys.executable, "-m", "Kix.cli", "list-blocks"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert out.returncode == 0
    assert "core.move" in out.stdout
    assert "math.op.add" in out.stdout


def test_cli_demo_runs_and_reports():
    import subprocess
    out = subprocess.run(
        [sys.executable, "-m", "Kix.cli", "demo", "--quiet"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert out.returncode == 0, out.stderr


def test_cli_demo_writes_png(tmp_path):
    import subprocess
    target = tmp_path / "demo.png"
    out = subprocess.run(
        [sys.executable, "-m", "Kix.cli", "demo", "--png", str(target), "--quiet"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert out.returncode == 0, out.stderr
    assert target.exists()
    assert target.stat().st_size > 100


def test_cli_make_demo_then_run(tmp_path):
    """Fluxo completo: make-demo → run + PNG."""
    import subprocess
    kix = tmp_path / "demo.kix"
    png = tmp_path / "out.png"

    # 1. make-demo
    r1 = subprocess.run(
        [sys.executable, "-m", "Kix.cli", "make-demo", str(kix), "--quiet"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r1.returncode == 0, r1.stderr
    assert kix.exists()

    # 2. run com PNG
    r2 = subprocess.run(
        [sys.executable, "-m", "Kix.cli", "run", str(kix), "--png", str(png), "--quiet"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r2.returncode == 0, r2.stderr
    assert png.exists()

    # 3. JSON também
    js = tmp_path / "out.json"
    r3 = subprocess.run(
        [sys.executable, "-m", "Kix.cli", "run", str(kix), "--json", str(js), "--quiet"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r3.returncode == 0, r3.stderr
    data = json.loads(js.read_text())
    assert data["blocks_run"] == 4
    assert data["sprite"]["position"][0] == pytest.approx(80.0)


def test_cli_run_missing_file():
    import subprocess
    out = subprocess.run(
        [sys.executable, "-m", "Kix.cli", "run", "/tmp/does-not-exist-12345.kix"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert out.returncode == 2
    assert "não encontrado" in out.stderr
