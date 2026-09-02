"""Haptic feedback — vibração sutil em eventos chave no celular.

Usa ``plyer`` quando disponível (Android/iOS); no desktop (testes,
desenvolvimento) é um no-op silencioso. Não quebramos a app se ``plyer``
não estiver instalado — fallback gracioso.
"""

from __future__ import annotations

import logging

_log = logging.getLogger(__name__)

_VIBRATOR = None
_AVAILABLE = False
_TRIED = False


def _ensure() -> None:
    """Importa plyer.vibrator uma única vez."""
    global _VIBRATOR, _AVAILABLE, _TRIED
    if _TRIED:
        return
    _TRIED = True
    try:
        from plyer.vibrator import vibrator  # type: ignore
        _VIBRATOR = vibrator
        _AVAILABLE = True
    except Exception:
        _AVAILABLE = False


def impact(style: str = "light") -> None:
    """Vibra conforme o tipo de interação.

    ``style`` aceitos:
        - ``"light"``  : toque curto (~10ms) — tap genérico
        - ``"medium"`` : ~20ms — confirmação (criar projeto, salvar)
        - ``"heavy"``  : ~40ms — drag iniciado, delete
        - ``"error"``  : padrão de erro (3 pulsos curtos)
    """
    _ensure()
    if not _AVAILABLE or _VIBRATOR is None:
        return
    try:
        if style == "error":
            # 3 pulsos curtos — fallback para vibrate(pattern) se existir.
            for _ in range(3):
                _VIBRATOR.vibrate(0.05)
        else:
            duration = {"light": 0.01, "medium": 0.02, "heavy": 0.04}.get(
                style, 0.01
            )
            _VIBRATOR.vibrate(duration)
    except Exception as exc:
        # Hardware indisponível ou sem permissão — silenciar pra não
        # quebrar a UX (vibração é cosmético).
        _log.debug("haptic feedback falhou: %s", exc)