"""Blocos de áudio avançado (pitch, pan, fade, mic) + Som+ (M8).

M8: rename de "audio_advanced" para "Som+" na UI — categoria alinhada
com a cor canônica ``CAT_SOUND`` (Pocket Code). Blocos existentes
mantêm o ``category="audio_advanced"`` por compatibilidade com
projetos salvos; novos blocos Som+ usam ``category="sound"`` para
receber a cor nova.

Decisão Catroid: o app original repete o bloco "tocar som" 5 vezes
em níveis de abstração diferentes sem ganho real. Som+ adiciona
controles de produção musical (EQ, pan, ducking, crossfade) sem
duplicar blocos.
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
from Kix.core.theme import CAT_AUDIO_ADV, CAT_SOUND, CAT_SOUND_LIGHT


# --- Base (8 blocos M3.3) — cor legacy CAT_AUDIO_ADV ---------------------
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
AUDIO_VOLUME_REPORTER = KixBlock(
    id="audio.volume_reporter", name="volume", category="sound",
    color=CAT_SOUND_LIGHT,
    visual=BlockVisual(root=Group(children=[Text("volume")])),
    inputs=[], outputs=[SocketDef("volume", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return audio.volume"),
    permissions={"sound"},
)
AUDIO_MIC_FREQUENCY = KixBlock(
    id="audio.mic.frequency", name="frequência do som do microfone",
    category="sound", color=CAT_SOUND_LIGHT,
    visual=BlockVisual(root=Group(children=[Text("frequência do microfone")])),
    inputs=[], outputs=[SocketDef("frequency", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return audio.mic.frequency"),
    permissions={"sound", "device"},
)


# ============================================================ Som+ (M8 — +10)
# Melhorias sobre o áudio do Catroid: crossfade, ducking, EQ preset,
# pan estéreo amplo, reverb e delay como efeitos, loop on/off. Cor
# canônica ``CAT_SOUND`` (Pocket Code) — categoria alinhada com a paleta.
SOUND_FADE_IN_V2 = KixBlock(
    id="sound.fade_in",
    name="Fade in (s)",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Fade in "), BlockInput("seconds"), Text(" s")])),
    inputs=[SocketDef("seconds", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior("python", "await audio.fade_in(float(self.seconds))"),
    permissions={"sound"},
)

SOUND_FADE_OUT_V2 = KixBlock(
    id="sound.fade_out",
    name="Fade out (s)",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Fade out "), BlockInput("seconds"), Text(" s")])),
    inputs=[SocketDef("seconds", SocketKind.NUMBER, default=2.0)],
    outputs=[],
    behavior=BlockBehavior("python", "await audio.fade_out(float(self.seconds))"),
    permissions={"sound"},
)

SOUND_CROSSFADE = KixBlock(
    id="sound.crossfade",
    name="Crossfade",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[
        Text("Crossfade de "), BlockInput("from_sound"),
        Text(" para "), BlockInput("to_sound"),
        Text(" em "), BlockInput("seconds"), Text(" s"),
    ])),
    inputs=[SocketDef("from_sound", SocketKind.SOUND),
            SocketDef("to_sound", SocketKind.SOUND),
            SocketDef("seconds", SocketKind.NUMBER, default=3.0)],
    outputs=[],
    behavior=BlockBehavior("python",
        "await audio.crossfade(self.from_sound, self.to_sound, float(self.seconds))"),
    permissions={"sound"},
)

SOUND_EQ_PRESET = KixBlock(
    id="sound.eq_preset",
    name="Equalizador (preset)",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("EQ preset "), BlockInput("preset")])),
    inputs=[SocketDef("preset", SocketKind.STRING, default="flat")],
    outputs=[],
    behavior=BlockBehavior("python", "audio.eq_preset(self.preset)"),
    permissions={"sound"},
)

SOUND_PAN_STEREO = KixBlock(
    id="sound.pan_stereo",
    name="Pan estéreo",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Pan estéreo "), BlockInput("pan"), Text(" (-1 esq / 1 dir)")])),
    inputs=[SocketDef("pan", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior("python", "audio.pan = float(self.pan)"),
    permissions={"sound"},
)

SOUND_REVERB_ROOM = KixBlock(
    id="sound.reverb_room",
    name="Reverb sala",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Reverb sala intensidade "), BlockInput("amount")])),
    inputs=[SocketDef("amount", SocketKind.NUMBER, default=0.3)],
    outputs=[],
    behavior=BlockBehavior("python", "audio.reverb('room', float(self.amount))"),
    permissions={"sound"},
)

SOUND_REVERB_CAVE = KixBlock(
    id="sound.reverb_cave",
    name="Reverb caverna",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Reverb caverna intensidade "), BlockInput("amount")])),
    inputs=[SocketDef("amount", SocketKind.NUMBER, default=0.6)],
    outputs=[],
    behavior=BlockBehavior("python", "audio.reverb('cave', float(self.amount))"),
    permissions={"sound"},
)

SOUND_DELAY = KixBlock(
    id="sound.delay",
    name="Delay",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[
        Text("Delay "), BlockInput("ms"),
        Text(" ms feedback "), BlockInput("feedback"),
    ])),
    inputs=[SocketDef("ms", SocketKind.NUMBER, default=250),
            SocketDef("feedback", SocketKind.NUMBER, default=0.4)],
    outputs=[],
    behavior=BlockBehavior("python",
        "audio.delay(int(self.ms), float(self.feedback))"),
    permissions={"sound"},
)

SOUND_LOOP = KixBlock(
    id="sound.loop",
    name="Loop on/off",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[
        Text("Som "), BlockInput("sound"),
        Text(" loop "), BlockInput("on"),
    ])),
    inputs=[SocketDef("sound", SocketKind.SOUND),
            SocketDef("on", SocketKind.BOOLEAN, default=True)],
    outputs=[],
    behavior=BlockBehavior("python",
        "audio.loop(self.sound, bool(self.on))"),
    permissions={"sound"},
)

SOUND_DUCKING = KixBlock(
    id="sound.ducking",
    name="Ducking (música abaixa com voz)",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[
        Text("Ducking: música "), BlockInput("music"),
        Text(" voz "), BlockInput("voice"),
        Text(" redução "), BlockInput("reduction"), Text(" dB"),
    ])),
    inputs=[SocketDef("music", SocketKind.SOUND),
            SocketDef("voice", SocketKind.SOUND),
            SocketDef("reduction", SocketKind.NUMBER, default=12)],
    outputs=[],
    behavior=BlockBehavior("python",
        "audio.ducking(self.music, self.voice, float(self.reduction))"),
    permissions={"sound"},
)


AUDIO_ADV = (AUDIO_PLAY_PITCHED, AUDIO_SET_PAN, AUDIO_FADE_IN, AUDIO_FADE_OUT,
             AUDIO_EQUALIZER, AUDIO_MIC_INPUT,
             AUDIO_VOLUME_REPORTER, AUDIO_MIC_FREQUENCY,
             # Som+ (M8)
             SOUND_FADE_IN_V2, SOUND_FADE_OUT_V2, SOUND_CROSSFADE,
             SOUND_EQ_PRESET, SOUND_PAN_STEREO,
             SOUND_REVERB_ROOM, SOUND_REVERB_CAVE, SOUND_DELAY,
             SOUND_LOOP, SOUND_DUCKING)

assert len(AUDIO_ADV) == 18, f"esperado 18 (8 base + 10 Som+), obtido {len(AUDIO_ADV)}"