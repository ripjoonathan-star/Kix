"""Resolução de valores de input para uma instância de bloco em runtime.

Quando o executor roda um bloco, ele recebe um mapeamento `inputs` que
associa o nome de cada `SocketDef` ao valor resolvido (literal, ou saída
de outro bloco). `InstanceBinding` é apenas um `dict` tipado; ele
encapsula o contrato e oferece helpers de validação.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InstanceBinding:
    """Valores resolvidos dos inputs de uma instância de bloco.

    Não conhece o `KixBlock` — apenas mapeia `socket_name → valor`.
    Valores são responsabilidade do dispatcher (literal da UI, ou saída
    do bloco anterior).
    """

    values: dict[str, Any] = field(default_factory=dict)

    def get(self, name: str, default: Any = None) -> Any:
        return self.values.get(name, default)

    def set(self, name: str, value: Any) -> None:
        self.values[name] = value

    def to_dict(self) -> dict[str, Any]:
        return dict(self.values)
