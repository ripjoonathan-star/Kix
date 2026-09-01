"""Blocos de gerenciamento de layers.

Layers agrupam objetos na cena com:
- name (identificador)
- category: ui | background | player | enemy | other
- z_index (ordem de renderização)
- visible (esconde/exibe)
- collidable (filtra colisão)
- shader (efeito visual)

18 blocos: criar, mover, reordenar, visibilidade, colisão, shader,
contagem, swap, etc.
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
from Kix.core.theme import CAT_LAYERS


# Helper para construir visual rapidamente
def _g(*children):
    return Group(children=list(children))


# 1. Criar layer
LAYER_CREATE = KixBlock(
    id="layer.create", name="Criar layer", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Criar layer "), BlockInput("name"),
        Text(" do tipo "), BlockInput("category"),
    )),
    inputs=[
        SocketDef("name", SocketKind.STRING, default="Layer 1"),
        SocketDef("category", SocketKind.STRING, default="other"),
    ],
    outputs=[],
    behavior=BlockBehavior("python", "layers.create(self.name, self.category)"),
)

# 2. Remover layer
LAYER_REMOVE = KixBlock(
    id="layer.remove", name="Remover layer", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(Text("Remover layer "), BlockInput("name"))),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "layers.remove(self.name)"),
)

# 3. Layer acima de outra (reordenar)
LAYER_ABOVE = KixBlock(
    id="layer.above", name="Layer acima de", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Layer "), BlockInput("a"),
        Text(" acima de "), BlockInput("b"),
    )),
    inputs=[
        SocketDef("a", SocketKind.STRING, default=""),
        SocketDef("b", SocketKind.STRING, default=""),
    ],
    outputs=[],
    behavior=BlockBehavior("python", "layers.above(self.a, self.b)"),
)

# 4. Trocar duas layers (swap)
LAYER_SWAP = KixBlock(
    id="layer.swap", name="Trocar layers", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Trocar layers "), BlockInput("a"), Text(" e "), BlockInput("b"),
    )),
    inputs=[
        SocketDef("a", SocketKind.STRING, default=""),
        SocketDef("b", SocketKind.STRING, default=""),
    ],
    outputs=[],
    behavior=BlockBehavior("python", "layers.swap(self.a, self.b)"),
)

# 5. Definir z_index explícito
LAYER_SET_Z = KixBlock(
    id="layer.set_z", name="Definir ordem", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Ordem da layer "), BlockInput("name"),
        Text(" = "), BlockInput("z"),
    )),
    inputs=[
        SocketDef("name", SocketKind.STRING, default=""),
        SocketDef("z", SocketKind.NUMBER, default=0),
    ],
    outputs=[],
    behavior=BlockBehavior("python", "layers.set_z(self.name, self.z)"),
)

# 6. Mostrar layer
LAYER_SHOW = KixBlock(
    id="layer.show", name="Mostrar layer", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(Text("Mostrar layer "), BlockInput("name"))),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "layers.show(self.name)"),
)

# 7. Esconder layer
LAYER_HIDE = KixBlock(
    id="layer.hide", name="Esconder layer", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(Text("Esconder layer "), BlockInput("name"))),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "layers.hide(self.name)"),
)

# 8. Layer visível? (reporter boolean)
LAYER_IS_VISIBLE = KixBlock(
    id="layer.is_visible", name="Layer visível?", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(Text("Layer "), BlockInput("name"), Text(" visível?"))),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[SocketDef("visible", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return layers.is_visible(self.name)"),
)

# 9. Permitir colisão com layer
LAYER_COLLISION_ON = KixBlock(
    id="layer.collision_on", name="Permitir colisão", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Permitir colisão com "), BlockInput("name"),
    )),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "layers.set_collidable(self.name, True)"),
)

# 10. Bloquear colisão com layer
LAYER_COLLISION_OFF = KixBlock(
    id="layer.collision_off", name="Bloquear colisão", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Bloquear colisão com "), BlockInput("name"),
    )),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "layers.set_collidable(self.name, False)"),
)

# 11. Layer permite colisão? (reporter)
LAYER_IS_COLLIDABLE = KixBlock(
    id="layer.is_collidable", name="Layer permite colisão?",
    category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Layer "), BlockInput("name"), Text(" permite colisão?"),
    )),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[SocketDef("collidable", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return layers.is_collidable(self.name)"),
)

# 12. Aplicar shader a todas as layers exceto [N]
LAYER_SHADER_EXCEPT = KixBlock(
    id="layer.shader_except", name="Aplicar shader exceto",
    category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Aplicar shader "), BlockInput("shader"),
        Text(" em todas layers exceto "), BlockInput("except_name"),
    )),
    inputs=[
        SocketDef("shader", SocketKind.STRING, default="grayscale"),
        SocketDef("except_name", SocketKind.STRING, default=""),
    ],
    outputs=[],
    behavior=BlockBehavior("python", "layers.apply_shader_except(self.shader, self.except_name)"),
)

# 13. Aplicar shader a uma layer
LAYER_APPLY_SHADER = KixBlock(
    id="layer.apply_shader", name="Aplicar shader", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Aplicar shader "), BlockInput("shader"),
        Text(" à layer "), BlockInput("name"),
    )),
    inputs=[
        SocketDef("shader", SocketKind.STRING, default=""),
        SocketDef("name", SocketKind.STRING, default=""),
    ],
    outputs=[],
    behavior=BlockBehavior("python", "layers.set_shader(self.name, self.shader)"),
)

# 14. Remover shader da layer
LAYER_CLEAR_SHADER = KixBlock(
    id="layer.clear_shader", name="Remover shader", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(Text("Remover shader de "), BlockInput("name"))),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "layers.clear_shader(self.name)"),
)

# 16. Mover objeto para layer
LAYER_MOVE_OBJECT = KixBlock(
    id="layer.move_object", name="Mover objeto para layer",
    category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Mover objeto "), BlockInput("obj"),
        Text(" para layer "), BlockInput("name"),
    )),
    inputs=[
        SocketDef("obj", SocketKind.STRING, default=""),
        SocketDef("name", SocketKind.STRING, default=""),
    ],
    outputs=[],
    behavior=BlockBehavior("python", "layers.add_object(self.name, self.obj)"),
)

# 17. Contagem de objetos na layer
LAYER_OBJECT_COUNT = KixBlock(
    id="layer.object_count", name="Objetos na layer",
    category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(Text("Objetos na layer "), BlockInput("name"))),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[SocketDef("count", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return layers.object_count(self.name)"),
)

# 18. Layer contém object?
LAYER_CONTAINS = KixBlock(
    id="layer.contains", name="Layer contém?", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Layer "), BlockInput("name"),
        Text(" contém "), BlockInput("obj"), Text("?"),
    )),
    inputs=[
        SocketDef("name", SocketKind.STRING, default=""),
        SocketDef("obj", SocketKind.STRING, default=""),
    ],
    outputs=[SocketDef("contains", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return layers.contains_object(self.name, self.obj)"),
)

# 19. Limpar layer (remove todos os objetos)
LAYER_CLEAR = KixBlock(
    id="layer.clear", name="Limpar layer", category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(Text("Limpar layer "), BlockInput("name"))),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "layers.clear(self.name)"),
)

# 20. Mudar categoria da layer
LAYER_SET_CATEGORY = KixBlock(
    id="layer.set_category", name="Mudar tipo da layer",
    category="layers", color=CAT_LAYERS,
    visual=BlockVisual(root=_g(
        Text("Mudar tipo da layer "), BlockInput("name"),
        Text(" para "), BlockInput("category"),
    )),
    inputs=[
        SocketDef("name", SocketKind.STRING, default=""),
        SocketDef("category", SocketKind.STRING, default="other"),
    ],
    outputs=[],
    behavior=BlockBehavior("python", "layers.set_category(self.name, self.category)"),
)


LAYERS = (
    LAYER_CREATE, LAYER_REMOVE, LAYER_ABOVE, LAYER_SWAP, LAYER_SET_Z,
    LAYER_SHOW, LAYER_HIDE, LAYER_IS_VISIBLE,
    LAYER_COLLISION_ON, LAYER_COLLISION_OFF, LAYER_IS_COLLIDABLE,
    LAYER_SHADER_EXCEPT, LAYER_APPLY_SHADER, LAYER_CLEAR_SHADER,
    LAYER_MOVE_OBJECT, LAYER_OBJECT_COUNT, LAYER_CONTAINS,
    LAYER_CLEAR, LAYER_SET_CATEGORY,
)

assert len(LAYERS) >= 18, f"esperado ≥18 layer blocks, obtido {len(LAYERS)}"


__all__ = ["LAYERS"]