"""Blocos matemáticos: sqrt, trig, arredondamento, min/max, random."""

import math as _math

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
from Kix.core.theme import CAT_MATH
from Kix.engine.decorator import kix_block


# --- M3.3: blocos Catroid faltando via decorator --------------------------
def _math_ln(n: float) -> float:
    return _math.log(n)


def _math_log10(n: float) -> float:
    return _math.log10(n)


def _math_pi() -> float:
    return _math.pi


def _math_atan(n: float) -> float:
    return _math.degrees(_math.atan(n))


def _math_mod(a: float, b: float) -> float:
    return a % b


def _math_round_to(n: float, decimals: int = 0) -> float:
    return round(n, decimals)


MATH_LN = kix_block(
    id="math.ln", category="math", color=CAT_MATH,
    name="ln", visual_style="math", permissions={"math"},
)(_math_ln)

MATH_LOG10 = kix_block(
    id="math.log10", category="math", color=CAT_MATH,
    name="log10", visual_style="math", permissions={"math"},
)(_math_log10)

MATH_PI = kix_block(
    id="math.pi", category="math", color=CAT_MATH,
    name="π", visual_style="raw", permissions={"math"},
)(_math_pi)

MATH_ATAN = kix_block(
    id="math.atan", category="math", color=CAT_MATH,
    name="atan", visual_style="math", permissions={"math"},
)(_math_atan)

MATH_MOD = kix_block(
    id="math.mod", category="math", color=CAT_MATH,
    name="mod", visual_style="math", permissions={"math"},
)(_math_mod)

MATH_ROUND_TO = kix_block(
    id="math.round_to", category="math", color=CAT_MATH,
    name="arredondar para", visual_style="math", permissions={"math"},
)(_math_round_to)


# Funções com 1 argumento ---------------------------------------------
MATH_SQRT = KixBlock(
    id="math.sqrt", name="√", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("√"), BlockInput("n")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=4)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.sqrt(self.n)"),
    permissions={"math"},
)
MATH_ABS = KixBlock(
    id="math.abs", name="|x|", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("|"), BlockInput("n"), Text("|")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=-1)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return abs(self.n)"),
    permissions={"math"},
)
MATH_SIN = KixBlock(
    id="math.sin", name="sin", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("sin("), BlockInput("deg"), Text(")")])),
    inputs=[SocketDef("deg", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.sin(math.radians(self.deg))"),
    permissions={"math"},
)
MATH_COS = KixBlock(
    id="math.cos", name="cos", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("cos("), BlockInput("deg"), Text(")")])),
    inputs=[SocketDef("deg", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.cos(math.radians(self.deg))"),
    permissions={"math"},
)
MATH_TAN = KixBlock(
    id="math.tan", name="tan", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("tan("), BlockInput("deg"), Text(")")])),
    inputs=[SocketDef("deg", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.tan(math.radians(self.deg))"),
    permissions={"math"},
)
MATH_ASIN = KixBlock(
    id="math.asin", name="asin", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("asin("), BlockInput("n"), Text(")°")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.degrees(math.asin(self.n))"),
    permissions={"math"},
)
MATH_ACOS = KixBlock(
    id="math.acos", name="acos", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("acos("), BlockInput("n"), Text(")°")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=1)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.degrees(math.acos(self.n))"),
    permissions={"math"},
)
MATH_ATAN2 = KixBlock(
    id="math.atan2", name="atan2", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("atan2("), BlockInput("y"), Text(", "), BlockInput("x"), Text(")°")])),
    inputs=[SocketDef("y", SocketKind.NUMBER, default=0),
            SocketDef("x", SocketKind.NUMBER, default=1)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.degrees(math.atan2(self.y, self.x))"),
    permissions={"math"},
)
MATH_FLOOR = KixBlock(
    id="math.floor", name="floor", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("floor("), BlockInput("n"), Text(")")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=1.5)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.floor(self.n)"),
    permissions={"math"},
)
MATH_CEIL = KixBlock(
    id="math.ceil", name="ceil", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("ceil("), BlockInput("n"), Text(")")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=1.5)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.ceil(self.n)"),
    permissions={"math"},
)
MATH_ROUND = KixBlock(
    id="math.round", name="round", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("round("), BlockInput("n"), Text(")")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=1.5)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return round(self.n)"),
    permissions={"math"},
)
MATH_POW = KixBlock(
    id="math.pow", name="pow", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[BlockInput("base"), Text("^"), BlockInput("exp")])),
    inputs=[SocketDef("base", SocketKind.NUMBER, default=2),
            SocketDef("exp", SocketKind.NUMBER, default=8)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.base ** self.exp"),
    permissions={"math"},
)
MATH_LOG = KixBlock(
    id="math.log", name="log", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("log("), BlockInput("n"), Text(", base "), BlockInput("base"), Text(")")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=100),
            SocketDef("base", SocketKind.NUMBER, default=10)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.log(self.n, self.base)"),
    permissions={"math"},
)
MATH_EXP = KixBlock(
    id="math.exp", name="exp", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("exp("), BlockInput("n"), Text(")")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=1)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import math; return math.exp(self.n)"),
    permissions={"math"},
)
MATH_RANDOM = KixBlock(
    id="math.random", name="aleatório", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("Aleatório entre "), BlockInput("a"), Text(" e "), BlockInput("b")])),
    inputs=[SocketDef("a", SocketKind.NUMBER, default=1),
            SocketDef("b", SocketKind.NUMBER, default=10)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "import random; return random.uniform(self.a, self.b)"),
    permissions={"math"},
)

# Funções com 2 argumentos ---------------------------------------------
MATH_MIN = KixBlock(
    id="math.min", name="min", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("min("), BlockInput("a"), Text(", "), BlockInput("b"), Text(")")])),
    inputs=[SocketDef("a", SocketKind.NUMBER, default=0),
            SocketDef("b", SocketKind.NUMBER, default=1)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return min(self.a, self.b)"),
    permissions={"math"},
)
MATH_MAX = KixBlock(
    id="math.max", name="max", category="math", color=CAT_MATH,
    visual=BlockVisual(root=Group(children=[Text("max("), BlockInput("a"), Text(", "), BlockInput("b"), Text(")")])),
    inputs=[SocketDef("a", SocketKind.NUMBER, default=0),
            SocketDef("b", SocketKind.NUMBER, default=1)],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return max(self.a, self.b)"),
    permissions={"math"},
)

MATH_BLOCKS = (MATH_SQRT, MATH_ABS, MATH_SIN, MATH_COS, MATH_TAN,
               MATH_ASIN, MATH_ACOS, MATH_ATAN2, MATH_FLOOR, MATH_CEIL,
               MATH_ROUND, MATH_POW, MATH_LOG, MATH_EXP, MATH_RANDOM,
               MATH_MIN, MATH_MAX,
               MATH_LN, MATH_LOG10, MATH_PI, MATH_ATAN, MATH_MOD, MATH_ROUND_TO)

assert len(MATH_BLOCKS) == 23, f"esperado 23, obtido {len(MATH_BLOCKS)}"