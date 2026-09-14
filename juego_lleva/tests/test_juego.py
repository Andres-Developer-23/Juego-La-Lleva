"""Prueba de integración de la regla clásica a través de Juego (headless)."""

import os
import unittest

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

from core.config import Config
from core.juego import Juego
from models.power_up import PowerUp


class TestReglaClasicaIntegracion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def setUp(self):
        self.juego = Juego(Config())

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
        self.assertEqual(len(juego.efectos), 1)
        self.assertGreater(len(juego.efectos[0]['particulas']), 0)

        juego.tiempo_ronda = 60
        juego._finalizar_ronda()

        self.assertEqual(juego.puntaje_service.tiempos_lleva[0], 10)
        self.assertEqual(juego.puntaje_service.tiempos_lleva[1], 50)
        self.assertEqual(juego.puntaje_service.obtener_ganador(), 0)
        self.assertEqual(juego.estado, "fin_ronda")

    def test_escudo_bloquea_el_toque(self):
        juego = self.juego
        juego.gestor_modos.iniciar_multijugador(juego, ["Ana", "Beto"])
        juego.set_lleva_inicial(0)
        ana, beto = juego.jugadores[0], juego.jugadores[1]

        beto.escudo = True
        juego._procesar_colision(ana, beto)

        self.assertTrue(ana.es_lleva)
        self.assertFalse(beto.escudo)
        self.assertEqual(juego.puntaje_service.tiempos_lleva.get(0, 0), 0)

    def test_recoger_power_up_aplica_efectos(self):
        juego = self.juego
        juego.gestor_modos.iniciar_multijugador(juego, ["Ana", "Beto"])
        juego.set_lleva_inicial(0)
        ana, beto = juego.jugadores[0], juego.jugadores[1]

        creado = PowerUp(0, 0, "velocidad")
        juego._recoger_power_up(ana, creado)
        self.assertEqual(ana.factor_velocidad, Config.FACTOR_VELOCIDAD_POWER)
        self.assertIn("velocidad", juego._timers_efectos(0))

        juego._recoger_power_up(ana, PowerUp(0, 0, "congelar"))
        self.assertGreater(juego._timers_efectos(1).get("congelar", 0), 0)

        juego._recoger_power_up(beto, PowerUp(0, 0, "escudo"))
        self.assertTrue(beto.escudo)

    def test_congelado_detiene_movimiento(self):
        juego = self.juego
        juego.gestor_modos.iniciar_multijugador(juego, ["Ana", "Beto"])
        juego.set_lleva_inicial(0)
        beto = juego.jugadores[1]
        juego._timers_efectos(1)["congelar"] = 3.0

        x_antes, y_antes = beto.x, beto.y
        juego._bucle_juego(0.5)
        self.assertEqual(beto.x, x_antes)
        self.assertEqual(beto.y, y_antes)
        self.assertGreater(juego._timers_efectos(1).get("congelar", 0), 0)

    def test_congelar_expira_y_se_limpia(self):
        juego = self.juego
        juego.gestor_modos.iniciar_multijugador(juego, ["Ana", "Beto"])
        juego.set_lleva_inicial(0)
        juego._timers_efectos(1)["congelar"] = 0.4

        juego._bucle_juego(0.5)
        self.assertNotIn("congelar", juego._timers_efectos(1))

    def test_dificultad_aplicada_a_ia(self):
        juego = self.juego
        juego.modo = "un_jugador"
        juego.nombres = ["Ana"]
        juego.gestor_modos.iniciar_un_jugador(juego, "Ana")
        juego.configuracion.establecer("dificultad_ia", "dificil")
        juego._aplicar_dificultad_ia()
        ia = juego.jugadores[1]
        self.assertEqual(ia.config.VELOCIDAD_IA, Config.DIFICULTADES["dificil"]["VELOCIDAD_IA"])


if __name__ == '__main__':
    unittest.main()