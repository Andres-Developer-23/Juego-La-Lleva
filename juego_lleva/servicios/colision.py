import math
from core.config import Config
from modelos.obstaculo import Obstaculo


class ColisionService:
    def __init__(self):
        self.config = Config()
        self.cooldown = 0
        self.COOLDOWN_FRAMES = 10

    def detectar_colision(self, j1, j2):
        rect1 = j1.obtener_rectangulo()
        rect2 = j2.obtener_rectangulo()
        return rect1.colliderect(rect2)

    def detectar_colisiones(self, jugadores):
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
        rect_j = jugador.obtener_rectangulo()
        rect_o = obstaculo.obtener_rectangulo()
        return rect_j.colliderect(rect_o)

    def rebote_obstaculo(self, jugador, obstaculo):
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
        rect_j = jugador.obtener_rectangulo()
        for obs in obstaculos:
            if obs.es_zona_lenta():
                rect_o = obs.obtener_rectangulo()
                if rect_j.colliderect(rect_o):
                    return True
        return False

    def limpiar_cooldown(self):
        self.cooldown = 0
