"""Punto de entrada principal del juego La Lleva."""

import sys

import pygame
from core.config import Config
from core.juego import Juego


def main():
    """Función principal que inicializa y ejecuta el juego."""
    pygame.init()
    config = Config()
    juego = Juego(config)
    juego.ejecutar()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
