"""Runtime do jogo: contexto, executor, serviços, sinais.

M3: `BlockBehavior.run(ctx)` realmente executa. `engine/` provê o
`RuntimeContext` (stage + services + estado compartilhado), o
`BlockExecutor` (compila + roda o source do bloco) e o `Services`
container (proxies para câmera, áudio, tilemap, rede, etc.). Veja o
plano em `plans/ancient-giggling-clarke.md` para o desenho completo.
"""

from Kix.engine.signals import (
    BlockSignal,
    BreakSignal,
    ContinueSignal,
    StopSignal,
    signal_name,
)
from Kix.engine.ctx import RuntimeContext, SpriteProxy, Stage, make_ctx
from Kix.engine.instances import InstanceBinding
from Kix.engine.services import Services
from Kix.engine.executor import BlockExecutor, compile_source
from Kix.engine.decorator import kix_block

__all__ = [
    "BlockExecutor", "compile_source",
    "RuntimeContext", "SpriteProxy", "Stage", "make_ctx",
    "InstanceBinding",
    "Services",
    "BlockSignal", "BreakSignal", "ContinueSignal", "StopSignal",
    "signal_name",
    "kix_block",
]
