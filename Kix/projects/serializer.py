"""Serialização JSON do formato `.kix`."""

from __future__ import annotations

import json
from typing import Any

from Kix.projects.model import KixProject

KIX_FORMAT = "kix"
KIX_VERSION = 1


class KixFormatError(ValueError):
    """Erro ao ler/escrever um arquivo .kix."""


def to_json(project: KixProject, *, indent: int | None = 2) -> str:
    """Serializa um KixProject para string JSON."""
    return json.dumps(project.to_dict(), indent=indent, ensure_ascii=False)


def to_dict(project: KixProject) -> dict:
    return project.to_dict()


def from_json(text: str) -> KixProject:
    """Desserializa string JSON para KixProject. Valida format/version."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise KixFormatError(f"JSON inválido: {e}") from e
    return from_dict(data)


def from_dict(data: dict) -> KixProject:
    if not isinstance(data, dict):
        raise KixFormatError(f"Esperado objeto JSON, recebi {type(data).__name__}")
    if data.get("format") != KIX_FORMAT:
        raise KixFormatError(
            f"format inválido: {data.get('format')!r} (esperado {KIX_FORMAT!r})"
        )
    version = data.get("version")
    if version != KIX_VERSION:
        raise KixFormatError(
            f"Versão não suportada: {version!r} (esperado {KIX_VERSION})"
        )
    return KixProject.from_dict(data)