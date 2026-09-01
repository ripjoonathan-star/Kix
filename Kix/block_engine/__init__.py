"""Engine de blocos: modelo universal, visual, comportamento."""

from Kix.block_engine.block import KixBlock, SocketDef, SocketKind
from Kix.block_engine.visual import (
    BlockVisual,
    Text,
    Number,
    EditableText,
    Boolean,
    Variable,
    Dropdown,
    Color,
    BlockInput,
    Icon,
    Separator,
    Space,
    Group,
    Slider,
    Angle,
    Position,
    ObjectRef,
    SpriteRef,
    SceneRef,
    SoundRef,
    FileRef,
)

__all__ = [
    "KixBlock",
    "SocketDef",
    "SocketKind",
    "BlockVisual",
    "Text", "Number", "EditableText", "Boolean", "Variable",
    "Dropdown", "Color", "BlockInput", "Icon", "Separator", "Space",
    "Group", "Slider", "Angle", "Position", "ObjectRef",
    "SpriteRef", "SceneRef", "SoundRef", "FileRef",
]