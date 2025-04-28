#!/usr/bin/env python3
# Ensure project root is on PYTHONPATH
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(__file__, '..', '..')))
"""
Example script: AI-driven particle field via OpenAI + WebSocket.
"""
import asyncio
import sys
from particle_field.ai_bridge import AIFieldBridge

async def main():
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    bridge = AIFieldBridge(api_key=api_key)
    await bridge.connect()
    print("Enter your command prompt (e.g., 'make the field happy'):")
    while True:
        prompt = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        prompt = prompt.strip()
        if not prompt:
            continue
        if prompt.lower() in ('exit', 'quit'):
            break
        await bridge.ask_and_drive(prompt)
    await bridge.close()

if __name__ == '__main__':
    asyncio.run(main())