"""Executor de blocos: compila e roda `BlockBehavior.source` em `async def`.

O executor é o coração do runtime: pega um `KixBlock` + valores de
input resolvidos + um `RuntimeContext`, e produz:

- mutações no sprite ativo (`self.position = ...`),
- efeitos em globals expostos como services (`camera.position = ...`),
- valor de retorno para reporters (`return math.sin(self.deg)`).

Fontes existentes em `Kix/blocks/*.py` foram escritas assumindo este
modelo. O executor:

1. Compila `source` em um módulo cujo corpo é
   `async def __kix_run__(): <source>`. O code object é cacheado por
   `BlockBehavior` (chave = id do behavior).
2. Constrói um `_SelfBinding` que materializa `self.<input>` (lê/
   escreve no dict de inputs) e delega para o sprite ativo quando o
   nome não é um input.
3. Constrói o namespace plano com `flat_namespace(services)` + builtin
   (`math`, `random`, `asyncio`).
4. `exec(code, ns)` e `await ns["__kix_run__"]()`.
5. Captura o return como output (se for reporter).

Se `behavior._callable` estiver setado (produzido pelo decorator M3.2),
o executor prioriza chamar o callable diretamente (sem `exec`).
"""

from __future__ import annotations

import ast
import asyncio
import math
import random
import types
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from Kix.block_engine.block import KixBlock
from Kix.block_engine.behavior import BlockBehavior
from Kix.engine.ctx import RuntimeContext, SpriteProxy


# --- Self binding ---------------------------------------------------------
class _SelfBinding:
    """Proxy para `self` dentro do source de um bloco.

    Ordem de resolução (leitura):
      1. `self.<input>` → input resolvido (dict mutável).
      2. `self.<sprite_attr>` → atributo do sprite ativo.
      3. `self.<ctx_attr>` → atributo do RuntimeContext (timer, clock, answer).
      4. caso contrário: `AttributeError`.

    Escrita: idem — primeiro input, depois sprite, depois ctx.

    Métodos auxiliares (para blocos de controle):
      - `await self.run(blocks)` → executa lista de dicts de blocos.
      - `await self.wait_until(cond)` → espera até a condição ser truthy.
      - `await self.wait(seconds)` → espera N segundos.
    """

    __slots__ = ("_inputs", "_sprite", "_ctx", "_extras", "_executor")

    def __init__(
        self,
        inputs: dict[str, Any],
        sprite: SpriteProxy | None,
        ctx: "RuntimeContext | None" = None,
        executor: "BlockExecutor | None" = None,
    ) -> None:
        object.__setattr__(self, "_inputs", inputs)
        object.__setattr__(self, "_sprite", sprite)
        object.__setattr__(self, "_ctx", ctx)
        object.__setattr__(self, "_extras", {})
        object.__setattr__(self, "_executor", executor)

    # ----- helpers para blocos de controle (M5) --------------------------
    async def run(self, blocks: list | None) -> None:
        """Executa uma lista de blocos (aninhados) em sequência.

        Cada item deve ser um dict (serializado de KixBlock) ou um
        KixBlock já reconstruído.
        """
        executor = object.__getattribute__(self, "_executor")
        ctx = object.__getattribute__(self, "_ctx")
        if executor is None or ctx is None or not blocks:
            return
        for item in blocks:
            if asyncio.current_task() and asyncio.current_task().cancelled():
                raise asyncio.CancelledError()
            block = item if hasattr(item, "behavior") else KixBlock.from_dict(item)
            inputs = {s.name: s.default for s in block.inputs}
            await executor.run_block(block, ctx, inputs)

    async def wait_until(self, condition) -> None:
        """Espera até `condition` ser truthy. Polling a cada 50ms."""
        while not condition:
            if asyncio.current_task() and asyncio.current_task().cancelled():
                raise asyncio.CancelledError()
            await asyncio.sleep(0.05)

    async def wait(self, seconds: float) -> None:
        await asyncio.sleep(max(0.0, float(seconds)))

    # ----- leitura ----------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        inputs = object.__getattribute__(self, "_inputs")
        if name in inputs:
            return inputs[name]
        sprite = object.__getattribute__(self, "_sprite")
        if sprite is not None and hasattr(sprite, name):
            return getattr(sprite, name)
        ctx = object.__getattribute__(self, "_ctx")
        if ctx is not None and hasattr(ctx, name):
            return getattr(ctx, name)
        extras = object.__getattribute__(self, "_extras")
        if name in extras:
            return extras[name]
        raise AttributeError(
            f"Atributo {name!r} não é input, sprite nem ctx"
        )

    # ----- escrita ----------------------------------------------------
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        inputs = object.__getattribute__(self, "_inputs")
        if name in inputs:
            inputs[name] = value
            return
        sprite = object.__getattribute__(self, "_sprite")
        if sprite is not None and hasattr(sprite, name):
            setattr(sprite, name, value)
            return
        ctx = object.__getattribute__(self, "_ctx")
        if ctx is not None and hasattr(ctx, name):
            setattr(ctx, name, value)
            return
        extras = object.__getattribute__(self, "_extras")
        extras[name] = value

    def __repr__(self) -> str:  # pragma: no cover
        sprite = object.__getattribute__(self, "_sprite")
        return f"_SelfBinding(sprite={sprite!r})"


# --- Compilação -----------------------------------------------------------
def compile_source_to_code(source: str) -> types.CodeType:
    """Embrulha `source` em `async def __kix_run__(): ...` e retorna o code object.

    O code object representa um módulo que define `__kix_run__`.
    Para executar: `exec(code, namespace)` e depois `await namespace['__kix_run__']()`.
    """
    tree = ast.parse(source, mode="exec")
    if not tree.body:
        raise ValueError("Source vazio")
    func = ast.AsyncFunctionDef(
        name="__kix_run__",
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body=tree.body,
        decorator_list=[],
        returns=None,
        type_comment=None,
    )
    ast.fix_missing_locations(func)
    module = ast.Module(body=[func], type_ignores=[])
    return compile(module, "<kix-block>", "exec")


def compile_source(source: str) -> Callable[..., Awaitable[Any]]:
    """Compat: embrulha em callable. Use `compile_source_to_code` em produção."""
    code = compile_source_to_code(source)
    namespace: dict[str, Any] = {}
    exec(code, namespace)
    return namespace["__kix_run__"]


# --- Executor -------------------------------------------------------------
@dataclass
class BlockExecutor:
    """Executa blocos. Uma instância é reutilizável."""

    _code_cache: dict[int, types.CodeType] = field(default_factory=dict)

    # ----- API pública ------------------------------------------------
    async def run_block(
        self,
        block: KixBlock,
        ctx: RuntimeContext,
        inputs: dict[str, Any] | None = None,
    ) -> Any:
        inputs = dict(inputs or {})
        behavior = block.behavior
        if behavior is None:
            return None
        return await self._execute(behavior, ctx, inputs)

    async def run_block_for_behavior(
        self,
        behavior: BlockBehavior,
        ctx: RuntimeContext,
        inputs: dict[str, Any],
    ) -> Any:
        if behavior is None:
            return None
        return await self._execute(behavior, ctx, inputs)

    # ----- core -------------------------------------------------------
    async def _execute(
        self,
        behavior: BlockBehavior,
        ctx: RuntimeContext,
        inputs: dict[str, Any],
    ) -> Any:
        # Decorator-produced: chama o callable diretamente.
        callable_ = getattr(behavior, "_callable", None)
        if callable_ is not None:
            try:
                result = callable_(**inputs)
            except TypeError:
                # Pode haver parâmetros extras no signature; cai para source.
                result = None
            if result is not None:
                if asyncio.iscoroutine(result):
                    result = await result
                return result

        # Source path: compila (cacheado) e executa num namespace novo.
        code = self._get_code(behavior)
        local_ns = self._build_namespace(ctx, inputs)
        local_ns["self"] = _SelfBinding(inputs, ctx.active_sprite, ctx, self)
        exec(code, local_ns)
        return await local_ns["__kix_run__"]()

    # ----- helpers ----------------------------------------------------
    def _get_code(self, behavior: BlockBehavior) -> types.CodeType:
        key = id(behavior)
        code = self._code_cache.get(key)
        if code is None:
            code = compile_source_to_code(behavior.source)
            self._code_cache[key] = code
        return code

    def _build_namespace(
        self,
        ctx: RuntimeContext,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        from Kix.engine.services import flat_namespace

        ns: dict[str, Any] = {
            "__builtins__": __builtins__,
            "math": math,
            "random": random,
            "asyncio": asyncio,
            "ctx": ctx,
        }
        ns.update(flat_namespace(ctx.services))
        return ns


__all__ = ["BlockExecutor", "compile_source", "compile_source_to_code", "_SelfBinding"]
