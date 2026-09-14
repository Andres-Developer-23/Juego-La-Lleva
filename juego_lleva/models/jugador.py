"""Modelo que representa a un jugador en el juego."""

import pygame
from core.config import Config
from interfaces.movible import Movible


class Jugador(Movible):
    """Clase que representa a un jugador con posición, estado y comportamiento de movimiento."""

    def __init__(self, x, y, id_jugador, nombre=None):
        """Inicializa un jugador con posición y identificación.

        Args:
            x (int): Coordenada horizontal inicial.
            y (int): Coordenada vertical inicial.
            id_jugador (int): Identificador único del jugador.
            nombre (str, optional): Nombre del jugador. Por defecto "J{id+1}".
        """
        self.x = x
        self.y = y
        self.id = id_jugador
        self.nombre = nombre or f"J{id_jugador + 1}"
        self._es_lleva = False
        self.config = Config()
        self.posicion_anterior = (x, y)
        self.factor_velocidad = 1.0
        self.escudo = False
        self.congelado = 0.0

    def obtener_posicion(self):
        """Obtiene la posición actual del jugador.

        Returns:
            tuple: Coordenadas (x, y) de la posición actual.
        """
        return (self.x, self.y)

    def _limitar_pantalla(self):
        """Limita la posición del jugador a los bordes de la pantalla."""
        self.x = max(0, min(self.x, self.config.ANCHO_PANTALLA - self.config.TAMAÑO_JUGADOR))
        self.y = max(0, min(self.y, self.config.ALTO_PANTALLA - self.config.TAMAÑO_JUGADOR))

    def obtener_rectangulo(self):
        """Obtiene el rectángulo de colisión del jugador.

        Returns:
            pygame.Rect: Rectángulo que define los límites del jugador para colisiones.
        """
        margen = int(self.config.TAMAÑO_JUGADOR * 0.2)
        return pygame.Rect(
            self.x + margen, self.y + margen,
            self.config.TAMAÑO_JUGADOR - margen * 2,
            self.config.TAMAÑO_JUGADOR - margen * 2
        )

    @property
    def es_lleva(self):
        """Indica si el jugador tiene la pelota (la lleva).

        Returns:
            bool: True si el jugador tiene la pelota, False en caso contrario.
        """
        return self._es_lleva

    @es_lleva.setter
    def es_lleva(self, valor):
        """Establece si el jugador tiene la pelota.

        Args:
            valor (bool): True si el jugador tiene la pelota, False en caso contrario.
        """
        self._es_lleva = valor