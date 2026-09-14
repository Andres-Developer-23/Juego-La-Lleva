"""Pruebas de la vista de efectos visuales."""

import os
import unittest

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

from views.efecto_view import EfectoView


class TestEfectoView(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.vista = EfectoView()
        self.pantalla = pygame.Surface((800, 600))

    def test_crear_toque_genera_anillo_y_particulas(self):
        efecto = self.vista.crear_toque(400, 300)
        self.assertEqual(efecto['tiempo'], 0)
        self.assertGreater(len(efecto['particulas']), 0)

    def test_actualizar_elimina_efectos_vencidos(self):
        efecto = self.vista.crear_toque(400, 300)
        efecto['tiempo'] = self.vista.DURACION - 0.1
        vivos = self.vista.actualizar([efecto], 0.2)
        self.assertEqual(vivos, [])

    def test_actualizar_conserva_efectos_nuevos(self):
        efecto = self.vista.crear_toque(400, 300)
        vivos = self.vista.actualizar([efecto], 0.1)
        self.assertEqual(len(vivos), 1)

    def test_renderizar_no_lanza_errores(self):
        efecto = self.vista.crear_toque(400, 300)
        self.vista.renderizar(self.pantalla, [efecto])
        self.vista.actualizar([efecto], 0.3)
        self.vista.renderizar(self.pantalla, [efecto])


if __name__ == '__main__':
    unittest.main()