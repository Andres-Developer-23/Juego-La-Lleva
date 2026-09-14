"""Modelo que representa a un jugador controlado por la computadora."""

import math
import random

from models.jugador import Jugador


class JugadorIA(Jugador):
    """Clase que representa a un jugador controlado por IA."""

    def __init__(self, x, y, id_jugador, nombre="IA"):
        """Inicializa una IA con posición e identificación.

        Args:
            x (int): Coordenada horizontal inicial.
            y (int): Coordenada vertical inicial.
            id_jugador (int): Identificador único del jugador.
            nombre (str, optional): Nombre del jugador. Por defecto "IA".
        """
        super().__init__(x, y, id_jugador, nombre)
        self.jugadores = []

    def _objetivo(self):
        """Encuentra al otro jugador de la partida.

        Returns:
            Jugador: El jugador contrario o None si no hay oponente.
        """
        for j in self.jugadores:
            if j is not self:
                return j
        return None

    def mover(self, teclas=None, en_zona_lenta=False):
        """Mueve la IA: persigue si es la lleva, huye si no lo es.

        Args:
            teclas: Se ignora (la IA no usa teclado).
            en_zona_lenta (bool): True si el jugador está en una zona que ralentiza.
        """
        objetivo = self._objetivo()
        if objetivo is None:
            return

        dx = objetivo.x - self.x
        dy = objetivo.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return

        velocidad = self.config.VELOCIDAD_JUGADOR
        if en_zona_lenta:
            velocidad *= self.config.FACTOR_RALENTIZACION

        direccion = 1 if self.es_lleva else -1
        paso_x = (dx / dist) * velocidad * direccion + random.uniform(-0.5, 0.5)
        paso_y = (dy / dist) * velocidad * direccion + random.uniform(-0.5, 0.5)

        self.x += paso_x
        self.y += paso_y

        self._limitar_pantalla()
        self.posicion_anterior = (self.x, self.y)