"""Blocos de áudio avançado (pitch, pan, fade, mic)."""

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
from Kix.core.theme import CAT_AUDIO_ADV


AUDIO_PLAY_PITCHED = KixBlock(
    id="audio.play_pitched", name="Tocar com pitch", category="audio_advanced", color=CAT_AUDIO_ADV,
    visual=BlockVisual(root=Group(children=[Text("Tocar "), BlockInput("sound"), Text(" pitch "), BlockInput("pitch")])),
    inputs=[SocketDef("sound", SocketKind.SOUND),
            SocketDef("pitch", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior("python", "self.play_sound(self.sound, pitch=self.pitch)"),
    permissions={"sound"},
)
AUDIO_SET_PAN = KixBlock(
    id="audio.set_pan", name="Pan", category="audio_advanced", color=CAT_AUDIO_ADV,
    visual=BlockVisual(root=Group(children=[Text("Pan (-1 a 1): "), BlockInput("pan")])),
    inputs=[SocketDef("pan", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior("python", "self.pan = self.pan"),
    permissions={"sound"},
)
AUDIO_FADE_IN = KixBlock(
    id="audio.fade_in", name="Fade in", category="audio_advanced", color=CAT_AUDIO_ADV,
    visual=BlockVisual(root=Group(children=[Text("Fade in por "), BlockInput("seconds"), Text(" s")])),
    inputs=[SocketDef("seconds", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.fade_in(self.seconds)"),
    permissions={"sound"},
)
AUDIO_FADE_OUT = KixBlock(
    id="audio.fade_out", name="Fade out", category="audio_advanced", color=CAT_AUDIO_ADV,
    visual=BlockVisual(root=Group(children=[Text("Fade out por "), BlockInput("seconds"), Text(" s")])),
    inputs=[SocketDef("seconds", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.fade_out(self.seconds)"),
    permissions={"sound"},
)
AUDIO_EQUALIZER = KixBlock(
    id="audio.set_eq", name="Equalizador", category="audio_advanced", color=CAT_AUDIO_ADV,
    visual=BlockVisual(root=Group(children=[Text("EQ "), BlockInput("band"), Text(" = "), BlockInput("gain"), Text(" dB")])),
    inputs=[SocketDef("band", SocketKind.NUMBER, default=0),
            SocketDef("gain", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior("python", "audio.eq[int(self.band)] = self.gain"),
    permissions={"sound"},
)
AUDIO_MIC_INPUT = KixBlock(
    id="audio.mic_level", name="Volume do microfone", category="audio_advanced", color=CAT_AUDIO_ADV,
    visual=BlockVisual(root=Group(children=[Text("Volume do microfone (0-1)")])),
    inputs=[],
    outputs=[SocketDef("level", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return audio.mic.level()"),
    permissions={"sound", "device"},
)

# --- M3.3: audio reporters faltando (2) ---------------------------------
AUDIO_VOLUME_REPORTER = KixBlock(
    id="audio.volume_reporter", name="volume", category="sound",
    color=CAT_AUDIO_ADV,
    visual=BlockVisual(root=Group(children=[Text("volume")])),
    inputs=[], outputs=[SocketDef("volume", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return audio.volume"),
    permissions={"sound"},
)
AUDIO_MIC_FREQUENCY = KixBlock(
    id="audio.mic.frequency", name="frequência do som do microfone",
    category="sound", color=CAT_AUDIO_ADV,
    visual=BlockVisual(root=Group(children=[Text("frequência do microfone")])),
    inputs=[], outputs=[SocketDef("frequency", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return audio.mic.frequency"),
    permissions={"sound", "device"},
)


AUDIO_ADV = (AUDIO_PLAY_PITCHED, AUDIO_SET_PAN, AUDIO_FADE_IN, AUDIO_FADE_OUT,
             AUDIO_EQUALIZER, AUDIO_MIC_INPUT,
             AUDIO_VOLUME_REPORTER, AUDIO_MIC_FREQUENCY)

assert len(AUDIO_ADV) == 8, f"esperado 8, obtido {len(AUDIO_ADV)}"