"""Blocos de fórmula: operadores matemáticos e lógicos como blocos de 1ª classe.

Catroid tem um editor de fórmula onde expressões inline podem usar
operadores. Aqui, cada operador é um bloco reporter separado — mais
simples e combinável com a paleta existente. Listas e comparação de
strings também cobertos.
"""

from Kix.block_engine import (
    BlockInput,
    BlockVisual,
    Group,
    KixBlock,
    SocketDef,
    SocketKind,
    Text,
)
from Kix.block_engine.behavior import BlockBehavior
from Kix.core.theme import CAT_MATH, CAT_STRINGS


# ============================================================ Aritmética
ARITH_BLOCKS = []
for _id, _name, _glyph, _op in [
    ("math.op.add",       "somar",        "+",  "self.a + self.b"),
    ("math.op.sub",       "subtrair",     "−",  "self.a - self.b"),
    ("math.op.mul",       "multiplicar",  "×",  "self.a * self.b"),
    ("math.op.div",       "dividir",      "÷",  "self.a / self.b if self.b else 0"),
    ("math.op.pow",       "potência",     "^",  "self.a ** self.b"),
    ("math.op.mod",       "módulo",       "mod","self.a % self.b if self.b else 0"),
]:
    _b = KixBlock(
        id=_id,
        name=_name,
        category="math",
        color=CAT_MATH,
        visual=BlockVisual(root=Group(children=[
            BlockInput("a"), Text(f" {_glyph} "), BlockInput("b"),
        ])),
        inputs=[
            SocketDef("a", SocketKind.NUMBER, default=0),
            SocketDef("b", SocketKind.NUMBER, default=0),
        ],
        outputs=[SocketDef("result", SocketKind.NUMBER)],
        behavior=BlockBehavior(language="python", source=f"return {_op}"),
        permissions={"math"},
    )
    ARITH_BLOCKS.append(_b)

# ============================================================ Unários
def _neg(n: float) -> float:
    return -float(n)

NEG = KixBlock(
    id="math.op.neg", name="negativo", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("−"), BlockInput("n")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return -float(self.n)"),
    permissions={"math"},
)
ARITH_BLOCKS.append(NEG)

# ============================================================ Comparação
CMP_BLOCKS = []
for _id, _name, _glyph, _op in [
    ("math.cmp.eq",  "=",  "=",  "self.a == self.b"),
    ("math.cmp.ne",  "≠",  "≠",  "self.a != self.b"),
    ("math.cmp.lt",  "<",  "<",  "self.a <  self.b"),
    ("math.cmp.le",  "≤",  "≤",  "self.a <= self.b"),
    ("math.cmp.gt",  ">",  ">",  "self.a >  self.b"),
    ("math.cmp.ge",  "≥",  "≥",  "self.a >= self.b"),
]:
    _b = KixBlock(
        id=_id,
        name=_name,
        category="math",
        color=CAT_MATH,
        visual=BlockVisual(root=Group(children=[
            BlockInput("a"), Text(f" {_glyph} "), BlockInput("b"),
        ])),
        inputs=[
            SocketDef("a", SocketKind.NUMBER, default=0),
            SocketDef("b", SocketKind.NUMBER, default=0),
        ],
        outputs=[SocketDef("result", SocketKind.BOOLEAN)],
        behavior=BlockBehavior(language="python", source=f"return bool({_op})"),
        permissions={"math"},
    )
    CMP_BLOCKS.append(_b)

# ============================================================ Lógica
LOGIC_BLOCKS = []
for _id, _name, _glyph, _op in [
    ("logic.and", "e", "e",   "bool(self.a) and bool(self.b)"),
    ("logic.or",  "ou", "ou", "bool(self.a) or  bool(self.b)"),
]:
    _b = KixBlock(
        id=_id,
        name=_name,
        category="math",
        color=CAT_MATH,
        visual=BlockVisual(root=Group(children=[
            BlockInput("a"), Text(f" {_glyph} "), BlockInput("b"),
        ])),
        inputs=[
            SocketDef("a", SocketKind.BOOLEAN, default=False),
            SocketDef("b", SocketKind.BOOLEAN, default=False),
        ],
        outputs=[SocketDef("result", SocketKind.BOOLEAN)],
        behavior=BlockBehavior(language="python", source=f"return {_op}"),
        permissions={"math"},
    )
    LOGIC_BLOCKS.append(_b)

NOT = KixBlock(
    id="logic.not", name="não", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("não "), BlockInput("a")])),
    inputs=[SocketDef("a", SocketKind.BOOLEAN, default=False)],
    outputs=[SocketDef("result", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return not bool(self.a)"),
    permissions={"math"},
)
LOGIC_BLOCKS.append(NOT)

# ============================================================ Strings
STR_OPS = []
for _id, _name, _glyph, _op in [
    ("str.eq", "string =",  "=",  "str(self.a) == str(self.b)"),
    ("str.ne", "string ≠",  "≠",  "str(self.a) != str(self.b)"),
    ("str.lt", "string <",  "<",  "str(self.a) <  str(self.b)"),
    ("str.gt", "string >",  ">",  "str(self.a) >  str(self.b)"),
    # str.contains já existe em Kix.blocks.strings — não duplicar.
]:
    _b = KixBlock(
        id=_id, name=_name, category="strings", color=CAT_STRINGS,
        visual=BlockVisual(root=Group(children=[
            BlockInput("a"), Text(f" {_glyph} "), BlockInput("b"),
        ])),
        inputs=[
            SocketDef("a", SocketKind.STRING, default=""),
            SocketDef("b", SocketKind.STRING, default=""),
        ],
        outputs=[SocketDef("result", SocketKind.BOOLEAN)],
        behavior=BlockBehavior(language="python", source=f"return {_op}"),
        permissions={"strings"},
    )
    STR_OPS.append(_b)

FORMULA_BLOCKS = tuple(ARITH_BLOCKS + CMP_BLOCKS + LOGIC_BLOCKS + STR_OPS)
