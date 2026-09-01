"""Sensores extras Catroid: GPS, NFC, bússola, luz, proximidade, inclinação.

Stubs honestos: cada reporter lê do `ctx.services.device` (ou
`physics`, etc.). Os valores não vêm de hardware real aqui — são
placeholders que o usuário pode setar via testes ou via uma futura
ponte Android. O importante é que a forma existe na paleta e roda.
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
from Kix.core.theme import CAT_DEVICE as CAT_SENSING  # alias


# ============================================================ GPS
GPS_LAT = KixBlock(
    id="sensing.gps_lat", name="latitude", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("latitude GPS")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.gps[0]"),
    permissions={"sensing"},
)
GPS_LNG = KixBlock(
    id="sensing.gps_lng", name="longitude", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("longitude GPS")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.gps[1]"),
    permissions={"sensing"},
)
GPS_ALT = KixBlock(
    id="sensing.gps_altitude", name="altitude", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("altitude GPS")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.gps[2]"),
    permissions={"sensing"},
)
GPS_ACCURACY = KixBlock(
    id="sensing.gps_accuracy", name="precisão GPS", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("precisão GPS (m)")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.gps_accuracy"),
    permissions={"sensing"},
)

# ============================================================ Bússola / orientação
COMPASS = KixBlock(
    id="sensing.compass", name="bússola", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("direção bússola (°)")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.compass"),
    permissions={"sensing"},
)

# ============================================================ Inclinação / acelerômetro
TILT_X = KixBlock(
    id="sensing.tilt_x", name="inclinação X", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("inclinação X")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.tilt[0]"),
    permissions={"sensing"},
)
TILT_Y = KixBlock(
    id="sensing.tilt_y", name="inclinação Y", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("inclinação Y")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.tilt[1]"),
    permissions={"sensing"},
)

# ============================================================ Ambiente
LIGHT = KixBlock(
    id="sensing.light", name="luz", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("sensor de luz")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.light"),
    permissions={"sensing"},
)
PROXIMITY = KixBlock(
    id="sensing.proximity", name="proximidade", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("sensor de proximidade")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.proximity"),
    permissions={"sensing"},
)
NOISE = KixBlock(
    id="sensing.noise", name="ruído", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("nível de ruído (dB)")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.noise"),
    permissions={"sensing"},
)
TEMPERATURE = KixBlock(
    id="sensing.temperature", name="temperatura", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("temperatura (°C)")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.temperature"),
    permissions={"sensing"},
)
HUMIDITY = KixBlock(
    id="sensing.humidity", name="umidade", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("umidade (%)")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.humidity"),
    permissions={"sensing"},
)
PRESSURE = KixBlock(
    id="sensing.pressure", name="pressão", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("pressão (hPa)")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.pressure"),
    permissions={"sensing"},
)

# ============================================================ NFC
NFC_LAST = KixBlock(
    id="sensing.nfc_last_tag", name="última tag NFC", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("última tag NFC lida")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return ctx.services.device.nfc_last_tag"),
    permissions={"sensing"},
)
NFC_HAS_READ = KixBlock(
    id="sensing.nfc_has_read", name="NFC foi lido?", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("leu NFC?")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return bool(ctx.services.device.nfc_last_tag)"),
    permissions={"sensing"},
)

# ============================================================ Face detection / OCR (stubs honestos)
FACE_COUNT = KixBlock(
    id="sensing.face_count", name="qtd. rostos", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("quantos rostos na câmera")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(
        language="python",
        source="raise NotImplementedError('face detection requer módulo nativo')",
    ),
    permissions={"sensing", "camera"},
)
TEXT_RECOGNIZED = KixBlock(
    id="sensing.text_recognized", name="texto OCR", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("texto reconhecido")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.STRING)],
    behavior=BlockBehavior(
        language="python",
        source="raise NotImplementedError('OCR requer módulo nativo')",
    ),
    permissions={"sensing", "camera"},
)

# ============================================================ Speech (stub)
SPEECH_RECOGNIZED = KixBlock(
    id="sensing.speech_recognized", name="fala reconhecida", category="sensing", color=CAT_SENSING,
    visual=BlockVisual(root=Group(children=[Text("última fala reconhecida")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.STRING)],
    behavior=BlockBehavior(
        language="python",
        source="return ctx.services.device.last_speech",
    ),
    permissions={"sensing", "audio"},
)

SENSORS = (
    GPS_LAT, GPS_LNG, GPS_ALT, GPS_ACCURACY, COMPASS,
    TILT_X, TILT_Y,
    LIGHT, PROXIMITY, NOISE, TEMPERATURE, HUMIDITY, PRESSURE,
    NFC_LAST, NFC_HAS_READ,
    FACE_COUNT, TEXT_RECOGNIZED, SPEECH_RECOGNIZED,
)
