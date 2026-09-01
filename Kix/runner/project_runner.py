"""Execução headless de um KixProject.

`run_project(path)`:
1. Lê o JSON e instancia o `KixProject`.
2. Constrói um `RuntimeContext` com tamanho vindo de `project.settings`.
3. Aplica o estado persistido (`project.state`) no sprite ativo.
4. Para cada bloco declarado em `project.blocks`, executa-o sequencialmente
   na ordem em que aparecem no JSON. Blocos com `body` (controle) já rodam
   o body via `_SelfBinding.run(body)` no executor M5.
5. Captura exceções por bloco (não derruba o run inteiro).
6. Retorna `ProjectRunResult` com contagens + sprite final + log.

Limitações:
- Não dispara triggers (`on_tap`, `on_message`, ...); roda tudo sequencial.
- Variáveis/lists são mantidas em memória, não persistidas entre runs.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from Kix.block_engine.block import KixBlock
from Kix.engine.ctx import RuntimeContext, SpriteProxy, make_ctx
from Kix.engine.executor import BlockExecutor
from Kix.projects.model import KixProject


# --- Resultado -------------------------------------------------------------
@dataclass
class ProjectRunResult:
    """Saída de `run_project` — observável + resumo."""

    project_name: str
    sprite: SpriteProxy | None
    variables: dict[str, Any]
    blocks_run: int = 0
    blocks_failed: int = 0
    errors: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Projeto: {self.project_name}",
            f"Sprite:  {self.sprite.name if self.sprite else '(nenhum)'}",
        ]
        if self.sprite:
            x, y = self.sprite.position
            lines.append(
                f"  posição=({x:.1f}, {y:.1f})  rotação={self.sprite.rotation:.1f}°  "
                f"escala={self.sprite.scale:.2f}  opacidade={self.sprite.opacity:.2f}"
            )
        lines.append(f"Blocos:  {self.blocks_run} ok, {self.blocks_failed} falharam")
        if self.variables:
            lines.append("Variáveis:")
            for k, v in self.variables.items():
                lines.append(f"  {k} = {v!r}")
        if self.log:
            lines.append("Log:")
            for line in self.log:
                lines.append(f"  {line}")
        if self.errors:
            lines.append("Erros:")
            for err in self.errors:
                lines.append(f"  {err}")
        return "\n".join(lines)


# --- Runner ----------------------------------------------------------------
async def _execute_blocks(
    blocks: list[dict[str, Any]],
    ctx: RuntimeContext,
    executor: BlockExecutor,
    result: ProjectRunResult,
) -> None:
    for raw in blocks:
        try:
            block = KixBlock.from_dict(raw)
        except Exception as exc:  # pragma: no cover - erro de parsing é raro
            result.blocks_failed += 1
            result.errors.append(f"bloco {raw.get('id', '?')}: parse falhou: {exc}")
            continue

        if block.behavior is None:
            # Bloco sem comportamento (ex.: SAY sem efeito visível): conta como ok silencioso
            result.blocks_run += 1
            continue

        # Preenche inputs com defaults declarados nos SocketDef do bloco.
        inputs: dict[str, Any] = {
            inp.name: inp.default for inp in block.inputs
        }

        try:
            await executor.run_block(block, ctx, inputs=inputs)
            result.blocks_run += 1
        except Exception as exc:
            result.blocks_failed += 1
            result.errors.append(f"bloco {block.id}: {type(exc).__name__}: {exc}")


def _apply_state(sprite: SpriteProxy, state: dict[str, Any]) -> None:
    """Restaura estado persistido de um sprite."""
    if "position" in state and isinstance(state["position"], (list, tuple)):
        sprite.position = (float(state["position"][0]), float(state["position"][1]))
    if "rotation" in state:
        sprite.rotation = float(state["rotation"])
    if "scale" in state:
        sprite.scale = float(state["scale"])
    if "opacity" in state:
        sprite.opacity = float(state["opacity"])
    if "tint" in state and isinstance(state["tint"], (list, tuple)):
        sprite.tint = tuple(float(x) for x in state["tint"])  # type: ignore[assignment]


def _apply_scene_bg(project: KixProject, ctx: RuntimeContext) -> None:
    """Aplica o background da primeira cena no stage (se a cena tiver cor hex)."""
    if not project.scenes:
        return
    scene = project.scenes[0]
    bg = scene.background
    if not isinstance(bg, str) or not bg.startswith("#"):
        return
    s = bg.lstrip("#")
    if len(s) != 6:
        return
    try:
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
    except ValueError:
        return
    ctx.stage.background = (r, g, b, 1.0)


def _project_to_blocks(project: KixProject) -> list[dict[str, Any]]:
    """Extrai a sequência de blocos top-level do projeto.

    O `KixProject.blocks` é uma lista plana de dicts (KixBlock serializados).
    A ordem no array = ordem de execução para o runner headless.
    """
    return [b if isinstance(b, dict) else b.to_dict() for b in project.blocks]


async def run_project(project: KixProject) -> ProjectRunResult:
    """Roda um KixProject em memória e devolve o estado final."""
    settings = project.settings
    ctx = make_ctx(screen_width=settings.width, screen_height=settings.height)
    _apply_scene_bg(project, ctx)

    # Restaura estado persistido no sprite ativo
    sprite = ctx.stage.active
    if sprite and project.state:
        _apply_state(sprite, project.state)

    result = ProjectRunResult(
        project_name=project.name,
        sprite=sprite,
        variables=dict(ctx.variables),
    )

    executor = BlockExecutor()
    await _execute_blocks(_project_to_blocks(project), ctx, executor, result)
    result.variables = dict(ctx.variables)
    return result


def run_project_dict(data: dict[str, Any]) -> ProjectRunResult:
    """Conveniência síncrona em torno de `run_project`."""
    return asyncio.run(run_project(KixProject.from_dict(data)))


def run_project_path(path: str | Path) -> ProjectRunResult:
    """Lê um arquivo .kix e roda headless."""
    text = Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    return run_project_dict(data)


__all__ = ["ProjectRunResult", "run_project", "run_project_dict", "run_project_path"]
