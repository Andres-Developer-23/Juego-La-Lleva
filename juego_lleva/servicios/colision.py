"""Servicio que maneja la detección y resolución de colisiones."""

import math
from core.config import Config
from models.obstaculo import Obstaculo


class ColisionService:
    """Clase que gestiona las colisiones entre jugadores y obstáculos."""

    def __init__(self):
        """Inicializa el servicio de colisiones con configuración por defecto."""
        self.config = Config()
        self.cooldown = 0
        self.COOLDOWN_FRAMES = 10

    def detectar_colision(self, j1, j2):
        """Detecta si dos jugadores están colisionando.

        Args:
            j1: Primer jugador.
            j2: Segundo jugador.

        Returns:
            bool: True si hay colisión, False en caso contrario.
        """
        rect1 = j1.obtener_rectangulo()
        rect2 = j2.obtener_rectangulo()
        return rect1.colliderect(rect2)

    def detectar_colisiones(self, jugadores):
        """Detecta todas las colisiones entre una lista de jugadores.

        Args:
            jugadores (list): Lista de jugadores a verificar.

        Returns:
            list: Lista de tuplas con pares de jugadores en colisión.
        """
        if self.cooldown > 0:
            self.cooldown -= 1
            return []

        colisiones = []
        for i, j1 in enumerate(jugadores):
            for j2 in jugadores[i + 1:]:
                if self.detectar_colision(j1, j2):
                    colisiones.append((j1, j2))

        if colisiones:
            self.cooldown = self.COOLDOWN_FRAMES

        return colisiones[:1]

    def separar_jugadores(self, j1, j2, tamano_jugador):
        """Separa dos jugadores que están colisionando.

        Args:
            j1: Primer jugador.
            j2: Segundo jugador.
            tamano_jugador (int): Tamaño del jugador para calcular separación.
        """
        dx = j1.x - j2.x
        dy = j1.y - j2.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0:
            j1.x += tamano_jugador
            return

        overlap = tamano_jugador - dist
        if overlap > 0:
            separacion = overlap / 2 + 1
            j1.x += (dx / dist) * separacion
            j1.y += (dy / dist) * separacion
            j2.x -= (dx / dist) * separacion
            j2.y -= (dy / dist) * separacion

    def detectar_colision_jugador_obstaculo(self, jugador, obstaculo):
        """Detecta si un jugador está colisionando con un obstáculo.

        Args:
            jugador: Jugador a verificar.
            obstaculo: Obstáculo a verificar.

        Returns:
            bool: True si hay colisión, False en caso contrario.
        """
        rect_j = jugador.obtener_rectangulo()
        rect_o = obstaculo.obtener_rectangulo()
        return rect_j.colliderect(rect_o)

    def rebote_obstaculo(self, jugador, obstaculo):
        """Aplica un rebote al jugador cuando colisiona con un obstáculo.

        Args:
            jugador: Jugador que rebota.
            obstaculo: Obstáculo con el que colisiona.
        """
        rect_j = jugador.obtener_rectangulo()
        rect_o = obstaculo.obtener_rectangulo()

        centro_j_x = rect_j.centerx
        centro_j_y = rect_j.centery
        centro_o_x = rect_o.centerx
        centro_o_y = rect_o.centery

        dx = centro_j_x - centro_o_x
        dy = centro_j_y - centro_o_y

        dist = math.sqrt(dx * dx + dy * dy)
        if dist == 0:
            dx = 1
            dist = 1

        fuerza = self.config.FUERZA_REBOTE
        jugador.x += (dx / dist) * fuerza
        jugador.y += (dy / dist) * fuerza

    def jugador_en_zona_lenta(self, jugador, obstaculos):
        """Verifica si un jugador está en una zona que ralentiza.

        Args:
            jugador: Jugador a verificar.
            obstaculos (list): Lista de obstáculos del juego.

        Returns:
            bool: True si el jugador está en zona lenta, False en caso contrario.
        """
        rect_j = jugador.obtener_rectangulo()
        for obs in obstaculos:
            if obs.es_zona_lenta():
                rect_o = obs.obtener_rectangulo()
                if rect_j.colliderect(rect_o):
                    return True
        return False

    def limpiar_cooldown(self):
        """Limpia el cooldown de colisiones."""
        self.cooldown = 0
