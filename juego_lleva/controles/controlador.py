"""Módulo de control que gestiona las entradas del teclado."""

import pygame


class Controlador:
    """Clase que administra la configuración de teclas para los jugadores."""

    def __init__(self):
        """Inicializa el controlador con la configuración de teclas para dos jugadores."""
        self.teclas_jugador1 = {
            'arriba': pygame.K_w,
            'abajo': pygame.K_s,
            'izquierda': pygame.K_a,
            'derecha': pygame.K_d
        }
        self.teclas_jugador2 = {
            'arriba': pygame.K_UP,
            'abajo': pygame.K_DOWN,
            'izquierda': pygame.K_LEFT,
            'derecha': pygame.K_RIGHT
        }

    def obtener_teclas_jugador(self, id_jugador):
        """Obtiene la configuración de teclas para un jugador.

        Args:
            id_jugador (int): ID del jugador (0 o 1).

        Returns:
            dict: Diccionario con las teclas asignadas al jugador.
        """
        if id_jugador == 0:
            return self.teclas_jugador1
        elif id_jugador == 1:
            return self.teclas_jugador2
        return self.teclas_jugador1
