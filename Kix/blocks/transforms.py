"""Blocos de movimento, câmera e joystick.

Inclui o subset essencial do Catroid (motion) + extensões para games estilo
Brawl Stars (joystick virtual, câmera que segue e shake).
"""

from Kix.block_engine import (
    BlockInput,
    BlockVisual,
    Group,
    KixBlock,
    Number,
    Position,
    Slider,
    SocketDef,
    SocketKind,
    Text,
)
from Kix.block_engine.behavior import BlockBehavior
from Kix.core.theme import CAT_CAMERA, CAT_JOYSTICK, CAT_MOTION


# ============================================================ Motion (15)
MOVE = KixBlock(
    id="motion.move",
    name="Mover",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Mover "), BlockInput("steps"), Text(" passos")])),
    inputs=[SocketDef("steps", SocketKind.NUMBER, default=10)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.translate(self.steps, 0)"),
    permissions={"transform"},
)

MOVE_XY = KixBlock(
    id="motion.move_xy",
    name="Mover X/Y",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Mover x:"), BlockInput("dx"), Text(" y:"), BlockInput("dy")])),
    inputs=[SocketDef("dx", SocketKind.NUMBER, default=10),
            SocketDef("dy", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.translate(self.dx, self.dy)"),
    permissions={"transform"},
)

MOVE_TO = KixBlock(
    id="motion.move_to",
    name="Ir para X/Y",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Ir para x:"), BlockInput("x"), Text(" y:"), BlockInput("y")])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=0),
            SocketDef("y", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.position = (self.x, self.y)"),
    permissions={"transform"},
)

MOVE_TO_OBJECT = KixBlock(
    id="motion.move_to_object",
    name="Ir para objeto",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Ir para "), BlockInput("target")])),
    inputs=[SocketDef("target", SocketKind.OBJECT)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.position = self.target.position"),
    permissions={"transform"},
)

SLIDE_TO = KixBlock(
    id="motion.slide_to",
    name="Deslizar para",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Deslizar para x:"), BlockInput("x"), Text(" y:"), BlockInput("y"), Text(" em "), BlockInput("duration"), Text(" s")])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=0),
            SocketDef("y", SocketKind.NUMBER, default=0),
            SocketDef("duration", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await self.slide(self.x, self.y, self.duration)"),
    permissions={"transform"},
)

ROTATE_BY = KixBlock(
    id="motion.rotate_by",
    name="Girar",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Girar "), BlockInput("angle"), Text("°")])),
    inputs=[SocketDef("angle", SocketKind.NUMBER, default=15)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.rotation += self.angle"),
    permissions={"transform"},
)

POINT_IN_DIRECTION = KixBlock(
    id="motion.point_in_direction",
    name="Apontar direção",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Apontar para "), BlockInput("direction"), Text("°")])),
    inputs=[SocketDef("direction", SocketKind.ANGLE, default=90)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.rotation = self.direction"),
    permissions={"transform"},
)

POINT_TOWARDS = KixBlock(
    id="motion.point_towards",
    name="Apontar para",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Apontar para "), BlockInput("target")])),
    inputs=[SocketDef("target", SocketKind.OBJECT)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.look_at(self.target)"),
    permissions={"transform"},
)

BOUNCE_IF_ON_EDGE = KixBlock(
    id="motion.bounce_if_on_edge",
    name="Rebater na borda",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Se na borda, rebater")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.bounce_if_on_edge()"),
    permissions={"transform"},
)

SET_X = KixBlock(
    id="motion.set_x",
    name="Definir X",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Definir x = "), BlockInput("x")])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.position = (self.x, self.position[1])"),
    permissions={"transform"},
)

SET_Y = KixBlock(
    id="motion.set_y",
    name="Definir Y",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Definir y = "), BlockInput("y")])),
    inputs=[SocketDef("y", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.position = (self.position[0], self.y)"),
    permissions={"transform"},
)

CHANGE_X = KixBlock(
    id="motion.change_x",
    name="Mudar X",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Mudar x por "), BlockInput("dx")])),
    inputs=[SocketDef("dx", SocketKind.NUMBER, default=10)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.position = (self.position[0] + self.dx, self.position[1])"),
    permissions={"transform"},
)

CHANGE_Y = KixBlock(
    id="motion.change_y",
    name="Mudar Y",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Mudar y por "), BlockInput("dy")])),
    inputs=[SocketDef("dy", SocketKind.NUMBER, default=10)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.position = (self.position[0], self.position[1] + self.dy)"),
    permissions={"transform"},
)

STOP_MOVING = KixBlock(
    id="motion.stop",
    name="Parar",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Parar de mover")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.velocity = (0, 0)"),
    permissions={"transform"},
)

SET_ROTATION_STYLE = KixBlock(
    id="motion.rotation_style",
    name="Estilo de rotação",
    category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("Estilo de rotação: "), BlockInput("style")])),
    inputs=[SocketDef("style", SocketKind.STRING, default="all around")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.rotation_style = self.style"),
    permissions={"transform"},
)


# ============================================================ Camera (8)
CAMERA_FOLLOW = KixBlock(
    id="camera.follow",
    name="Câmera seguir",
    category="camera",
    color=CAT_CAMERA,
    visual=BlockVisual(root=Group(children=[Text("Câmera seguir "), BlockInput("target")])),
    inputs=[SocketDef("target", SocketKind.OBJECT)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="camera.follow(self.target)"),
    permissions={"camera"},
)

CAMERA_GOTO = KixBlock(
    id="camera.goto",
    name="Câmera ir para",
    category="camera",
    color=CAT_CAMERA,
    visual=BlockVisual(root=Group(children=[Text("Câmera ir para x:"), BlockInput("x"), Text(" y:"), BlockInput("y")])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=0),
            SocketDef("y", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="camera.position = (self.x, self.y)"),
    permissions={"camera"},
)

CAMERA_FOLLOW_MOUSE = KixBlock(
    id="camera.follow_mouse",
    name="Câmera seguir mouse",
    category="camera",
    color=CAT_CAMERA,
    visual=BlockVisual(root=Group(children=[Text("Câmera seguir mouse"), BlockInput("enabled")])),
    inputs=[SocketDef("enabled", SocketKind.BOOLEAN, default=True)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="camera.follow_mouse = bool(self.enabled)"),
    permissions={"camera"},
)

CAMERA_STOP = KixBlock(
    id="camera.stop",
    name="Câmera parar",
    category="camera",
    color=CAT_CAMERA,
    visual=BlockVisual(root=Group(children=[Text("Câmera parar de seguir")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="camera.unfollow()"),
    permissions={"camera"},
)

CAMERA_ZOOM = KixBlock(
    id="camera.zoom",
    name="Zoom da câmera",
    category="camera",
    color=CAT_CAMERA,
    visual=BlockVisual(root=Group(children=[Text("Zoom = "), BlockInput("zoom")])),
    inputs=[SocketDef("zoom", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="camera.zoom = self.zoom"),
    permissions={"camera"},
)

CAMERA_SHAKE = KixBlock(
    id="camera.shake",
    name="Câmera tremer",
    category="camera",
    color=CAT_CAMERA,
    visual=BlockVisual(root=Group(children=[Text("Câmera tremer por "), BlockInput("duration"), Text(" s intensidade "), BlockInput("intensity")])),
    inputs=[SocketDef("duration", SocketKind.NUMBER, default=0.3),
            SocketDef("intensity", SocketKind.NUMBER, default=8.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await camera.shake(self.duration, self.intensity)"),
    permissions={"camera"},
)

CAMERA_LIMIT = KixBlock(
    id="camera.limit",
    name="Limite da câmera",
    category="camera",
    color=CAT_CAMERA,
    visual=BlockVisual(root=Group(children=[Text("Limite: x1:"), BlockInput("x1"), Text(" y1:"), BlockInput("y1"), Text(" x2:"), BlockInput("x2"), Text(" y2:"), BlockInput("y2")])),
    inputs=[SocketDef("x1", SocketKind.NUMBER, default=-1000),
            SocketDef("y1", SocketKind.NUMBER, default=-1000),
            SocketDef("x2", SocketKind.NUMBER, default=1000),
            SocketDef("y2", SocketKind.NUMBER, default=1000)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="camera.bounds = (self.x1, self.y1, self.x2, self.y2)"),
    permissions={"camera"},
)

CAMERA_RESET = KixBlock(
    id="camera.reset",
    name="Câmera reset",
    category="camera",
    color=CAT_CAMERA,
    visual=BlockVisual(root=Group(children=[Text("Resetar câmera")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="camera.reset()"),
    permissions={"camera"},
)


# ============================================================ Joystick (6)
JOYSTICK_CREATE = KixBlock(
    id="joystick.create",
    name="Criar joystick",
    category="joystick",
    color=CAT_JOYSTICK,
    visual=BlockVisual(root=Group(children=[Text("Criar joystick em x:"), BlockInput("x"), Text(" y:"), BlockInput("y"), Text(" raio:"), BlockInput("radius")])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=120),
            SocketDef("y", SocketKind.NUMBER, default=720),
            SocketDef("radius", SocketKind.NUMBER, default=80)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="joystick = Joystick(self.x, self.y, self.radius)"),
    permissions={"ui", "input"},
)

JOYSTICK_DIRECTION = KixBlock(
    id="joystick.direction",
    name="Direção do joystick",
    category="joystick",
    color=CAT_JOYSTICK,
    visual=BlockVisual(root=Group(children=[Text("Direção do joystick")])),
    inputs=[],
    outputs=[SocketDef("direction", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return joystick.direction"),
    permissions={"ui", "input"},
)

JOYSTICK_MAGNITUDE = KixBlock(
    id="joystick.magnitude",
    name="Magnitude do joystick",
    category="joystick",
    color=CAT_JOYSTICK,
    visual=BlockVisual(root=Group(children=[Text("Magnitude do joystick (0 a 1)")])),
    inputs=[],
    outputs=[SocketDef("magnitude", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return joystick.magnitude"),
    permissions={"ui", "input"},
)

JOYSTICK_DEADZONE = KixBlock(
    id="joystick.deadzone",
    name="Zona morta",
    category="joystick",
    color=CAT_JOYSTICK,
    visual=BlockVisual(root=Group(children=[Text("Definir zona morta: "), BlockInput("deadzone")])),
    inputs=[SocketDef("deadzone", SocketKind.NUMBER, default=0.1)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="joystick.deadzone = self.deadzone"),
    permissions={"ui", "input"},
)

JOYSTICK_IS_ACTIVE = KixBlock(
    id="joystick.is_active",
    name="Joystick ativo?",
    category="joystick",
    color=CAT_JOYSTICK,
    visual=BlockVisual(root=Group(children=[Text("Joystick está sendo tocado?")])),
    inputs=[],
    outputs=[SocketDef("active", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return joystick.is_active"),
    permissions={"ui", "input"},
)

JOYSTICK_ANGLE = KixBlock(
    id="joystick.angle",
    name="Ângulo do joystick",
    category="joystick",
    color=CAT_JOYSTICK,
    visual=BlockVisual(root=Group(children=[Text("Ângulo do joystick (°)")])),
    inputs=[],
    outputs=[SocketDef("angle", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return joystick.angle"),
    permissions={"ui", "input"},
)


# --- M3.3: motion property reporters (6) ---------------------------------
POSITION_X = KixBlock(
    id="motion.position_x", name="posição x", category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("posição x")])),
    inputs=[], outputs=[SocketDef("x", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.position[0]"),
    permissions={"transform"},
)
POSITION_Y = KixBlock(
    id="motion.position_y", name="posição y", category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("posição y")])),
    inputs=[], outputs=[SocketDef("y", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.position[1]"),
    permissions={"transform"},
)
SPRITE_SIZE = KixBlock(
    id="motion.size", name="tamanho", category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("tamanho")])),
    inputs=[], outputs=[SocketDef("size", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.size"),
    permissions={"transform"},
)
SPRITE_WIDTH = KixBlock(
    id="motion.width", name="largura", category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("largura")])),
    inputs=[], outputs=[SocketDef("width", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.fw"),
    permissions={"transform"},
)
SPRITE_HEIGHT = KixBlock(
    id="motion.height", name="altura", category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("altura")])),
    inputs=[], outputs=[SocketDef("height", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.fh"),
    permissions={"transform"},
)
SPRITE_DIRECTION = KixBlock(
    id="motion.direction", name="direção", category="motion",
    color=CAT_MOTION,
    visual=BlockVisual(root=Group(children=[Text("direção")])),
    inputs=[], outputs=[SocketDef("direction", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.direction"),
    permissions={"transform"},
)

# Aggregate para testes/serialização
TRANSFORMS = (MOVE, MOVE_XY, MOVE_TO, MOVE_TO_OBJECT, SLIDE_TO,
              ROTATE_BY, POINT_IN_DIRECTION, POINT_TOWARDS, BOUNCE_IF_ON_EDGE,
              SET_X, SET_Y, CHANGE_X, CHANGE_Y, STOP_MOVING, SET_ROTATION_STYLE,
              CAMERA_FOLLOW, CAMERA_GOTO, CAMERA_FOLLOW_MOUSE, CAMERA_STOP,
              CAMERA_ZOOM, CAMERA_SHAKE, CAMERA_LIMIT, CAMERA_RESET,
              JOYSTICK_CREATE, JOYSTICK_DIRECTION, JOYSTICK_MAGNITUDE,
              JOYSTICK_DEADZONE, JOYSTICK_IS_ACTIVE, JOYSTICK_ANGLE,
              POSITION_X, POSITION_Y, SPRITE_SIZE, SPRITE_WIDTH,
              SPRITE_HEIGHT, SPRITE_DIRECTION)

assert len(TRANSFORMS) == 35, f"esperado 35, obtido {len(TRANSFORMS)}"