"""Modelo visual de bloco: árvore de componentes.

A árvore é construída a partir de nós (dataclasses) que descrevem como o
bloco aparece na tela. A renderização real fica para o Visual Block Editor
(marco futuro). Aqui definimos só o modelo declarativo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# --- Nós terminais (sem filhos) --------------------------------------------
@dataclass
class Text:
    value: str


@dataclass
class Number:
    value: float = 0
    min: float | None = None
    max: float | None = None


@dataclass
class EditableText:
    value: str = ""
    placeholder: str = ""


@dataclass
class Boolean:
    value: bool = False


@dataclass
class Variable:
    name: str = ""
    kind: str = "any"               # "number" | "string" | "boolean" | "any"


@dataclass
class Dropdown:
    options: list[str] = field(default_factory=list)
    selected: str = ""


@dataclass
class Color:
    value: tuple[float, float, float, float] = (1, 1, 1, 1)


@dataclass
class BlockInput:
    """Marcador de socket — desenhado pelo renderer do bloco."""

    socket: str                     # nome do SocketDef correspondente


@dataclass
class Icon:
    name: str                       # ex.: "play", "pause", "pencil"
    size: int = 16


@dataclass
class Separator:
    vertical: bool = False


@dataclass
class Space:
    size: int = 8


@dataclass
class Slider:
    min: float = 0
    max: float = 100
    value: float = 0


@dataclass
class Angle:
    value: float = 0


@dataclass
class Position:
    x: float = 0
    y: float = 0


# --- Referências tipadas a entidades do projeto -----------------------------
@dataclass
class ObjectRef:
    object_id: str = ""


@dataclass
class SpriteRef:
    sprite_id: str = ""


@dataclass
class SceneRef:
    scene_id: str = ""


@dataclass
class SoundRef:
    sound_id: str = ""


@dataclass
class FileRef:
    path: str = ""


# --- Nó composto ----------------------------------------------------------
@dataclass
class Group:
    """Agrupa filhos em uma seção colapsável ou linha."""

    children: list[Any] = field(default_factory=list)
    label: str | None = None
    collapsible: bool = False
    collapsed: bool = False


# --- Raiz do visual -------------------------------------------------------
@dataclass
class BlockVisual:
    root: Any                       # um dos nós acima (tipicamente Group)


def _visual_to_dict(node: Any) -> dict:
    if isinstance(node, list):
        return {"kind": "list", "items": [_visual_to_dict(n) for n in node]}
    if node is None:
        return {"kind": "none"}
    d = {}
    for f in node.__dataclass_fields__:
        v = getattr(node, f)
        if isinstance(v, (str, int, float, bool)) or v is None:
            d[f] = v
        elif isinstance(v, tuple):
            d[f] = list(v)
        elif isinstance(v, list):
            d[f] = [_visual_to_dict(x) if hasattr(x, "__dataclass_fields__") else x
                    for x in v]
        elif hasattr(v, "__dataclass_fields__"):
            d[f] = _visual_to_dict(v)
        else:
            d[f] = v
    # discriminador por último para sobrescrever campos com mesmo nome (ex.: Variable.kind)
    d["kind"] = node.__class__.__name__
    return d


def _visual_from_dict(data: dict) -> Any:
    from Kix.block_engine import visual as _v

    kind = data.get("kind")
    if kind == "none":
        return None
    if kind == "list":
        return [_visual_from_dict(x) for x in data.get("items", [])]
    cls = getattr(_v, kind, None)
    if cls is None or not hasattr(cls, "__dataclass_fields__"):
        raise ValueError(f"Nó visual desconhecido: {kind!r}")
    kwargs = {f: data[f] for f in cls.__dataclass_fields__ if f in data}
    # reconstrói listas aninhadas como nós
    for f in cls.__dataclass_fields__:
        if f in kwargs and isinstance(kwargs[f], dict) and kwargs[f].get("kind") in _v.__dict__:
            kwargs[f] = _visual_from_dict(kwargs[f])
        if f in kwargs and isinstance(kwargs[f], list):
            kwargs[f] = [_visual_from_dict(x) if isinstance(x, dict) and "kind" in x else x
                         for x in kwargs[f]]
    return cls(**kwargs)


# Anexa to_dict/from_dict na classe BlockVisual usando os helpers
BlockVisual.to_dict = lambda self: _visual_to_dict(self.root)            # type: ignore[attr-defined]
BlockVisual.from_dict = staticmethod(lambda data: BlockVisual(root=_visual_from_dict(data)))  # type: ignore[attr-defined]