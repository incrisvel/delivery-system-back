import asyncio
import json
import socket
import uuid
from typing import Optional, Dict, Tuple

from fastapi.websockets import WebSocketState
import websockets
from fastapi import WebSocket


class RingNode:
    HEARTBEAT_INTERVAL = 1.0
    HEARTBEAT_TIMEOUT = 4.0
    RECONNECT_DELAY = 2.0
    DISCOVERY_PORT = 9999
    DISCOVERY_DURATION = 3.0
    DISCOVERY_INTERVAL = 0.2

    def __init__(
        self,
        my_address: str,
        websocket_path: str = "/ws/ring",
        node_id: Optional[str] = None,
    ):
        self.node_id = node_id or str(uuid.uuid4())[:8]
        self.my_address = my_address.rstrip("/")
        self.websocket_path = websocket_path
        self.ws_address = self.my_address.replace("http://", "ws://") + websocket_path

        self.next_ws_address: Optional[str] = None
        self.next_node_id: Optional[str] = None

        self.is_coordinator = False
        self.coordinator_id: Optional[str] = None
        self.coordinator_addr: Optional[str] = None

        self._running = False
        self._last_heartbeat = 0.0
        self._ws_send_lock = asyncio.Lock()
        self._next_ws = None
        self._tasks = []
        self._peers: Dict[str, Tuple[str, str]] = {}
        self._election_in_progress = False

    async def discover_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(False)
        try:
            sock.bind(("127.0.0.1", self.DISCOVERY_PORT))
        except Exception:
            sock.bind(("127.0.0.1", 0))

        msg = json.dumps(
            {
                "type": "DISCOVER",
                "node_id": self.node_id,
                "http_addr": self.my_address,
                "ws_addr": self.ws_address,
            }
        ).encode()
        end = asyncio.get_event_loop().time() + self.DISCOVERY_DURATION

        while asyncio.get_event_loop().time() < end:
            try:
                sock.sendto(msg, ("127.0.0.1", self.DISCOVERY_PORT))
            except Exception:
                pass
            
            while True:
                try:
                    data, _ = sock.recvfrom(4096)
                    p = json.loads(data.decode())
                    if p.get("type") == "DISCOVER" and p.get("node_id") != self.node_id:
                        self._peers[p["node_id"]] = (
                            p["http_addr"].rstrip("/"),
                            p["ws_addr"],
                        )
                except BlockingIOError:
                    break
                except Exception:
                    break
            await asyncio.sleep(self.DISCOVERY_INTERVAL)

        self._peers[self.node_id] = (self.my_address, self.ws_address)
        sock.close()

    async def start(self):
        print(f"Iniciando nó {self.node_id} na porta {self.my_address.split(':')[-1]}")

        await self.discover_peers()

        if len(self._peers) <= 1:
            print("Nenhum peer encontrado na primeira tentativa. Tentando novamente...")
            await asyncio.sleep(1)
            await self.discover_peers()

        await self._reform_ring()
        self._running = True
        self._last_heartbeat = asyncio.get_event_loop().time()

        loop = asyncio.get_event_loop()
        self._tasks = [
            loop.create_task(self._run_client()),
            loop.create_task(self._heartbeat_monitor()),
            loop.create_task(self._periodic_rediscovery()),
        ]

    async def _reform_ring(self):
        peers = dict(self._peers)
        sorted_ids = sorted(peers.keys())
        my_idx = sorted_ids.index(self.node_id)
        next_idx = (my_idx + 1) % len(sorted_ids)
        next_id = sorted_ids[next_idx]
        next_ws = peers[next_id][1]

        if len(sorted_ids) == 1 and sorted_ids[0] == self.node_id:
            print("Sou o único sobrevivente → assumindo como coordenador IMEDIATAMENTE")
            self.next_ws_address = None
            self.next_node_id = None
            self.is_coordinator = True
            self.coordinator_id = self.node_id
            self.coordinator_addr = self.my_address

            if self._next_ws:
                try:
                    await self._next_ws.close()
                except Exception:
                    pass
                self._next_ws = None
            return

        if next_ws != self.next_ws_address:
            print(f"Anel formado → próximo nó: {next_id} ({next_ws})")
            self.next_node_id = next_id
            self.next_ws_address = next_ws
            
            if self._next_ws:
                try:
                    await self._next_ws.close()
                except Exception:
                    pass
                self._next_ws = None

    async def _periodic_rediscovery(self):
        while self._running:
            await asyncio.sleep(5.0)
            if len(self._peers) <= 1 or (self.next_ws_address and not self._next_ws):
                old = len(self._peers)
                await self.discover_peers()
                if len(self._peers) > old:
                    await self._reform_ring()

    async def _run_client(self):
        while self._running:
            if not self.next_ws_address:
                await asyncio.sleep(1)
                continue

            try:
                print(f"Conectando ao próximo nó: {self.next_ws_address}")
                async with websockets.connect(
                    self.next_ws_address, ping_interval=None
                ) as ws:
                    self._next_ws = ws

                    await asyncio.gather(
                        self._send_heartbeat(ws), self._receive_from_next(ws)
                    )
            except Exception as e:
                error_msg = str(e)
                is_dead_node = (
                    isinstance(e, ConnectionRefusedError)
                    or "111" in error_msg  # Linux
                    or "10061" in error_msg  # Windows
                    or "1225" in error_msg  # Windows
                    or "recusou a conexão" in error_msg
                    or "Connection refused" in error_msg
                )

                if is_dead_node:
                    print(
                        f"CRÍTICO: Nó {self.next_node_id} morreu (Conexão Recusada: {error_msg}). Removendo do anel."
                    )

                    if self.next_node_id in self._peers:
                        del self._peers[self.next_node_id]

                    await self._reform_ring()

                    if not self.is_coordinator and len(self._peers) > 1:
                        asyncio.create_task(self.start_election())
                else:
                    print(
                        f"Conexão com próximo perdida (Tentando reconectar): {error_msg}"
                    )

                self._next_ws = None
                await asyncio.sleep(self.RECONNECT_DELAY)

    async def _send_heartbeat(self, ws):
        while True:
            try:
                await ws.send(json.dumps({"type": "HEARTBEAT", "from": self.node_id}))
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
            except Exception:
                break

    async def _receive_from_next(self, ws):
        while True:
            try:
                data = await asyncio.wait_for(ws.recv(), timeout=10)
                msg = json.loads(data)
                await self._handle_message(msg)
            except Exception:
                break

    async def _heartbeat_monitor(self):
        while self._running:
            if (
                self.next_ws_address
                and (asyncio.get_event_loop().time() - self._last_heartbeat)
                > self.HEARTBEAT_TIMEOUT
            ):
                print("Próximo nó não responde → iniciando eleição")
                await self.start_election()
            await asyncio.sleep(0.5)

    async def start_election(self):
        if self._election_in_progress:
            return
        self._election_in_progress = True
        print(f"Iniciando eleição (ID: {self.node_id})")
        try:
            await self._send_to_next(
                {"type": "ELECTION", "ids": [self.node_id], "origin": self.node_id}
            )
        finally:
            await asyncio.sleep(1)
            self._election_in_progress = False

    async def _handle_message(self, msg: dict):
        type = msg.get("type")

        if type in ["HEARTBEAT", "HEARTBEAT_ACK"]:
            self._last_heartbeat = asyncio.get_event_loop().time()

        elif type == "ELECTION":
            ids = msg.get("ids", [])
            origin = msg.get("origin")
            if self.node_id not in ids:
                ids.append(self.node_id)
            if origin == self.node_id:
                winner = max(ids)
                await self._broadcast_coordinator(winner)
            else:
                await asyncio.sleep(0.08)
                await self._send_to_next(
                    {"type": "ELECTION", "ids": ids, "origin": origin}
                )
        elif type == "COORDINATOR":
            self.coordinator_id = msg.get("coordinator_id")
            self.coordinator_addr = msg.get("coordinator_addr")
            self.is_coordinator = self.node_id == self.coordinator_id
            
            print(f"Coordenador: {self.coordinator_id} | Eu sou? {self.is_coordinator}")
            
            if msg.get("origin") != self.node_id:
                await asyncio.sleep(0.08)
                await self._send_to_next(msg)

    async def _broadcast_coordinator(self, coord_id: str):
        await self._send_to_next(
            {
                "type": "COORDINATOR",
                "coordinator_id": coord_id,
                "coordinator_addr": self.my_address
                if coord_id == self.node_id
                else self.coordinator_addr,
                "origin": self.node_id,
            }
        )

    async def _send_to_next(self, msg: dict):
        async with self._ws_send_lock:
            if self._next_ws:
                try:
                    await self._next_ws.send(json.dumps(msg))
                    return
                except Exception:
                    pass
                
            if self.next_ws_address:
                try:
                    async with websockets.connect(
                        self.next_ws_address, ping_interval=None, open_timeout=3
                    ) as ws:
                        await ws.send(json.dumps(msg))
                except Exception as e:
                    print(f"Falha ao enviar: {e}")

    async def handle_incoming_ws(self, websocket: WebSocket):
        await websocket.accept()
        try:
            async for data in websocket.iter_text():
                msg = json.loads(data)

                if msg.get("type") == "HEARTBEAT":
                    self._last_heartbeat = asyncio.get_event_loop().time()

                    await websocket.send_text(
                        json.dumps({"type": "HEARTBEAT_ACK", "from": self.node_id})
                    )

                await self._handle_message(msg)
        except Exception as e:
            print(f"Incoming WS fechado: {e}")
        finally:
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.close()
                except RuntimeError:
                    pass

    async def stop(self):
        self._running = False
        for t in self._tasks:
            if not t.done():
                t.cancel()
        if self._next_ws:
            try:
                await self._next_ws.close()
            except Exception:
                pass
