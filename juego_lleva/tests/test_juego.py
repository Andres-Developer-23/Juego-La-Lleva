"""Prueba de integración de la regla clásica a través de Juego (headless)."""

import os
import unittest

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

from core.config import Config
from core.juego import Juego


class TestReglaClasicaIntegracion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.juego = Juego(Config())

    def test_transferencia_y_ganador(self):
        juego = self.juego
        juego.gestor_modos.iniciar_multijugador(juego, ["Ana", "Beto"])
        juego.set_lleva_inicial(0)

        juego.tiempo_ronda = 10
        juego.tiempo_inicio_lleva = 0
        beto, ana = juego.jugadores[1], juego.jugadores[0]
        juego._transferir_lleva(ana, beto)

        self.assertFalse(ana.es_lleva)
        self.assertTrue(beto.es_lleva)
        self.assertEqual(juego.puntaje_service.tiempos_lleva[0], 10)

        juego.tiempo_ronda = 60
        juego._finalizar_ronda()

        self.assertEqual(juego.puntaje_service.tiempos_lleva[0], 10)
        self.assertEqual(juego.puntaje_service.tiempos_lleva[1], 50)
        self.assertEqual(juego.puntaje_service.obtener_ganador(), 0)
        self.assertEqual(juego.estado, "fin_ronda")


if __name__ == '__main__':
    unittest.main()