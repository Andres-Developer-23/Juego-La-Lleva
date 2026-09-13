"""Vista responsable del renderizado del entorno del juego."""

import pygame

from views.obstaculo_view import ObstaculoView


class EntornoView:
    """Clase que maneja la presentación visual del entorno."""

    def __init__(self):
        """Inicializa la vista del entorno con un ObstaculoView delegado."""
        self.obstaculo_view = ObstaculoView()

    def renderizar(self, pantalla, entorno, tiempo_animacion=0):
        """Renderiza el entorno completo en la pantalla.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            entorno: Objeto entorno a renderizar.
            tiempo_animacion (float): Tiempo para animaciones.
        """
        for obs in entorno.obstaculos:
            self.obstaculo_view.renderizar(pantalla, obs, tiempo_animacion)

        for p in entorno.particulas_fondo:
            surface = pygame.Surface((p['tamaño'] * 2, p['tamaño'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (100, 100, 140, p['alpha']),
                             (p['tamaño'], p['tamaño']), p['tamaño'])
            pantalla.blit(surface, (int(p['x']) - p['tamaño'], int(p['y']) - p['tamaño']))
