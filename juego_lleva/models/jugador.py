import math
import random

import pygame
from core.config import Config
from interfaces.movible import Movible


class Jugador(Movible):
    def __init__(self, x, y, id_jugador, nombre=None):
        self.x = x
        self.y = y
        self.id = id_jugador
        self.nombre = nombre or f"J{id_jugador + 1}"
        self._es_lleva = False
        self.config = Config()
        self.posicion_anterior = (x, y)
        self.explotando = False
        self.tiempo_explosion = 0
        self.DURACION_EXPLOSION = 2.0

    def obtener_posicion(self):
        return (self.x, self.y)

    def obtener_rectangulo(self):
        margen = int(self.config.TAMAÑO_JUGADOR * 0.2)
        return pygame.Rect(
            self.x + margen, self.y + margen,
            self.config.TAMAÑO_JUGADOR - margen * 2,
            self.config.TAMAÑO_JUGADOR - margen * 2
        )

    @property
    def es_lleva(self):
        return self._es_lleva

    @es_lleva.setter
    def es_lleva(self, valor):
        self._es_lleva = valor

    def iniciar_explosion(self):
        self.explotando = True
        self.tiempo_explosion = 0

    def actualizar_explosion(self, delta_tiempo):
        if self.explotando:
            self.tiempo_explosion += delta_tiempo

    def explosion_terminada(self):
        return self.tiempo_explosion >= self.DURACION_EXPLOSION

    def actualizar(self, delta_tiempo):
        self.posicion_anterior = (self.x, self.y)
        self.actualizar_explosion(delta_tiempo)