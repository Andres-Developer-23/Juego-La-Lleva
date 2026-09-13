import sys

import pygame
from controles.controlador import Controlador
from models.jugador_humano import JugadorHumano
from servicios.colision import ColisionService
from servicios.puntaje import PuntajeService
from ui.interfaz import Interfaz

from core.config import Config
from core.gestor_modos import GestorModos

from views.jugador_view import JugadorView
from views.entorno_view import EntornoView


class Juego:
    def __init__(self, config):
        self.config = config
        self.pantalla = pygame.display.set_mode(
            (config.ANCHO_PANTALLA, config.ALTO_PANTALLA))
        pygame.display.set_caption("La Lleva - Juego Tradicional Colombiano")
        self.reloj = pygame.time.Clock()
        self.controlador = Controlador()
        self.interfaz = Interfaz()
        self.puntaje_service = PuntajeService()
        self.servicio_colision = ColisionService()
        self.gestor_modos = GestorModos()
        self.jugadores = []
        self.jugadores_views = []
        self.entorno_view = EntornoView()
        self.tiempo_ronda = 0
        self.estado = "menu"
        self.tiempo_inicio_lleva = 0
        self.mouse_pos = None
        self.click_realizado = False
        self.tiempo_anterior = 0
        self.countdown_valor = 3
        self.countdown_timer = 0
        self.nombres = ["J1", "J2"]
        self.nombre_activo = 0
        self.fondo = self._cargar_fondo()
        self.jugador_explotando = None
        self.ganador_explosion = None

    def _cargar_fondo(self):
        try:
            imagen = pygame.image.load(self.config.FONDO).convert()
            return pygame.transform.scale(imagen, (self.config.ANCHO_PANTALLA, self.config.ALTO_PANTALLA))
        except:
            return None

    def ejecutar(self):
        self.tiempo_anterior = pygame.time.get_ticks() / 1000.0
        while True:
            tiempo_actual = pygame.time.get_ticks() / 1000.0
            delta_tiempo = tiempo_actual - self.tiempo_anterior
            self.tiempo_anterior = tiempo_actual

            self.mouse_pos = pygame.mouse.get_pos()
            self.click_realizado = False
            self.eventos_pendientes = []

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.click_realizado = True
                self.eventos_pendientes.append(evento)

            self.interfaz.actualizar(delta_tiempo)

            if self.estado == "menu":
                self._menu_principal()
            elif self.estado == "nombres":
                self._pantalla_nombres()
            elif self.estado == "jugando":
                self._bucle_juego(delta_tiempo)
            elif self.estado == "fin_ronda":
                self._pantalla_fin_ronda()
            elif self.estado == "ayuda":
                self._pantalla_ayuda()
            elif self.estado == "countdown":
                self._pantalla_countdown(delta_tiempo)
            elif self.estado == "explosion":
                self._pantalla_explosion(delta_tiempo)

    def _menu_principal(self):
        accion = self.interfaz.obtener_accion_menu(self.mouse_pos, self.click_realizado)

        if accion == "jugar":
            self.nombres = ["J1", "J2"]
            self.nombre_activo = 0
            self.estado = "nombres"
        elif accion == "ayuda":
            self.estado = "ayuda"
        elif accion == "salir":
            pygame.quit()
            sys.exit()

        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    self.nombres = ["J1", "J2"]
                    self.nombre_activo = 0
                    self.estado = "nombres"
                elif evento.key == pygame.K_2:
                    pygame.quit()
                    exit()

        self.interfaz.dibujar_menu_principal(self.pantalla, self.mouse_pos)
        pygame.display.flip()

    def _pantalla_nombres(self):
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.estado = "menu"
                    return
                elif evento.key == pygame.K_TAB:
                    self.nombre_activo = (self.nombre_activo + 1) % 2
                elif evento.key == pygame.K_RETURN:
                    self.gestor_modos.iniciar_multijugador(self, self.nombres)
                    self.estado = "countdown"
                    self.countdown_valor = 3
                    self.countdown_timer = 0
                    return
                elif evento.key == pygame.K_BACKSPACE:
                    self.nombres[self.nombre_activo] = self.nombres[self.nombre_activo][:-1]
                elif evento.unicode.isprintable() and len(self.nombres[self.nombre_activo]) < 12:
                    self.nombres[self.nombre_activo] += evento.unicode

        if self.click_realizado and self.mouse_pos:
            x, y = self.mouse_pos
            if (self.config.ANCHO_PANTALLA // 2 - 140 <= x <= self.config.ANCHO_PANTALLA // 2 + 140 and
                520 <= y <= 570):
                self.gestor_modos.iniciar_multijugador(self, self.nombres)
                self.estado = "countdown"
                self.countdown_valor = 3
                self.countdown_timer = 0
                return

        self.interfaz.dibujar_pantalla_nombres(self.pantalla, self.nombres,
                                                self.nombre_activo, self.mouse_pos)
        pygame.display.flip()

    def _pantalla_ayuda(self):
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.estado = "menu"
                return

        self.interfaz.dibujar_ayuda(self.pantalla, self.mouse_pos)

        if self.click_realizado and self.mouse_pos:
            x, y = self.mouse_pos
            if (self.config.ANCHO_PANTALLA // 2 - 100 <= x <= self.config.ANCHO_PANTALLA // 2 + 100 and
                670 <= y <= 720):
                self.estado = "menu"

        pygame.display.flip()
        self.reloj.tick(self.config.FPS)

    def _pantalla_countdown(self, delta_tiempo):
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.estado = "menu"
                return

        self.countdown_timer += delta_tiempo

        if self.countdown_timer >= 1.0:
            self.countdown_timer = 0
            self.countdown_valor -= 1
            if self.countdown_valor <= 0:
                self.estado = "jugando"
                return

        self.interfaz.dibujar_countdown(self.pantalla, self.countdown_valor)
        pygame.display.flip()
        self.reloj.tick(self.config.FPS)

    def _bucle_juego(self, delta_tiempo):
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.estado = "menu"
                return

        teclas = pygame.key.get_pressed()

        obstaculos = self.gestor_modos.entorno.obstaculos

        for jugador in self.jugadores:
            en_zona = self.servicio_colision.jugador_en_zona_lenta(jugador, obstaculos)
            jugador.mover(teclas, en_zona)

        for jugador in self.jugadores:
            for obs in obstaculos:
                if obs.tipo == "caja" and self.servicio_colision.detectar_colision_jugador_obstaculo(jugador, obs):
                    self.servicio_colision.rebote_obstaculo(jugador, obs)

        colisiones = self.servicio_colision.detectar_colisiones(self.jugadores)
        for j1, j2 in colisiones:
            self._procesar_colision(j1, j2)
            self.servicio_colision.separar_jugadores(j1, j2, self.config.TAMAÑO_JUGADOR)

        self.tiempo_ronda += 1 / self.config.FPS
        if self.tiempo_ronda >= self.config.DURACION_RONDA:
            self._finalizar_ronda()
            return

        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill(self.config.COLOR_FONDO)

        self.entorno_view.renderizar(self.pantalla, self.gestor_modos.entorno, self.tiempo_ronda)

        for i, jugador in enumerate(self.jugadores):
            if i < len(self.jugadores_views):
                self.jugadores_views[i].renderizar(self.pantalla, jugador, delta_tiempo)

        self.interfaz.dibujar_hud(self.pantalla, self.tiempo_ronda,
                                  self.puntaje_service.tiempos_lleva, self.jugadores)

        pygame.display.flip()
        self.reloj.tick(self.config.FPS)

    def _pantalla_explosion(self, delta_tiempo):
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.estado = "menu"
                return

        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill(self.config.COLOR_FONDO)

        self.entorno_view.renderizar(self.pantalla, self.gestor_modos.entorno, self.tiempo_ronda)

        for i, jugador in enumerate(self.jugadores):
            if i < len(self.jugadores_views):
                self.jugadores_views[i].renderizar(self.pantalla, jugador, delta_tiempo)

        self.interfaz.dibujar_hud(self.pantalla, self.tiempo_ronda,
                                  self.puntaje_service.tiempos_lleva, self.jugadores)

        if self.jugador_explotando and self.jugador_explotando.explosion_terminada():
            self.estado = "fin_ronda"

        pygame.display.flip()
        self.reloj.tick(self.config.FPS)

    def _procesar_colision(self, j1, j2):
        if j1.es_lleva:
            self._iniciar_explosion(j1, j2)
        elif j2.es_lleva:
            self._iniciar_explosion(j2, j1)

    def _iniciar_explosion(self, quien_tiene_lleva, quien_explota):
        tiempo_lleva = self.tiempo_ronda - self.tiempo_inicio_lleva
        self.puntaje_service.registrar_lleva(quien_tiene_lleva.id, tiempo_lleva)
        self.ganador_explosion = quien_tiene_lleva
        self.jugador_explotando = quien_explota
        quien_explota.iniciar_explosion()
        self.estado = "explosion"

    def _finalizar_ronda(self):
        for jugador in self.jugadores:
            if jugador.es_lleva:
                tiempo_lleva = self.tiempo_ronda - self.tiempo_inicio_lleva
                self.puntaje_service.registrar_lleva(jugador.id, tiempo_lleva)
                self.ganador_explosion = None
        self.estado = "fin_ronda"

    def _pantalla_fin_ronda(self):
        if self.ganador_explosion:
            ganador = self.ganador_explosion.id
        else:
            ganador = self.puntaje_service.obtener_ganador()

        accion = self.interfaz.obtener_accion_fin_ronda(self.mouse_pos, self.click_realizado)

        if accion == "revancha":
            self.gestor_modos.iniciar_multijugador(self, self.nombres)
            self.estado = "countdown"
            self.countdown_valor = 3
            self.countdown_timer = 0
            return
        elif accion == "menu":
            self.estado = "menu"
            return

        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                self.gestor_modos.iniciar_multijugador(self, self.nombres)
                self.estado = "countdown"
                self.countdown_valor = 3
                self.countdown_timer = 0
                return
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.estado = "menu"
                return

        self.pantalla.fill(self.config.COLOR_FONDO)
        self.interfaz.dibujar_fin_ronda(self.pantalla, ganador,
                                        self.puntaje_service.tiempos_lleva, self.mouse_pos,
                                        self.jugadores)
        pygame.display.flip()

    def crear_jugador(self, x, y, id_jugador, teclas=None, nombre=None):
        jugador = JugadorHumano(x, y, id_jugador, teclas, nombre)
        self.jugadores.append(jugador)
        jugador_view = JugadorView()
        jugador_view.cargar_sprites(jugador)
        self.jugadores_views.append(jugador_view)
        return jugador

    def set_lleva_inicial(self, id_jugador):
        for j in self.jugadores:
            j.es_lleva = (j.id == id_jugador)
        self.tiempo_inicio_lleva = 0
        self.servicio_colision.limpiar_cooldown()
