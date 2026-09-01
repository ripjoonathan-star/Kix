"""Compartilhamento por link (formato stub catroware/Catroid share).

Catroid Pocket Code gera URLs do tipo:

    https://share.catrob.at/.../project/<id>

O conteúdo (JSON serializado do projeto) é incluído em um payload base64
URL-safe que segue o formato MediaWiki-style "XML{"key":"value"}".

Aqui implementamos:
    encode_share_url(project)  → URL stub com o JSON do projeto embedded
    decode_share_url(url)      → recupera o KixProject

Não há servidor real — é só o formato. Servidor e upload ficam para M12+.
"""

from __future__ import annotations

import base64
import json
import zlib
from typing import Any
from urllib.parse import quote, unquote, urlparse, parse_qs


SHARE_PREFIX = "kix://share/"
SHARE_HOST = "share.kixapp.local"


def encode_share_payload(project_dict: dict) -> str:
    """Compacta JSON do projeto em base64 URL-safe."""
    text = json.dumps(project_dict, ensure_ascii=False)
    compressed = zlib.compress(text.encode("utf-8"))
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def decode_share_payload(payload: str) -> dict:
    """Descompacta payload base64 → dict do projeto."""
    padded = payload + "=" * (-len(payload) % 4)
    compressed = base64.urlsafe_b64decode(padded.encode("ascii"))
    text = zlib.decompress(compressed).decode("utf-8")
    return json.loads(text)


def encode_share_url(project_dict: dict, *, host: str = SHARE_HOST) -> str:
    """Gera URL stub de compartilhamento."""
    payload = encode_share_payload(project_dict)
    return f"kix://share/{host}/{quote(payload, safe='')}"


def decode_share_url(url: str) -> dict:
    """Decodifica URL stub → dict do projeto.

    Aceita tanto `kix://share/<host>/<payload>` quanto
    `kix://share/<host>/<name>/<payload>` quanto
    `https://share.kixapp.local/?p=<payload>`.
    """
    parsed = urlparse(url)
    if parsed.scheme == "kix":
        parts = parsed.path.lstrip("/").split("/")
        if len(parts) < 2:
            raise ValueError(f"URL de share inválida: {url!r}")
        # path = "/<host>/<name?>/<payload>"
        # payload é sempre o último segmento
        payload = unquote(parts[-1])
        return decode_share_payload(payload)
    if parsed.query:
        qs = parse_qs(parsed.query)
        if "p" in qs:
            return decode_share_payload(qs["p"][0])
    raise ValueError(f"Não consegui decodificar URL: {url!r}")


def share_link_for_project(name: str, project_dict: dict) -> str:
    """Helper que inclui o nome no path (mais legível)."""
    payload = encode_share_payload(project_dict)
    return f"kix://share/{SHARE_HOST}/{quote(name, safe='')}/{quote(payload, safe='')}"


# --- helpers para o dialog "Gerar link de compartilhamento rápido" --------

def is_shareable_url(url: str) -> bool:
    """Detecta se uma URL é no formato kix://share/."""
    return url.startswith(SHARE_PREFIX) or url.startswith(f"https://{SHARE_HOST}")


__all__ = [
    "encode_share_payload",
    "decode_share_payload",
    "encode_share_url",
    "decode_share_url",
    "share_link_for_project",
    "is_shareable_url",
    "SHARE_PREFIX",
    "SHARE_HOST",
]