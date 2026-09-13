"""Modelo que representa a un jugador controlado por un humano."""

from models.jugador import Jugador


class JugadorHumano(Jugador):
    """Clase que representa a un jugador controlado por teclado."""

    def __init__(self, x, y, id_jugador, teclas, nombre=None):
        """Inicializa un jugador humano con configuración de teclas.

        Args:
            x (int): Coordenada horizontal inicial.
            y (int): Coordenada vertical inicial.
            id_jugador (int): Identificador único del jugador.
            teclas (dict): Diccionario que mapea acciones a teclas del teclado.
            nombre (str, optional): Nombre del jugador. Por defecto "J{id+1}".
        """
        super().__init__(x, y, id_jugador, nombre)
        self.teclas = teclas

    def mover(self, teclas_presionadas=None, en_zona_lenta=False):
        """Mueve el jugador según las teclas presionadas.

        Args:
            teclas_presionadas: Estado de las teclas del teclado.
            en_zona_lenta (bool): True si el jugador está en una zona que ralentiza.
        """
        if teclas_presionadas is None:
            return

        velocidad = self.config.VELOCIDAD_JUGADOR
        if en_zona_lenta:
            velocidad *= self.config.FACTOR_RALENTIZACION

        if teclas_presionadas[self.teclas['arriba']]:
            self.y -= velocidad
        if teclas_presionadas[self.teclas['abajo']]:
            self.y += velocidad
        if teclas_presionadas[self.teclas['izquierda']]:
            self.x -= velocidad
        if teclas_presionadas[self.teclas['derecha']]:
            self.x += velocidad

        self._limitar_pantalla()

    def _limitar_pantalla(self):
        """Limita la posición del jugador a los bordes de la pantalla."""
        self.x = max(0, min(self.x, self.config.ANCHO_PANTALLA - self.config.TAMAÑO_JUGADOR))
        self.y = max(0, min(self.y, self.config.ALTO_PANTALLA - self.config.TAMAÑO_JUGADOR))