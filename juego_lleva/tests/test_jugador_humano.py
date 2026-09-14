"""Pruebas del movimiento por tiempo real del jugador humano."""

import os
import unittest

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from core.config import Config
from models.jugador_humano import JugadorHumano


class TestJugadorHumanoRealTime(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.teclas = {
            'arriba': 1, 'abajo': 2, 'izquierda': 3, 'derecha': 4
        }

    def _presionadas(self, *teclas):
        estado = {1: False, 2: False, 3: False, 4: False}
        for t in teclas:
            estado[t] = True
        return estado

    def test_mueve_velocidad_en_px_por_segundo(self):
        jugador = JugadorHumano(0, 0, 0, self.teclas)
        jugador.mover(self._presionadas(self.teclas['derecha']), delta_tiempo=1.0)
        self.assertAlmostEqual(jugador.x, self.config.VELOCIDAD_JUGADOR, delta=1)

    def test_delta_escala_el_desplazamiento(self):
        jugador = JugadorHumano(0, 0, 0, self.teclas)
        jugador.mover(self._presionadas(self.teclas['derecha']), delta_tiempo=0.5)
        self.assertAlmostEqual(jugador.x, self.config.VELOCIDAD_JUGADOR / 2, delta=1)

    def test_diagonal_mueve_en_ambos_ejes(self):
        jugador = JugadorHumano(100, 100, 0, self.teclas)
        jugador.mover(self._presionadas(self.teclas['arriba'], self.teclas['derecha']),
                      delta_tiempo=0.5)
        self.assertLess(jugador.y, 100)
        self.assertGreater(jugador.x, 100)

    def test_zona_lenta_reduce_velocidad(self):
        jugador = JugadorHumano(0, 0, 0, self.teclas)
        jugador.mover(self._presionadas(self.teclas['derecha']),
                      en_zona_lenta=True, delta_tiempo=1.0)
        esperado = self.config.VELOCIDAD_JUGADOR * self.config.FACTOR_RALENTIZACION
        self.assertAlmostEqual(jugador.x, esperado, delta=1)

    def test_limita_en_los_bordes(self):
        jugador = JugadorHumano(0, 0, 0, self.teclas)
        jugador.mover(self._presionadas(self.teclas['arriba'], self.teclas['izquierda']),
                      delta_tiempo=10.0)
        self.assertEqual(jugador.x, 0)
        self.assertEqual(jugador.y, 0)


if __name__ == '__main__':
    unittest.main()