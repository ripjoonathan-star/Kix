"""Blocos de save/load de estado de jogo (persistência local).

`storage` é um dict exposto pelo Services container (namespaced por
projeto). Além dos blocos básicos (set/get/has/delete), existem:

- `storage.list_keys` → lista todas as chaves
- `storage.clear` → limpa tudo
- `storage.set_number` / `storage.set_boolean` → variantes tipadas
- `storage.get_number` / `storage.get_boolean` → variantes tipadas
- `storage.delete_all` → apaga todas
"""

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
from Kix.core.theme import CAT_STORAGE


# ============================================================ Básicos
STORAGE_SET = KixBlock(
    id="storage.set", name="Salvar texto", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[Text("Salvar "), BlockInput("key"), Text(" = "), BlockInput("value")])),
    inputs=[SocketDef("key", SocketKind.STRING, default="hp"),
            SocketDef("value", SocketKind.STRING, default="100")],
    outputs=[],
    behavior=BlockBehavior("python", "storage[self.key] = self.value"),
    permissions={"storage"},
)
STORAGE_GET = KixBlock(
    id="storage.get", name="Ler texto", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[Text("Ler "), BlockInput("key"), Text(" (padrão "), BlockInput("default"), Text(")")])),
    inputs=[SocketDef("key", SocketKind.STRING, default="hp"),
            SocketDef("default", SocketKind.STRING, default="")],
    outputs=[SocketDef("value", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return storage.get(self.key, self.default)"),
    permissions={"storage"},
)
STORAGE_HAS = KixBlock(
    id="storage.has", name="Tem chave?", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[Text("Storage tem "), BlockInput("key")])),
    inputs=[SocketDef("key", SocketKind.STRING, default="")],
    outputs=[SocketDef("exists", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return self.key in storage"),
    permissions={"storage"},
)
STORAGE_DELETE = KixBlock(
    id="storage.delete", name="Deletar chave", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[Text("Deletar "), BlockInput("key")])),
    inputs=[SocketDef("key", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "storage.pop(self.key, None)"),
    permissions={"storage"},
)

# ============================================================ Tipados
STORAGE_SET_NUMBER = KixBlock(
    id="storage.set_number", name="Salvar número", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[
        Text("Salvar "), BlockInput("key"), Text(" = nº "), BlockInput("value"),
    ])),
    inputs=[SocketDef("key", SocketKind.STRING, default="score"),
            SocketDef("value", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior("python", "storage[self.key] = float(self.value)"),
    permissions={"storage"},
)
STORAGE_GET_NUMBER = KixBlock(
    id="storage.get_number", name="Ler número", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[
        Text("Ler nº "), BlockInput("key"), Text(" (padrão "), BlockInput("default"), Text(")"),
    ])),
    inputs=[SocketDef("key", SocketKind.STRING, default="score"),
            SocketDef("default", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(
        "python",
        "v = storage.get(self.key, self.default); return float(v) if isinstance(v,(int,float)) else float(self.default)",
    ),
    permissions={"storage"},
)
STORAGE_SET_BOOL = KixBlock(
    id="storage.set_boolean", name="Salvar booleano", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[
        Text("Salvar "), BlockInput("key"), Text(" = bool "), BlockInput("value"),
    ])),
    inputs=[SocketDef("key", SocketKind.STRING, default="unlocked"),
            SocketDef("value", SocketKind.BOOLEAN, default=False)],
    outputs=[],
    behavior=BlockBehavior("python", "storage[self.key] = bool(self.value)"),
    permissions={"storage"},
)
STORAGE_GET_BOOL = KixBlock(
    id="storage.get_boolean", name="Ler booleano", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[
        Text("Ler bool "), BlockInput("key"), Text(" (padrão "), BlockInput("default"), Text(")"),
    ])),
    inputs=[SocketDef("key", SocketKind.STRING, default="unlocked"),
            SocketDef("default", SocketKind.BOOLEAN, default=False)],
    outputs=[SocketDef("value", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(
        "python",
        "v = storage.get(self.key, self.default); return bool(v) if isinstance(v,bool) else bool(self.default)",
    ),
    permissions={"storage"},
)

# ============================================================ Avançados
STORAGE_LIST_KEYS = KixBlock(
    id="storage.list_keys", name="Listar chaves", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[Text("todas as chaves (JSON)")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.STRING)],
    behavior=BlockBehavior("python", "import json; return json.dumps(sorted(storage.keys()))"),
    permissions={"storage"},
)
STORAGE_CLEAR = KixBlock(
    id="storage.clear", name="Limpar tudo", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[Text("Limpar todo o storage")])),
    inputs=[], outputs=[],
    behavior=BlockBehavior("python", "storage.clear()"),
    permissions={"storage"},
)
STORAGE_SIZE = KixBlock(
    id="storage.size", name="Nº de chaves", category="storage", color=CAT_STORAGE,
    visual=BlockVisual(root=Group(children=[Text("quantas chaves salvas")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return len(storage)"),
    permissions={"storage"},
)

STORAGE_BLOCKS = (
    STORAGE_SET, STORAGE_GET, STORAGE_HAS, STORAGE_DELETE,
    STORAGE_SET_NUMBER, STORAGE_GET_NUMBER,
    STORAGE_SET_BOOL, STORAGE_GET_BOOL,
    STORAGE_LIST_KEYS, STORAGE_CLEAR, STORAGE_SIZE,
)

assert len(STORAGE_BLOCKS) == 11, f"esperado 11, obtido {len(STORAGE_BLOCKS)}"
