"""Blocos de notificações: toast, alert, dialog."""

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
from Kix.core.theme import CAT_NOTIFICATIONS


NOTIF_TOAST = KixBlock(
    id="notif.toast", name="Toast", category="notifications", color=CAT_NOTIFICATIONS,
    visual=BlockVisual(root=Group(children=[Text("Toast: "), BlockInput("message"), Text(" por "), BlockInput("seconds"), Text(" s")])),
    inputs=[SocketDef("message", SocketKind.STRING, default=""),
            SocketDef("seconds", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior("python", "ui.toast(self.message, self.seconds)"),
    permissions={"ui", "device"},
)
NOTIF_ALERT = KixBlock(
    id="notif.alert", name="Alerta", category="notifications", color=CAT_NOTIFICATIONS,
    visual=BlockVisual(root=Group(children=[Text("Alerta: "), BlockInput("title"), Text(" — "), BlockInput("body")])),
    inputs=[SocketDef("title", SocketKind.STRING, default=""),
            SocketDef("body", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "ui.alert(self.title, self.body)"),
    permissions={"ui", "device"},
)
NOTIF_DIALOG = KixBlock(
    id="notif.dialog", name="Diálogo", category="notifications", color=CAT_NOTIFICATIONS,
    visual=BlockVisual(root=Group(children=[Text("Diálogo: "), BlockInput("question")])),
    inputs=[SocketDef("question", SocketKind.STRING, default="")],
    outputs=[SocketDef("answer", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return await ui.dialog(self.question)"),
    permissions={"ui", "device"},
)

NOTIFICATIONS = (NOTIF_TOAST, NOTIF_ALERT, NOTIF_DIALOG)

assert len(NOTIFICATIONS) == 3, f"esperado 3, obtido {len(NOTIFICATIONS)}"