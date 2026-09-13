import pygame
from core.config import Config


class Obstaculo:
    TIPO_CAJA = "caja"
    TIPO_ZONA = "zona"

    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.config = Config()

        if tipo == self.TIPO_CAJA:
            self.ancho = self.config.TAMAÑO_CAJA
            self.alto = self.config.TAMAÑO_CAJA
        else:
            self.ancho = self.config.TAMAÑO_ZONA
            self.alto = self.config.TAMAÑO_ZONA

    def obtener_rectangulo(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

    def es_zona_lenta(self):
        return self.tipo == self.TIPO_ZONA