"""Modelo universal de bloco: KixBlock.

Um único dataclass serve para qualquer bloco — o que diferencia blocos
é a combinação de `visual` + `inputs` + `outputs` + `behavior` + `permissions`.
A spec é explícita: NÃO criar uma classe por bloco.
"""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from typing import Any

from Kix.block_engine.visual import BlockVisual


class SocketKind(enum.Enum):
    """Tipos que um socket (entrada/saída) pode aceitar."""

    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    VARIABLE = "variable"           # aceita getter de variável
    OBJECT = "object"               # referência a objeto do projeto
    SPRITE = "sprite"
    SCENE = "scene"
    SOUND = "sound"
    FILE = "file"
    COLOR = "color"
    ANGLE = "angle"
    POSITION = "position"
    BLOCK = "block"                 # socket que aceita outro bloco (aninhamento)


@dataclass
class SocketDef:
    """Definição de um socket (entrada ou saída) de um bloco."""

    name: str
    kind: SocketKind
    default: Any = None
    label: str | None = None        # rótulo exibido; padrão = name


@dataclass
class KixBlock:
    """Bloco universal do Kix.

    Toda definição de bloco — builtin, custom ou importado — é uma instância
    desta classe. Blocos não se instanciam em runtime; `KixBlock` é o
    *molde* (template) que o editor usa para criar instâncias conectáveis.
    """

    id: str
    name: str
    category: str
    color: tuple[float, float, float, float]
    visual: BlockVisual
    inputs: list[SocketDef] = field(default_factory=list)
    outputs: list[SocketDef] = field(default_factory=list)
    behavior: "BlockBehavior | None" = None
    permissions: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = f"anon.{uuid.uuid4().hex[:8]}"
        # validações leves — falha cedo em vez de na renderização
        unknown = {s.name for s in self.inputs + self.outputs if not isinstance(s.kind, SocketKind)}
        if unknown:
            raise ValueError(f"KixBlock {self.id!r}: sockets com kind inválido: {unknown}")

    # --- serialização (round-trip JSON) -----------------------------------
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "color": list(self.color),
            "visual": self.visual.to_dict(),
            "inputs": [{"name": s.name, "kind": s.kind.value, "default": s.default, "label": s.label}
                       for s in self.inputs],
            "outputs": [{"name": s.name, "kind": s.kind.value, "default": s.default, "label": s.label}
                        for s in self.outputs],
            "behavior": self.behavior.to_dict() if self.behavior else None,
            "permissions": sorted(self.permissions),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KixBlock":
        from Kix.block_engine.visual import BlockVisual as _BV
        from Kix.block_engine.behavior import BlockBehavior

        behavior_data = data.get("behavior")
        behavior = BlockBehavior.from_dict(behavior_data) if behavior_data else None

        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            color=tuple(data["color"]),
            visual=_BV.from_dict(data["visual"]),
            inputs=[SocketDef(name=s["name"], kind=SocketKind(s["kind"]),
                              default=s.get("default"), label=s.get("label"))
                    for s in data.get("inputs", [])],
            outputs=[SocketDef(name=s["name"], kind=SocketKind(s["kind"]),
                               default=s.get("default"), label=s.get("label"))
                     for s in data.get("outputs", [])],
            behavior=behavior,
            permissions=set(data.get("permissions", [])),
        )