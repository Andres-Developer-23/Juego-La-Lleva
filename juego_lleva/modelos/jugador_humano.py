from modelos.jugador import Jugador


class JugadorHumano(Jugador):
    def __init__(self, x, y, id_jugador, teclas, nombre=None):
        super().__init__(x, y, id_jugador, nombre)
        self.teclas = teclas

    def mover(self, teclas_presionadas=None, en_zona_lenta=False):
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
        self.x = max(0, min(self.x, self.config.ANCHO_PANTALLA - self.config.TAMAÑO_JUGADOR))
        self.y = max(0, min(self.y, self.config.ALTO_PANTALLA - self.config.TAMAÑO_JUGADOR))
