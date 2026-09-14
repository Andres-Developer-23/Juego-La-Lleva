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

    def mover(self, teclas=None, en_zona_lenta=False, delta_tiempo=None):
        """Mueve la IA: persigue si es la lleva, huye si no lo es.

        La IA es ligeramente más lenta que el jugador humano y huye aún más
        despacio, para que la partida sea desafiante pero ganable.

        Args:
            teclas: Se ignora (la IA no usa teclado).
            en_zona_lenta (bool): True si el jugador está en una zona que ralentiza.
            delta_tiempo (float, optional): Tiempo transcurrido en segundos.
                Por defecto equivale a un frame (1/FPS).
        """
        objetivo = self._objetivo()
        if objetivo is None:
            return

        dx = objetivo.x - self.x
        dy = objetivo.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return

        dt = delta_tiempo if delta_tiempo is not None else 1.0 / self.config.FPS

        velocidad = self.config.VELOCIDAD_IA * dt
        if en_zona_lenta:
            velocidad *= self.config.FACTOR_RALENTIZACION
        if self.es_lleva:
            velocidad *= self.config.FACTOR_IA_HUYENDO

        direccion = 1 if self.es_lleva else -1
        variacion = random.uniform(-1, 1) * self.config.VARIACION_IA * dt

        paso_x = (dx / dist) * velocidad * direccion + variacion
        paso_y = (dy / dist) * velocidad * direccion + variacion

        self.x += paso_x
        self.y += paso_y

        self._limitar_pantalla()
        self.posicion_anterior = (self.x, self.y)