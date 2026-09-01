"""Backpack (Mochila) — stash de blocos para arrastar entre projetos.

Inspirado em Pocket Code: a Mochila persiste blocos customizados para
reuso entre projetos. Armazenamento em arquivo JSON no user data dir.

API:
    Backpack.add(block_dict)      → adiciona um bloco
    Backpack.list()               → lista blocos (dicts serializados)
    Backpack.remove(block_id)     → remove por id
    Backpack.export_to_project(name)  → injeta no projeto alvo
    Backpack.import_from_project(name, block_ids)  → puxa blocos

Implementação M7: estrutura + persistência. Drag-and-drop real fica para
M8 (Kivy DragBehavior).
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class BackpackBlock:
    """Snapshot de um bloco para a mochila."""

    id: str                              # id único na mochila
    block: dict[str, Any]                # dict serializado do bloco
    origin: str = ""                     # projeto de origem
    added_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "block": self.block,
            "origin": self.origin,
            "added_at": self.added_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BackpackBlock":
        return cls(
            id=data.get("id") or f"bp_{uuid.uuid4().hex[:8]}",
            block=dict(data.get("block", {})),
            origin=str(data.get("origin", "")),
            added_at=data.get("added_at") or _now_iso(),
        )


class Backpack:
    """Mochila persistente de blocos (JSON no user data dir)."""

    def __init__(self, base_dir: Path | None = None):
        if base_dir is None:
            try:
                from Kix.core.paths import user_data_dir
                self.base_dir = Path(user_data_dir()) / "backpack.json"
            except Exception:
                self.base_dir = Path.home() / ".kix" / "backpack.json"
        else:
            self.base_dir = Path(base_dir)
        self._items: list[BackpackBlock] = []
        self._load()

    # --- persistência ----------------------------------------------------
    def _load(self) -> None:
        if not self.base_dir.exists():
            self._items = []
            return
        try:
            data = json.loads(self.base_dir.read_text(encoding="utf-8"))
            self._items = [BackpackBlock.from_dict(d) for d in data.get("items", [])]
        except (OSError, json.JSONDecodeError):
            self._items = []

    def _save(self) -> None:
        payload = {"version": 1, "items": [b.to_dict() for b in self._items]}
        self.base_dir.parent.mkdir(parents=True, exist_ok=True)
        self.base_dir.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- API ------------------------------------------------------------
    def add(self, block_dict: dict, origin: str = "") -> BackpackBlock:
        entry = BackpackBlock(
            id=f"bp_{uuid.uuid4().hex[:8]}",
            block=dict(block_dict),
            origin=origin,
        )
        self._items.append(entry)
        self._save()
        return entry

    def list(self) -> list[BackpackBlock]:
        return list(self._items)

    def get(self, block_id: str) -> BackpackBlock | None:
        for b in self._items:
            if b.id == block_id:
                return b
        return None

    def remove(self, block_id: str) -> bool:
        for i, b in enumerate(self._items):
            if b.id == block_id:
                self._items.pop(i)
                self._save()
                return True
        return False

    def clear(self) -> None:
        self._items = []
        self._save()

    def import_from_project(
        self,
        project_name: str,
        block_ids: list[str],
        base_dir: Path | None = None,
    ) -> int:
        """Importa blocos de um projeto para a mochila. Retorna quantos foram importados."""
        from Kix.projects.manager import ProjectManager

        manager = ProjectManager(base_dir=base_dir)
        try:
            project = manager.load(project_name)
        except FileNotFoundError:
            return 0
        # Os blocos no projeto vivem em project.blocks (lista de dicts)
        all_blocks = {
            (b.get("id") if isinstance(b, dict) else getattr(b, "id", "")): b
            for b in project.blocks
        }
        added = 0
        for bid in block_ids:
            entry = all_blocks.get(bid)
            if entry is None:
                continue
            block_dict = entry if isinstance(entry, dict) else entry.to_dict()
            self.add(block_dict, origin=project_name)
            added += 1
        return added

    def export_to_project(
        self,
        project_name: str,
        block_ids: list[str] | None = None,
        base_dir: Path | None = None,
    ) -> int:
        """Exporta blocos da mochila para um projeto. Retorna quantos foram exportados."""
        from Kix.projects.manager import ProjectManager

        manager = ProjectManager(base_dir=base_dir)
        try:
            project = manager.load(project_name)
        except FileNotFoundError:
            return 0
        targets = block_ids if block_ids is not None else [b.id for b in self._items]
        added = 0
        existing_ids = {
            (b.get("id") if isinstance(b, dict) else getattr(b, "id", ""))
            for b in project.blocks
        }
        for bid in targets:
            entry = self.get(bid)
            if entry is None:
                continue
            if entry.block.get("id") in existing_ids:
                # gera novo id para evitar colisão
                entry.block["id"] = f"{entry.block.get('id', 'bk')}_{uuid.uuid4().hex[:6]}"
            project.blocks.append(entry.block)
            existing_ids.add(entry.block["id"])
            added += 1
        if added:
            manager.save(project)
        return added


__all__ = ["Backpack", "BackpackBlock"]