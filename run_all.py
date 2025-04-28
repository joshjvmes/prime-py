"""
run_all.py: Unified launcher to start WebSocket server, VisPy canvas, and AI bridge.
Usage:
  python run_all.py [--no-web] [--no-vispy] [--no-ai]
Environment:
  OPENAI_API_KEY must be set for AI mode.
"""
import os
import sys
import argparse
import threading
import webbrowser
import time
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

from ws_server import app, field
from vispy import app as vispy_app
from particle_field.ai_bridge import AIFieldBridge

def start_web():
    """Start the FastAPI WebSocket server."""
    try:
        import uvicorn
        port = int(os.environ.get('PORT', 8000))
        logger.info(f"Starting WebSocket server on port {port}")
        uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')
    except Exception as e:
        logger.exception("WebSocket server failed to start")

def start_ai():
    """Start the AI bridge REPL loop asynchronously."""
    async def ai_loop():
        try:
            bridge = AIFieldBridge()
            await bridge.connect()
            logger.info("AI Bridge connected. Enter prompts (exit to quit):")
            loop = asyncio.get_event_loop()
            while True:
                prompt = await loop.run_in_executor(None, sys.stdin.readline)
                if not prompt:
                    continue
                prompt = prompt.strip()
                if prompt.lower() in ('exit', 'quit'):
                    break
                await bridge.ask_and_drive(prompt)
            await bridge.close()
        except Exception:
            logger.exception("AI Bridge encountered an error")
    asyncio.run(ai_loop())

def main():
    parser = argparse.ArgumentParser(description="Unified launcher for ParticleField system.")
    parser.add_argument('--no-web', action='store_true', help='Disable WebSocket server')
    parser.add_argument('--no-vispy', action='store_true', help='Disable VisPy canvas')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI bridge')
    args = parser.parse_args()

    if not args.no_web:
        threading.Thread(target=start_web, daemon=True).start()
        logger.info("WebSocket server launching...")
        # Open browser after short delay
        port = os.environ.get('PORT', '8000')
        url = f"http://localhost:{port}/"
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
        # Wait for server to be up before starting AI
        time.sleep(2.0)
    if not args.no_ai:
        threading.Thread(target=start_ai, daemon=True).start()
        logger.info("AI Bridge launching...")
    if not args.no_vispy:
        logger.info("Starting VisPy canvas...")
        vispy_app.run()
    else:
        logger.info("VisPy disabled; main loop idle.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down main loop")

if __name__ == '__main__':
    main()