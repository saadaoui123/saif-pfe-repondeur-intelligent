

import asyncio
import websockets
import wave
import json
import logging
import os

# ─── Logger 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("VoskClient")

AUDIO_FILE = "/home/saif/test.wav"
WS_URL     = "ws://127.0.0.1:2700"
CHUNK_SIZE = 4000


async def receive_results(ws):
    """Tâche dédiée à la réception des résultats."""
    async for raw in ws:
        r = json.loads(raw)
        if r["type"] == "final":
            logger.info("✅ FINAL   : %s", r["text"])
        else:
            logger.debug("… PARTIAL : %s", r["text"])


async def test_stt():
    logger.info("Connexion au serveur STT → %s", WS_URL)

    if not os.path.exists(AUDIO_FILE):
        logger.error("Fichier introuvable : %s", AUDIO_FILE)
        return

    try:
        async with websockets.connect(WS_URL) as ws:
            logger.info("Connecté ✅")

            recv_task = asyncio.create_task(receive_results(ws))

            with wave.open(AUDIO_FILE, "rb") as wf:
                logger.info("Envoi de l'audio : %s", AUDIO_FILE)
                while True:
                    data = wf.readframes(CHUNK_SIZE)
                    if not data:
                        break
                    await ws.send(data)

            await asyncio.wait_for(recv_task, timeout=2.0)

    except asyncio.TimeoutError:
        logger.info("Fin de réception (timeout normal)")
    except Exception as e:
        logger.exception("Erreur : %s", e)

    logger.info("Test terminé ✅")


if __name__ == "__main__":
    asyncio.run(test_stt())