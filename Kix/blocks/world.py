"""Blocos de mundo: tilemap + spritesheet + layers."""

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
from Kix.core.theme import CAT_LAYERS, CAT_SPRITESHEET, CAT_TILEMAP


# ============================================================ Tilemap (10)
TILEMAP_LOAD = KixBlock(
    id="tilemap.load",
    name="Carregar tilemap",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Carregar tilemap "), BlockInput("path")])),
    inputs=[SocketDef("path", SocketKind.FILE)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="tilemap.load(self.path)"),
    permissions={"tilemap"},
)

TILEMAP_TILE_AT = KixBlock(
    id="tilemap.tile_at",
    name="Tile em X/Y",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Tile em x:"), BlockInput("x"), Text(" y:"), BlockInput("y")])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=0),
            SocketDef("y", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("tile_id", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return tilemap.tile_at(int(self.x), int(self.y))"),
    permissions={"tilemap"},
)

TILEMAP_SET_TILE = KixBlock(
    id="tilemap.set_tile",
    name="Definir tile",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Definir tile em x:"), BlockInput("x"), Text(" y:"), BlockInput("y"), Text(" = "), BlockInput("tile_id")])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=0),
            SocketDef("y", SocketKind.NUMBER, default=0),
            SocketDef("tile_id", SocketKind.NUMBER, default=1)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="tilemap.set_tile(int(self.x), int(self.y), self.tile_id)"),
    permissions={"tilemap"},
)

TILEMAP_CLEAR = KixBlock(
    id="tilemap.clear",
    name="Limpar tilemap",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Limpar tilemap")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="tilemap.clear()"),
    permissions={"tilemap"},
)

TILEMAP_FILL = KixBlock(
    id="tilemap.fill",
    name="Preencher região",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Preencher x1:"), BlockInput("x1"), Text(" y1:"), BlockInput("y1"), Text(" x2:"), BlockInput("x2"), Text(" y2:"), BlockInput("y2"), Text(" com "), BlockInput("tile_id")])),
    inputs=[SocketDef("x1", SocketKind.NUMBER, default=0),
            SocketDef("y1", SocketKind.NUMBER, default=0),
            SocketDef("x2", SocketKind.NUMBER, default=10),
            SocketDef("y2", SocketKind.NUMBER, default=10),
            SocketDef("tile_id", SocketKind.NUMBER, default=1)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="tilemap.fill(self.x1, self.y1, self.x2, self.y2, self.tile_id)"),
    permissions={"tilemap"},
)

TILEMAP_COLLIDES = KixBlock(
    id="tilemap.collides",
    name="Colide em X/Y?",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Colide em x:"), BlockInput("x"), Text(" y:"), BlockInput("y")])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=0),
            SocketDef("y", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("collides", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return tilemap.is_solid(int(self.x), int(self.y))"),
    permissions={"tilemap"},
)

TILEMAP_SAVE = KixBlock(
    id="tilemap.save",
    name="Salvar tilemap",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Salvar como "), BlockInput("path")])),
    inputs=[SocketDef("path", SocketKind.FILE)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="tilemap.save(self.path)"),
    permissions={"tilemap", "storage"},
)

TILEMAP_WIDTH = KixBlock(
    id="tilemap.width",
    name="Largura do tilemap",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Largura do tilemap (tiles)")])),
    inputs=[],
    outputs=[SocketDef("width", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return tilemap.width"),
    permissions={"tilemap"},
)

TILEMAP_HEIGHT = KixBlock(
    id="tilemap.height",
    name="Altura do tilemap",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Altura do tilemap (tiles)")])),
    inputs=[],
    outputs=[SocketDef("height", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return tilemap.height"),
    permissions={"tilemap"},
)

TILEMAP_OFFSET = KixBlock(
    id="tilemap.offset",
    name="Offset de câmera",
    category="tilemap",
    color=CAT_TILEMAP,
    visual=BlockVisual(root=Group(children=[Text("Offset tilemap x:"), BlockInput("dx"), Text(" y:"), BlockInput("dy")])),
    inputs=[SocketDef("dx", SocketKind.NUMBER, default=0),
            SocketDef("dy", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="tilemap.offset = (self.dx, self.dy)"),
    permissions={"tilemap"},
)


# ============================================================ Spritesheet (8)
SHEET_LOAD = KixBlock(
    id="sheet.load",
    name="Carregar spritesheet",
    category="spritesheet",
    color=CAT_SPRITESHEET,
    visual=BlockVisual(root=Group(children=[Text("Carregar "), BlockInput("path"), Text(" "), BlockInput("fw"), Text("x"), BlockInput("fh")])),
    inputs=[SocketDef("path", SocketKind.FILE),
            SocketDef("fw", SocketKind.NUMBER, default=64),
            SocketDef("fh", SocketKind.NUMBER, default=64)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="sheet = Spritesheet(self.path, self.fw, self.fh)"),
    permissions={"spritesheet"},
)

SHEET_SET_ANIMATION = KixBlock(
    id="sheet.set_animation",
    name="Definir animação",
    category="spritesheet",
    color=CAT_SPRITESHEET,
    visual=BlockVisual(root=Group(children=[Text("Animação = "), BlockInput("name")])),
    inputs=[SocketDef("name", SocketKind.STRING, default="idle")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.set_animation(self.name)"),
    permissions={"spritesheet"},
)

SHEET_CURRENT = KixBlock(
    id="sheet.current",
    name="Animação atual",
    category="spritesheet",
    color=CAT_SPRITESHEET,
    visual=BlockVisual(root=Group(children=[Text("Animação atual")])),
    inputs=[],
    outputs=[SocketDef("name", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return self.current_animation"),
    permissions={"spritesheet"},
)

SHEET_NEXT_FRAME = KixBlock(
    id="sheet.next_frame",
    name="Próximo frame",
    category="spritesheet",
    color=CAT_SPRITESHEET,
    visual=BlockVisual(root=Group(children=[Text("Próximo frame")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.frame_index += 1"),
    permissions={"spritesheet"},
)

SHEET_PREV_FRAME = KixBlock(
    id="sheet.prev_frame",
    name="Frame anterior",
    category="spritesheet",
    color=CAT_SPRITESHEET,
    visual=BlockVisual(root=Group(children=[Text("Frame anterior")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.frame_index -= 1"),
    permissions={"spritesheet"},
)

SHEET_PAUSE = KixBlock(
    id="sheet.pause",
    name="Pausar animação",
    category="spritesheet",
    color=CAT_SPRITESHEET,
    visual=BlockVisual(root=Group(children=[Text("Pausar animação")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.animating = False"),
    permissions={"spritesheet"},
)

SHEET_RESUME = KixBlock(
    id="sheet.resume",
    name="Continuar animação",
    category="spritesheet",
    color=CAT_SPRITESHEET,
    visual=BlockVisual(root=Group(children=[Text("Continuar animação")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.animating = True"),
    permissions={"spritesheet"},
)

SHEET_LOOP = KixBlock(
    id="sheet.loop",
    name="Loop da animação",
    category="spritesheet",
    color=CAT_SPRITESHEET,
    visual=BlockVisual(root=Group(children=[Text("Loop: "), BlockInput("enabled")])),
    inputs=[SocketDef("enabled", SocketKind.BOOLEAN, default=True)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.loop_animation = bool(self.enabled)"),
    permissions={"spritesheet"},
)


# ============================================================ Layers (8)
LAYER_CREATE = KixBlock(
    id="layers.create",
    name="Criar layer",
    category="layers",
    color=CAT_LAYERS,
    visual=BlockVisual(root=Group(children=[Text("Criar layer "), BlockInput("name")])),
    inputs=[SocketDef("name", SocketKind.STRING, default="layer1")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="layers.create(self.name)"),
    permissions={"layers"},
)

LAYER_CURRENT = KixBlock(
    id="layers.current",
    name="Layer atual",
    category="layers",
    color=CAT_LAYERS,
    visual=BlockVisual(root=Group(children=[Text("Layer atual")])),
    inputs=[],
    outputs=[SocketDef("name", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return layers.current"),
    permissions={"layers"},
)

LAYER_SWITCH = KixBlock(
    id="layers.switch",
    name="Mudar para layer",
    category="layers",
    color=CAT_LAYERS,
    visual=BlockVisual(root=Group(children=[Text("Mudar para "), BlockInput("name")])),
    inputs=[SocketDef("name", SocketKind.STRING, default="layer1")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="layers.switch(self.name)"),
    permissions={"layers"},
)

LAYER_HIDE = KixBlock(
    id="layers.hide",
    name="Esconder layer",
    category="layers",
    color=CAT_LAYERS,
    visual=BlockVisual(root=Group(children=[Text("Esconder "), BlockInput("name")])),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="layers[self.name].visible = False"),
    permissions={"layers"},
)

LAYER_SHOW = KixBlock(
    id="layers.show",
    name="Mostrar layer",
    category="layers",
    color=CAT_LAYERS,
    visual=BlockVisual(root=Group(children=[Text("Mostrar "), BlockInput("name")])),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="layers[self.name].visible = True"),
    permissions={"layers"},
)

LAYER_SET_Z = KixBlock(
    id="layers.set_z",
    name="Definir ordem Z",
    category="layers",
    color=CAT_LAYERS,
    visual=BlockVisual(root=Group(children=[Text("Z-order de "), BlockInput("name"), Text(" = "), BlockInput("z")])),
    inputs=[SocketDef("name", SocketKind.STRING, default=""),
            SocketDef("z", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="layers[self.name].z = self.z"),
    permissions={"layers"},
)

LAYER_FORWARD = KixBlock(
    id="layers.forward",
    name="Mover para frente",
    category="layers",
    color=CAT_LAYERS,
    visual=BlockVisual(root=Group(children=[Text("Mover "), BlockInput("name"), Text(" para frente")])),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="layers[self.name].z += 1"),
    permissions={"layers"},
)

LAYER_BACKWARD = KixBlock(
    id="layers.backward",
    name="Mover para trás",
    category="layers",
    color=CAT_LAYERS,
    visual=BlockVisual(root=Group(children=[Text("Mover "), BlockInput("name"), Text(" para trás")])),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="layers[self.name].z -= 1"),
    permissions={"layers"},
)


WORLD = (TILEMAP_LOAD, TILEMAP_TILE_AT, TILEMAP_SET_TILE, TILEMAP_CLEAR,
         TILEMAP_FILL, TILEMAP_COLLIDES, TILEMAP_SAVE, TILEMAP_WIDTH,
         TILEMAP_HEIGHT, TILEMAP_OFFSET,
         SHEET_LOAD, SHEET_SET_ANIMATION, SHEET_CURRENT, SHEET_NEXT_FRAME,
         SHEET_PREV_FRAME, SHEET_PAUSE, SHEET_RESUME, SHEET_LOOP,
         LAYER_CREATE, LAYER_CURRENT, LAYER_SWITCH, LAYER_HIDE, LAYER_SHOW,
         LAYER_SET_Z, LAYER_FORWARD, LAYER_BACKWARD)

assert len(WORLD) == 26, f"esperado 26, obtido {len(WORLD)}"