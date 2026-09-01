"""Blocos de controle: loops, condicionais, clones, mensagens."""

from Kix.block_engine import (
    BlockInput,
    BlockVisual,
    Boolean,
    Group,
    KixBlock,
    Number,
    SocketDef,
    SocketKind,
    Text,
)
from Kix.block_engine.behavior import BlockBehavior
from Kix.core.theme import CAT_CONTROL, CAT_EVENT


# ============================================================ Wait / loops
WAIT = KixBlock(
    id="control.wait",
    name="Esperar",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Esperar "), BlockInput("seconds"), Text(" s")])),
    inputs=[SocketDef("seconds", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await self.wait(self.seconds)"),
    permissions={"control"},
)

WAIT_UNTIL = KixBlock(
    id="control.wait_until",
    name="Esperar até",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Esperar até "), BlockInput("condition")])),
    inputs=[SocketDef("condition", SocketKind.BOOLEAN)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await self.wait_until(self.condition)"),
    permissions={"control"},
)

REPEAT = KixBlock(
    id="control.repeat",
    name="Repetir",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Repetir "), BlockInput("times"), Text(" vezes"), BlockInput("body")])),
    inputs=[SocketDef("times", SocketKind.NUMBER, default=10),
            SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="for _ in range(self.times): await self.run(self.body)"),
    permissions={"control"},
)

FOREVER = KixBlock(
    id="control.forever",
    name="Sempre",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Sempre"), BlockInput("body")])),
    inputs=[SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="while True: await self.run(self.body)"),
    permissions={"control"},
)

IF = KixBlock(
    id="control.if",
    name="Se",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Se "), BlockInput("condition"), Text(" então"), BlockInput("body")])),
    inputs=[SocketDef("condition", SocketKind.BOOLEAN),
            SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="if self.condition: await self.run(self.body)"),
    permissions={"control"},
)

IF_ELSE = KixBlock(
    id="control.if_else",
    name="Se senão",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Se "), BlockInput("condition"), Text(" então"), BlockInput("then_body"), Text(" senão"), BlockInput("else_body")])),
    inputs=[SocketDef("condition", SocketKind.BOOLEAN),
            SocketDef("then_body", SocketKind.BLOCK),
            SocketDef("else_body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior(language="python", source=(
        "if self.condition: await self.run(self.then_body)"
        "else: await self.run(self.else_body)"
    )),
    permissions={"control"},
)

REPEAT_UNTIL = KixBlock(
    id="control.repeat_until",
    name="Repetir até",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Repetir até "), BlockInput("condition"), BlockInput("body")])),
    inputs=[SocketDef("condition", SocketKind.BOOLEAN),
            SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="while not self.condition: await self.run(self.body)"),
    permissions={"control"},
)

STOP_ALL = KixBlock(
    id="control.stop_all",
    name="Parar tudo",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Parar tudo")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.stop_all()"),
    permissions={"control"},
)

CONTINUE = KixBlock(
    id="control.continue",
    name="Continuar",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Pular para próxima iteração")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="raise ContinueSignal()"),
    permissions={"control"},
)

BREAK = KixBlock(
    id="control.break",
    name="Sair do loop",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Sair do loop")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="raise BreakSignal()"),
    permissions={"control"},
)

CREATE_CLONE = KixBlock(
    id="control.clone",
    name="Criar clone",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Criar clone de mim")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.clone()"),
    permissions={"control"},
)

WHEN_CLONE_START = KixBlock(
    id="control.clone_start",
    name="Quando eu começar como clone",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Quando eu começar como clone"), BlockInput("body")])),
    inputs=[SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await self.run(self.body)"),
    permissions={"control"},
)

DELETE_CLONE = KixBlock(
    id="control.delete_clone",
    name="Deletar clone",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Deletar este clone")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.delete()"),
    permissions={"control"},
)

BROADCAST = KixBlock(
    id="control.broadcast",
    name="Enviar mensagem",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Enviar "), BlockInput("message")])),
    inputs=[SocketDef("message", SocketKind.STRING, default="msg1")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="broadcast(self.message)"),
    permissions={"control"},
)

BROADCAST_AND_WAIT = KixBlock(
    id="control.broadcast_wait",
    name="Enviar e esperar",
    category="control",
    color=CAT_CONTROL,
    visual=BlockVisual(root=Group(children=[Text("Enviar "), BlockInput("message"), Text(" e esperar")])),
    inputs=[SocketDef("message", SocketKind.STRING, default="msg1")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await broadcast_and_wait(self.message)"),
    permissions={"control"},
)


CONTROL = (WAIT, WAIT_UNTIL, REPEAT, FOREVER, IF, IF_ELSE, REPEAT_UNTIL,
           STOP_ALL, CONTINUE, BREAK, CREATE_CLONE, WHEN_CLONE_START,
           DELETE_CLONE, BROADCAST, BROADCAST_AND_WAIT)

assert len(CONTROL) == 15, f"esperado 15, obtido {len(CONTROL)}"