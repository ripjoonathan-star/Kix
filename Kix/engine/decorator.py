"""Decorator `@kix_block` — define um `KixBlock` a partir de uma função Python.

Sintaxe:

    from Kix.engine.decorator import kix_block
    from Kix.core.theme import CAT_MATH

    @kix_block(id="math.ln", category="math", color=CAT_MATH,
               name="ln", permissions={"math"})
    def math_ln(n: float) -> float:
        \"\"\"Logaritmo natural.\"\"\"
        import math
        return math.log(n)

Regras:

- `id`, `category`, `color` são obrigatórios.
- `name` default = `__name__` (com underscore → espaço).
- `permissions` default = `set()`.
- Anotações de parâmetro → `SocketDef`:
    * `float` / `int` → `SocketKind.NUMBER`
    * `str` → `SocketKind.STRING`
    * `bool` → `SocketKind.BOOLEAN`
    * `KixVariable` ou qualquer outro → `SocketKind.VARIABLE` (fallback seguro)
    * ausente → `SocketKind.NUMBER` + warning
- Anotação de retorno → `outputs`:
    * `-> float`  → `SocketDef("result", NUMBER)`
    * `-> tuple[T, ...]` → múltiplos `out_<i>` sockets na ordem
    * `-> None` / ausente → `outputs=[]`
- `visual_style`:
    * `"math"` → `name(p1, p2, ...)`
    * `"setter"` → `Definir p1 = p2`  (aceita kwargs `prefix`, `assignment`)
    * `"raw"`   → `name p1 p2 ...`
- `*args` / `**kwargs` levantam `TypeError` na decoração.
- O `BlockBehavior.source` gerado chama o callable diretamente; o
  executor prioriza `_callable` quando presente (não passa por `exec`).
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import typing
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, get_args, get_origin

from Kix.block_engine import (
    BlockInput,
    BlockVisual,
    Group,
    KixBlock,
    SocketDef,
    SocketKind,
    Text,
)
from Kix.block_engine.behavior import BlockBehavior


# --- Annotação → SocketKind ------------------------------------------------
_TYPE_MAP: dict[Any, SocketKind] = {
    float: SocketKind.NUMBER,
    int: SocketKind.NUMBER,
    str: SocketKind.STRING,
    bool: SocketKind.BOOLEAN,
}


def _resolve_string_annotation(fn: Callable[..., Any]) -> dict[str, Any]:
    """Resolve anotações como string (PEP 563) para tipos reais.

    Retorna `{param_name: real_type, 'return': real_type}`.
    """
    try:
        return typing.get_type_hints(fn)
    except Exception:
        return {}


def _annotation_to_kind(annotation: Any) -> SocketKind:
    """Converte uma anotação Python para `SocketKind`. Fallback seguro."""
    if annotation is inspect.Parameter.empty or annotation is None:
        return SocketKind.NUMBER
    if isinstance(annotation, str):
        # PEP 563: anotações podem vir como string. Sem resolver,
        # tratamos como tipo desconhecido.
        return SocketKind.VARIABLE
    origin = get_origin(annotation)
    if origin is None:
        return _TYPE_MAP.get(annotation, SocketKind.VARIABLE)
    # Optional[T], Union[T, None] etc — usa o primeiro arg não-None
    args = get_args(annotation)
    for a in args:
        if a is not type(None):
            return _annotation_to_kind(a)
    return SocketKind.VARIABLE


# --- Visual templates ------------------------------------------------------
def _visual_for_math(name: str, inputs: list[SocketDef]) -> BlockVisual:
    children: list[Any] = [Text(f"{name}(")]
    for i, s in enumerate(inputs):
        if i > 0:
            children.append(Text(", "))
        children.append(BlockInput(s.name))
    children.append(Text(")"))
    return BlockVisual(root=Group(children=children))


def _visual_for_setter(name: str, inputs: list[SocketDef]) -> BlockVisual:
    if len(inputs) < 2:
        return _visual_for_raw(name, inputs)
    children: list[Any] = [Text(f"{name} "), BlockInput(inputs[0].name),
                           Text(" = "), BlockInput(inputs[1].name)]
    for extra in inputs[2:]:
        children.append(Text(" "))
        children.append(BlockInput(extra.name))
    return BlockVisual(root=Group(children=children))


def _visual_for_raw(name: str, inputs: list[SocketDef]) -> BlockVisual:
    children: list[Any] = [Text(f"{name}")]
    for s in inputs:
        children.append(Text(" "))
        children.append(BlockInput(s.name))
    return BlockVisual(root=Group(children=children))


_STYLES = {
    "math": _visual_for_math,
    "setter": _visual_for_setter,
    "raw": _visual_for_raw,
}


# --- Saída a partir da anotação de retorno ---------------------------------
def _outputs_from_return(annotation: Any) -> list[SocketDef]:
    if annotation is inspect.Parameter.empty or annotation is None:
        return []
    origin = get_origin(annotation)
    if origin is tuple:
        args = get_args(annotation)
        return [SocketDef(f"out_{i}", _annotation_to_kind(a))
                for i, a in enumerate(args)]
    return [SocketDef("result", _annotation_to_kind(annotation))]


# --- Decorator -------------------------------------------------------------
@dataclass
class _DecoratorState:
    id: str
    category: str
    color: tuple[float, float, float, float]
    name: str
    permissions: set[str]
    visual_style: str
    visual: BlockVisual | None
    inputs_override: list[SocketDef] | None


def kix_block(
    *,
    id: str,
    category: str,
    color: tuple[float, float, float, float],
    name: str | None = None,
    permissions: set[str] | None = None,
    visual_style: str = "raw",
    visual: BlockVisual | None = None,
    inputs: list[SocketDef] | None = None,
) -> Callable[[Callable[..., Any]], KixBlock]:
    """Decorador factory — recebe metadados e devolve o decorator propriamente dito."""
    state = _DecoratorState(
        id=id,
        category=category,
        color=tuple(color),
        name=name or id.split(".")[-1].replace("_", " "),
        permissions=set(permissions or ()),
        visual_style=visual_style,
        visual=visual,
        inputs_override=list(inputs) if inputs is not None else None,
    )

    def decorator(fn: Callable[..., Any]) -> KixBlock:
        return _build_block(fn, state)

    return decorator


def _build_block(fn: Callable[..., Any], st: _DecoratorState) -> KixBlock:
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())
    resolved = _resolve_string_annotation(fn)

    # *args / **kwargs são proibidos
    for p in params:
        if p.kind in {p.VAR_POSITIONAL, p.VAR_KEYWORD}:
            raise TypeError(
                f"@kix_block não suporta *args/**kwargs em {fn.__name__!r}"
            )

    # Inputs: usa override se fornecido; caso contrário infere do signature
    if st.inputs_override is not None:
        socket_inputs = st.inputs_override
    else:
        socket_inputs = []
        for p in params:
            # Prefer annotation resolvida (string → tipo real)
            annotation = resolved.get(p.name, p.annotation)
            if annotation is inspect.Parameter.empty:
                warnings.warn(
                    f"@kix_block {st.id!r}: parâmetro {p.name!r} sem "
                    f"anotação — assumindo NUMBER",
                    UserWarning,
                    stacklevel=2,
                )
            kind = _annotation_to_kind(annotation)
            default = (p.default if p.default is not inspect.Parameter.empty
                       else None)
            socket_inputs.append(SocketDef(p.name, kind, default=default))

    # Outputs
    return_annotation = resolved.get("return", sig.return_annotation)
    outputs = _outputs_from_return(return_annotation)

    # Visual
    if st.visual is not None:
        visual = st.visual
    else:
        builder = _STYLES.get(st.visual_style, _visual_for_raw)
        visual = builder(st.name, socket_inputs)

    # Behavior com _callable
    behavior = BlockBehavior(
        language="python",
        source=f"# decorator-built: {_callable_source(fn)}",
        _callable=_wrap_callable(fn, params),
    )

    return KixBlock(
        id=st.id,
        name=st.name,
        category=st.category,
        color=st.color,
        visual=visual,
        inputs=socket_inputs,
        outputs=outputs,
        behavior=behavior,
        permissions=set(st.permissions),
    )


def _wrap_callable(fn: Callable[..., Any], params: list[inspect.Parameter]) -> Callable[..., Any]:
    """Embrulha a função de modo que aceitar inputs parciais não levante TypeError."""
    required = {p.name for p in params if p.default is inspect.Parameter.empty}

    @functools.wraps(fn)
    def wrapper(**kwargs):
        # Preenche defaults que não foram passados
        merged = {}
        for p in params:
            if p.name in kwargs:
                merged[p.name] = kwargs[p.name]
            elif p.default is not inspect.Parameter.empty:
                merged[p.name] = p.default
        # Se faltar required, deixa para a função levantar
        return fn(**merged)

    # Mantém referência à função original para introspecção
    wrapper.__wrapped__ = fn  # type: ignore[attr-defined]
    return wrapper


def _callable_source(fn: Callable[..., Any]) -> str:
    return f"callable={fn.__module__}.{fn.__qualname__}"


__all__ = ["kix_block"]
