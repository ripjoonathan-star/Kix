"""Blocos de Evento (hat-blocks) — Pocket Code style.

Todos têm `is_hat=True` → renderizam com topo convexo (forma hat).

Replicam os eventos da screenshot 9 do Pocket Code:
- Quando a cena começar
- Quando tocado
- Quando a tela for pressionada
- Quando o sprite for solto
- Quando o dedo mover sobre o sprite
- Quando o dedo mover na tela
- Quando você receber mensagem N
- Quando o sinal for recebido 'msg' (com parâmetros)
- Transmitir a todos com parâmetros

Mais o broadcast simples (Enviar / Enviar e esperar).
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
from Kix.core.theme import CAT_EVENT


# --- Hat blocks (topo convexo) ---------------------------------------------

HAT_SCENE_START = KixBlock(
    id="event.scene_start", name="Quando a cena começar",
    category="event", color=CAT_EVENT, is_hat=True,
    visual=BlockVisual(root=Group(children=[
        Text("Quando a cena começar"),
    ])),
    inputs=[SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.run(self.body)"),
)

HAT_TAP = KixBlock(
    id="event.tap", name="Quando tocado",
    category="event", color=CAT_EVENT, is_hat=True,
    visual=BlockVisual(root=Group(children=[Text("Quando tocado")])),
    inputs=[SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.run(self.body)"),
)

HAT_SCREEN_PRESSED = KixBlock(
    id="event.screen_pressed", name="Quando a tela for pressionada",
    category="event", color=CAT_EVENT, is_hat=True,
    visual=BlockVisual(root=Group(children=[
        Text("Quando a tela for pressionada"),
    ])),
    inputs=[SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.run(self.body)"),
)

HAT_SPRITE_RELEASE = KixBlock(
    id="event.sprite_release", name="Quando o sprite for solto",
    category="event", color=CAT_EVENT, is_hat=True,
    visual=BlockVisual(root=Group(children=[
        Text("Quando o sprite for solto"),
    ])),
    inputs=[SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.run(self.body)"),
)

HAT_FINGER_OVER_SPRITE = KixBlock(
    id="event.finger_over_sprite",
    name="Quando o dedo mover sobre o sprite",
    category="event", color=CAT_EVENT, is_hat=True,
    visual=BlockVisual(root=Group(children=[
        Text("Quando o dedo mover sobre o sprite"),
    ])),
    inputs=[SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.run(self.body)"),
)

HAT_FINGER_ON_SCREEN = KixBlock(
    id="event.finger_on_screen",
    name="Quando o dedo mover na tela",
    category="event", color=CAT_EVENT, is_hat=True,
    visual=BlockVisual(root=Group(children=[
        Text("Quando o dedo mover na tela"),
    ])),
    inputs=[SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.run(self.body)"),
)

HAT_MESSAGE_RECEIVED = KixBlock(
    id="event.message_received", name="Quando você receber mensagem",
    category="event", color=CAT_EVENT, is_hat=True,
    visual=BlockVisual(root=Group(children=[
        Text("Quando você receber mensagem "), BlockInput("message"),
    ])),
    inputs=[SocketDef("message", SocketKind.STRING, default="mensagem 1"),
            SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.run(self.body)"),
)

HAT_SIGNAL_RECEIVED = KixBlock(
    id="event.signal_received", name="Quando o sinal for recebido",
    category="event", color=CAT_EVENT, is_hat=True,
    visual=BlockVisual(root=Group(children=[
        Text("Quando o sinal for recebido "), BlockInput("signal"),
        Text(" salvar parâmetros em "), BlockInput("var"),
    ])),
    inputs=[SocketDef("signal", SocketKind.STRING, default="mensagem 1"),
            SocketDef("var", SocketKind.STRING, default="novo"),
            SocketDef("body", SocketKind.BLOCK)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.run(self.body)"),
)


# --- Blocos de mensagem (não-hat) ------------------------------------------

BROADCAST = KixBlock(
    id="event.broadcast", name="Enviar mensagem",
    category="event", color=CAT_EVENT,
    visual=BlockVisual(root=Group(children=[
        Text("Enviar "), BlockInput("message"),
    ])),
    inputs=[SocketDef("message", SocketKind.STRING, default="mensagem 1")],
    outputs=[],
    behavior=BlockBehavior("python", "broadcast(self.message)"),
)

BROADCAST_AND_WAIT = KixBlock(
    id="event.broadcast_wait", name="Enviar e aguardar",
    category="event", color=CAT_EVENT,
    visual=BlockVisual(root=Group(children=[
        Text("Enviar e aguardar "), BlockInput("message"),
    ])),
    inputs=[SocketDef("message", SocketKind.STRING, default="mensagem 1")],
    outputs=[],
    behavior=BlockBehavior("python", "await broadcast_and_wait(self.message)"),
)

BROADCAST_PARAMS = KixBlock(
    id="event.broadcast_params", name="Transmitir a todos com parâmetros",
    category="event", color=CAT_EVENT,
    visual=BlockVisual(root=Group(children=[
        Text("Transmitir a todos com parâmetros Sinal "),
        BlockInput("signal"),
        Text(" Parâmetros "), BlockInput("params"),
    ])),
    inputs=[SocketDef("signal", SocketKind.STRING, default="mensagem 1"),
            SocketDef("params", SocketKind.STRING, default="any data...")],
    outputs=[],
    behavior=BlockBehavior("python", "broadcast_params(self.signal, self.params)"),
)


EVENTS = (
    HAT_SCENE_START, HAT_TAP, HAT_SCREEN_PRESSED, HAT_SPRITE_RELEASE,
    HAT_FINGER_OVER_SPRITE, HAT_FINGER_ON_SCREEN,
    HAT_MESSAGE_RECEIVED, HAT_SIGNAL_RECEIVED,
    BROADCAST, BROADCAST_AND_WAIT, BROADCAST_PARAMS,
)

assert len(EVENTS) == 11, f"esperado 11 eventos, obtido {len(EVENTS)}"


__all__ = ["EVENTS"]
