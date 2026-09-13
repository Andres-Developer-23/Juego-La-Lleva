"""Gestor de modos de juego que administra la inicialización de partidas."""

from controles.controlador import Controlador
from models.entorno import Entorno


class GestorModos:
    """Clase que administra los diferentes modos de juego."""

    def __init__(self):
        """Inicializa el gestor con controlador y entorno."""
        self.controlador = Controlador()
        self.entorno = Entorno()

    def iniciar_multijugador(self, juego, nombres=None):
        """Inicia una partida multijugador con los jugadores especificados.

        Args:
            juego: Instancia del juego principal.
            nombres (list, optional): Lista de nombres para los jugadores.
        """
        juego.jugadores.clear()
        juego.jugadores_views.clear()

        positions = [(100, 100), (900, 100)]

        for i in range(2):
            teclas = self.controlador.obtener_teclas_jugador(i)
            nombre = nombres[i] if nombres and i < len(nombres) else f"J{i + 1}"
            juego.crear_jugador(positions[i][0], positions[i][1],
                                i, teclas=teclas, nombre=nombre)

        self.entorno.generar_obstaculos(juego.jugadores)

        juego.set_lleva_inicial(0)
        juego.tiempo_ronda = 0
        juego.puntaje_service.reiniciar()
