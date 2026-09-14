"""Vista que dibuja los efectos visuales de corta duración (toques, colisiones)."""

import math
import random

import pygame


class EfectoView:
    """Clase que actualiza y renderiza los efectos (anillo + partículas)."""

    DURACION = 0.6
    COLOR_ANILLO = (255, 215, 0)
    COLOR_PARTICULA = (255, 215, 0)

    def __init__(self):
        """Inicializa la vista de efectos sin estados persistentes."""
        self.tiempo_animacion = 0

    def actualizar(self, efectos, delta_tiempo):
        """Actualiza el tiempo de vida de los efectos y elimina los vencidos.

        Args:
            efectos (list): Lista de efectos activos.
            delta_tiempo (float): Tiempo transcurrido desde la última actualización.

        Returns:
            list: Lista de efectos que siguen vivos.
        """
        self.tiempo_animacion += delta_tiempo
        vivos = []
        for efecto in efectos:
            efecto['tiempo'] += delta_tiempo
            if efecto['tiempo'] >= self.DURACION:
                continue

            for particula in efecto['particulas']:
                particula['x'] += particula['vx'] * delta_tiempo
                particula['y'] += particula['vy'] * delta_tiempo
                particula['vida'] -= delta_tiempo
            efecto['particulas'] = [p for p in efecto['particulas'] if p['vida'] > 0]
            vivos.append(efecto)
        return vivos

    def renderizar(self, pantalla, efectos):
        """Dibuja los efectos activos sobre la pantalla.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            efectos (list): Lista de efectos activos.
        """
        for efecto in efectos:
            t = efecto['tiempo']
            progreso = t / self.DURACION
            alfa = int(255 * (1 - progreso))

            radio = int(12 + progreso * 150)
            anillo = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(anillo, (*self.COLOR_ANILLO, alfa),
                               (radio, radio), radio, 4)
            pantalla.blit(anillo, (int(efecto['x']) - radio, int(efecto['y']) - radio))

            for particula in efecto['particulas']:
                alfa_p = int(255 * (particula['vida'] / 0.7))
                radio_p = max(2, int(6 * particula['vida'] / 0.7))
                superficie = pygame.Surface((radio_p * 2, radio_p * 2), pygame.SRCALPHA)
                pygame.draw.circle(superficie, (*self.COLOR_PARTICULA, alfa_p),
                                   (radio_p, radio_p), radio_p)
                pantalla.blit(superficie, (int(particula['x']) - radio_p,
                                           int(particula['y']) - radio_p))

    def crear_toque(self, x, y):
        """Crea un efecto de toque en la posición indicada.

        Args:
            x (float): Coordenada horizontal del toque.
            y (float): Coordenada vertical del toque.

        Returns:
            dict: Efecto listo para agregarse a la lista de activos.
        """
        particulas = []
        for _ in range(14):
            angulo = random.uniform(0, math.pi * 2)
            velocidad = random.uniform(40, 140)
            particulas.append({
                'x': x,
                'y': y,
                'vx': math.cos(angulo) * velocidad,
                'vy': math.sin(angulo) * velocidad,
                'vida': random.uniform(0.5, 0.7)
            })
        return {
            'x': x,
            'y': y,
            'tiempo': 0.0,
            'particulas': particulas
        }