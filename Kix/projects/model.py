"""Modelo de dados de um projeto Kix.

Estrutura mínima viável: scenes → objects → scripts → blocks. O conteúdo de
blocks custom vive na lista `blocks` (KixBlocks serializáveis). O runtime
de scenes/scripts/sprites vem em marcos futuros; aqui só garantimos a forma
e a serialização.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@dataclass
class ProjectSettings:
    width: int = 390
    height: int = 844
    orientation: str = "portrait"          # "portrait" | "landscape"

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "orientation": self.orientation,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectSettings":
        return cls(
            width=int(data.get("width", 390)),
            height=int(data.get("height", 844)),
            orientation=data.get("orientation", "portrait"),
        )


@dataclass
class KixScript:
    id: str = field(default_factory=lambda: _new_id("scr"))
    trigger: str = "on_start"              # "on_start" | "on_tap" | "on_message" | ...
    blocks: list[str] = field(default_factory=list)   # ids de KixBlock (custom) ou refs

    def to_dict(self) -> dict:
        return {"id": self.id, "trigger": self.trigger, "blocks": list(self.blocks)}

    @classmethod
    def from_dict(cls, data: dict) -> "KixScript":
        return cls(
            id=data.get("id") or _new_id("scr"),
            trigger=data.get("trigger", "on_start"),
            blocks=list(data.get("blocks", [])),
        )


@dataclass
class KixObject:
    id: str = field(default_factory=lambda: _new_id("obj"))
    name: str = "Ator"
    kind: str = "sprite"                   # "sprite" | "background" | "text"
    image: str | None = None               # path relativo a partir do .kix
    scripts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "image": self.image,
            "scripts": list(self.scripts),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KixObject":
        return cls(
            id=data.get("id") or _new_id("obj"),
            name=data.get("name", "Ator"),
            kind=data.get("kind", "sprite"),
            image=data.get("image"),
            scripts=list(data.get("scripts", [])),
        )


@dataclass
class KixScene:
    id: str = field(default_factory=lambda: _new_id("scn"))
    name: str = "Cena"
    background: str = "#FFFFFF"
    objects: list[str] = field(default_factory=list)   # ids de KixObject

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "background": self.background,
            "objects": list(self.objects),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KixScene":
        return cls(
            id=data.get("id") or _new_id("scn"),
            name=data.get("name", "Cena"),
            background=data.get("background", "#FFFFFF"),
            objects=list(data.get("objects", [])),
        )


@dataclass
class KixProject:
    name: str = "Sem nome"
    description: str = ""
    created_at: str = field(default_factory=_now_iso)
    modified_at: str = field(default_factory=_now_iso)
    scenes: list[KixScene] = field(default_factory=list)
    objects: list[KixObject] = field(default_factory=list)
    scripts: list[KixScript] = field(default_factory=list)
    blocks: list[Any] = field(default_factory=list)         # KixBlock serializados via .to_dict()
    settings: ProjectSettings = field(default_factory=ProjectSettings)
    # Estado persistido do sprite ativo (posição, rotação, etc.) entre execuções.
    # None = estado inicial (centro, rotação 0). Sobrescrito ao final de cada run.
    state: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        self.modified_at = _now_iso()

    def to_dict(self) -> dict:
        from Kix.projects.serializer import KIX_FORMAT, KIX_VERSION

        return {
            "format": KIX_FORMAT,
            "version": KIX_VERSION,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "scenes": [s.to_dict() for s in self.scenes],
            "objects": [o.to_dict() for o in self.objects],
            "scripts": [s.to_dict() for s in self.scripts],
            "blocks": [b if isinstance(b, dict) else b.to_dict() for b in self.blocks],
            "settings": self.settings.to_dict(),
            "state": dict(self.state),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KixProject":
        return cls(
            name=data.get("name", "Sem nome"),
            description=data.get("description", ""),
            created_at=data.get("created_at") or _now_iso(),
            modified_at=data.get("modified_at") or _now_iso(),
            scenes=[KixScene.from_dict(s) for s in data.get("scenes", [])],
            objects=[KixObject.from_dict(o) for o in data.get("objects", [])],
            scripts=[KixScript.from_dict(s) for s in data.get("scripts", [])],
            blocks=list(data.get("blocks", [])),  # ficam como dicts — caller decide se reconstrói
            settings=ProjectSettings.from_dict(data.get("settings", {})),
            state=dict(data.get("state") or {}),
        )