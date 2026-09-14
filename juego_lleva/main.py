"""Punto de entrada principal del juego La Lleva."""

import asyncio
import sys

import pygame
from core.config import Config
from core.juego import Juego

ES_PLATAFORMA_WEB = sys.platform == "emscripten"


def crear_juego():
    """Inicializa pygame y devuelve una instancia del juego."""
    pygame.init()
    config = Config()
    return Juego(config)


async def _bucle_web(juego):
    """Bucle de juego en la web: cede el control al navegador cada frame."""
    while True:
        juego._procesar_frame()
        await asyncio.sleep(0)


def main():
    """Función principal: ejecuta el juego en escritorio o en la web."""
    juego = crear_juego()
    if ES_PLATAFORMA_WEB:
        asyncio.run(_bucle_web(juego))
    else:
        juego.ejecutar()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()