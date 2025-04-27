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
        # Define request handler class
        controller = self
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                self.request.sendall(b'ParticleField Controller connected\n')
                file = self.request.makefile('r')
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        cmd = msg.get('command')
                        args = msg.get('args', [])
                        if hasattr(controller.field, cmd):
                            fn = getattr(controller.field, cmd)
                            fn(*args)
                            self.request.sendall(b'OK\n')
                        else:
                            self.request.sendall(b'ERROR: unknown command\n')
                    except Exception as e:
                        err = f'ERROR: {e}\n'.encode('utf-8')
                        self.request.sendall(err)
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