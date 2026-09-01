"""Blocos de física: gravidade, velocidade, força, atrito, raycast."""

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
from Kix.core.theme import CAT_PHYSICS


PHYS_SET_GRAVITY = KixBlock(
    id="physics.set_gravity", name="Definir gravidade", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Gravidade = "), BlockInput("g")])),
    inputs=[SocketDef("g", SocketKind.NUMBER, default=9.8)],
    outputs=[],
    behavior=BlockBehavior("python", "physics.gravity = self.g"),
    permissions={"physics"},
)
PHYS_GET_GRAVITY = KixBlock(
    id="physics.get_gravity", name="Gravidade atual", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Gravidade atual")])),
    inputs=[],
    outputs=[SocketDef("g", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return physics.gravity"),
    permissions={"physics"},
)
PHYS_SET_VELOCITY = KixBlock(
    id="physics.set_velocity", name="Definir velocidade", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Velocidade x:"), BlockInput("vx"), Text(" y:"), BlockInput("vy")])),
    inputs=[SocketDef("vx", SocketKind.NUMBER, default=0),
            SocketDef("vy", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior("python", "self.velocity = (self.vx, self.vy)"),
    permissions={"physics"},
)
PHYS_GET_VELOCITY = KixBlock(
    id="physics.get_velocity", name="Velocidade", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Velocidade atual")])),
    inputs=[],
    outputs=[SocketDef("vx", SocketKind.NUMBER),
             SocketDef("vy", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.velocity"),
    permissions={"physics"},
)
PHYS_ADD_FORCE = KixBlock(
    id="physics.add_force", name="Aplicar força", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Força x:"), BlockInput("fx"), Text(" y:"), BlockInput("fy")])),
    inputs=[SocketDef("fx", SocketKind.NUMBER, default=0),
            SocketDef("fy", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior("python", "self.apply_force(self.fx, self.fy)"),
    permissions={"physics"},
)
PHYS_FRICTION = KixBlock(
    id="physics.set_friction", name="Atrito", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Atrito = "), BlockInput("friction")])),
    inputs=[SocketDef("friction", SocketKind.NUMBER, default=0.1)],
    outputs=[],
    behavior=BlockBehavior("python", "self.friction = self.friction"),
    permissions={"physics"},
)
PHYS_BOUNCE = KixBlock(
    id="physics.set_bounce", name="Fator de pulo", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Fator de pulo = "), BlockInput("bounce")])),
    inputs=[SocketDef("bounce", SocketKind.NUMBER, default=0.5)],
    outputs=[],
    behavior=BlockBehavior("python", "self.bounce = self.bounce"),
    permissions={"physics"},
)
PHYS_MASS = KixBlock(
    id="physics.set_mass", name="Massa", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Massa = "), BlockInput("mass")])),
    inputs=[SocketDef("mass", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior("python", "self.mass = self.mass"),
    permissions={"physics"},
)
PHYS_RAYCAST = KixBlock(
    id="physics.raycast", name="Raycast", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Raycast ângulo "), BlockInput("angle"), Text(" alcance "), BlockInput("range")])),
    inputs=[SocketDef("angle", SocketKind.ANGLE, default=0),
            SocketDef("range", SocketKind.NUMBER, default=500)],
    outputs=[SocketDef("hit", SocketKind.BOOLEAN),
             SocketDef("distance", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return physics.raycast(self.angle, self.range)"),
    permissions={"physics"},
)
PHYS_COLLIDE_WORLD = KixBlock(
    id="physics.collide_world", name="Colide com mundo?", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Colidindo com mundo?")])),
    inputs=[],
    outputs=[SocketDef("colliding", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return self.collide_world()"),
    permissions={"physics"},
)
PHYS_ON_GROUND = KixBlock(
    id="physics.on_ground", name="No chão?", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Estou no chão?")])),
    inputs=[],
    outputs=[SocketDef("grounded", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return self.on_ground"),
    permissions={"physics"},
)
PHYS_JUMP = KixBlock(
    id="physics.jump", name="Pular", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Pular com força "), BlockInput("force")])),
    inputs=[SocketDef("force", SocketKind.NUMBER, default=300)],
    outputs=[],
    behavior=BlockBehavior("python", "self.jump(self.force)"),
    permissions={"physics"},
)

PHYSICS = (PHYS_SET_GRAVITY, PHYS_GET_GRAVITY, PHYS_SET_VELOCITY, PHYS_GET_VELOCITY,
           PHYS_ADD_FORCE, PHYS_FRICTION, PHYS_BOUNCE, PHYS_MASS,
           PHYS_RAYCAST, PHYS_COLLIDE_WORLD, PHYS_ON_GROUND, PHYS_JUMP)

assert len(PHYSICS) == 12, f"esperado 12, obtido {len(PHYSICS)}"