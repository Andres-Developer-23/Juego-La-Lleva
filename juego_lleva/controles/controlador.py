import pygame


class Controlador:
    def __init__(self):
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
        if id_jugador == 0:
            return self.teclas_jugador1
        elif id_jugador == 1:
            return self.teclas_jugador2
        return self.teclas_jugador1
