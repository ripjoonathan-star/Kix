"""Blocos da categoria Shaders — efeitos visuais via shader (M8).

Cada bloco aplica um efeito de pós-processamento (full-screen quad) ao
palco inteiro ou ao sprite alvo. Efeitos implementados como GLSL no
backend; aqui só definimos a API/block-level.

Cor da categoria: ``CAT_SHADERS`` (placeholder atual — categoria com
identidade visual forte para destacar que é "avançado/efeito").
"""

from __future__ import annotations

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
from Kix.core.theme import CAT_SHADERS


SHADER_BLUR_SOFT = KixBlock(
    id="shader.blur_soft",
    name="Blur suave",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Blur suave intensidade "), BlockInput("amount")])),
    inputs=[SocketDef("amount", SocketKind.NUMBER, default=0.5)],
    outputs=[],
    behavior=BlockBehavior("python", "shaders.apply('blur', amount=float(self.amount))"),
    permissions={"stage"},
)

SHADER_BLUR_STRONG = KixBlock(
    id="shader.blur_strong",
    name="Blur forte",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Blur forte intensidade "), BlockInput("amount")])),
    inputs=[SocketDef("amount", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior("python", "shaders.apply('blur_strong', amount=float(self.amount))"),
    permissions={"stage"},
)

SHADER_PIXELATE = KixBlock(
    id="shader.post.pixelate",
    name="Pixelizar",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Pixelizar bloco "), BlockInput("size")])),
    inputs=[SocketDef("size", SocketKind.NUMBER, default=8)],
    outputs=[],
    behavior=BlockBehavior("python", "shaders.apply('pixelate', size=int(self.size))"),
    permissions={"stage"},
)

SHADER_SEPIA = KixBlock(
    id="shader.post.sepia",
    name="Sépia",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Sépia intensidade "), BlockInput("amount")])),
    inputs=[SocketDef("amount", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior("python", "shaders.apply('sepia', amount=float(self.amount))"),
    permissions={"stage"},
)

SHADER_GRAYSCALE = KixBlock(
    id="shader.post.grayscale",
    name="Escala de cinza",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Escala de cinza")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "shaders.apply('grayscale')"),
    permissions={"stage"},
)

SHADER_INVERT = KixBlock(
    id="shader.invert",
    name="Inverter cores",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Inverter cores")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "shaders.apply('invert')"),
    permissions={"stage"},
)

SHADER_NEON_EDGE = KixBlock(
    id="shader.neon_edge",
    name="Borda neon",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[
        Text("Borda neon cor "), BlockInput("color"),
        Text(" largura "), BlockInput("width"),
    ])),
    inputs=[SocketDef("color", SocketKind.COLOR, default=(0.063, 0.725, 0.506, 1)),
            SocketDef("width", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior("python",
        "shaders.apply('neon_edge', color=tuple(self.color), width=float(self.width))"),
    permissions={"stage"},
)

SHADER_BLOOM = KixBlock(
    id="shader.bloom",
    name="Brilho extra",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Brilho (bloom) intensidade "), BlockInput("amount")])),
    inputs=[SocketDef("amount", SocketKind.NUMBER, default=1.5)],
    outputs=[],
    behavior=BlockBehavior("python", "shaders.apply('bloom', amount=float(self.amount))"),
    permissions={"stage"},
)

SHADER_WAVE = KixBlock(
    id="shader.wave",
    name="Ondulação",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[
        Text("Ondulação amplitude "), BlockInput("amp"),
        Text(" freq "), BlockInput("freq"),
    ])),
    inputs=[SocketDef("amp", SocketKind.NUMBER, default=10),
            SocketDef("freq", SocketKind.NUMBER, default=20)],
    outputs=[],
    behavior=BlockBehavior("python",
        "shaders.apply('wave', amp=float(self.amp), freq=float(self.freq))"),
    permissions={"stage"},
)

SHADER_CHROMA = KixBlock(
    id="shader.chroma",
    name="Chroma (aberração RGB)",
    category="shaders",
    color=CAT_SHADERS,
    visual=BlockVisual(root=Group(children=[Text("Chroma aberração RGB "), BlockInput("offset")])),
    inputs=[SocketDef("offset", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior("python", "shaders.apply('chroma', offset=float(self.offset))"),
    permissions={"stage"},
)


SHADER_BLOCKS = (SHADER_BLUR_SOFT, SHADER_BLUR_STRONG, SHADER_PIXELATE,
                 SHADER_SEPIA, SHADER_GRAYSCALE, SHADER_INVERT,
                 SHADER_NEON_EDGE, SHADER_BLOOM, SHADER_WAVE, SHADER_CHROMA)

assert len(SHADER_BLOCKS) == 10, f"esperado 10, obtido {len(SHADER_BLOCKS)}"
