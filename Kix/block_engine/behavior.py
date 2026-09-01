"""Comportamento de bloco: código-fonte em Python (Lua entra em marco futuro).

M3: `BlockBehavior.run(ctx)` delega ao `BlockExecutor`, que compila e
executa o source de fato. O executor fica em `Kix/engine/executor.py`
(import lazy para evitar ciclo: engine → block_engine).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class BlockBehavior:
    language: str                   # "python" (M3); "lua" depois
    source: str                     # código-fonte como string
    # Campo opcional usado pelo decorator `@kix_block` (M3.2). Não é
    # serializado em `to_dict`; após round-trip o executor cai no path
    # `source` (o source é auto-gerado e replayável).
    _callable: Callable[..., Any] | None = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict:
        return {"language": self.language, "source": self.source}

    @classmethod
    def from_dict(cls, data: dict) -> "BlockBehavior":
        return cls(language=data["language"], source=data["source"])

    # ------------------------------------------------------------------
    # Execução
    # ------------------------------------------------------------------
    async def aexecute(self, ctx: Any, inputs: dict[str, Any] | None = None) -> Any:
        """Versão async — recomendada."""
        from Kix.engine.ctx import RuntimeContext
        from Kix.engine.executor import BlockExecutor

        if not isinstance(ctx, RuntimeContext):
            raise TypeError(
                f"BlockBehavior.run exige RuntimeContext; recebi {type(ctx).__name__}"
            )
        # Reusa o executor cacheado no ctx se existir.
        executor: BlockExecutor = getattr(ctx, "_executor", None) or BlockExecutor()
        # Acesso ao bloco via closure: o caller deve usar `executor.run_block`.
        # Aqui mantemos compatibilidade delegando.
        return await executor.run_block_for_behavior(self, ctx, inputs or {})

    def run(self, ctx: Any, inputs: dict[str, Any] | None = None) -> Any:
        """Executa sincronamente (cria um event loop). Para testes rápidos.

        Em produção prefira `BlockExecutor().run_block(block, ctx, inputs)`.
        """
        return asyncio.run(self.aexecute(ctx, inputs))
