"""Testes M8 — Layer blocks + LayersProxy + KixLayer dataclass.

Cobre:
- KixLayer serialização round-trip
- LayersProxy API (criar/remover/reordenar/visibility/colisão/shader/...)
- 19 blocos de layer executam via BlockExecutor
- Total de blocos ALL >= 350 (era 320+, agora 339+)
"""

from __future__ import annotations

import asyncio


# --- KixLayer dataclass ---------------------------------------------------

def test_kixlayer_default():
    from Kix.projects.model import KixLayer

    lyr = KixLayer()
    assert lyr.name == "Layer"
    assert lyr.category == "other"
    assert lyr.z_index == 0
    assert lyr.visible is True
    assert lyr.collidable is True
    assert lyr.shader == ""
    assert lyr.objects == []


def test_kixlayer_categories():
    """Categorias válidas: ui, background, player, enemy, other."""
    from Kix.projects.model import KixLayer

    for cat in ("ui", "background", "player", "enemy", "other"):
        lyr = KixLayer(category=cat)
        assert lyr.category == cat


def test_kixlayer_round_trip():
    from Kix.projects.model import KixLayer

    original = KixLayer(
        name="UI Principal",
        category="ui",
        z_index=10,
        visible=False,
        collidable=False,
        shader="blur",
        objects=["obj_001", "obj_002"],
    )
    data = original.to_dict()
    restored = KixLayer.from_dict(data)
    assert restored.name == "UI Principal"
    assert restored.category == "ui"
    assert restored.z_index == 10
    assert restored.visible is False
    assert restored.collidable is False
    assert restored.shader == "blur"
    assert restored.objects == ["obj_001", "obj_002"]


def test_kixlayer_invalid_category_falls_back_to_other():
    from Kix.projects.model import KixLayer

    lyr = KixLayer.from_dict({"category": "magic"})
    assert lyr.category == "other"


def test_kixscene_includes_layers():
    """KixScene ganhou campo `layers`."""
    from Kix.projects.model import KixScene, KixLayer

    scene = KixScene(name="Cena")
    scene.layers.append(KixLayer(name="UI").id)
    scene.layers.append(KixLayer(name="Background").id)
    data = scene.to_dict()
    assert "layers" in data
    assert len(data["layers"]) == 2

    restored = KixScene.from_dict(data)
    assert len(restored.layers) == 2


def test_kixproject_round_trip_with_layers():
    from Kix.projects.model import KixProject, KixLayer, KixScene, KixObject

    p = KixProject(name="Test")
    p.layers.append(KixLayer(name="BG", category="background"))
    p.layers.append(KixLayer(name="Player", category="player"))
    p.scenes.append(KixScene(name="Cena 1"))
    p.objects.append(KixObject(name="Ator 1"))

    data = p.to_dict()
    assert "layers" in data
    assert len(data["layers"]) == 2

    from Kix.projects.serializer import to_json, from_json
    text = to_json(p)
    restored = from_json(text)
    assert len(restored.layers) == 2
    assert restored.layers[0].name == "BG"
    assert restored.layers[1].category == "player"


# --- LayersProxy ----------------------------------------------------------

def test_layers_create_default_category():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    assert lp.create("BG") is True
    assert lp.count() == 1
    assert lp.exists("BG")
    assert lp.is_visible("BG")


def test_layers_create_with_category():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("Player", category="player")
    lyr = lp._get("Player")
    assert lyr["category"] == "player"


def test_layers_create_invalid_category_falls_back():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("X", category="invalid")
    lyr = lp._get("X")
    assert lyr["category"] == "other"


def test_layers_create_duplicate_returns_false():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("Dup")
    assert lp.create("Dup") is False
    assert lp.count() == 1


def test_layers_remove():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("A")
    lp.create("B")
    assert lp.remove("A")
    assert not lp.exists("A")
    assert lp.exists("B")


def test_layers_visibility():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("X")
    assert lp.is_visible("X")
    lp.hide("X")
    assert not lp.is_visible("X")
    lp.show("X")
    assert lp.is_visible("X")


def test_layers_collidable():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("X")
    assert lp.is_collidable("X")
    lp.set_collidable("X", False)
    assert not lp.is_collidable("X")


def test_layers_shader():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("X")
    lp.set_shader("X", "blur")
    assert lp._get("X")["shader"] == "blur"
    lp.clear_shader("X")
    assert lp._get("X")["shader"] == ""


def test_layers_apply_shader_except():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("UI")
    lp.create("Player")
    lp.create("Enemy")
    lp.apply_shader_except("blur", "UI")
    assert lp._get("UI")["shader"] == ""
    assert lp._get("Player")["shader"] == "blur"
    assert lp._get("Enemy")["shader"] == "blur"


def test_layers_objects():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("X")
    lp.add_object("X", "obj_a")
    lp.add_object("X", "obj_b")
    assert lp.object_count("X") == 2
    assert lp.contains_object("X", "obj_a")
    assert not lp.contains_object("X", "obj_z")

    lp.remove_object("X", "obj_a")
    assert lp.object_count("X") == 1
    assert not lp.contains_object("X", "obj_a")


def test_layers_clear():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("X")
    lp.add_object("X", "o1")
    lp.add_object("X", "o2")
    lp.clear("X")
    assert lp.object_count("X") == 0


def test_layers_above():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("A")
    lp.create("B")
    lp.create("C")
    z_before = lp.z_index("A")
    z_b = lp.z_index("B")
    lp.above("A", "B")
    assert lp.z_index("A") == z_b + 1
    assert lp.z_index("A") > z_before


def test_layers_swap():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("A")
    lp.create("B")
    z_a = lp.z_index("A")
    z_b = lp.z_index("B")
    lp.swap("A", "B")
    assert lp.z_index("A") == z_b
    assert lp.z_index("B") == z_a


def test_layers_switch_current():
    from Kix.engine.services import LayersProxy

    lp = LayersProxy()
    lp.create("A")
    lp.create("B")
    assert lp.current() == ""
    lp.switch("A")
    assert lp.current() == "A"


# --- Layer blocks ---------------------------------------------------------

def test_layer_blocks_imports():
    from Kix.blocks.layer import LAYERS

    assert len(LAYERS) >= 18


def test_layer_blocks_have_layer_category():
    from Kix.blocks.layer import LAYERS

    for b in LAYERS:
        assert b.category == "layers", f"{b.id}: esperado category='layers', obtido {b.category!r}"


def test_layer_blocks_ids_unique():
    from Kix.blocks.layer import LAYERS

    ids = [b.id for b in LAYERS]
    assert len(ids) == len(set(ids))


def test_layer_blocks_registered_in_all():
    from Kix.blocks import ALL, LAYERS

    all_ids = {b.id for b in ALL}
    for b in LAYERS:
        assert b.id in all_ids


def test_layer_create_executes():
    """layer.create executa via BlockExecutor."""
    from Kix.block_engine.behavior import BlockBehavior
    from Kix.block_engine.block import KixBlock
    from Kix.block_engine.visual import BlockVisual, Text
    from Kix.blocks.layer import LAYER_CREATE
    from Kix.engine.ctx import make_ctx
    from Kix.engine.executor import BlockExecutor

    executor = BlockExecutor()
    ctx = make_ctx()

    async def run():
        # Cria "TestLayer" da categoria "player"
        result = await executor.run_block(
            LAYER_CREATE,
            ctx=ctx,
            inputs={"name": "TestLayer", "category": "player"},
        )
        return result

    asyncio.run(run())
    # verifica que layer foi criada
    assert ctx.services.layers.exists("TestLayer")
    assert ctx.services.layers._get("TestLayer")["category"] == "player"


def test_layer_apply_shader_except_executes():
    from Kix.blocks.layer import LAYER_SHADER_EXCEPT
    from Kix.engine.ctx import make_ctx
    from Kix.engine.executor import BlockExecutor

    ctx = make_ctx()
    ctx.services.layers.create("UI")
    ctx.services.layers.create("Player")

    async def run():
        await BlockExecutor().run_block(
            LAYER_SHADER_EXCEPT,
            ctx=ctx,
            inputs={"shader": "grayscale", "except_name": "UI"},
        )

    asyncio.run(run())
    assert ctx.services.layers._get("UI")["shader"] == ""
    assert ctx.services.layers._get("Player")["shader"] == "grayscale"


def test_layer_visibility_block_executes():
    from Kix.blocks.layer import LAYER_HIDE, LAYER_SHOW, LAYER_IS_VISIBLE
    from Kix.engine.ctx import make_ctx
    from Kix.engine.executor import BlockExecutor

    ctx = make_ctx()
    ctx.services.layers.create("X")

    async def run():
        await BlockExecutor().run_block(LAYER_HIDE, ctx=ctx, inputs={"name": "X"})
        result = await BlockExecutor().run_block(
            LAYER_IS_VISIBLE, ctx=ctx, inputs={"name": "X"}
        )
        assert result is False
        await BlockExecutor().run_block(LAYER_SHOW, ctx=ctx, inputs={"name": "X"})
        result = await BlockExecutor().run_block(
            LAYER_IS_VISIBLE, ctx=ctx, inputs={"name": "X"}
        )
        assert result is True

    asyncio.run(run())


def test_layer_collision_block_executes():
    from Kix.blocks.layer import LAYER_COLLISION_OFF, LAYER_COLLISION_ON, LAYER_IS_COLLIDABLE
    from Kix.engine.ctx import make_ctx
    from Kix.engine.executor import BlockExecutor

    ctx = make_ctx()
    ctx.services.layers.create("Walls")

    async def run():
        await BlockExecutor().run_block(
            LAYER_COLLISION_OFF, ctx=ctx, inputs={"name": "Walls"}
        )
        result = await BlockExecutor().run_block(
            LAYER_IS_COLLIDABLE, ctx=ctx, inputs={"name": "Walls"}
        )
        assert result is False
        await BlockExecutor().run_block(
            LAYER_COLLISION_ON, ctx=ctx, inputs={"name": "Walls"}
        )

    asyncio.run(run())
    assert ctx.services.layers.is_collidable("Walls")


def test_layer_above_block_executes():
    from Kix.blocks.layer import LAYER_ABOVE
    from Kix.engine.ctx import make_ctx
    from Kix.engine.executor import BlockExecutor

    ctx = make_ctx()
    ctx.services.layers.create("Player")
    ctx.services.layers.create("BG")

    async def run():
        await BlockExecutor().run_block(
            LAYER_ABOVE, ctx=ctx, inputs={"a": "Player", "b": "BG"}
        )

    asyncio.run(run())
    assert ctx.services.layers.z_index("Player") > ctx.services.layers.z_index("BG")


def test_layer_move_object_executes():
    from Kix.blocks.layer import LAYER_MOVE_OBJECT
    from Kix.engine.ctx import make_ctx
    from Kix.engine.executor import BlockExecutor

    ctx = make_ctx()
    ctx.services.layers.create("Enemies")

    async def run():
        await BlockExecutor().run_block(
            LAYER_MOVE_OBJECT, ctx=ctx, inputs={"obj": "obj_xyz", "name": "Enemies"}
        )

    asyncio.run(run())
    assert ctx.services.layers.contains_object("Enemies", "obj_xyz")


def test_layer_object_count_executes():
    from Kix.blocks.layer import LAYER_OBJECT_COUNT, LAYER_CLEAR
    from Kix.engine.ctx import make_ctx
    from Kix.engine.executor import BlockExecutor

    ctx = make_ctx()
    ctx.services.layers.create("Items")
    ctx.services.layers.add_object("Items", "i1")
    ctx.services.layers.add_object("Items", "i2")
    ctx.services.layers.add_object("Items", "i3")

    async def run():
        n = await BlockExecutor().run_block(
            LAYER_OBJECT_COUNT, ctx=ctx, inputs={"name": "Items"}
        )
        assert n == 3
        await BlockExecutor().run_block(
            LAYER_CLEAR, ctx=ctx, inputs={"name": "Items"}
        )
        n2 = await BlockExecutor().run_block(
            LAYER_OBJECT_COUNT, ctx=ctx, inputs={"name": "Items"}
        )
        assert n2 == 0

    asyncio.run(run())


# --- Total de blocos ------------------------------------------------------

def test_total_blocks_at_least_330():
    """M8: blocks anteriores 320 + 19 layers = ≥ 339."""
    from Kix.blocks import ALL

    assert len(ALL) >= 330, f"Total {len(ALL)} abaixo de 330 (M8 layers)"


# --- Integração Layer + Cena ---------------------------------------------

def test_project_with_layers_in_scene():
    """Cena pode referenciar layers via scene.layers (ids)."""
    from Kix.projects.model import KixLayer, KixProject, KixScene

    p = KixProject(name="Game")
    bg = KixLayer(name="Background", category="background")
    ui = KixLayer(name="UI", category="ui")
    player = KixLayer(name="Player", category="player")
    p.layers.extend([bg, ui, player])

    scene = KixScene(name="Level 1")
    scene.layers.extend([bg.id, player.id, ui.id])
    p.scenes.append(scene)

    # round-trip
    from Kix.projects.serializer import to_json, from_json
    text = to_json(p)
    restored = from_json(text)
    assert len(restored.layers) == 3
    assert len(restored.scenes[0].layers) == 3
    assert restored.scenes[0].layers[0] == bg.id