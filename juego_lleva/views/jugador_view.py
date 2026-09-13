import math
import random

import pygame
from core.config import Config


class JugadorView:
    def __init__(self):
        self.config = Config()
        self.tiempo_animacion = 0
        self.particulas_rastro = []
        self.trail_timer = 0
        self.sprite_normal = None
        self.sprite_lleva = None
        self.particulas_explosion = []

    def cargar_sprites(self, jugador):
        self.sprite_normal = self._cargar_sprite(
            self.config.SPRITE_J1 if jugador.id == 0 else self.config.SPRITE_J2
        )
        self.sprite_lleva = self._cargar_sprite(self.config.SPRITE_LLEVA)

    def _cargar_sprite(self, ruta):
        try:
            imagen = pygame.image.load(ruta).convert_alpha()
            return pygame.transform.scale(imagen, (self.config.TAMAÑO_JUGADOR, self.config.TAMAÑO_JUGADOR))
        except:
            return None

    def renderizar(self, pantalla, jugador, tiempo_delta=0):
        self.tiempo_animacion += tiempo_delta
        self.trail_timer += tiempo_delta

        if jugador.explotando:
            self._renderizar_explosion(pantalla, jugador, tiempo_delta)
            return

        if self.trail_timer > 0.05:
            self._agregar_particula_rastro(jugador)
            self.trail_timer = 0

        self._actualizar_particulas(tiempo_delta)

        for p in self.particulas_rastro:
            alpha = int(180 * p['vida'])
            surface = pygame.Surface((int(p['tamaño'] * 2), int(p['tamaño'] * 2)), pygame.SRCALPHA)
            color_alpha = (*p['color'], alpha)
            pygame.draw.circle(surface, color_alpha, (int(p['tamaño']), int(p['tamaño'])), int(p['tamaño']))
            pantalla.blit(surface, (int(p['x']) - int(p['tamaño']), int(p['y']) - int(p['tamaño'])))

        color_base = self.config.COLOR_JUGADOR_1 if jugador.id == 0 else self.config.COLOR_JUGADOR_2

        sombra = pygame.Surface((self.config.TAMAÑO_JUGADOR + 8, self.config.TAMAÑO_JUGADOR // 2 + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 60), sombra.get_rect())
        pantalla.blit(sombra, (jugador.x + 1, jugador.y + self.config.TAMAÑO_JUGADOR - 3))

        sprite_actual = self.sprite_lleva if jugador.es_lleva else self.sprite_normal

        if jugador.es_lleva:
            for i in range(3):
                radio_pulso = (25 + i * 8) + math.sin(self.tiempo_animacion * 6 + i) * (5 + i * 2)
                alpha_pulso = int(40 - i * 12)
                superficie_pulso = pygame.Surface((int(radio_pulso * 4), int(radio_pulso * 4)), pygame.SRCALPHA)
                pygame.draw.circle(superficie_pulso, (255, 50, 50, max(alpha_pulso, 10)),
                                 (int(radio_pulso * 2), int(radio_pulso * 2)), int(radio_pulso))
                pantalla.blit(superficie_pulso, (jugador.x + self.config.TAMAÑO_JUGADOR // 2 - int(radio_pulso * 2),
                                                 jugador.y + self.config.TAMAÑO_JUGADOR // 2 - int(radio_pulso * 2)))

            if sprite_actual:
                pantalla.blit(sprite_actual, (jugador.x - 1, jugador.y - 1))
            else:
                pygame.draw.rect(pantalla, (180, 30, 30),
                               (jugador.x - 3, jugador.y - 3, self.config.TAMAÑO_JUGADOR + 6, self.config.TAMAÑO_JUGADOR + 6),
                               border_radius=9)
                pygame.draw.rect(pantalla, self.config.COLOR_LLEVA,
                               (jugador.x - 1, jugador.y - 1, self.config.TAMAÑO_JUGADOR + 2, self.config.TAMAÑO_JUGADOR + 2),
                               border_radius=7)
                pygame.draw.rect(pantalla, (255, 255, 255),
                               (jugador.x + 1, jugador.y + 1, self.config.TAMAÑO_JUGADOR - 2, self.config.TAMAÑO_JUGADOR - 2),
                               border_radius=5)
        else:
            if sprite_actual:
                pantalla.blit(sprite_actual, (jugador.x, jugador.y))
            else:
                pygame.draw.rect(pantalla, (color_base[0] // 2, color_base[1] // 2, color_base[2] // 2),
                               (jugador.x + 2, jugador.y + 2, self.config.TAMAÑO_JUGADOR, self.config.TAMAÑO_JUGADOR),
                               border_radius=7)
                pygame.draw.rect(pantalla, color_base,
                               (jugador.x, jugador.y, self.config.TAMAÑO_JUGADOR, self.config.TAMAÑO_JUGADOR),
                               border_radius=6)
                surface_brillo = pygame.Surface((self.config.TAMAÑO_JUGADOR - 6, self.config.TAMAÑO_JUGADOR // 2 - 2), pygame.SRCALPHA)
                surface_brillo.fill((255, 255, 255, 50))
                pygame.draw.rect(surface_brillo, (255, 255, 255, 50),
                               (0, 0, self.config.TAMAÑO_JUGADOR - 6, self.config.TAMAÑO_JUGADOR // 2 - 2),
                               border_radius=4)
                pantalla.blit(surface_brillo, (jugador.x + 3, jugador.y + 3))

        fuente = pygame.font.SysFont(None, 24)
        texto = fuente.render(jugador.nombre, True, (255, 255, 255))
        pantalla.blit(texto, (jugador.x + self.config.TAMAÑO_JUGADOR // 2 - texto.get_width() // 2,
                             jugador.y - texto.get_height() - 4))

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

    def _agregar_particula_rastro(self, jugador):
        dx = jugador.x - jugador.posicion_anterior[0]
        dy = jugador.y - jugador.posicion_anterior[1]
        velocidad = math.sqrt(dx * dx + dy * dy)

        if velocidad > 1:
            color = self.config.COLOR_LLEVA if jugador.es_lleva else (
                self.config.COLOR_JUGADOR_1 if jugador.id == 0 else self.config.COLOR_JUGADOR_2
            )
            self.particulas_rastro.append({
                'x': jugador.x + self.config.TAMAÑO_JUGADOR // 2,
                'y': jugador.y + self.config.TAMAÑO_JUGADOR // 2,
                'velocidad_x': -dx * 0.3 + random.uniform(-0.5, 0.5),
                'velocidad_y': -dy * 0.3 + random.uniform(-0.5, 0.5),
                'tamaño': random.randint(3, 6) if jugador.es_lleva else random.randint(2, 4),
                'color': color,
                'vida': 1.0
            })

    def _renderizar_explosion(self, pantalla, jugador, tiempo_delta):
        jugador.actualizar_explosion(tiempo_delta)
        self._generar_particulas_explosion(jugador)
        self._actualizar_particulas_explosion(tiempo_delta)

        for p in self.particulas_explosion:
            alpha = int(255 * p['vida'])
            surface = pygame.Surface((int(p['tamaño'] * 2), int(p['tamaño'] * 2)), pygame.SRCALPHA)
            color_alpha = (*p['color'], alpha)
            pygame.draw.circle(surface, color_alpha, (int(p['tamaño']), int(p['tamaño'])), int(p['tamaño']))
            pantalla.blit(surface, (int(p['x']) - int(p['tamaño']), int(p['y']) - int(p['tamaño'])))

        flash_alpha = int(200 * (1 - jugador.tiempo_explosion / jugador.DURACION_EXPLOSION))
        if flash_alpha > 0:
            flash = pygame.Surface((self.config.ANCHO_PANTALLA, self.config.ALTO_PANTALLA), pygame.SRCALPHA)
            flash.fill((255, 255, 255, flash_alpha))
            pantalla.blit(flash, (0, 0))

    def _generar_particulas_explosion(self, jugador):
        if not self.particulas_explosion:
            centro_x = jugador.x + self.config.TAMAÑO_JUGADOR // 2
            centro_y = jugador.y + self.config.TAMAÑO_JUGADOR // 2
            color_jugador = self.config.COLOR_JUGADOR_1 if jugador.id == 0 else self.config.COLOR_JUGADOR_2

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

    def _actualizar_particulas_explosion(self, delta_tiempo):
        nuevas_particulas = []
        for p in self.particulas_explosion:
            p['vida'] -= delta_tiempo * 0.7
            p['x'] += p['velocidad_x'] * delta_tiempo
            p['y'] += p['velocidad_y'] * delta_tiempo
            p['velocidad_x'] *= 0.98
            p['velocidad_y'] *= 0.98
            p['tamaño'] *= 0.97
            if p['vida'] > 0:
                nuevas_particulas.append(p)
        self.particulas_explosion = nuevas_particulas