"""Vista responsable del renderizado de jugadores en pantalla.

Dibuja personajes procedimentales (cabeza, cuerpo, brazos y piernas) con
animación de marcha sincronizada con la velocidad, giro según la dirección y
señalización clara de "la lleva" (pañuelo y aura) sin perder el color propio.
"""

import math
import random

import pygame
from core.config import Config


class JugadorView:
    """Clase que maneja la presentación visual de un jugador."""

    PIEL = (238, 203, 168)
    PIEL_OSCURA = (198, 158, 122)

    def __init__(self):
        """Inicializa la vista del jugador con configuración por defecto."""
        self.config = Config()
        self.tiempo_animacion = 0
        self.fase_caminar = 0
        self.particulas_rastro = []
        self.trail_timer = 0
        self.sprite_normal = None
        self.sprite_lleva = None
        self.s = self.config.TAMAÑO_JUGADOR / 95.0

    def cargar_sprites(self, jugador):
        """Carga los sprites correspondientes al jugador (compatibilidad).

        El renderizado principal es procedural, pero se conserva la carga por
        si algún modo desea usar imágenes externas.

        Args:
            jugador: Objeto jugador con id para determinar sprites.
        """
        self.sprite_normal = self._cargar_sprite(
            self.config.SPRITE_J1 if jugador.id == 0 else self.config.SPRITE_J2
        )
        self.sprite_lleva = self._cargar_sprite(self.config.SPRITE_LLEVA)

    def _cargar_sprite(self, ruta):
        """Carga un sprite desde una ruta de archivo.

        Args:
            ruta (str): Ruta al archivo de imagen.

        Returns:
            pygame.Surface: Sprite cargado o None si hay error.
        """
        try:
            imagen = pygame.image.load(ruta).convert_alpha()
            return pygame.transform.scale(imagen, (self.config.TAMAÑO_JUGADOR, self.config.TAMAÑO_JUGADOR))
        except (pygame.error, OSError):
            return None

    def _color_oscuro(self, color):
        """Devuelve una versión oscurecida de un color.

        Args:
            color (tuple): Color RGB.

        Returns:
            tuple: Color oscurecido.
        """
        return (int(color[0] * 0.55), int(color[1] * 0.55), int(color[2] * 0.55))

    def renderizar(self, pantalla, jugador, tiempo_delta=0):
        """Renderiza el jugador en la pantalla.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            jugador: Objeto jugador a renderizar.
            tiempo_delta (float): Tiempo transcurrido desde la última actualización.
        """
        self.tiempo_animacion += tiempo_delta
        self.trail_timer += tiempo_delta
        self.fase_caminar += jugador.velocidad_abs * tiempo_delta * 0.022

        if self.trail_timer > 0.05:
            self._agregar_particula_rastro(jugador)
            self.trail_timer = 0

        self._actualizar_particulas(tiempo_delta)

        cx = jugador.x + self.config.TAMAÑO_JUGADOR // 2
        pie_y = jugador.y + self.config.TAMAÑO_JUGADOR

        self._dibujar_aura_lleva(pantalla, jugador, cx, pie_y)
        self._dibujar_sombra(pantalla, cx, pie_y, jugador)

        sprite = self._componer_personaje(jugador)
        if jugador.direccion_cara < 0:
            sprite = pygame.transform.flip(sprite, True, False)

        agachado = 0
        if jugador.tropezando > 0:
            agachado = int(10 * self.s)
        pantalla.blit(sprite, (int(cx - sprite.get_width() // 2),
                               int(pie_y - sprite.get_height() + agachado)))

        if jugador.escudo:
            self._dibujar_escudo(pantalla, jugador, cx, pie_y)

        self._dibujar_nombre(pantalla, jugador)

    def _componer_personaje(self, jugador):
        """Compone el muñeco procedural en una superficie independiente.

        Args:
            jugador: Objeto jugador del que se toman estado y colores.

        Returns:
            pygame.Surface: Muñeco dibujado mirando a la derecha.
        """
        s = self.s
        ancho = int(150 * s)
        alto = int(160 * s)
        superficie = pygame.Surface((ancho, alto), pygame.SRCALPHA)

        color = self.config.COLOR_JUGADOR_1 if jugador.id == 0 else self.config.COLOR_JUGADOR_2
        oscuro = self._color_oscuro(color)
        if jugador.es_lleva:
            color = (min(color[0] + 40, 255), max(color[1] - 25, 0), max(color[2] - 25, 0))
            oscuro = self._color_oscuro(color)

        fx = ancho // 2
        hip_y = alto - 48 * s
        hombro_y = hip_y - 34 * s
        rugido = 3.0 + (0.25 if jugador.velocidad_abs > 150 * s else 0)
        paso = math.sin(self.fase_caminar)
        paso2 = math.sin(self.fase_caminar + math.pi)

        inclina = int(6 * s) if jugador.velocidad_abs > 120 * s else 0

        pie_izq = (fx + paso * 13 * s, alto - 8 * s - max(0.0, math.cos(self.fase_caminar)) * 5 * s)
        pie_der = (fx + paso2 * 13 * s, alto - 8 * s - max(0.0, math.cos(self.fase_caminar + math.pi)) * 5 * s)

        for pie, fase in ((pie_izq, paso), (pie_der, paso2)):
            rodilla = (fx + fase * 8 * s, (hip_y + pie[1]) / 2)
            pygame.draw.line(superficie, oscuro, (fx, hip_y), rodilla, max(4, int(9 * s)))
            pygame.draw.line(superficie, oscuro, rodilla, pie, max(4, int(9 * s)))
            pygame.draw.circle(superficie, self._color_oscuro(oscuro), pie, int(6.5 * s))

        torso = pygame.Rect(int(fx - 23 * s), int(hombro_y - inclina), int(46 * s), int(hip_y - hombro_y + 4 * s))
        pygame.draw.rect(superficie, oscuro, torso.move(int(2 * s), int(3 * s)), border_radius=int(12 * s))
        pygame.draw.rect(superficie, color, torso, border_radius=int(12 * s))
        brillo = pygame.Rect(torso.x + 4, torso.y + 4, int(torso.w * 0.45), int(torso.h * 0.35))
        pygame.draw.rect(superficie, (255, 255, 255, 26), brillo, border_radius=int(8 * s))

        hombro = (fx, hombro_y - inclina)
        brazo_izq = (fx - paso * 14 * s, hombro[1] + 34 * s)
        brazo_der = (fx + paso2 * 14 * s, hombro[1] + 34 * s)
        for brazo in (brazo_izq, brazo_der):
            pygame.draw.line(superficie, self.PIEL, hombro, brazo, max(4, int(8 * s)))
            pygame.draw.circle(superficie, self.PIEL, brazo, int(5 * s))

        cabeza_y = hombro_y - inclina - 30 * s
        pygame.draw.circle(superficie, self.PIEL, (fx, int(cabeza_y)), int(21 * s))
        rect_pelo = pygame.Rect(0, 0, ancho, int(cabeza_y))
        superficie.set_clip(rect_pelo)
        pygame.draw.circle(superficie, (60, 45, 30), (fx, int(cabeza_y + 6 * s)), int(19 * s))
        superficie.set_clip(None)

        ojo_x = fx + 7 * s
        ojo_y = int(cabeza_y + 2 * s)
        pygame.draw.circle(superficie, (255, 255, 255), (int(ojo_x), int(ojo_y)), int(4.5 * s))
        pygame.draw.circle(superficie, (30, 25, 20), (int(ojo_x + 1.5 * s), int(ojo_y)), int(2.2 * s))
        sonrisa = pygame.Rect(int(fx - 2 * s), int(cabeza_y + 8 * s), int(12 * s), int(6 * s))
        pygame.draw.arc(superficie, (80, 50, 40), sonrisa, 0.2, math.pi - 0.2, 2)

        if jugador.tropezando > 0:
            for i in range(3):
                pygame.draw.circle(superficie, (255, 255, 60, 150), (fx - 14 * s, cabeza_y - 22 * s - i * 6), int(2 * s))

        if jugador.es_lleva:
            cuello_y = hombro_y - 6 * s
            for i, lado in enumerate((-1, 1)):
                ondeo = math.sin(self.tiempo_animacion * 9 + i) * 6 * s
                p1 = (fx + lado * 10 * s, cuello_y)
                p2 = (fx + lado * (34 * s) + ondeo, cuello_y - 8 * s)
                p3 = (fx + lado * (46 * s), cuello_y + 4 * s)
                p4 = (fx + lado * (30 * s), cuello_y - 6 * s)
                pygame.draw.polygon(superficie, (232, 40, 40), [p1, p2, p3, p4])
            pygame.draw.polygon(superficie, (255, 255, 255), [
                (fx - 4 * s, cuello_y), (fx + 4 * s, cuello_y),
                (fx + 4 * s, cuello_y + 16 * s), (fx - 4 * s, cuello_y + 16 * s)])

        return superficie

    def _dibujar_aura_lleva(self, pantalla, jugador, cx, pie_y):
        """Dibuja el aura roja pulsante alrededor del jugador que lleva.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            jugador: Jugador objetivo.
            cx (int): Centro horizontal del jugador.
            pie_y (int): Posición vertical de los pies.
        """
        if not jugador.es_lleva:
            return
        centro = (cx, pie_y - int(self.config.TAMAÑO_JUGADOR * 0.55))
        for i in range(3):
            radio = int((22 + i * 9) * self.s + math.sin(self.tiempo_animacion * 6 + i) * (4 + i * 2) * self.s)
            alpha = max(12, int(45 - i * 13))
            capa = pygame.Surface((radio * 2 + 8, radio * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(capa, (255, 45, 45, alpha), (radio + 4, radio + 4), radio)
            pantalla.blit(capa, (centro[0] - radio - 4, centro[1] - radio - 4))

    def _dibujar_sombra(self, pantalla, cx, pie_y, jugador):
        """Dibuja la sombra elíptica bajo los pies del jugador.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            cx (int): Centro horizontal del jugador.
            pie_y (int): Posición vertical de los pies.
            jugador: Jugador al que pertenece la sombra.
        """
        encogido = 0.82 if jugador.tropezando > 0 else 1.0
        ancho_s = int(54 * self.s * encogido)
        sombra = pygame.Surface((ancho_s + 10, 26), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 70), (5, 4, ancho_s, 18))
        pantalla.blit(sombra, (cx - sombra.get_width() // 2, pie_y - 6))

    def _dibujar_escudo(self, pantalla, jugador, cx, pie_y):
        """Dibuja el anillo de escudo alrededor del jugador.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            jugador: Jugador con escudo.
            cx (int): Centro horizontal del jugador.
            pie_y (int): Posición vertical de los pies.
        """
        radio = int(48 * self.s)
        capa = pygame.Surface((radio * 2 + 8, radio * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(capa, (110, 155, 255, 120), (radio + 4, radio + 4), radio, 5)
        pygame.draw.circle(capa, (160, 200, 255, 70), (radio + 4, radio + 4), radio - 8, 3)
        centro = (cx, pie_y - int(self.config.TAMAÑO_JUGADOR * 0.55))
        pantalla.blit(capa, (centro[0] - radio - 4, centro[1] - radio - 4))

    def _dibujar_nombre(self, pantalla, jugador):
        """Dibuja el nombre del jugador con contorno legible.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            jugador: Jugador al que pertenece el nombre.
        """
        fuente = pygame.font.SysFont(None, 24)
        texto = fuente.render(jugador.nombre, True, (255, 255, 255))
        contorno = fuente.render(jugador.nombre, True, (15, 15, 25))
        cx = jugador.x + self.config.TAMAÑO_JUGADOR // 2
        ty = jugador.y - 8
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    pantalla.blit(contorno, (cx - texto.get_width() // 2 + dx, ty + dy))
        pantalla.blit(texto, (cx - texto.get_width() // 2, ty))

    def _actualizar_particulas(self, delta_tiempo):
        """Actualiza el estado de las partículas de rastro.

        Args:
            delta_tiempo (float): Tiempo transcurrido desde la última actualización.
        """
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
        """Agrega una nueva partícula de rastro al jugador.

        Args:
            jugador: Objeto jugador para obtener posición y color.
        """
        velocidad = jugador.velocidad_abs

        if velocidad > 60:
            color = self.config.COLOR_LLEVA if jugador.es_lleva else (
                self.config.COLOR_JUGADOR_1 if jugador.id == 0 else self.config.COLOR_JUGADOR_2
            )
            self.particulas_rastro.append({
                'x': jugador.x + self.config.TAMAÑO_JUGADOR // 2,
                'y': jugador.y + self.config.TAMAÑO_JUGADOR,
                'velocidad_x': random.uniform(-30, 30),
                'velocidad_y': -jugador.vy * 0.15 + random.uniform(-10, 10),
                'tamaño': random.randint(2, 4) if not jugador.es_lleva else random.randint(3, 6),
                'color': color,
                'vida': 1.0
            })