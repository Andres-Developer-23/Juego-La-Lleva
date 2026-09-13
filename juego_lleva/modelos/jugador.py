import math
import random

import pygame
from core.config import Config
from interfaces.movible import Movible
from interfaces.renderizable import Renderizable


class Jugador(Movible, Renderizable):
    def __init__(self, x, y, id_jugador, nombre=None):
        self.x = x
        self.y = y
        self.id = id_jugador
        self.nombre = nombre or f"J{id_jugador + 1}"
        self._es_lleva = False
        self.config = Config()
        self.tiempo_animacion = 0
        self.posicion_anterior = (x, y)
        self.particulas_rastro = []
        self.trail_timer = 0
        self.sprite_normal = self._cargar_sprite(self.config.SPRITE_J1 if id_jugador == 0 else self.config.SPRITE_J2)
        self.sprite_lleva = self._cargar_sprite(self.config.SPRITE_LLEVA)
        self.explotando = False
        self.particulas_explosion = []
        self.tiempo_explosion = 0
        self.DURACION_EXPLOSION = 2.0

    def _cargar_sprite(self, ruta):
        try:
            imagen = pygame.image.load(ruta).convert_alpha()
            return pygame.transform.scale(imagen, (self.config.TAMAÑO_JUGADOR, self.config.TAMAÑO_JUGADOR))
        except:
            return None

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

    def _actualizar_particulas(self, delta_tiempo):
        nuevas_particulas = []
        for p in self.particulas_rastro:
            p['vida'] -= delta_tiempo * 2
            p['x'] += p['velocidad_x'] * delta_tiempo
            p['y'] += p['velocidad_y'] * delta_tiempo
            p['tamaño'] *= 0.95
            if p['vida'] > 0:
                nuevas_particulas.append(p)
        self.particulas_rastro = nuevas_particulas

    def _agregar_particula_rastro(self):
        dx = self.x - self.posicion_anterior[0]
        dy = self.y - self.posicion_anterior[1]
        velocidad = math.sqrt(dx * dx + dy * dy)

        if velocidad > 1:
            color = self.config.COLOR_LLEVA if self.es_lleva else (
                self.config.COLOR_JUGADOR_1 if self.id == 0 else self.config.COLOR_JUGADOR_2
            )
            self.particulas_rastro.append({
                'x': self.x + self.config.TAMAÑO_JUGADOR // 2,
                'y': self.y + self.config.TAMAÑO_JUGADOR // 2,
                'velocidad_x': -dx * 0.3 + random.uniform(-0.5, 0.5),
                'velocidad_y': -dy * 0.3 + random.uniform(-0.5, 0.5),
                'tamaño': random.randint(3, 6) if self.es_lleva else random.randint(2, 4),
                'color': color,
                'vida': 1.0
            })

    def renderizar(self, pantalla, tiempo_delta=0):
        self.tiempo_animacion += tiempo_delta
        self.trail_timer += tiempo_delta

        if self.explotando:
            self._renderizar_explosion(pantalla, tiempo_delta)
            return

        if self.trail_timer > 0.05:
            self._agregar_particula_rastro()
            self.trail_timer = 0

        self._actualizar_particulas(tiempo_delta)

        for p in self.particulas_rastro:
            alpha = int(180 * p['vida'])
            surface = pygame.Surface((int(p['tamaño'] * 2), int(p['tamaño'] * 2)), pygame.SRCALPHA)
            color_alpha = (*p['color'], alpha)
            pygame.draw.circle(surface, color_alpha, (int(p['tamaño']), int(p['tamaño'])), int(p['tamaño']))
            pantalla.blit(surface, (int(p['x']) - int(p['tamaño']), int(p['y']) - int(p['tamaño'])))

        color_base = self.config.COLOR_JUGADOR_1 if self.id == 0 else self.config.COLOR_JUGADOR_2

        sombra = pygame.Surface((self.config.TAMAÑO_JUGADOR + 8, self.config.TAMAÑO_JUGADOR // 2 + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 60), sombra.get_rect())
        pantalla.blit(sombra, (self.x + 1, self.y + self.config.TAMAÑO_JUGADOR - 3))

        sprite_actual = self.sprite_lleva if self.es_lleva else self.sprite_normal

        if self.es_lleva:
            for i in range(3):
                radio_pulso = (25 + i * 8) + math.sin(self.tiempo_animacion * 6 + i) * (5 + i * 2)
                alpha_pulso = int(40 - i * 12)
                superficie_pulso = pygame.Surface((int(radio_pulso * 4), int(radio_pulso * 4)), pygame.SRCALPHA)
                pygame.draw.circle(superficie_pulso, (255, 50, 50, max(alpha_pulso, 10)),
                                 (int(radio_pulso * 2), int(radio_pulso * 2)), int(radio_pulso))
                pantalla.blit(superficie_pulso, (self.x + self.config.TAMAÑO_JUGADOR // 2 - int(radio_pulso * 2),
                                                 self.y + self.config.TAMAÑO_JUGADOR // 2 - int(radio_pulso * 2)))

            if sprite_actual:
                pantalla.blit(sprite_actual, (self.x - 1, self.y - 1))
            else:
                pygame.draw.rect(pantalla, (180, 30, 30),
                               (self.x - 3, self.y - 3, self.config.TAMAÑO_JUGADOR + 6, self.config.TAMAÑO_JUGADOR + 6),
                               border_radius=9)
                pygame.draw.rect(pantalla, self.config.COLOR_LLEVA,
                               (self.x - 1, self.y - 1, self.config.TAMAÑO_JUGADOR + 2, self.config.TAMAÑO_JUGADOR + 2),
                               border_radius=7)
                pygame.draw.rect(pantalla, (255, 255, 255),
                               (self.x + 1, self.y + 1, self.config.TAMAÑO_JUGADOR - 2, self.config.TAMAÑO_JUGADOR - 2),
                               border_radius=5)
        else:
            if sprite_actual:
                pantalla.blit(sprite_actual, (self.x, self.y))
            else:
                pygame.draw.rect(pantalla, (color_base[0] // 2, color_base[1] // 2, color_base[2] // 2),
                               (self.x + 2, self.y + 2, self.config.TAMAÑO_JUGADOR, self.config.TAMAÑO_JUGADOR),
                               border_radius=7)
                pygame.draw.rect(pantalla, color_base,
                               (self.x, self.y, self.config.TAMAÑO_JUGADOR, self.config.TAMAÑO_JUGADOR),
                               border_radius=6)
                surface_brillo = pygame.Surface((self.config.TAMAÑO_JUGADOR - 6, self.config.TAMAÑO_JUGADOR // 2 - 2), pygame.SRCALPHA)
                surface_brillo.fill((255, 255, 255, 50))
                pygame.draw.rect(surface_brillo, (255, 255, 255, 50),
                               (0, 0, self.config.TAMAÑO_JUGADOR - 6, self.config.TAMAÑO_JUGADOR // 2 - 2),
                               border_radius=4)
                pantalla.blit(surface_brillo, (self.x + 3, self.y + 3))

        fuente = pygame.font.SysFont(None, 24)
        texto = fuente.render(self.nombre, True, (255, 255, 255))
        pantalla.blit(texto, (self.x + self.config.TAMAÑO_JUGADOR // 2 - texto.get_width() // 2,
                             self.y - texto.get_height() - 4))

        self.posicion_anterior = (self.x, self.y)

    def iniciar_explosion(self):
        self.explotando = True
        self.tiempo_explosion = 0
        self.particulas_explosion = []
        centro_x = self.x + self.config.TAMAÑO_JUGADOR // 2
        centro_y = self.y + self.config.TAMAÑO_JUGADOR // 2
        color_jugador = self.config.COLOR_JUGADOR_1 if self.id == 0 else self.config.COLOR_JUGADOR_2
        for _ in range(40):
            angulo = random.uniform(0, 2 * math.pi)
            velocidad = random.uniform(80, 250)
            self.particulas_explosion.append({
                'x': centro_x,
                'y': centro_y,
                'velocidad_x': math.cos(angulo) * velocidad,
                'velocidad_y': math.sin(angulo) * velocidad,
                'tamaño': random.randint(4, 12),
                'color': color_jugador,
                'vida': 1.0
            })
        for _ in range(20):
            angulo = random.uniform(0, 2 * math.pi)
            velocidad = random.uniform(40, 150)
            self.particulas_explosion.append({
                'x': centro_x,
                'y': centro_y,
                'velocidad_x': math.cos(angulo) * velocidad,
                'velocidad_y': math.sin(angulo) * velocidad,
                'tamaño': random.randint(6, 16),
                'color': (255, 200, 50),
                'vida': 1.0
            })
        for _ in range(15):
            angulo = random.uniform(0, 2 * math.pi)
            velocidad = random.uniform(20, 100)
            self.particulas_explosion.append({
                'x': centro_x,
                'y': centro_y,
                'velocidad_x': math.cos(angulo) * velocidad,
                'velocidad_y': math.sin(angulo) * velocidad,
                'tamaño': random.randint(3, 8),
                'color': (255, 255, 255),
                'vida': 1.0
            })

    def _renderizar_explosion(self, pantalla, tiempo_delta):
        self.tiempo_explosion += tiempo_delta
        nuevas_particulas = []
        for p in self.particulas_explosion:
            p['vida'] -= tiempo_delta * 0.7
            p['x'] += p['velocidad_x'] * tiempo_delta
            p['y'] += p['velocidad_y'] * tiempo_delta
            p['velocidad_x'] *= 0.98
            p['velocidad_y'] *= 0.98
            p['tamaño'] *= 0.97
            if p['vida'] > 0:
                nuevas_particulas.append(p)
        self.particulas_explosion = nuevas_particulas
        for p in self.particulas_explosion:
            alpha = int(255 * p['vida'])
            surface = pygame.Surface((int(p['tamaño'] * 2), int(p['tamaño'] * 2)), pygame.SRCALPHA)
            color_alpha = (*p['color'], alpha)
            pygame.draw.circle(surface, color_alpha, (int(p['tamaño']), int(p['tamaño'])), int(p['tamaño']))
            pantalla.blit(surface, (int(p['x']) - int(p['tamaño']), int(p['y']) - int(p['tamaño'])))
        flash_alpha = int(200 * (1 - self.tiempo_explosion / self.DURACION_EXPLOSION))
        if flash_alpha > 0:
            flash = pygame.Surface((self.config.ANCHO_PANTALLA, self.config.ALTO_PANTALLA), pygame.SRCALPHA)
            flash.fill((255, 255, 255, flash_alpha))
            pantalla.blit(flash, (0, 0))

    def explosion_terminada(self):
        return self.tiempo_explosion >= self.DURACION_EXPLOSION and len(self.particulas_explosion) == 0
