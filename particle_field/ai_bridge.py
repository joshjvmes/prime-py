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
        system = {"role": "system", "content": "You control a particle field. Respond with JSON {command, args}."}
        user = {"role": "user", "content": prompt}
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[system, user],
            temperature=temperature,
            max_tokens=100,
        )
        content = resp.choices[0].message.content.strip()
        try:
            cmd = json.loads(content)
            await self.send_command(cmd.get("command"), cmd.get("args", []))
        except Exception as e:
            print("Failed to parse JSON from model:", content, e)

    async def close(self):
        await self.ws.close()