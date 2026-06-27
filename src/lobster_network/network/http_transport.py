"""
HTTP 传输层 - HTTP Transport for Node-to-Node Communication

Replaces the file-only NFS transport with real HTTP communication,
enabling nodes on different machines to exchange messages over the
network using only the Python standard library.

Endpoints served:
    POST /messages/{node_id}  - Deliver a message to *node_id*.
    GET  /messages/{node_id}  - Retrieve and drain pending messages for *node_id*.
    GET  /heartbeat           - Liveness probe.
    GET  /registry/nodes      - List all nodes known to this server.

Usage:
    transport = HTTPTransport(port=8199)
    transport.start_server("0.0.0.0", 8199)

    # Send a message to a remote node
    ok = transport.send_message(
        "http://remote-host:8199",
        {"from_node": "alice", "to_node": "bob", "payload": {...}},
    )

    # Retrieve messages addressed to us
    messages = transport.receive_messages("bob")

    transport.stop_server()
"""

from __future__ import annotations

import json
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_PORT = 8199
_HTTP_TIMEOUT = 10  # seconds – used for all outbound requests
_CONTENT_TYPE = "application/json; charset=utf-8"


# ---------------------------------------------------------------------------
# HTTPTransport
# ---------------------------------------------------------------------------

class HTTPTransport:
    """HTTP-based transport for node-to-node communication.

    Enables real network communication between nodes on different
    machines, replacing the file-only NFS transport.  The server runs
    in a daemon thread so it never blocks the caller.

    Args:
        base_url: Optional public base URL of *this* node (e.g.
            ``"http://192.168.1.10:8199"``).  Used only for self-
            advertisement in registry sync; it is **not** required for
            the server to function.
        port: Default port for :meth:`start_server` when none is given
            explicitly.
    """

    def __init__(self, base_url: Optional[str] = None, port: int = _DEFAULT_PORT):
        self.base_url: Optional[str] = base_url.rstrip("/") if base_url else None
        self.port: int = port

        # Shared mutable state accessed by both the server thread and
        # the main thread – always guard with ``_lock``.
        self._message_store: Dict[str, List[dict]] = {}
        self._node_registry: Dict[str, dict] = {}
        self._lock: threading.Lock = threading.Lock()

        # Server handles – populated by ``start_server``.
        self._server: Optional[HTTPServer] = None
        self._server_thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Client (outbound) API
    # ------------------------------------------------------------------

    def send_message(self, target_node_url: str, message_data: dict) -> bool:
        """POST *message_data* to the remote node's message inbox.

        The target path is derived from the ``"to_node"`` key inside
        *message_data* (falling back to ``"unknown"``).

        Args:
            target_node_url: Base URL of the target node
                (e.g. ``"http://10.0.0.2:8199"``).
            message_data: Arbitrary JSON-serialisable dict.  Should
                contain at least ``"from_node"`` and ``"to_node"``.

        Returns:
            ``True`` if the remote server accepted the message
            (HTTP 201), ``False`` otherwise.
        """
        to_node = message_data.get("to_node", "unknown")
        url = f"{target_node_url.rstrip('/')}/messages/{to_node}"
        body = json.dumps(message_data, ensure_ascii=False).encode("utf-8")

        req = Request(url, data=body, method="POST")
        req.add_header("Content-Type", _CONTENT_TYPE)

        try:
            with urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
                return resp.status == 201
        except (URLError, OSError, ValueError):
            return False

    def receive_messages(self, node_id: str) -> List[dict]:
        """Return and drain all pending messages addressed to *node_id*.

        This reads directly from the local in-memory store (no HTTP
        round-trip) so it is safe and fast to call from the node's own
        process.

        Args:
            node_id: The recipient node identifier.

        Returns:
            A list of message dicts; empty when there is nothing
            queued.
        """
        with self._lock:
            messages = self._message_store.pop(node_id, [])
        return messages

    def heartbeat(self, node_url: str) -> dict:
        """Probe a remote node's ``/heartbeat`` endpoint.

        Args:
            node_url: Base URL of the target node.

        Returns:
            The JSON response dict on success, or
            ``{"status": "offline", "error": "..."}`` on failure.
        """
        url = f"{node_url.rstrip('/')}/heartbeat"
        try:
            with urlopen(url, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (URLError, OSError, ValueError) as exc:
            return {"status": "offline", "error": str(exc)}

    def discover_nodes(self, registry_url: str) -> List[dict]:
        """Fetch the list of active nodes from a remote registry.

        Args:
            registry_url: Base URL of the node acting as the registry
                authority.

        Returns:
            A list of node-info dicts, or an empty list on failure.
        """
        url = f"{registry_url.rstrip('/')}/registry/nodes"
        try:
            with urlopen(url, timeout=_HTTP_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data if isinstance(data, list) else []
        except (URLError, OSError, ValueError):
            return []

    def sync_registry(self, local_nodes: List[dict], registry_url: str) -> dict:
        """Push *local_nodes* to a central registry and merge the reply.

        The remote server is expected to respond with a JSON object
        containing at least a ``"nodes"`` key with the merged node
        list.  On success the local registry cache is updated.

        Args:
            local_nodes: Node-info dicts to advertise.
            registry_url: Base URL of the central registry.

        Returns:
            The full response dict from the registry, or
            ``{"error": "..."}`` on failure.
        """
        url = f"{registry_url.rstrip('/')}/registry/sync"
        body = json.dumps({"nodes": local_nodes}, ensure_ascii=False).encode("utf-8")

        req = Request(url, data=body, method="POST")
        req.add_header("Content-Type", _CONTENT_TYPE)

        try:
            with urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                # Merge returned nodes into the local cache.
                with self._lock:
                    for node in result.get("nodes", []):
                        nid = node.get("node_id")
                        if nid:
                            self._node_registry[nid] = node
                return result
        except (URLError, OSError, ValueError) as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Server (inbound) API
    # ------------------------------------------------------------------

    def register_node(self, node_info: dict) -> None:
        """Add or update a node in the local registry cache.

        This is a convenience helper for populating the registry that
        ``GET /registry/nodes`` serves.

        Args:
            node_info: A dict that must contain at least ``"node_id"``.
        """
        nid = node_info.get("node_id")
        if not nid:
            return
        with self._lock:
            self._node_registry[nid] = node_info

    def start_server(self, host: str = "0.0.0.0", port: Optional[int] = None) -> None:
        """Start the HTTP server in a background daemon thread.

        The server exposes the four endpoints documented at module
        level.  It is safe to call this method at most once; calling
        it again while the server is running is a no-op.

        Args:
            host: Bind address.
            port: Bind port.  Falls back to the instance ``port``
                attribute when *None*.
        """
        if self._server is not None:
            return  # Already running.

        bind_port = port if port is not None else self.port

        # Capture references for the handler closures.
        message_store = self._message_store
        node_registry = self._node_registry
        lock = self._lock

        class _NodeRequestHandler(BaseHTTPRequestHandler):
            """Routes inbound HTTP requests to the transport's stores."""

            # Silence per-request log lines on stderr.
            def log_message(self, fmt: str, *args: object) -> None:  # noqa: D401
                pass

            # ---- GET ----

            def do_GET(self) -> None:  # noqa: N802 (stdlib convention)
                path = self.path.rstrip("/")

                if path.startswith("/messages/"):
                    node_id = path.split("/")[-1]
                    with lock:
                        # Return a copy; do not drain – explicit drain
                        # is done via ``receive_messages``.
                        messages = list(message_store.get(node_id, []))
                    self._send_json(200, messages)

                elif path == "/heartbeat":
                    self._send_json(200, {
                        "status": "ok",
                        "timestamp": datetime.now().isoformat(),
                    })

                elif path == "/registry/nodes":
                    with lock:
                        nodes = list(node_registry.values())
                    self._send_json(200, nodes)

                else:
                    self._send_json(404, {"error": f"Unknown path: {self.path}"})

            # ---- POST ----

            def do_POST(self) -> None:  # noqa: N802
                path = self.path.rstrip("/")

                if path.startswith("/messages/"):
                    node_id = path.split("/")[-1]
                    content_length = int(self.headers.get("Content-Length", 0))
                    raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
                    try:
                        data = json.loads(raw.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        self._send_json(400, {"error": f"Invalid JSON: {exc}"})
                        return

                    with lock:
                        message_store.setdefault(node_id, []).append(data)

                    self._send_json(201, {
                        "status": "received",
                        "node_id": node_id,
                        "queued": len(message_store.get(node_id, [])),
                    })

                elif path == "/registry/sync":
                    content_length = int(self.headers.get("Content-Length", 0))
                    raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
                    try:
                        payload = json.loads(raw.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        self._send_json(400, {"error": f"Invalid JSON: {exc}"})
                        return

                    incoming_nodes = payload.get("nodes", [])
                    with lock:
                        for node in incoming_nodes:
                            nid = node.get("node_id")
                            if nid:
                                node_registry[nid] = node
                        merged = list(node_registry.values())

                    self._send_json(200, {
                        "status": "synced",
                        "nodes": merged,
                        "total": len(merged),
                    })

                else:
                    self._send_json(404, {"error": f"Unknown path: {self.path}"})

            # ---- helpers ----

            def _send_json(self, code: int, data: object) -> None:
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", _CONTENT_TYPE)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self._server = HTTPServer((host, bind_port), _NodeRequestHandler)
        self._server_thread = threading.Thread(
            target=self._server.serve_forever,
            name=f"lobster-http-transport-{bind_port}",
            daemon=True,
        )
        self._server_thread.start()

    def stop_server(self) -> None:
        """Gracefully shut down the HTTP server.

        Blocks until the server thread has exited.  Safe to call even
        when the server was never started.
        """
        server = self._server
        if server is None:
            return

        # ``shutdown()`` must be called from a different thread than the
        # one running ``serve_forever`` – which is always the case here
        # because we call it from the main (or caller's) thread.
        server.shutdown()
        self._server = None

        if self._server_thread is not None:
            self._server_thread.join(timeout=5.0)
            self._server_thread = None

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        """``True`` when the HTTP server is currently listening."""
        return self._server is not None

    def pending_count(self, node_id: Optional[str] = None) -> int:
        """Return the number of queued messages.

        Args:
            node_id: Count only messages for this node.  When *None*
                the total across all nodes is returned.
        """
        with self._lock:
            if node_id is not None:
                return len(self._message_store.get(node_id, []))
            return sum(len(msgs) for msgs in self._message_store.values())

    def __repr__(self) -> str:
        status = "running" if self.is_running else "stopped"
        return (
            f"HTTPTransport(base_url={self.base_url!r}, port={self.port}, "
            f"status={status})"
        )
