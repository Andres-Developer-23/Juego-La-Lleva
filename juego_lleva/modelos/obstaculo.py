import math

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

    def renderizar(self, pantalla, tiempo_animacion=0):
        if self.tipo == self.TIPO_CAJA:
            self._renderizar_caja(pantalla)
        else:
            self._renderizar_zona(pantalla, tiempo_animacion)

    def _renderizar_caja(self, pantalla):
        sombra = pygame.Surface((self.ancho + 4, self.alto + 4), pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, 80), (2, 2, self.ancho, self.alto), border_radius=6)
        pantalla.blit(sombra, (self.x, self.y))

        pygame.draw.rect(pantalla, (80, 70, 60),
                        (self.x, self.y, self.ancho, self.alto),
                        border_radius=6)
        pygame.draw.rect(pantalla, (110, 100, 85),
                        (self.x + 2, self.y + 2, self.ancho - 4, self.alto - 4),
                        border_radius=5)
        pygame.draw.rect(pantalla, (140, 130, 110),
                        (self.x + 4, self.y + 4, self.ancho - 8, self.alto // 2 - 4),
                        border_radius=4)
        pygame.draw.rect(pantalla, (60, 55, 45),
                        (self.x, self.y, self.ancho, self.alto),
                        2, border_radius=6)

    def _renderizar_zona(self, pantalla, tiempo_animacion):
        centro_x = self.x + self.ancho // 2
        centro_y = self.y + self.alto // 2
        radio = self.ancho // 2

        pulso = math.sin(tiempo_animacion * 2) * 0.1 + 0.9
        radio_actual = int(radio * pulso)

        superficie = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        pygame.draw.ellipse(superficie, (40, 120, 200, 50),
                           (0, 0, self.ancho, self.alto))
        pygame.draw.ellipse(superficie, (60, 150, 230, 80),
                           (4, 4, self.ancho - 8, self.alto - 8))
        pygame.draw.ellipse(superficie, (80, 180, 255, 40),
                           (8, 8, self.ancho - 16, self.alto - 16))

        for i in range(3):
            offset = math.sin(tiempo_animacion * 3 + i * 2) * 3
            alpha = int(30 - i * 8)
            pygame.draw.ellipse(superficie, (100, 200, 255, max(alpha, 10)),
                               (int(self.ancho * 0.2) + int(offset), int(self.alto * 0.3),
                                int(self.ancho * 0.6), int(self.alto * 0.4)))

        pantalla.blit(superficie, (self.x, self.y))
