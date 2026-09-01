"""Smoke tests para a integração UI (M4).

Cobre o fluxo:
    Dashboard cria projeto
    → EditorScreen recebe project.blocks (lista de dicts)
    → PalcoTab.run() executa blocos via BlockExecutor
    → sprite ativo muda de posição

Os widgets Kivy (Dashboard/Editor/Palco) não são instanciados aqui —
estes testes exercitam o pipeline de dados sem precisar de display.
"""

from __future__ import annotations

import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from Kix.block_engine import KixBlock
from Kix.blocks.builtin import MOVE, WAIT, SAY
from Kix.engine.ctx import make_ctx
from Kix.engine.executor import BlockExecutor
from Kix.projects.manager import ProjectManager
from Kix.projects.model import KixProject
from Kix.projects.serializer import from_json, to_json


# ---------- Dashboard → ProjectManager ------------------------------------
def test_project_manager_creates_and_lists(tmp_path: Path):
    """Criar projeto no disco e listar de volta (simula Dashboard)."""
    mgr = ProjectManager(base_dir=tmp_path)
    p1 = mgr.create("Aventura")
    p2 = mgr.create("Pong")
    assert mgr.exists("Aventura")
    assert mgr.exists("Pong")

    infos = mgr.list()
    names = {i.name for i in infos}
    assert names == {"Aventura", "Pong"}


def test_project_manager_duplicate_name_raises(tmp_path: Path):
    mgr = ProjectManager(base_dir=tmp_path)
    mgr.create("Duplicado")
    with pytest.raises(FileExistsError):
        mgr.create("Duplicado")


# ---------- EditorScreen → project.blocks ---------------------------------
def test_project_carries_blocks_round_trip(tmp_path: Path):
    """Editor adiciona blocos → projeto serializa → carrega de volta com blocos."""
    mgr = ProjectManager(base_dir=tmp_path)
    project = mgr.create("Demo")

    # Simula o ProgramacaoTab._add_block
    project.blocks.append(MOVE.to_dict())
    project.blocks.append(WAIT.to_dict())
    project.blocks.append(MOVE.to_dict())
    mgr.save(project)

    # Recarrega como o EditorScreen.load_project faria
    loaded = mgr.load("Demo")
    assert len(loaded.blocks) == 3
    assert all(isinstance(b, dict) for b in loaded.blocks)
    # E cada bloco pode ser reidratado
    for bdata in loaded.blocks:
        block = KixBlock.from_dict(bdata)
        assert block.id in {"core.move", "core.wait"}


# ---------- PalcoTab → BlockExecutor -------------------------------------
async def test_palco_run_executes_blocks_and_moves_sprite(tmp_path: Path):
    """O equivalente puro-Python do que PalcoTab._run faz."""
    mgr = ProjectManager(base_dir=tmp_path)
    project = mgr.create("Move Demo")
    project.blocks.append(MOVE.to_dict())      # steps default = 10
    project.blocks.append(WAIT.to_dict())      # 1s default — vamos usar asyncio.wait_for
    mgr.save(project)

    loaded = mgr.load("Move Demo")
    ctx = make_ctx()
    stage = ctx.stage
    sprite = stage.active
    start_x = sprite.position[0]

    executor = BlockExecutor()
    for bdata in loaded.blocks:
        block = KixBlock.from_dict(bdata)
        inputs = {s.name: s.default for s in block.inputs}
        # WAIT usa asyncio.sleep — não queremos esperar 1s no teste.
        if block.id == "core.wait":
            inputs["seconds"] = 0
        await executor.run_block(block, ctx, inputs)

    # após 1× MOVE(steps=10), x deve ter crescido 10
    assert sprite.position[0] == start_x + 10, (
        f"esperado x={start_x + 10}, obtido x={sprite.position[0]}"
    )


async def test_palco_run_with_no_blocks_is_noop(tmp_path: Path):
    """Projeto sem blocos não deve levantar (early return em PalcoTab.run)."""
    mgr = ProjectManager(base_dir=tmp_path)
    project = mgr.create("Vazio")
    mgr.save(project)

    loaded = mgr.load("Vazio")
    assert not loaded.blocks
    # PalcoTab.run() retornaria imediatamente; aqui só garantimos que a
    # pipeline "blocks=[] → executor não é chamado" não falha.


async def test_executor_handles_move_block_with_custom_steps(tmp_path: Path):
    """Mover com steps customizado funciona end-to-end."""
    mgr = ProjectManager(base_dir=tmp_path)
    project = mgr.create("Custom")
    project.blocks.append(MOVE.to_dict())
    project.blocks.append(MOVE.to_dict())
    mgr.save(project)

    loaded = mgr.load("Custom")
    ctx = make_ctx()
    sprite = ctx.stage.active
    sprite.position = (0, 0)

    executor = BlockExecutor()
    for bdata in loaded.blocks:
        block = KixBlock.from_dict(bdata)
        inputs = {s.name: s.default for s in block.inputs}
        inputs["steps"] = 25
        await executor.run_block(block, ctx, inputs)

    assert sprite.position == (50, 0)


# ---------- ProjectInfo está pronto para o Dashboard ----------------------
def test_project_info_has_required_fields(tmp_path: Path):
    mgr = ProjectManager(base_dir=tmp_path)
    mgr.create("Info Test")
    infos = mgr.list()
    assert len(infos) == 1
    info = infos[0]
    assert info.name == "Info Test"
    assert info.path.exists()
    assert info.modified_at  # ISO string
    assert info.size_bytes > 0
