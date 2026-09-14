"""Módulo principal del juego que orquesta todos los componentes MVC."""

import random
import sys

import pygame
from controles.tactil import ControladorTactil
from models.jugador_humano import JugadorHumano
from models.jugador_ia import JugadorIA
from servicios.audio import ServicioAudio
from servicios.colision import ColisionService
from servicios.configuracion import ConfiguracionService
from servicios.power_up_service import PowerUpService
from servicios.puntaje import PuntajeService
from servicios.ranking import RankingService
from servicios.ronda import RondaService
from ui.interfaz import Interfaz

from core.config import Config
from core.gestor_modos import GestorModos

from views.jugador_view import JugadorView
from views.entorno_view import EntornoView
from views.efecto_view import EfectoView
from views.power_up_view import PowerUpView


class TeclasFusionadas:
    """Mapa de teclas que combina el teclado físico con teclas virtuales."""

    def __init__(self, base, extras):
        self.base = base
        self.extras = set(extras)

    def __getitem__(self, codigo):
        return bool(self.base[codigo]) or codigo in self.extras


class Juego:
    """Clase principal que orquesta el juego completo."""

    def __init__(self, config):
        """Inicializa el juego con la configuración especificada.

        Args:
            config: Instancia de Config con los parámetros del juego.
        """
        self.config = config
        self.pantalla = pygame.display.set_mode(
            (config.ANCHO_PANTALLA, config.ALTO_PANTALLA))
        pygame.display.set_caption("La Lleva - Juego Tradicional Colombiano")
        self.reloj = pygame.time.Clock()
        self.interfaz = Interfaz()
        self.tactil = ControladorTactil(config.ANCHO_PANTALLA, config.ALTO_PANTALLA)
        self.configuracion = ConfiguracionService(config.SETTINGS_PATH)
        self.duracion_ronda = self.configuracion.obtener("duracion_ronda")
        self.puntaje_service = PuntajeService()
        self.servicio_colision = ColisionService()
        self.ranking_service = RankingService(config.RANKING_PATH)
        self.ronda_service = RondaService(self.puntaje_service)
        self.power_up_service = PowerUpService(config)
        self.audio = ServicioAudio()
        self.audio.set_volumen_sfx(self.configuracion.obtener("volumen_sfx"))
        self.audio.set_volumen_musica(self.configuracion.obtener("volumen_musica"))
        self.musica_activa = True
        if self.configuracion.obtener("pantalla_completa"):
            self._alternar_pantalla_completa()
        self.modo = "dos_jugadores"
        self.gestor_modos = GestorModos()
        self.jugadores = []
        self.jugadores_views = []
        self.entorno_view = EntornoView()
        self.efecto_view = EfectoView()
        self.efectos = []
        self.power_up_view = PowerUpView()
        self.power_ups = []
        self.power_up_timer = 0
        self.efectos_activos = {}
        self.tiempo_ronda = 0
        self.estado = "menu"
        self.opcion_activa = 0
        self.opcion_menu = 0
        self.toasts = []
        self.tiempo_inicio_lleva = 0
        self.fade_alpha = 0
        self.mouse_pos = None
        self.click_realizado = False
        self.tiempo_anterior = 0
        self.eventos_pendientes = []
        self.countdown_valor = 3
        self.countdown_timer = 0
        self.nombres = ["J1", "J2"]
        self.nombre_activo = 0
        self.fondo = self._cargar_fondo()
        self._ranking_registrado = False

    def _cargar_fondo(self):
        """Carga la imagen de fondo del juego.

        Returns:
            pygame.Surface: Imagen de fondo escalada o None si hay error.
        """
        try:
            imagen = pygame.image.load(self.config.FONDO).convert()
            return pygame.transform.scale(imagen, (self.config.ANCHO_PANTALLA, self.config.ALTO_PANTALLA))
        except (pygame.error, OSError):
            return None

    def _alternar_pantalla_completa(self):
        """Alterna entre modo ventana y pantalla completa."""
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            pass

    def _gestionar_musica(self):
        """Inicia o detiene la música según la preferencia del jugador."""
        if not self.audio.activo:
            return
        if self.musica_activa and not self.audio.musica_suena():
            self.audio.reproducir_musica()
        elif not self.musica_activa and self.audio.musica_suena():
            self.audio.detener_musica()

    def ejecutar(self):
        """Ejecuta el bucle principal del juego."""
        self.tiempo_anterior = pygame.time.get_ticks() / 1000.0
        while True:
            self._procesar_frame()

    def _procesar_frame(self):
        """Procesa un frame completo del juego."""
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
            if evento.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
                self.tactil.procesar_evento(evento)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    self._alternar_pantalla_completa()
                    self.configuracion.establecer(
                        "pantalla_completa", bool(pygame.display.get_fullscreen()))
                elif evento.key == pygame.K_m and self.estado != "nombres":
                    self.musica_activa = not self.musica_activa
            self.eventos_pendientes.append(evento)

        self.interfaz.actualizar(delta_tiempo)
        self._gestionar_musica()
        if self.toasts:
            self.toasts = self.interfaz.actualizar_toasts(self.toasts, delta_tiempo)

        if self.estado == "menu":
            self._menu_principal()
        elif self.estado == "nombres":
            self._pantalla_nombres()
        elif self.estado == "jugando":
            self._bucle_juego(delta_tiempo)
        elif self.estado == "pausa":
            self._pantalla_pausa()
        elif self.estado == "fin_ronda":
            self._pantalla_fin_ronda()
        elif self.estado == "ayuda":
            self._pantalla_ayuda()
        elif self.estado == "countdown":
            self._pantalla_countdown(delta_tiempo)
        elif self.estado == "ranking":
            self._pantalla_ranking()
        elif self.estado == "opciones":
            self._pantalla_opciones()

        if self.fade_alpha > 0:
            fundido = pygame.Surface(
                (self.config.ANCHO_PANTALLA, self.config.ALTO_PANTALLA), pygame.SRCALPHA)
            fundido.fill((0, 0, 0, int(self.fade_alpha)))
            self.pantalla.blit(fundido, (0, 0))
            self.fade_alpha = max(0, self.fade_alpha - delta_tiempo * 255 / self.config.DURACION_FUNDIDO_SEG)
            pygame.display.flip()

    def _menu_principal(self):
        """Maneja la pantalla del menú principal con mouse y teclado."""
        accion = self.interfaz.obtener_accion_menu(self.mouse_pos, self.click_realizado)

        if accion:
            self._ejecutar_accion_menu(accion)
            return

        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    self._ejecutar_accion_menu("un_jugador")
                    return
                elif evento.key == pygame.K_2:
                    self._ejecutar_accion_menu("jugar")
                    return
                elif evento.key == pygame.K_3:
                    self._ejecutar_accion_menu("opciones")
                    return
                elif evento.key == pygame.K_UP:
                    self.opcion_menu = (self.opcion_menu - 1) % self.config.BOTONES_MENU
                    self.audio.clic()
                elif evento.key == pygame.K_DOWN:
                    self.opcion_menu = (self.opcion_menu + 1) % self.config.BOTONES_MENU
                    self.audio.clic()
                elif evento.key == pygame.K_RETURN:
                    self._ejecutar_accion_menu(self.interfaz.acciones_menu[self.opcion_menu])
                    return

        self.interfaz.dibujar_menu_principal(self.pantalla, self.mouse_pos, self.opcion_menu)
        pygame.display.flip()

    def _ejecutar_accion_menu(self, accion):
        """Ejecuta la acción seleccionada en el menú principal.

        Args:
            accion (str): Identificador de la acción del menú.
        """
        if accion == "un_jugador":
            self.modo = "un_jugador"
            self.nombres = ["J1"]
            self.nombre_activo = 0
            self.estado = "nombres"
        elif accion == "jugar":
            self.modo = "dos_jugadores"
            self.nombres = ["J1", "J2"]
            self.nombre_activo = 0
            self.estado = "nombres"
        elif accion == "ayuda":
            self.estado = "ayuda"
        elif accion == "ranking":
            self.estado = "ranking"
        elif accion == "opciones":
            self.estado = "opciones"
            self.opcion_activa = 0
        elif accion == "salir":
            pygame.quit()
            sys.exit()
        self.audio.clic()
        if accion not in ("salir",):
            self.opcion_menu = self.interfaz.acciones_menu.index(accion)

    def _pantalla_nombres(self):
        """Maneja la pantalla de ingreso de nombres."""
        cantidad_jugadores = len(self.nombres)
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self._volver_al_menu()
                    return
                elif evento.key == pygame.K_TAB and cantidad_jugadores > 1:
                    self.nombre_activo = (self.nombre_activo + 1) % cantidad_jugadores
                elif evento.key == pygame.K_RETURN:
                    self._iniciar_partida()
                    return
                elif evento.key == pygame.K_BACKSPACE:
                    self.nombres[self.nombre_activo] = self.nombres[self.nombre_activo][:-1]
                elif evento.unicode.isprintable() and len(self.nombres[self.nombre_activo]) < 12:
                    self.nombres[self.nombre_activo] += evento.unicode

        if self.click_realizado and self.mouse_pos:
            x, y = self.mouse_pos
            if (self.config.ANCHO_PANTALLA // 2 - 140 <= x <= self.config.ANCHO_PANTALLA // 2 + 140 and
                520 <= y <= 570):
                self._iniciar_partida()
                return

        self.interfaz.dibujar_pantalla_nombres(self.pantalla, self.nombres,
                                                self.nombre_activo, self.mouse_pos,
                                                cantidad_jugadores)
        pygame.display.flip()

    def _pantalla_ayuda(self):
        """Maneja la pantalla de ayuda."""
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self._volver_al_menu()
                return

        self.interfaz.dibujar_ayuda(self.pantalla, self.mouse_pos)

        if self.click_realizado and self.mouse_pos:
            x, y = self.mouse_pos
            if (self.config.ANCHO_PANTALLA // 2 - 100 <= x <= self.config.ANCHO_PANTALLA // 2 + 100 and
                670 <= y <= 720):
                self._volver_al_menu()

        pygame.display.flip()
        self.reloj.tick(self.config.FPS)

    def _pantalla_countdown(self, delta_tiempo):
        """Maneja la pantalla de countdown antes de iniciar la partida.

        Args:
            delta_tiempo (float): Tiempo transcurrido desde la última actualización.
        """
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self._volver_al_menu()
                return

        self.countdown_timer += delta_tiempo

        if self.countdown_timer >= 1.0:
            self.countdown_timer = 0
            self.countdown_valor -= 1
            if self.countdown_valor <= 0:
                self.audio.inicio()
                self._mostrar_toast("¡A jugar!", self.config.COLOR_LIBRE)
                self.estado = "jugando"
                return
            self.audio.beep()

        self.interfaz.dibujar_countdown(self.pantalla, self.countdown_valor)
        pygame.display.flip()
        self.reloj.tick(self.config.FPS)

    def _bucle_juego(self, delta_tiempo):
        """Ejecuta el bucle principal de juego.

        Args:
            delta_tiempo (float): Tiempo transcurrido desde la última actualización.
        """
        if self.tactil.consumir_pausa():
            self.estado = "pausa"
            return

        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_p):
                self.estado = "pausa"
                return

        teclas = self._teclas_fusionadas()

        obstaculos = self.gestor_modos.entorno.obstaculos
        self.gestor_modos.entorno.actualizar(delta_tiempo)

        self._actualizar_power_ups(delta_tiempo)
        self._actualizar_efectos_activos(delta_tiempo)

        for jugador in self.jugadores:
            if self._timers_efectos(jugador.id).get("congelar", 0) > 0:
                continue
            en_zona = self.servicio_colision.jugador_en_zona_lenta(jugador, obstaculos)
            jugador.mover(teclas, en_zona, delta_tiempo)

        for jugador in self.jugadores:
            for obs in obstaculos:
                if obs.tipo == "caja" and self.servicio_colision.detectar_colision_jugador_obstaculo(jugador, obs):
                    self.servicio_colision.rebote_obstaculo(jugador, obs, delta_tiempo)

        colisiones = self.servicio_colision.detectar_colisiones(self.jugadores)
        for j1, j2 in colisiones:
            self._procesar_colision(j1, j2)
            self.servicio_colision.separar_jugadores(j1, j2, self.config.TAMAÑO_JUGADOR)

        self.tiempo_ronda += delta_tiempo
        if self.tiempo_ronda >= self.duracion_ronda:
            self._finalizar_ronda()
            return

        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill(self.config.COLOR_FONDO)

        self.entorno_view.renderizar(self.pantalla, self.gestor_modos.entorno, self.tiempo_ronda)
        self.power_up_view.renderizar(self.pantalla, self.power_ups, self.tiempo_ronda)

        for i, jugador in enumerate(self.jugadores):
            if i < len(self.jugadores_views):
                self.jugadores_views[i].renderizar(self.pantalla, jugador, delta_tiempo)

        self.efectos = self.efecto_view.actualizar(self.efectos, delta_tiempo)
        self.efecto_view.renderizar(self.pantalla, self.efectos)

        self.interfaz.dibujar_hud(self.pantalla, self.tiempo_ronda,
                                  self.puntaje_service.tiempos_lleva, self.jugadores,
                                  self.duracion_ronda, self.efectos_activos)
        self.interfaz.dibujar_toasts(self.pantalla, self.toasts)
        self.tactil.dibujar(self.pantalla)

        pygame.display.flip()
        self.reloj.tick(self.config.FPS)

    def _teclas_fusionadas(self):
        """Combina las teclas físicas con las teclas virtuales táctiles.

        Returns:
            TeclasFusionadas: Objeto que indexa teclas físicas y virtuales.
        """
        return TeclasFusionadas(pygame.key.get_pressed(), self.tactil.teclas_activas())

    def _mostrar_toast(self, texto, color=None):
        """Muestra una notificación breve en pantalla.

        Args:
            texto (str): Mensaje a mostrar.
            color (tuple, optional): Color del texto.
        """
        if len(self.toasts) >= 4:
            self.toasts.pop(0)
        self.toasts.append({
            'texto': texto,
            'color': color or (255, 255, 255),
            'tiempo': 0.0,
            'duracion': 2.5,
        })

    def _timers_efectos(self, id_jugador):
        """Devuelve los temporizadores de efectos de un jugador.

        Args:
            id_jugador (int): ID del jugador.

        Returns:
            dict: Mapa tipo -> segundos restantes.
        """
        return self.efectos_activos.setdefault(id_jugador, {})

    def _actualizar_efectos_activos(self, delta_tiempo):
        """Decrementa los temporizadores de efectos y revierte los vencidos.

        Args:
            delta_tiempo (float): Tiempo transcurrido desde la última actualización.
        """
        vencidos = []
        for id_jugador, timers in list(self.efectos_activos.items()):
            for tipo in list(timers):
                timers[tipo] -= delta_tiempo
                if timers[tipo] <= 0:
                    vencidos.append((id_jugador, tipo))
                    del timers[tipo]
            if not timers:
                del self.efectos_activos[id_jugador]

        for id_jugador, tipo in vencidos:
            if tipo == "velocidad":
                jugador = next((j for j in self.jugadores if j.id == id_jugador), None)
                if jugador:
                    jugador.factor_velocidad = 1.0

    def _actualizar_power_ups(self, delta_tiempo):
        """Genera, envejece y recolecta power-ups durante la ronda.

        Args:
            delta_tiempo (float): Tiempo transcurrido desde la última actualización.
        """
        self.power_up_timer += delta_tiempo
        if self.power_up_timer >= self.config.POWER_UP_FRECUENCIA_SEG:
            self.power_up_timer = 0
            nuevo = self.power_up_service.crear(self.jugadores, self.power_ups)
            if nuevo:
                self.power_ups.append(nuevo)

        for pu in self.power_ups:
            pu.vida -= delta_tiempo

        for jugador in self.jugadores:
            rect_jugador = jugador.obtener_rectangulo()
            for pu in list(self.power_ups):
                if rect_jugador.colliderect(pu.obtener_rectangulo()):
                    self._recoger_power_up(jugador, pu)
                    self.power_ups.remove(pu)

        self.power_ups = [pu for pu in self.power_ups if not pu.expirado()]

    def _recoger_power_up(self, jugador, power_up):
        """Aplica el efecto de un power-up recogido.

        Args:
            jugador: Jugador que recogió el power-up.
            power_up: Power-up recogido.
        """
        rival = next((j for j in self.jugadores if j.id != jugador.id), None)
        efecto = self.power_up_service.efecto(jugador, rival, power_up.tipo)
        if not efecto:
            return
        id_objetivo, tipo, duracion = efecto
        objetivo = next((j for j in self.jugadores if j.id == id_objetivo), None)
        if objetivo is None:
            return

        if tipo == "velocidad":
            objetivo.factor_velocidad = self.config.FACTOR_VELOCIDAD_POWER
            self._timers_efectos(id_objetivo)["velocidad"] = duracion
        elif tipo == "congelar":
            self._timers_efectos(id_objetivo)["congelar"] = duracion
        elif tipo == "escudo":
            objetivo.escudo = True

        color = self.power_up_view.COLORES.get(power_up.tipo, (255, 215, 0))
        if len(self.efectos) < 6:
            self.efectos.append(self.efecto_view.crear_toque(power_up.x, power_up.y, color, 10))
        self.audio.clic()

        if tipo == "velocidad":
            self._mostrar_toast(f"¡{objetivo.nombre}: VELOCIDAD!", color)
        elif tipo == "congelar":
            self._mostrar_toast(f"¡{objetivo.nombre} CONGELADO!", color)
        elif tipo == "escudo":
            self._mostrar_toast(f"¡{objetivo.nombre}: ESCUDO!", color)

    def _pantalla_pausa(self):
        """Maneja la pantalla de pausa durante la partida."""
        if self.tactil.consumir_pausa():
            self.estado = "jugando"
            return
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.estado = "jugando"
                    return
                if evento.key == pygame.K_q:
                    self._volver_al_menu()
                    return

        self.interfaz.dibujar_pausa(self.pantalla)
        pygame.display.flip()
        self.reloj.tick(self.config.FPS)

    def _procesar_colision(self, j1, j2):
        """Procesa la colisión entre dos jugadores.

        Args:
            j1: Primer jugador involucrado.
            j2: Segundo jugador involucrado.
        """
        if j1.es_lleva:
            if getattr(j2, "escudo", False):
                self._romper_escudo(j2, j1)
            else:
                self._transferir_lleva(j1, j2)
        elif j2.es_lleva:
            if getattr(j1, "escudo", False):
                self._romper_escudo(j1, j2)
            else:
                self._transferir_lleva(j2, j1)

    def _romper_escudo(self, protegido, llevador):
        """Consume el escudo de un jugador y bloquea el toque.

        Args:
            protegido: Jugador que poseía el escudo.
            llevador: Jugador que intentó tocarlo (sigue siendo 'La Lleva').
        """
        protegido.escudo = False
        self.audio.clic()
        self._mostrar_toast(f"¡Escudo de {protegido.nombre} bloqueado!", (100, 150, 255))
        x1, y1 = llevador.obtener_posicion()
        x2, y2 = protegido.obtener_posicion()
        if len(self.efectos) < 6:
            self.efectos.append(self.efecto_view.crear_anillo((x1 + x2) / 2, (y1 + y2) / 2, (100, 150, 255)))

    def _transferir_lleva(self, quien_tiene_lleva, quien_recibe):
        """Transfiere el rol de 'La Lleva' al jugador tocado.

        Args:
            quien_tiene_lleva: Jugador que tenía el rol de 'La Lleva'.
            quien_recibe: Jugador que fue tocado y pasa a ser 'La Lleva'.
        """
        self.tiempo_inicio_lleva = self.ronda_service.transferir_lleva(
            quien_tiene_lleva, quien_recibe, self.tiempo_ronda, self.tiempo_inicio_lleva)
        self._crear_efecto_toque(quien_tiene_lleva, quien_recibe)
        self.audio.tocar()
        self._mostrar_toast(f"¡{quien_recibe.nombre} es La Lleva!", self.config.COLOR_LLEVA)

    def _crear_efecto_toque(self, j1, j2):
        """Crea un efecto visual en el punto medio del toque.

        Args:
            j1: Primer jugador involucrado en el toque.
            j2: Segundo jugador involucrado en el toque.
        """
        x1, y1 = j1.obtener_posicion()
        x2, y2 = j2.obtener_posicion()
        if len(self.efectos) < 6:
            self.efectos.append(self.efecto_view.crear_toque((x1 + x2) / 2, (y1 + y2) / 2))

    def _finalizar_ronda(self):
        """Finaliza la ronda actual y determina el ganador."""
        self.ronda_service.cerrar_lleva_actual(self.jugadores, self.tiempo_ronda,
                                               self.tiempo_inicio_lleva)
        ganador = self.puntaje_service.obtener_ganador()
        if ganador is not None:
            nombre = next((j.nombre for j in self.jugadores if j.id == ganador), "Jugador")
            self._mostrar_toast(f"¡{nombre} gana!", self.config.COLOR_DORADO)
            ganador_jugador = next((j for j in self.jugadores if j.id == ganador), None)
            if ganador_jugador:
                x, y = ganador_jugador.obtener_posicion()
                for _ in range(8):
                    if len(self.efectos) >= 10:
                        break
                    self.efectos.append(self.efecto_view.crear_toque(
                        x + random.uniform(-80, 80), y + random.uniform(-80, 80),
                        self.config.COLOR_DORADO, 6))
        self.audio.fin_ronda()
        self.estado = "fin_ronda"

    def _pantalla_fin_ronda(self):
        """Maneja la pantalla de fin de ronda mostrando resultados."""
        ganador = self.puntaje_service.obtener_ganador()

        if not self._ranking_registrado:
            self._registrar_en_ranking(ganador)
            self._ranking_registrado = True

        accion = self.interfaz.obtener_accion_fin_ronda(self.mouse_pos, self.click_realizado)

        if accion == "revancha":
            self._iniciar_partida()
            return
        elif accion == "menu":
            self._volver_al_menu()
            return

        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_r):
                self._iniciar_partida()
                return
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self._volver_al_menu()
                return

        self.pantalla.fill(self.config.COLOR_FONDO)
        self.interfaz.dibujar_fin_ronda(self.pantalla, ganador,
                                        self.puntaje_service.tiempos_lleva, self.mouse_pos,
                                        self.jugadores)
        pygame.display.flip()

    def _registrar_en_ranking(self, ganador_id):
        """Registra la partida actual en el ranking.

        Args:
            ganador_id (int): ID del jugador ganador.
        """
        if ganador_id is None:
            return
        ganador_nombre = next((j.nombre for j in self.jugadores if j.id == ganador_id), f"J{ganador_id + 1}")
        tiempo_ganador = self.puntaje_service.tiempos_lleva.get(ganador_id, 0)
        jugadores_tiempos = {}
        for j in self.jugadores:
            jugadores_tiempos[j.nombre] = self.puntaje_service.tiempos_lleva.get(j.id, 0)
        self.ranking_service.registrar_partida(ganador_nombre, tiempo_ganador, jugadores_tiempos)

    def _pantalla_ranking(self):
        """Maneja la pantalla de ranking."""
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self._volver_al_menu()
                return

        accion = self.interfaz.obtener_accion_ranking(self.mouse_pos, self.click_realizado)
        if accion == "volver":
            self._volver_al_menu()
            return

        entradas = self.ranking_service.obtener_top(10)
        self.interfaz.dibujar_ranking(self.pantalla, entradas, self.mouse_pos)
        pygame.display.flip()

    def _pantalla_opciones(self):
        """Maneja la pantalla de opciones configurables."""
        for evento in self.eventos_pendientes:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self._volver_al_menu()
                    return
                elif evento.key == pygame.K_UP:
                    self.opcion_activa = (self.opcion_activa - 1) % 5
                elif evento.key == pygame.K_DOWN:
                    self.opcion_activa = (self.opcion_activa + 1) % 5
                elif evento.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self._cambiar_opcion(self.opcion_activa, evento.key == pygame.K_RIGHT)
                elif evento.key == pygame.K_RETURN:
                    self._cambiar_opcion(self.opcion_activa, True)

        accion = self.interfaz.obtener_accion_opciones(self.mouse_pos, self.click_realizado)
        if accion:
            if accion[0] == "volver":
                self._volver_al_menu()
                return
            if accion[0] == "cambiar":
                _, clave, direccion = accion
                self._aplicar_opcion(clave, direccion)

        self.interfaz.dibujar_opciones(self.pantalla, self.configuracion,
                                        self.opcion_activa, self.mouse_pos)
        pygame.display.flip()

    def _cambiar_opcion(self, indice, aumentar):
        """Cambia el valor de la opción seleccionada con el teclado.

        Args:
            indice (int): Índice de la fila seleccionada.
            aumentar (bool): True para incrementar, False para decrementar.
        """
        claves = ["duracion_ronda", "dificultad_ia", "volumen_musica", "volumen_sfx", "pantalla_completa"]
        if 0 <= indice < len(claves):
            self._aplicar_opcion(claves[indice], 1 if aumentar else -1)

    def _aplicar_opcion(self, clave, direccion):
        """Aplica un cambio de opción y sus efectos colaterales.

        Args:
            clave (str): Nombre de la clave de configuración.
            direccion (int): Paso (1 o -1).
        """
        self.configuracion.siguiente(clave, direccion)
        if clave == "duracion_ronda":
            self.duracion_ronda = self.configuracion.obtener("duracion_ronda")
        elif clave == "volumen_musica":
            self.audio.set_volumen_musica(self.configuracion.obtener("volumen_musica"))
            if self.musica_activa:
                self.audio.set_volumen_musica(self.configuracion.obtener("volumen_musica"))
        elif clave == "volumen_sfx":
            self.audio.set_volumen_sfx(self.configuracion.obtener("volumen_sfx"))
        elif clave == "pantalla_completa":
            self._alternar_pantalla_completa()
        self.audio.clic()

    def _iniciar_partida(self):
        """Prepara y arranca una partida, sin importar desde qué pantalla se invoque."""
        self._normalizar_nombres()
        self.toasts.clear()
        if self.modo == "un_jugador":
            self.gestor_modos.iniciar_un_jugador(self, self.nombres[0] if self.nombres else "J1")
        else:
            self.gestor_modos.iniciar_multijugador(self, self.nombres)
        self._aplicar_dificultad_ia()
        self._ranking_registrado = False
        self.efectos.clear()
        self.power_ups.clear()
        self.power_up_timer = 0
        self.efectos_activos.clear()
        for jugador in self.jugadores:
            jugador.escudo = False
            jugador.factor_velocidad = 1.0
            jugador.congelado = 0.0
        self.estado = "countdown"
        self.countdown_valor = 3
        self.countdown_timer = 0
        self.fade_alpha = 255
        self.audio.beep()

    def _normalizar_nombres(self):
        """Ajusta los nombres de los jugadores antes de iniciar (sin espacios vacíos)."""
        cantidad = len(self.nombres)
        for i in range(cantidad):
            nombre = (self.nombres[i] or "").strip()
            if not nombre:
                nombre = f"J{i + 1}"
            self.nombres[i] = nombre[:12]

    def _aplicar_dificultad_ia(self):
        """Aplica la dificultad seleccionada al jugador controlado por IA."""
        nivel = self.configuracion.obtener("dificultad_ia")
        parametros = self.config.DIFICULTADES.get(nivel, self.config.DIFICULTADES["normal"])
        for jugador in self.jugadores:
            if isinstance(jugador, JugadorIA):
                jugador.config.VELOCIDAD_IA = parametros["VELOCIDAD_IA"]
                jugador.config.VARIACION_IA = parametros["VARIACION_IA"]
                jugador.config.FACTOR_IA_HUYENDO = parametros["FACTOR_IA_HUYENDO"]

    def _volver_al_menu(self):
        """Vuelve al menú principal limpiando el estado de la partida."""
        self.estado = "menu"
        self.jugadores.clear()
        self.jugadores_views.clear()
        self.tiempo_ronda = 0
        self.tiempo_inicio_lleva = 0
        self.efectos.clear()
        self.power_ups.clear()
        self.efectos_activos.clear()
        self.toasts.clear()
        self.fade_alpha = 255
        self._ranking_registrado = False

    def crear_jugador(self, x, y, id_jugador, teclas=None, nombre=None):
        """Crea un nuevo jugador y su vista correspondiente.

        Args:
            x (int): Coordenada horizontal inicial.
            y (int): Coordenada vertical inicial.
            id_jugador (int): Identificador único del jugador.
            teclas (dict, optional): Configuración de teclas para el jugador.
            nombre (str, optional): Nombre del jugador.

        Returns:
            JugadorHumano: Jugador creado.
        """
        jugador = JugadorHumano(x, y, id_jugador, teclas, nombre)
        jugador_view = JugadorView()
        jugador_view.cargar_sprites(jugador)
        self.jugadores.append(jugador)
        self.jugadores_views.append(jugador_view)
        return jugador

    def crear_jugador_ia(self, x, y, id_jugador, nombre="IA"):
        """Crea un jugador controlado por IA y su vista correspondiente.

        Args:
            x (int): Coordenada horizontal inicial.
            y (int): Coordenada vertical inicial.
            id_jugador (int): Identificador único del jugador.
            nombre (str, optional): Nombre del jugador. Por defecto "IA".

        Returns:
            JugadorIA: Jugador creado.
        """
        jugador = JugadorIA(x, y, id_jugador, nombre)
        jugador.jugadores = self.jugadores
        jugador_view = JugadorView()
        jugador_view.cargar_sprites(jugador)
        self.jugadores.append(jugador)
        self.jugadores_views.append(jugador_view)
        return jugador

    def set_lleva_inicial(self, id_jugador):
        """Establece qué jugador tiene la pelota inicialmente.

        Args:
            id_jugador (int): ID del jugador que tendrá la pelota.
        """
        self.ronda_service.asignar_lleva_inicial(self.jugadores, id_jugador)
        self.tiempo_inicio_lleva = 0
        self.servicio_colision.limpiar_cooldown()
