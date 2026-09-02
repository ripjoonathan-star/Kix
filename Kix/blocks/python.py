"""Blocos da categoria "Python Puro" (spec seção 3.3).

Diferente das outras categorias, estes blocos não têm comportamento
pré-definido em ``BlockBehavior`` — o usuário escreve o código Python
literal que será executado dentro do motor do jogo. O sandboxing
(namespace restrito, lista de variáveis expostas) é responsabilidade
do runtime; este módulo apenas registra os blocos.

Blocos:
- ``python.exec``  — comando (sem retorno) — roda statements no loop de update
- ``python.eval``  — reporter (retorna valor) — avalia expressão de 1 linha

Cores conforme spec seção 3.3:
- ``CAT_PYTHON``     #3776AB — tom base para ``python.exec``
- ``CAT_PYTHON_LIGHT`` #6FA8D8 — tom claro para ``python.eval`` (reporter)
"""

from __future__ import annotations

from Kix.block_engine import (
    BlockVisual,
    Group,
    KixBlock,
    SocketDef,
    SocketKind,
    Text,
)
from Kix.block_engine.behavior import BlockBehavior
from Kix.core.theme import CAT_PYTHON, CAT_PYTHON_LIGHT


EXEC_PYTHON = KixBlock(
    id="python.exec",
    name="Executar código Python",
    category="python",
    color=CAT_PYTHON,
    visual=BlockVisual(root=Group(
        label=None,
        children=[Text("Executar código Python")],
    )),
    # O input multilinha é renderizado pelo editor especial
    # (Kix/ui/code_editor.py) — o SocketKind.STRING guarda o código
    # completo como string única com \n. O editor com numeração de
    # linha + monospace é responsabilidade do popup, não do bloco.
    inputs=[SocketDef("code", SocketKind.STRING, default="")],
    outputs=[],
    # Sem BlockBehavior — o runtime interpreta ``code`` em sandbox.
    behavior=None,
    permissions={"stage"},
)


EVAL_PYTHON = KixBlock(
    id="python.eval",
    name="Avaliar expressão Python",
    category="python",
    color=CAT_PYTHON_LIGHT,
    visual=BlockVisual(root=Group(
        label=None,
        children=[Text("Avaliar expressão Python")],
    )),
    inputs=[SocketDef("expr", SocketKind.STRING, default="")],
    # Reporter — encaixável em outros blocos como o campo de fórmula.
    outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=None,
    permissions={"stage"},
)


PYTHON_BLOCKS = (EXEC_PYTHON, EVAL_PYTHON)
