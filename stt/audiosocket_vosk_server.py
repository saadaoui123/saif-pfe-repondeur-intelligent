import asyncio
import json
import logging
import re
import struct
import time

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.context_loader import load_scenarios, get_context_hint
from llm.ollama_client  import ask_mistral

from vosk import Model, KaldiRecognizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("audiosocket_server.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("AudioSocketSTT")

MODEL_PATH   = "/home/saif/saif_pfe/models/vosk-model-fr-0.22"
HOST         = "0.0.0.0"
PORT         = 6000
SAMPLE_RATE  = 8000
MIN_TEXT_LEN = 3

INTENTS: dict[str, list[str]] = {
    "PRENDRE_RDV":   ["rendez", "rdv", "prendre", "voudrais", "veux", "demain", "aujourdhui"],
    "URGENCE":       ["mal", "douleur", "urgent", "urgence", "dent", "dents", "saigne", "fort"],
    "ANNULER_RDV":   ["annuler", "changer", "modifier", "reporter"],
    "PRIX_HORAIRES": ["combien", "prix", "horaire", "horaires", "ouverts", "ouvert", "tarif"],
    "CONFIRMATION":  ["oui", "ok", "daccord"],
    "NEGATION":      ["non", "pas"],
}

def detect_intent(text: str) -> str:
    for intent, keywords in INTENTS.items():
        if any(kw in text for kw in keywords):
            return intent
    return "UNKNOWN"


logger.info("Chargement du modèle Vosk...")
model = Model(MODEL_PATH)
logger.info("Modèle chargé \n")

SCENARIOS = load_scenarios()
logger.info("Scénarios chargés \n")


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


async def read_packet(reader: asyncio.StreamReader) -> tuple[int | None, bytes | None]:
    """
    Lit un paquet AudioSocket :
      Byte 0     : type  (0x00 = fin, 0x10 = audio PCM)
      Bytes 1-2  : longueur payload (big-endian uint16)
      Bytes 3..N : payload audio
    """
    try:
        header = await reader.readexactly(3)
    except asyncio.IncompleteReadError:
        return None, None

    msg_type = header[0]
    msg_len  = struct.unpack(">H", header[1:3])[0]

    payload = await reader.readexactly(msg_len) if msg_len > 0 else b""
    return msg_type, payload


async def handle_call(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    logger.info("Appel entrant : %s", addr)
    logger.info("─" * 40)

    rec          = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(False)
    last_partial = ""
    start_time   = time.perf_counter()
    conversation = []

    try:
        while True:
            msg_type, payload = await read_packet(reader)

            if msg_type is None:
                break

            if msg_type == 0x00:
                logger.info("Signal fin d'appel reçu")
                break

            if msg_type == 0x10 and payload:

                accepted = await asyncio.to_thread(rec.AcceptWaveform, payload)

                if accepted:
                    raw  = await asyncio.to_thread(rec.Result)
                    text = clean_text(json.loads(raw).get("text", ""))

                    if len(text) >= MIN_TEXT_LEN:
                        latency = time.perf_counter() - start_time
                        intent  = detect_intent(text)

                        logger.info(" FINAL   (%.2fs) : %s", latency, text)
                        logger.info(" INTENT            : %s", intent)
                        logger.info("─" * 40)

                        hint     = get_context_hint(text, SCENARIOS)
                        enriched = f"{hint} Patient dit: {text}" if hint else text

                        conversation.append({"role": "user", "content": enriched})
                        reponse = ask_mistral(conversation)
                        conversation.append({"role": "assistant", "content": reponse})

                        logger.info(" AIDEN             : %s", reponse)
                        logger.info("─" * 40)

                        start_time   = time.perf_counter()
                        last_partial = ""

                else:
                    raw     = await asyncio.to_thread(rec.PartialResult)
                    partial = clean_text(json.loads(raw).get("partial", ""))

                    if partial and partial != last_partial:
                        logger.debug("… PARTIAL : %s", partial)
                        last_partial = partial

    except asyncio.IncompleteReadError:
        logger.info("Connexion fermée par le client : %s", addr)
    except Exception as e:
        logger.exception("Erreur inattendue [%s] : %s", addr, e)
    finally:
        writer.close()
        await writer.wait_closed()
        logger.info("Appel terminé : %s\n", addr)


async def main():
    server = await asyncio.start_server(handle_call, HOST, PORT)
    logger.info("Serveur AudioSocket STT actif → %s:%d\n", HOST, PORT)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Serveur arrêté proprement ⏹")
