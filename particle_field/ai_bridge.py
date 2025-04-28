"""
ai_bridge: OpenAI-driven controller for ParticleField over WebSocket.
"""
import os
import json
import asyncio
import openai
import websockets

class AIFieldBridge:
    """
    Connects to a ParticleField WebSocket and drives it based on OpenAI responses.
    Expects OpenAI to respond with JSON: {"command": ..., "args": [...]}.
    """
    def __init__(self, api_key=None, ws_url="ws://localhost:8000/ws", model="gpt-4"):
        openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.ws_url = ws_url
        self.model = model

    async def connect(self):
        # Try connecting with retries
        retries = 5
        delay = 1.0
        for attempt in range(1, retries + 1):
            try:
                self.ws = await websockets.connect(self.ws_url)
                # receive optional greeting
                try:
                    greeting = await asyncio.wait_for(self.ws.recv(), timeout=2.0)
                    print("Connected to field:", greeting)
                except Exception:
                    pass
                return
            except Exception as e:
                print(f"AIFieldBridge: connect attempt {attempt}/{retries} failed: {e}")
                if attempt < retries:
                    await asyncio.sleep(delay)
        raise RuntimeError(f"AIFieldBridge: could not connect to {self.ws_url}")

    async def send_command(self, command, args=None):
        msg = {"command": command, "args": args or []}
        await self.ws.send(json.dumps(msg))
        resp = await self.ws.recv()
        print("Ack:", resp)

    async def ask_and_drive(self, prompt, temperature=0.7):
        # Ask the model for a JSON command
        # System prompt defines valid commands and JSON-only responses
        system = {
            "role": "system",
            "content": (
                "You are an AI controller for a Python GPU-accelerated particle field. "
                "The only valid JSON commands are:\n"
                "- set_shape(shape_name) where shape_name in [sphere, cube, pyramid, torus, galaxy, wave, helix, lissajous, spiral, trefoil]\n"
                "- set_color(color_name) where color_name in [fire, neon, nature, rainbow]\n"
                "- trigger_morph(duration_ms)\n"
                "- express(emotion, intensity, duration_ms) where emotion in [joy, calm, angry, neutral, surprised, thoughtful, sad, excited]\n"
                "When responding, output ONLY a JSON object with keys 'command' and 'args', e.g. {\"command\":\"set_shape\",\"args\":[\"cube\"]}. "
                "Do not include any additional text or comments. If the user request cannot be mapped, respond with {\"error\":\"<reason>\"}."
            )
        }
        user = {"role": "user", "content": prompt}
        # Prepare parameters
        params = {
            'model': self.model,
            'messages': [system, user],
            'temperature': temperature,
            'max_tokens': 100,
        }
        # Determine which client to use (new OpenAI client vs legacy)
        if hasattr(openai, 'OpenAI'):
            # openai>=1.x: use the new client
            client = openai.OpenAI()
            chat_mod = client.chat.completions
        else:
            # openai<1.0: fallback to old ChatCompletion
            if hasattr(openai, 'ChatCompletion'):
                chat_mod = openai.ChatCompletion
            else:
                # fallback to module path
                chat_mod = openai.chat.completions
        # Perform the request, with optional streaming support
        content = ''
        stream = params.copy()
        stream['stream'] = True
        # Try async streaming
        try:
            if hasattr(chat_mod, 'acreate'):
                # openai>=1.x async stream
                async for chunk in chat_mod.acreate(**stream):
                    delta = getattr(chunk.choices[0].delta, 'content', None)
                    if delta:
                        print(delta, end='', flush=True)
                        content += delta
            else:
                # Legacy sync stream
                for chunk in chat_mod.create(**stream):
                    delta = chunk.choices[0].delta.get('content', '')
                    print(delta, end='', flush=True)
                    content += delta
        except Exception:
            # Fallback to non-streaming
            resp = (await chat_mod.acreate(**params)) if hasattr(chat_mod, 'acreate') else chat_mod.create(**params)
            try:
                content = resp.choices[0].message.content
            except AttributeError:
                # legacy structure
                content = resp.choices[0].text
        # newline after streaming output
        print()
        # Prepare final text: prefer streamed content, else full response
        text = content.strip()
        if not text:
            try:
                text = resp.choices[0].message.content.strip()
            except Exception:
                # legacy field
                text = resp.choices[0].text.strip()
        # Parse one or more JSON objects from text
        decoder = json.JSONDecoder()
        idx = 0
        s = text
        while True:
            s = s.lstrip()
            if not s:
                break
            try:
                obj, offset = decoder.raw_decode(s)
            except Exception as e:
                print("Failed to parse JSON from model:", s, e)
                break
            # Handle error responses without sending to server
            if 'error' in obj:
                print("AI returned error:", obj.get('error'))
            else:
                cmd = obj.get('command')
                args = obj.get('args', [])
                if isinstance(cmd, str):
                    try:
                        await self.send_command(cmd, args)
                    except Exception as e:
                        print(f"Failed to send command {cmd}:", e)
                else:
                    print("No valid command to send, skipping:", obj)
            # Advance past the parsed object
            s = s[offset:]

    async def close(self):
        await self.ws.close()