

import asyncio
import logging
import struct

# ─── Logger 
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("debug_server.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("DebugServer")

HOST = "0.0.0.0"
PORT = 6000


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr  = writer.get_extra_info("peername")
    total = 0
    logger.info("Client connecté : %s", addr)

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                logger.info("Client déconnecté : %s", addr)
                break

            total += len(data)
            logger.debug("Reçu %d bytes (total : %d)", len(data), total)
            logger.debug("HEX [0:32] : %s", data[:32].hex())
            logger.debug("Byte[0] type : 0x%02x", data[0])

            if len(data) >= 3:
                msg_len = struct.unpack(">H", data[1:3])[0]
                logger.debug("Length field : %d", msg_len)

    except Exception as e:
        logger.exception("Erreur client [%s] : %s", addr, e)
    finally:
        writer.close()
        await writer.wait_closed()
        logger.info("Session fermée : %s | Total reçu : %d bytes", addr, total)


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    logger.info("Debug server actif → %s:%d", HOST, PORT)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())