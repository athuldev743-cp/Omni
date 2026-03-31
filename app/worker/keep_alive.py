import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)

PING_URL = "https://omni-backend-phxz.onrender.com/health"
PING_INTERVAL_SECONDS = 600  # ping every 10 minutes

async def keep_alive():
    """Ping self every 10 min so Render free tier doesn't sleep."""
    await asyncio.sleep(30)  # wait for startup to finish first
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(PING_URL)
                logger.info(f"Keep-alive ping: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Keep-alive ping failed: {e}")
        await asyncio.sleep(PING_INTERVAL_SECONDS)