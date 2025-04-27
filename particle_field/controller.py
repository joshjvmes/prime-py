"""
FieldController: a simple TCP JSON controller for remote clients to drive a ParticleField.
"""
import json
import threading
import socketserver

class FieldController:
    """
    Launches a TCP server to receive JSON commands and invoke methods on a ParticleField instance.
    Each JSON message should have the form:
      {"command": "method_name", "args": [arg1, arg2, ...]}
    """
    def __init__(self, field, host='localhost', port=8765):
        self.field = field
        self.host = host
        self.port = port
        # track connected clients (sockets)
        self.clients = []
        # register for field events
        try:
            self.field.add_listener(self._on_event)
        except Exception:
            pass
        # Define request handler class
        controller = self
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                # Add this client to list
                controller.clients.append(self.request)
                self.request.sendall(b'Connected to ParticleField Controller\n')
                file = self.request.makefile('r')
                try:
                    for line in file:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            msg = json.loads(line)
                            cmd = msg.get('command')
                            args = msg.get('args', [])
                            if hasattr(controller.field, cmd):
                                getattr(controller.field, cmd)(*args)
                                self.request.sendall(b'OK\n')
                            else:
                                self.request.sendall(b'ERROR: unknown command\n')
                        except Exception as e:
                            err = f'ERROR: {e}\n'.encode('utf-8')
                            self.request.sendall(err)
                finally:
                    # Remove client on disconnect
                    if self.request in controller.clients:
                        controller.clients.remove(self.request)
        # Create server
        self.server = socketserver.ThreadingTCPServer((host, port), Handler)
        # Run server in background thread
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f'FieldController listening on {host}:{port}')

    def shutdown(self):
        """Shutdown the controller server."""
        self.server.shutdown()
        self.thread.join()
    
    def _on_event(self, msg):
        """Internal callback: broadcast events to all clients."""
        data = (json.dumps(msg) + '\n').encode('utf-8')
        for sock in list(self.clients):
            try:
                sock.sendall(data)
            except Exception:
                self.clients.remove(sock)