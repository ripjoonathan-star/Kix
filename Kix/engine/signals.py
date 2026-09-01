"""Sinais de controle de fluxo usados pelos blocos de controle.

`control.continue` levanta `ContinueSignal`, `control.break` levanta
`BreakSignal`, `control.stop_all` levanta `StopSignal`. O executor
propaga até o caller (testes) ou até o dispatcher de scripts aninhados
(marco futuro).
"""

from __future__ import annotations


class BlockSignal(BaseException):
    """Sinal levantado por blocos de controle. Base para Continue/Break/Stop."""

    pass


class ContinueSignal(BlockSignal):
    """`control.continue` — pula para a próxima iteração do loop mais próximo."""

    pass


class BreakSignal(BlockSignal):
    """`control.break` — sai do loop mais próximo."""

    pass


class StopSignal(BlockSignal):
    """`control.stop_all` — interrompe todos os scripts."""

    pass


def signal_name(exc: BaseException) -> str:
    return type(exc).__name__
