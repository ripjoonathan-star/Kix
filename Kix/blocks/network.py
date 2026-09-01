"""Blocos de rede: TCP, UDP, HTTP, WebSocket."""

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
from Kix.core.theme import CAT_NETWORK


# ============================================================ TCP (4)
TCP_CONNECT = KixBlock(
    id="net.tcp_connect",
    name="Conectar TCP",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Conectar TCP a "), BlockInput("host"), Text(":"), BlockInput("port")])),
    inputs=[SocketDef("host", SocketKind.STRING, default="127.0.0.1"),
            SocketDef("port", SocketKind.NUMBER, default=8080)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await tcp.connect(self.host, self.port)"),
    permissions={"network"},
)

TCP_SEND = KixBlock(
    id="net.tcp_send",
    name="Enviar TCP",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Enviar "), BlockInput("data"), Text(" via TCP")])),
    inputs=[SocketDef("data", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await tcp.send(self.data.encode())"),
    permissions={"network"},
)

TCP_RECEIVE = KixBlock(
    id="net.tcp_receive",
    name="Receber TCP",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Receber "), BlockInput("nbytes"), Text(" bytes via TCP")])),
    inputs=[SocketDef("nbytes", SocketKind.NUMBER, default=1024)],
    outputs=[SocketDef("data", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return (await tcp.recv(self.nbytes)).decode(errors='replace')"),
    permissions={"network"},
)

TCP_CLOSE = KixBlock(
    id="net.tcp_close",
    name="Fechar TCP",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Fechar TCP")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await tcp.close()"),
    permissions={"network"},
)


# ============================================================ UDP (2)
UDP_SEND = KixBlock(
    id="net.udp_send",
    name="Enviar UDP",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Enviar "), BlockInput("data"), Text(" para "), BlockInput("host"), Text(":"), BlockInput("port"), Text(" via UDP")])),
    inputs=[SocketDef("data", SocketKind.STRING, default=""),
            SocketDef("host", SocketKind.STRING, default="127.0.0.1"),
            SocketDef("port", SocketKind.NUMBER, default=8080)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="udp.sendto(self.data.encode(), (self.host, self.port))"),
    permissions={"network"},
)

UDP_RECEIVE = KixBlock(
    id="net.udp_receive",
    name="Receber UDP",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Receber UDP")])),
    inputs=[],
    outputs=[SocketDef("data", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return udp.recvfrom(4096)[0].decode(errors='replace')"),
    permissions={"network"},
)


# ============================================================ HTTP (5)
HTTP_GET = KixBlock(
    id="net.http_get",
    name="HTTP GET",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("GET "), BlockInput("url")])),
    inputs=[SocketDef("url", SocketKind.STRING, default="https://api.example.com")],
    outputs=[SocketDef("body", SocketKind.STRING),
             SocketDef("status", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="r = await http.get(self.url); return r.text, r.status"),
    permissions={"network"},
)

HTTP_POST = KixBlock(
    id="net.http_post",
    name="HTTP POST",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("POST "), BlockInput("url"), Text(" body "), BlockInput("body")])),
    inputs=[SocketDef("url", SocketKind.STRING, default=""),
            SocketDef("body", SocketKind.STRING, default="{}")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await http.post(self.url, data=self.body)"),
    permissions={"network"},
)

HTTP_PUT = KixBlock(
    id="net.http_put",
    name="HTTP PUT",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("PUT "), BlockInput("url"), Text(" body "), BlockInput("body")])),
    inputs=[SocketDef("url", SocketKind.STRING, default=""),
            SocketDef("body", SocketKind.STRING, default="{}")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await http.put(self.url, data=self.body)"),
    permissions={"network"},
)

HTTP_DELETE = KixBlock(
    id="net.http_delete",
    name="HTTP DELETE",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("DELETE "), BlockInput("url")])),
    inputs=[SocketDef("url", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await http.delete(self.url)"),
    permissions={"network"},
)

HTTP_HEADERS = KixBlock(
    id="net.http_headers",
    name="Definir header",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Header "), BlockInput("key"), Text(" = "), BlockInput("value")])),
    inputs=[SocketDef("key", SocketKind.STRING, default="Content-Type"),
            SocketDef("value", SocketKind.STRING, default="application/json")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="http.headers[self.key] = self.value"),
    permissions={"network"},
)


# ============================================================ WebSocket (3)
WS_CONNECT = KixBlock(
    id="net.ws_connect",
    name="Conectar WebSocket",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Conectar WS a "), BlockInput("url")])),
    inputs=[SocketDef("url", SocketKind.STRING, default="wss://echo.websocket.events")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await ws.connect(self.url)"),
    permissions={"network"},
)

WS_SEND = KixBlock(
    id="net.ws_send",
    name="Enviar WebSocket",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Enviar WS "), BlockInput("data")])),
    inputs=[SocketDef("data", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await ws.send(self.data)"),
    permissions={"network"},
)

WS_RECEIVE = KixBlock(
    id="net.ws_receive",
    name="Receber WebSocket",
    category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("Receber WS")])),
    inputs=[],
    outputs=[SocketDef("message", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return await ws.recv()"),
    permissions={"network"},
)


# --- M3.3: network reporters faltando (3) ---------------------------------
NETWORK_IS_CONNECTED = KixBlock(
    id="network.is_connected", name="conectado à internet", category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("conectado à internet")])),
    inputs=[], outputs=[SocketDef("connected", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return network.is_connected"),
    permissions={"network"},
)
NETWORK_LOCAL_IP = KixBlock(
    id="network.local_ip", name="IP do servidor local", category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("IP do servidor local")])),
    inputs=[], outputs=[SocketDef("ip", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return network.local_ip"),
    permissions={"network"},
)
NETWORK_LOCAL_PORT = KixBlock(
    id="network.local_port", name="porta do servidor local", category="network",
    color=CAT_NETWORK,
    visual=BlockVisual(root=Group(children=[Text("porta do servidor local")])),
    inputs=[], outputs=[SocketDef("port", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return network.local_port"),
    permissions={"network"},
)


NETWORK = (TCP_CONNECT, TCP_SEND, TCP_RECEIVE, TCP_CLOSE,
           UDP_SEND, UDP_RECEIVE,
           HTTP_GET, HTTP_POST, HTTP_PUT, HTTP_DELETE, HTTP_HEADERS,
           WS_CONNECT, WS_SEND, WS_RECEIVE,
           NETWORK_IS_CONNECTED, NETWORK_LOCAL_IP, NETWORK_LOCAL_PORT)

assert len(NETWORK) == 17, f"esperado 17, obtido {len(NETWORK)}"