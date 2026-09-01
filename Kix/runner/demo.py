"""Projeto demo embutido no runner.

`demo_project()` devolve um `KixProject` que demonstra os blocos
essenciais: mover, esperar, girar, mudar cor de fundo. Útil para:

- `python3 -m Kix.cli demo` — roda e imprime o estado final.
- `python3 -m Kix.cli make-demo foo.kix` — salva o projeto demo.
- Testes de fumaça do executor.
"""

from __future__ import annotations

import json
from pathlib import Path

from Kix.blocks.builtin import MOVE, WAIT, COMPUTE
from Kix.blocks.formula import ARITH_BLOCKS
from Kix.projects.model import KixProject, KixScene, KixObject, KixScript
from Kix.projects.serializer import from_json, to_json


def _find(blocks, id_):
    for b in blocks:
        if b.id == id_:
            return b
    raise KeyError(id_)


def _with_inputs(block, **inputs):
    """Constrói um dict do bloco com `inputs` materializados (default + override).

    O executor aceita `inputs={}` e usa os defaults de SocketDef. Aqui
    também gravamos o override nos campos do bloco serializado, então o
    JSON reflete o que vai rodar.
    """
    data = block.to_dict()
    for inp in data.get("inputs", []):
        if inp["name"] in inputs:
            inp["default"] = inputs[inp["name"]]
    return data


def demo_project() -> KixProject:
    """Mover 50px, esperar 1s, girar 45°, mover mais 30px."""
    obj = KixObject(name="Ator")
    obj.kind = "sprite"
    scr = KixScript(trigger="on_start")
    scr.blocks = ["demo.move1", "demo.wait", "demo.rotate", "demo.move2"]
    obj.scripts = [scr.id]

    scene = KixScene(name="Demo", background="#10B981")
    scene.objects = [obj.id]

    return KixProject(
        name="Demo Mover",
        description="Demo headless: mover + esperar + girar",
        scenes=[scene],
        objects=[obj],
        scripts=[scr],
        blocks=[
            _with_inputs(MOVE, steps=50),
            _with_inputs(WAIT, seconds=0.0),  # zero em teste = sem sleep
            _with_inputs(_find(ARITH_BLOCKS, "math.op.add"), a=10, b=35),  # vira reporter → 45
            _with_inputs(MOVE, steps=30),
        ],
    )


def write_demo(path: Path) -> Path:
    """Grava o projeto demo em `path`."""
    text = to_json(demo_project())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def load_demo_json() -> str:
    """Retorna a string JSON do projeto demo (sem gravar)."""
    return to_json(demo_project())


__all__ = ["demo_project", "write_demo", "load_demo_json"]
