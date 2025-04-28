import json
import pytest
from fastapi.testclient import TestClient
from ws_server import app

@pytest.fixture(scope='module')
def client():
    return TestClient(app)

def test_ws_command_ack(client):
    # Connect to WebSocket and send a valid command
    with client.websocket_connect('/ws') as ws:
        # Send set_shape command
        cmd = {"command": "set_shape", "args": ["sphere"]}
        ws.send_text(json.dumps(cmd))
        # Expect acknowledgment
        data = ws.receive_text()
        msg = json.loads(data)
        assert msg.get('ack') == 'set_shape'
        assert msg.get('args') == ['sphere']

def test_ws_unknown_command(client):
    with client.websocket_connect('/ws') as ws:
        cmd = {"command": "no_such_cmd", "args": []}
        ws.send_text(json.dumps(cmd))
        data = ws.receive_text()
        msg = json.loads(data)
        assert 'error' in msg and 'Unknown command' in msg['error']