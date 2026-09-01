"""Blocos de manipulação de texto."""

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
from Kix.core.theme import CAT_STRINGS


STR_LENGTH = KixBlock(
    id="str.length", name="comprimento", category="strings", color=CAT_STRINGS,
    visual=BlockVisual(root=Group(children=[Text("comprimento("), BlockInput("s"), Text(")")])),
    inputs=[SocketDef("s", SocketKind.STRING, default="")],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return len(self.s)"),
    permissions=set(),
)
STR_CONTAINS = KixBlock(
    id="str.contains", name="contém?", category="strings", color=CAT_STRINGS,
    visual=BlockVisual(root=Group(children=[BlockInput("haystack"), Text(" contém "), BlockInput("needle")])),
    inputs=[SocketDef("haystack", SocketKind.STRING, default=""),
            SocketDef("needle", SocketKind.STRING, default="")],
    outputs=[SocketDef("result", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return self.needle in self.haystack"),
    permissions=set(),
)
STR_REPLACE = KixBlock(
    id="str.replace", name="substituir", category="strings", color=CAT_STRINGS,
    visual=BlockVisual(root=Group(children=[Text("substituir "), BlockInput("old"), Text(" por "), BlockInput("new"), Text(" em "), BlockInput("s")])),
    inputs=[SocketDef("s", SocketKind.STRING, default=""),
            SocketDef("old", SocketKind.STRING, default=""),
            SocketDef("new", SocketKind.STRING, default="")],
    outputs=[SocketDef("result", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return self.s.replace(self.old, self.new)"),
    permissions=set(),
)
STR_UPPER = KixBlock(
    id="str.upper", name="MAIÚSCULAS", category="strings", color=CAT_STRINGS,
    visual=BlockVisual(root=Group(children=[Text("MAIÚSCULAS("), BlockInput("s"), Text(")")])),
    inputs=[SocketDef("s", SocketKind.STRING, default="")],
    outputs=[SocketDef("result", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return self.s.upper()"),
    permissions=set(),
)
STR_LOWER = KixBlock(
    id="str.lower", name="minúsculas", category="strings", color=CAT_STRINGS,
    visual=BlockVisual(root=Group(children=[Text("minúsculas("), BlockInput("s"), Text(")")])),
    inputs=[SocketDef("s", SocketKind.STRING, default="")],
    outputs=[SocketDef("result", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return self.s.lower()"),
    permissions=set(),
)
STR_CHAR_AT = KixBlock(
    id="str.char_at", name="caractere em", category="strings", color=CAT_STRINGS,
    visual=BlockVisual(root=Group(children=[Text("caractere "), BlockInput("i"), Text(" de "), BlockInput("s")])),
    inputs=[SocketDef("s", SocketKind.STRING, default=""),
            SocketDef("i", SocketKind.NUMBER, default=1)],
    outputs=[SocketDef("result", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return self.s[self.i - 1] if 1 <= self.i <= len(self.s) else ''"),
    permissions=set(),
)
STR_SUBSTRING = KixBlock(
    id="str.substring", name="substring", category="strings", color=CAT_STRINGS,
    visual=BlockVisual(root=Group(children=[Text("substring de "), BlockInput("s"), Text(" entre "), BlockInput("start"), Text(" e "), BlockInput("end")])),
    inputs=[SocketDef("s", SocketKind.STRING, default=""),
            SocketDef("start", SocketKind.NUMBER, default=1),
            SocketDef("end", SocketKind.NUMBER, default=3)],
    outputs=[SocketDef("result", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return self.s[self.start - 1:self.end]"),
    permissions=set(),
)
STR_SPLIT = KixBlock(
    id="str.split", name="dividir", category="strings", color=CAT_STRINGS,
    visual=BlockVisual(root=Group(children=[Text("dividir "), BlockInput("s"), Text(" por "), BlockInput("sep")])),
    inputs=[SocketDef("s", SocketKind.STRING, default=""),
            SocketDef("sep", SocketKind.STRING, default=",")],
    outputs=[SocketDef("parts", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return self.s.split(self.sep)"),
    permissions=set(),
)

STRINGS = (STR_LENGTH, STR_CONTAINS, STR_REPLACE, STR_UPPER, STR_LOWER,
           STR_CHAR_AT, STR_SUBSTRING, STR_SPLIT)

assert len(STRINGS) == 8, f"esperado 8, obtido {len(STRINGS)}"