"""Lego NXT, Arduino, Makey-Makey — stubs honestos via services.

Os blocos existem na paleta e rodam sem erro, mas o comportamento real
depende de drivers nativos (Bluetooth para NXT/Arduino, USB HID para
Makey-Makey). Aqui cada operação:

- Grava a chamada em `ctx.services.<driver>._attrs["last_*"]` para que
  testes possam verificar a intenção.
- Lê de atributos inicializados com defaults seguros (0.0 / False / "").

Drivers reais são plugados via `ctx.services.nxt.connect(...)` etc.
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
from Kix.core.theme import CAT_NETWORK, CAT_DEVICE


# ============================================================ Lego NXT
NXT_CONNECT = KixBlock(
    id="lego.nxt.connect", name="NXT conectar", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Conectar NXT "), BlockInput("address")])),
    inputs=[SocketDef("address", SocketKind.STRING, default="00:00:00:00:00:00")],
    outputs=[],
    behavior=BlockBehavior("python", "ctx.services.nxt.connect(self.address)"),
    permissions={"hardware", "network"},
)
NXT_DISCONNECT = KixBlock(
    id="lego.nxt.disconnect", name="NXT desconectar", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Desconectar NXT")])),
    inputs=[], outputs=[],
    behavior=BlockBehavior("python", "ctx.services.nxt.disconnect()"),
    permissions={"hardware", "network"},
)
NXT_MOTOR = KixBlock(
    id="lego.nxt.motor", name="NXT motor", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[
        Text("NXT motor "), BlockInput("port"),
        Text(" velocidade "), BlockInput("speed"),
        Text(" por "), BlockInput("duration"), Text(" s"),
    ])),
    inputs=[
        SocketDef("port", SocketKind.STRING, default="A"),
        SocketDef("speed", SocketKind.NUMBER, default=50),
        SocketDef("duration", SocketKind.NUMBER, default=1.0),
    ],
    outputs=[],
    behavior=BlockBehavior(
        "python",
        "ctx.services.nxt.motor(self.port, self.speed, self.duration)",
    ),
    permissions={"hardware", "network"},
)
NXT_TOUCH = KixBlock(
    id="lego.nxt.touch", name="NXT sensor de toque", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("NXT toque porta "), BlockInput("port")])),
    inputs=[SocketDef("port", SocketKind.STRING, default="1")],
    outputs=[SocketDef("value", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return ctx.services.nxt.touch(self.port)"),
    permissions={"hardware", "network"},
)
NXT_SOUND = KixBlock(
    id="lego.nxt.sound", name="NXT som", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("NXT som porta "), BlockInput("port")])),
    inputs=[SocketDef("port", SocketKind.STRING, default="2")],
    outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return ctx.services.nxt.sound(self.port)"),
    permissions={"hardware", "network"},
)
NXT_LIGHT = KixBlock(
    id="lego.nxt.light", name="NXT luz", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("NXT luz porta "), BlockInput("port")])),
    inputs=[SocketDef("port", SocketKind.STRING, default="3")],
    outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return ctx.services.nxt.light(self.port)"),
    permissions={"hardware", "network"},
)
NXT_ULTRASONIC = KixBlock(
    id="lego.nxt.ultrasonic", name="NXT ultrassom", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("NXT ultrassom porta "), BlockInput("port")])),
    inputs=[SocketDef("port", SocketKind.STRING, default="4")],
    outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return ctx.services.nxt.ultrasonic(self.port)"),
    permissions={"hardware", "network"},
)
NXT_PLAY_TONE = KixBlock(
    id="lego.nxt.play_tone", name="NXT tocar nota", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[
        Text("NXT nota "), BlockInput("frequency"),
        Text(" Hz por "), BlockInput("duration"), Text(" ms"),
    ])),
    inputs=[
        SocketDef("frequency", SocketKind.NUMBER, default=440),
        SocketDef("duration", SocketKind.NUMBER, default=500),
    ],
    outputs=[],
    behavior=BlockBehavior(
        "python",
        "ctx.services.nxt.play_tone(self.frequency, self.duration)",
    ),
    permissions={"hardware", "network"},
)

# ============================================================ Arduino
ARDUINO_CONNECT = KixBlock(
    id="arduino.connect", name="Arduino conectar", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Conectar Arduino "), BlockInput("port")])),
    inputs=[SocketDef("port", SocketKind.STRING, default="/dev/ttyUSB0")],
    outputs=[],
    behavior=BlockBehavior("python", "ctx.services.arduino.connect(self.port)"),
    permissions={"hardware", "network"},
)
ARDUINO_DISCONNECT = KixBlock(
    id="arduino.disconnect", name="Arduino desconectar", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Desconectar Arduino")])),
    inputs=[], outputs=[],
    behavior=BlockBehavior("python", "ctx.services.arduino.disconnect()"),
    permissions={"hardware", "network"},
)
ARDUINO_DIGITAL_WRITE = KixBlock(
    id="arduino.digital_write", name="Arduino digital write", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[
        Text("Arduino pino "), BlockInput("pin"),
        Text(" digital "), BlockInput("value"),
    ])),
    inputs=[
        SocketDef("pin", SocketKind.NUMBER, default=13),
        SocketDef("value", SocketKind.BOOLEAN, default=True),
    ],
    outputs=[],
    behavior=BlockBehavior(
        "python",
        "ctx.services.arduino.digital_write(self.pin, bool(self.value))",
    ),
    permissions={"hardware", "network"},
)
ARDUINO_DIGITAL_READ = KixBlock(
    id="arduino.digital_read", name="Arduino digital read", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Arduino ler pino "), BlockInput("pin")])),
    inputs=[SocketDef("pin", SocketKind.NUMBER, default=2)],
    outputs=[SocketDef("value", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return ctx.services.arduino.digital_read(self.pin)"),
    permissions={"hardware", "network"},
)
ARDUINO_ANALOG_WRITE = KixBlock(
    id="arduino.analog_write", name="Arduino PWM", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[
        Text("Arduino pino "), BlockInput("pin"), Text(" PWM "), BlockInput("value"),
    ])),
    inputs=[
        SocketDef("pin", SocketKind.NUMBER, default=9),
        SocketDef("value", SocketKind.NUMBER, default=128),
    ],
    outputs=[],
    behavior=BlockBehavior(
        "python",
        "ctx.services.arduino.analog_write(self.pin, int(self.value))",
    ),
    permissions={"hardware", "network"},
)
ARDUINO_ANALOG_READ = KixBlock(
    id="arduino.analog_read", name="Arduino analog read", category="network", color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Arduino ler analógico "), BlockInput("pin")])),
    inputs=[SocketDef("pin", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return ctx.services.arduino.analog_read(self.pin)"),
    permissions={"hardware", "network"},
)

# ============================================================ Makey-Makey
MAKEY_CONNECT = KixBlock(
    id="makey.connect", name="Makey conectar", category="device", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Conectar Makey-Makey")])),
    inputs=[], outputs=[],
    behavior=BlockBehavior("python", "ctx.services.makey.connect()"),
    permissions={"hardware"},
)
MAKEY_IS_PRESSED = KixBlock(
    id="makey.is_pressed", name="Makey pressionado?", category="device", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Makey tecla "), BlockInput("key"), Text(" pressionada?")])),
    inputs=[SocketDef("key", SocketKind.STRING, default="SPACE")],
    outputs=[SocketDef("value", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return ctx.services.makey.is_pressed(self.key)"),
    permissions={"hardware"},
)

LEGO_BLOCKS = (
    NXT_CONNECT, NXT_DISCONNECT, NXT_MOTOR, NXT_TOUCH,
    NXT_SOUND, NXT_LIGHT, NXT_ULTRASONIC, NXT_PLAY_TONE,
)
ARDUINO_BLOCKS = (
    ARDUINO_CONNECT, ARDUINO_DISCONNECT,
    ARDUINO_DIGITAL_WRITE, ARDUINO_DIGITAL_READ,
    ARDUINO_ANALOG_WRITE, ARDUINO_ANALOG_READ,
)
MAKEY_BLOCKS = (MAKEY_CONNECT, MAKEY_IS_PRESSED)

HARDWARE_BLOCKS = LEGO_BLOCKS + ARDUINO_BLOCKS + MAKEY_BLOCKS
