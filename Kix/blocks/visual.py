"""Blocos visuais: looks + shaders + pen.

Looks cobre transformação visual do sprite (tamanho, opacidade, camadas).
Shaders cobrem efeitos em tempo real (blur, glow, pixelate).
Pen cobre desenho procedural (catroid-style).
"""

from Kix.block_engine import (
    BlockInput,
    BlockVisual,
    Color,
    Group,
    KixBlock,
    SocketDef,
    SocketKind,
    Text,
)
from Kix.block_engine.behavior import BlockBehavior
from Kix.core.theme import CAT_LOOKS, CAT_PEN, CAT_SHADERS


# ============================================================ Looks (10)
SAY = KixBlock(
    id="looks.say",
    name="Dizer",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Dizer "), BlockInput("message"), Text(" por "), BlockInput("duration"), Text(" s")])),
    inputs=[SocketDef("message", SocketKind.STRING, default="Olá!"),
            SocketDef("duration", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await self.show_speech(self.message, self.duration)"),
    permissions={"looks"},
)

THINK = KixBlock(
    id="looks.think",
    name="Pensar",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Pensar "), BlockInput("message"), Text(" por "), BlockInput("duration"), Text(" s")])),
    inputs=[SocketDef("message", SocketKind.STRING, default="Hmm..."),
            SocketDef("duration", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await self.show_thought(self.message, self.duration)"),
    permissions={"looks"},
)

SHOW = KixBlock(
    id="looks.show",
    name="Mostrar",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Mostrar")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.visible = True"),
    permissions={"looks"},
)

HIDE = KixBlock(
    id="looks.hide",
    name="Esconder",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Esconder")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.visible = False"),
    permissions={"looks"},
)

SET_SIZE = KixBlock(
    id="looks.set_size",
    name="Definir tamanho",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Tamanho = "), BlockInput("size"), Text(" %")])),
    inputs=[SocketDef("size", SocketKind.NUMBER, default=100)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.scale = self.size / 100"),
    permissions={"looks"},
)

CHANGE_SIZE = KixBlock(
    id="looks.change_size",
    name="Mudar tamanho",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Mudar tamanho por "), BlockInput("delta"), Text(" %")])),
    inputs=[SocketDef("delta", SocketKind.NUMBER, default=10)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.scale += self.delta / 100"),
    permissions={"looks"},
)

SET_TINT = KixBlock(
    id="looks.set_tint",
    name="Definir cor (tint)",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Tingir com "), BlockInput("color")])),
    inputs=[SocketDef("color", SocketKind.COLOR, default=(1, 1, 1, 1))],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.tint = self.color"),
    permissions={"looks"},
)

SET_OPACITY = KixBlock(
    id="looks.set_opacity",
    name="Definir transparência",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Opacidade = "), BlockInput("opacity"), Text(" %")])),
    inputs=[SocketDef("opacity", SocketKind.NUMBER, default=100)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.opacity = self.opacity_pct / 100"),
    permissions={"looks"},
)

GO_TO_FRONT = KixBlock(
    id="looks.go_to_front",
    name="Enviar para frente",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Enviar para frente")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.layer = max_depth()"),
    permissions={"looks"},
)

GO_TO_BACK = KixBlock(
    id="looks.go_to_back",
    name="Enviar para trás",
    category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("Enviar para trás")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.layer = 0"),
    permissions={"looks"},
)


# ============================================================ Shaders (8)
SHADER_BLUR = KixBlock(
    id="shader.blur",
    name="Aplicar blur",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Aplicar blur intensidade "), BlockInput("intensity")])),
    inputs=[SocketDef("intensity", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.shader = Blur(self.intensity)"),
    permissions={"shaders"},
)

SHADER_GLOW = KixBlock(
    id="shader.glow",
    name="Aplicar glow",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Aplicar glow cor "), BlockInput("color"), Text(" raio "), BlockInput("radius")])),
    inputs=[SocketDef("color", SocketKind.COLOR, default=(1, 0.9, 0.4, 1)),
            SocketDef("radius", SocketKind.NUMBER, default=8.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.shader = Glow(self.color, self.radius)"),
    permissions={"shaders"},
)

SHADER_PIXELATE = KixBlock(
    id="shader.pixelate",
    name="Aplicar pixelate",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Pixelar (tamanho "), BlockInput("size"), Text(")")])),
    inputs=[SocketDef("size", SocketKind.NUMBER, default=4.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.shader = Pixelate(self.size)"),
    permissions={"shaders"},
)

SHADER_SEPIA = KixBlock(
    id="shader.sepia",
    name="Aplicar sépia",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Aplicar sépia")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.shader = Sepia()"),
    permissions={"shaders"},
)

SHADER_GRAYSCALE = KixBlock(
    id="shader.grayscale",
    name="Aplicar escala de cinza",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Aplicar escala de cinza")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.shader = Grayscale()"),
    permissions={"shaders"},
)

SHADER_SHARPEN = KixBlock(
    id="shader.sharpen",
    name="Aumentar nitidez",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Nitidez: "), BlockInput("amount")])),
    inputs=[SocketDef("amount", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.shader = Sharpen(self.amount)"),
    permissions={"shaders"},
)

SHADER_VIGNETTE = KixBlock(
    id="shader.vignette",
    name="Aplicar vinheta",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Vinheta intensidade "), BlockInput("amount")])),
    inputs=[SocketDef("amount", SocketKind.NUMBER, default=0.5)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.shader = Vignette(self.amount)"),
    permissions={"shaders"},
)

SHADER_RESET = KixBlock(
    id="shader.reset",
    name="Resetar shader",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Remover shader")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.shader = None"),
    permissions={"shaders"},
)


# ============================================================ Pen (8)
PEN_DOWN = KixBlock(
    id="pen.down",
    name="Baixar caneta",
    category="pen",
    color=CAT_PEN,
    visual=BlockVisual(root=Group(children=[Text("Baixar caneta")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="pen.down()"),
    permissions={"canvas"},
)

PEN_UP = KixBlock(
    id="pen.up",
    name="Subir caneta",
    category="pen",
    color=CAT_PEN,
    visual=BlockVisual(root=Group(children=[Text("Subir caneta")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="pen.up()"),
    permissions={"canvas"},
)

PEN_COLOR = KixBlock(
    id="pen.color",
    name="Cor da caneta",
    category="pen",
    color=CAT_PEN,
    visual=BlockVisual(root=Group(children=[Text("Cor da caneta: "), BlockInput("color")])),
    inputs=[SocketDef("color", SocketKind.COLOR, default=(1, 1, 1, 1))],
    outputs=[],
    behavior=BlockBehavior(language="python", source="pen.color = self.color"),
    permissions={"canvas"},
)

PEN_SIZE = KixBlock(
    id="pen.size",
    name="Espessura da caneta",
    category="pen",
    color=CAT_PEN,
    visual=BlockVisual(root=Group(children=[Text("Espessura = "), BlockInput("size")])),
    inputs=[SocketDef("size", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="pen.size = self.size"),
    permissions={"canvas"},
)

PEN_OPACITY = KixBlock(
    id="pen.opacity",
    name="Transparência da caneta",
    category="pen",
    color=CAT_PEN,
    visual=BlockVisual(root=Group(children=[Text("Opacidade da caneta = "), BlockInput("opacity"), Text(" %")])),
    inputs=[SocketDef("opacity", SocketKind.NUMBER, default=100)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="pen.opacity = self.opacity / 100"),
    permissions={"canvas"},
)

PEN_STAMP = KixBlock(
    id="pen.stamp",
    name="Carimbar",
    category="pen",
    color=CAT_PEN,
    visual=BlockVisual(root=Group(children=[Text("Carimbar")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="pen.stamp()"),
    permissions={"canvas"},
)

PEN_CLEAR = KixBlock(
    id="pen.clear",
    name="Limpar tudo",
    category="pen",
    color=CAT_PEN,
    visual=BlockVisual(root=Group(children=[Text("Limpar tudo")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="pen.clear()"),
    permissions={"canvas"},
)

PEN_CHANGE_COLOR = KixBlock(
    id="pen.change_color",
    name="Mudar cor da caneta",
    category="pen",
    color=CAT_PEN,
    visual=BlockVisual(root=Group(children=[Text("Mudar cor por "), BlockInput("delta")])),
    inputs=[SocketDef("delta", SocketKind.NUMBER, default=10)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="pen.hue = (pen.hue + self.delta) % 360"),
    permissions={"canvas"},
)


# --- M3.3: property reporters do objeto (10) -----------------------------
OBJECT_NAME = KixBlock(
    id="looks.object_name", name="nome_do_objeto", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("nome do objeto")])),
    inputs=[], outputs=[SocketDef("name", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return self.name"),
    permissions={"transform"},
)
OBJECT_ROTATION = KixBlock(
    id="looks.object_rotation", name="direção", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("direção")])),
    inputs=[], outputs=[SocketDef("rotation", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.rotation"),
    permissions={"transform"},
)
OBJECT_OPACITY = KixBlock(
    id="looks.object_opacity", name="transparência", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("transparência")])),
    inputs=[], outputs=[SocketDef("opacity", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.opacity"),
    permissions={"transform"},
)
OBJECT_BRIGHTNESS = KixBlock(
    id="looks.object_brightness", name="brilho", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("brilho")])),
    inputs=[], outputs=[SocketDef("brightness", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.brightness"),
    permissions={"transform"},
)
OBJECT_TINT = KixBlock(
    id="looks.object_tint", name="cor", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("cor")])),
    inputs=[], outputs=[SocketDef("tint", SocketKind.COLOR)],
    behavior=BlockBehavior("python", "return self.tint"),
    permissions={"transform"},
)
LOOK_INDEX = KixBlock(
    id="looks.look_index", name="número da aparência", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("número da aparência")])),
    inputs=[], outputs=[SocketDef("index", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.frame_index"),
    permissions={"transform"},
)
LOOK_NAME = KixBlock(
    id="looks.look_name", name="nome da aparência", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("nome da aparência")])),
    inputs=[], outputs=[SocketDef("name", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return self.current_animation"),
    permissions={"transform"},
)
LOOK_WIDTH = KixBlock(
    id="looks.look_width", name="largura da aparência", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("largura da aparência")])),
    inputs=[], outputs=[SocketDef("width", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.fw"),
    permissions={"transform"},
)
LOOK_HEIGHT = KixBlock(
    id="looks.look_height", name="altura da aparência", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("altura da aparência")])),
    inputs=[], outputs=[SocketDef("height", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.fh"),
    permissions={"transform"},
)
LOOK_COUNT = KixBlock(
    id="looks.look_count", name="número de aparências", category="looks",
    color=CAT_LOOKS,
    visual=BlockVisual(root=Group(children=[Text("número de aparências")])),
    inputs=[], outputs=[SocketDef("count", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return self.count"),
    permissions={"transform"},
)

VISUAL = (SAY, THINK, SHOW, HIDE, SET_SIZE, CHANGE_SIZE, SET_TINT, SET_OPACITY,
          GO_TO_FRONT, GO_TO_BACK,
          SHADER_BLUR, SHADER_GLOW, SHADER_PIXELATE, SHADER_SEPIA,
          SHADER_GRAYSCALE, SHADER_SHARPEN, SHADER_VIGNETTE, SHADER_RESET,
          PEN_DOWN, PEN_UP, PEN_COLOR, PEN_SIZE, PEN_OPACITY, PEN_STAMP,
          PEN_CLEAR, PEN_CHANGE_COLOR,
          OBJECT_NAME, OBJECT_ROTATION, OBJECT_OPACITY, OBJECT_BRIGHTNESS,
          OBJECT_TINT, LOOK_INDEX, LOOK_NAME, LOOK_WIDTH, LOOK_HEIGHT,
          LOOK_COUNT)

assert len(VISUAL) == 36, f"esperado 36, obtido {len(VISUAL)}"