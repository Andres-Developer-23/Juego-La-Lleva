"""Módulo de interfaz de usuario que maneja todos los elementos visuales del juego."""

import pygame
import math
import random
from core.config import Config


class Interfaz:
    """Clase que gestiona toda la interfaz de usuario del juego."""

    def __init__(self):
        """Inicializa la interfaz con fuentes y partículas decorativas."""
        self.config = Config()
        self.fuente_titulo = pygame.font.SysFont(None, 72)
        self.fuente_subtitulo = pygame.font.SysFont(None, 36)
        self.fuente_boton = pygame.font.SysFont(None, 32)
        self.fuente_pequena = pygame.font.SysFont(None, 24)
        self.fuente_hud = pygame.font.SysFont(None, 28)
        self.fuente_grande = pygame.font.SysFont(None, 56)
        self.fuente_countdown = pygame.font.SysFont(None, 120)
        self.tiempo_animacion = 0
        self.particulas = []
        self._generar_particulas_menu()

    def _generar_particulas_menu(self):
        """Genera partículas decorativas para el menú."""
        for _ in range(40):
            self.particulas.append({
                'x': random.randint(0, self.config.ANCHO_PANTALLA),
                'y': random.randint(0, self.config.ALTO_PANTALLA),
                'tamaño': random.randint(2, 5),
                'velocidad_x': random.uniform(-0.5, 0.5),
                'velocidad_y': random.uniform(-0.3, 0.3),
                'alpha': random.randint(20, 60),
                'fase': random.uniform(0, math.pi * 2)
            })

    def actualizar(self, delta_tiempo):
        """Actualiza las animaciones de la interfaz.

        Args:
            delta_tiempo (float): Tiempo transcurrido desde la última actualización.
        """
        self.tiempo_animacion += delta_tiempo
        for p in self.particulas:
            p['x'] += p['velocidad_x']
            p['y'] += p['velocidad_y']
            p['fase'] += 0.02
            p['alpha'] = int(30 + 20 * math.sin(p['fase']))

            if p['x'] < 0:
                p['x'] = self.config.ANCHO_PANTALLA
            elif p['x'] > self.config.ANCHO_PANTALLA:
                p['x'] = 0
            if p['y'] < 0:
                p['y'] = self.config.ALTO_PANTALLA
            elif p['y'] > self.config.ALTO_PANTALLA:
                p['y'] = 0

    def dibujar_particulas_menu(self, pantalla):
        """Dibuja las partículas decorativas del menú.

        Args:
            pantalla: Superficie de pygame donde dibujar.
        """
        for p in self.particulas:
            surface = pygame.Surface((p['tamaño'] * 2, p['tamaño'] * 2), pygame.SRCALPHA)
            color = (80 + int(40 * math.sin(p['fase'])),
                    80 + int(40 * math.sin(p['fase'] + 1)),
                    120 + int(30 * math.sin(p['fase'] + 2)))
            pygame.draw.circle(surface, (*color, p['alpha']),
                             (p['tamaño'], p['tamaño']), p['tamaño'])
            pantalla.blit(surface, (int(p['x']) - p['tamaño'], int(p['y']) - p['tamaño']))

    def dibujar_boton(self, pantalla, texto, x, y, ancho, alto, hover=False):
        """Dibuja un botón con efecto hover.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            texto (str): Texto del botón.
            x (int): Posición horizontal.
            y (int): Posición vertical.
            ancho (int): Ancho del botón.
            alto (int): Alto del botón.
            hover (bool): True si el mouse está sobre el botón.
        """
        if hover:
            escala = 1.05
            nuevo_ancho = int(ancho * escala)
            nuevo_alto = int(alto * escala)
            nuevo_x = x - (nuevo_ancho - ancho) // 2
            nuevo_y = y - (nuevo_alto - alto) // 2
        else:
            nuevo_ancho, nuevo_alto, nuevo_x, nuevo_y = ancho, alto, x, y

        sombra_surface = pygame.Surface((nuevo_ancho, nuevo_alto), pygame.SRCALPHA)
        sombra_surface.fill((0, 0, 0, 50))
        pygame.draw.rect(sombra_surface, (0, 0, 0, 50), (0, 0, nuevo_ancho, nuevo_alto), border_radius=14)
        pantalla.blit(sombra_surface, (nuevo_x + 4, nuevo_y + 4))

        color = self.config.COLOR_BOTON_HOVER if hover else self.config.COLOR_BOTON
        pygame.draw.rect(pantalla, color, (nuevo_x, nuevo_y, nuevo_ancho, nuevo_alto), border_radius=12)

        gradient_surface = pygame.Surface((nuevo_ancho, nuevo_alto // 2), pygame.SRCALPHA)
        gradient_surface.fill((255, 255, 255, 20))
        pygame.draw.rect(gradient_surface, (255, 255, 255, 20),
                       (0, 0, nuevo_ancho, nuevo_alto // 2), border_radius=12)
        pantalla.blit(gradient_surface, (nuevo_x, nuevo_y))

        pygame.draw.rect(pantalla, self.config.COLOR_BORDE, (nuevo_x, nuevo_y, nuevo_ancho, nuevo_alto), 2, border_radius=12)

        if hover:
            brillo = pygame.Surface((nuevo_ancho - 4, nuevo_alto - 4), pygame.SRCALPHA)
            brillo.fill((255, 255, 255, 25))
            pygame.draw.rect(brillo, (255, 255, 255, 25), (0, 0, nuevo_ancho - 4, nuevo_alto - 4), border_radius=10)
            pantalla.blit(brillo, (nuevo_x + 2, nuevo_y + 2))

        texto_render = self.fuente_boton.render(texto, True, (255, 255, 255))
        pantalla.blit(texto_render, (nuevo_x + nuevo_ancho // 2 - texto_render.get_width() // 2,
                                     nuevo_y + nuevo_alto // 2 - texto_render.get_height() // 2))

    def dibujar_panel(self, pantalla, x, y, ancho, alto, alpha=180):
        """Dibuja un panel semitransparente.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            x (int): Posición horizontal.
            y (int): Posición vertical.
            ancho (int): Ancho del panel.
            alto (int): Alto del panel.
            alpha (int): Nivel de transparencia (0-255).
        """
        sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 30))
        pygame.draw.rect(sombra, (0, 0, 0, 30), (0, 0, ancho, alto), border_radius=10)
        pantalla.blit(sombra, (x + 5, y + 5))

        surface = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        surface.fill((30, 30, 50, alpha))
        pygame.draw.rect(surface, self.config.COLOR_BORDE, (0, 0, ancho, alto), 2, border_radius=10)
        pantalla.blit(surface, (x, y))

    def _dentro_boton(self, pos, x, y, ancho, alto):
        """Verifica si una posición está dentro de un botón.

        Args:
            pos (tuple): Posición (x, y) a verificar.
            x (int): Posición horizontal del botón.
            y (int): Posición vertical del botón.
            ancho (int): Ancho del botón.
            alto (int): Alto del botón.

        Returns:
            bool: True si la posición está dentro del botón.
        """
        return x <= pos[0] <= x + ancho and y <= pos[1] <= y + alto

    def dibujar_hud(self, pantalla, tiempo, puntajes, jugadores):
        """Dibuja el heads-up display con información del juego.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            tiempo (float): Tiempo transcurrido de la ronda.
            puntajes (dict): Diccionario con tiempos de cada jugador.
            jugadores (list): Lista de jugadores activos.
        """
        self.dibujar_panel(pantalla, 0, 0, self.config.ANCHO_PANTALLA, 70, 220)

        tiempo_restante = max(0, self.config.DURACION_RONDA - tiempo)
        porcentaje_tiempo = tiempo_restante / self.config.DURACION_RONDA

        barra_x = 20
        barra_y = 12
        barra_ancho = 150
        barra_alto = 16
        pygame.draw.rect(pantalla, (40, 40, 60), (barra_x, barra_y, barra_ancho, barra_alto), border_radius=8)
        if porcentaje_tiempo > 0.3:
            color_barra = self.config.COLOR_LIBRE
        elif porcentaje_tiempo > 0.1:
            color_barra = self.config.COLOR_DORADO
        else:
            color_barra = self.config.COLOR_LLEVA
        ancho_barra = int(barra_ancho * porcentaje_tiempo)
        pygame.draw.rect(pantalla, color_barra, (barra_x, barra_y, ancho_barra, barra_alto), border_radius=8)
        pygame.draw.rect(pantalla, (255, 255, 255, 60), (barra_x, barra_y, ancho_barra, barra_alto // 2), border_radius=6)

        texto_tiempo = self.fuente_hud.render(f"{int(tiempo_restante)}s", True, (255, 255, 255))
        pantalla.blit(texto_tiempo, (barra_x + barra_ancho + 10, barra_y - 2))

        x_jugador = 280
        for jugador in jugadores:
            if jugador.es_lleva:
                color = self.config.COLOR_LLEVA
                indicador = "LA LLEVA"
                pulso = abs(math.sin(self.tiempo_animacion * 6)) * 0.3 + 0.7
                color_texto = (int(255 * pulso), int(100 * pulso), int(100 * pulso))
            else:
                color = self.config.COLOR_JUGADOR_1 if jugador.id == 0 else self.config.COLOR_JUGADOR_2
                indicador = "Libre"
                color_texto = (255, 255, 255)

            pygame.draw.rect(pantalla, color, (x_jugador, 20, 18, 18), border_radius=4)
            pygame.draw.rect(pantalla, (255, 255, 255), (x_jugador, 20, 18, 18), 1, border_radius=4)

            texto_j = self.fuente_hud.render(f"{jugador.nombre}: {indicador}", True, color_texto)
            pantalla.blit(texto_j, (x_jugador + 24, 18))

            tiempo_j = puntajes.get(jugador.id, 0)
            texto_t = self.fuente_pequena.render(f"({int(tiempo_j)}s)", True, self.config.COLOR_PLATA)
            pantalla.blit(texto_t, (x_jugador + 24 + texto_j.get_width() + 5, 22))

            x_jugador += 240

        texto_salir = self.fuente_pequena.render("ESC: Menu", True, self.config.COLOR_PLATA)
        pantalla.blit(texto_salir, (self.config.ANCHO_PANTALLA - 90, 28))

    def dibujar_menu_principal(self, pantalla, mouse_pos=None):
        """Dibuja el menú principal del juego.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            mouse_pos (tuple, optional): Posición del mouse para efectos hover.
        """
        try:
            fondo_menu = pygame.image.load(self.config.FONDO_MENU).convert()
            fondo_menu = pygame.transform.scale(fondo_menu, (self.config.ANCHO_PANTALLA, self.config.ALTO_PANTALLA))
            pantalla.blit(fondo_menu, (0, 0))
            overlay = pygame.Surface((self.config.ANCHO_PANTALLA, self.config.ALTO_PANTALLA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            pantalla.blit(overlay, (0, 0))
        except:
            pantalla.fill(self.config.COLOR_FONDO)

        for i in range(0, self.config.ALTO_PANTALLA, 3):
            offset = math.sin(i * 0.015 + self.tiempo_animacion * 1.5) * 8
            alpha = int(25 + 15 * math.sin(i * 0.02 + self.tiempo_animacion * 2))
            color_linea = (35 + alpha // 8, 35 + alpha // 8, 55 + alpha // 4)
            pygame.draw.line(pantalla, color_linea, (int(offset), i), (self.config.ANCHO_PANTALLA + int(offset), i))

        self.dibujar_particulas_menu(pantalla)

        titulo_y = 100 + math.sin(self.tiempo_animacion * 1.5) * 8

        for desplazamiento in range(6, 0, -1):
            alpha = int(40 - desplazamiento * 6)
            sombra_surface = self.fuente_titulo.render("LA LLEVA", True, (0, 0, 0))
            pantalla.blit(sombra_surface, (self.config.ANCHO_PANTALLA // 2 - sombra_surface.get_width() // 2 + desplazamiento,
                                          titulo_y + desplazamiento))

        texto_titulo = self.fuente_titulo.render("LA LLEVA", True, self.config.COLOR_DORADO)
        brillo_titulo = pygame.Surface((texto_titulo.get_width(), texto_titulo.get_height() // 2), pygame.SRCALPHA)
        brillo_titulo.fill((255, 255, 255, 30))
        pantalla.blit(texto_titulo, (self.config.ANCHO_PANTALLA // 2 - texto_titulo.get_width() // 2, titulo_y))
        pantalla.blit(brillo_titulo, (self.config.ANCHO_PANTALLA // 2 - texto_titulo.get_width() // 2, titulo_y))

        texto_sub = self.fuente_subtitulo.render("Juego Tradicional Colombiano", True, self.config.COLOR_PLATA)
        pantalla.blit(texto_sub, (self.config.ANCHO_PANTALLA // 2 - texto_sub.get_width() // 2, 195))

        self.dibujar_panel(pantalla, self.config.ANCHO_PANTALLA // 2 - 190, 260, 380, 325, 160)

        botones = [
            ("Jugar", 280),
            ("Como Jugar", 355),
            ("Ranking", 430),
            ("Salir", 505)
        ]

        for texto_boton, y in botones:
            hover = mouse_pos and self._dentro_boton(mouse_pos, self.config.ANCHO_PANTALLA // 2 - 140, y, 280, 50)
            self.dibujar_boton(pantalla, texto_boton, self.config.ANCHO_PANTALLA // 2 - 140, y, 280, 50, hover)

        self.dibujar_panel(pantalla, self.config.ANCHO_PANTALLA // 2 - 170, 615, 340, 70, 130)
        controles = "J1: WASD   |   J2: Flechas"
        texto_ctrl = self.fuente_pequena.render(controles, True, self.config.COLOR_PLATA)
        pantalla.blit(texto_ctrl, (self.config.ANCHO_PANTALLA // 2 - texto_ctrl.get_width() // 2, 640))

    def dibujar_pantalla_nombres(self, pantalla, nombres, nombre_activo, mouse_pos=None):
        """Dibuja la pantalla de ingreso de nombres.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            nombres (list): Lista de nombres de jugadores.
            nombre_activo (int): Índice del nombre que se está editando.
            mouse_pos (tuple, optional): Posición del mouse para efectos hover.
        """
        pantalla.fill(self.config.COLOR_FONDO)
        self.dibujar_particulas_menu(pantalla)

        titulo = self.fuente_grande.render("Nombres de Jugadores", True, self.config.COLOR_DORADO)
        pantalla.blit(titulo, (self.config.ANCHO_PANTALLA // 2 - titulo.get_width() // 2, 80))

        self.dibujar_panel(pantalla, self.config.ANCHO_PANTALLA // 2 - 220, 160, 440, 340, 180)

        for i in range(2):
            y_campo = 200 + i * 120
            color_label = self.config.COLOR_JUGADOR_1 if i == 0 else self.config.COLOR_JUGADOR_2
            label = self.fuente_boton.render(f"Jugador {i + 1}:", True, color_label)
            pantalla.blit(label, (self.config.ANCHO_PANTALLA // 2 - 180, y_campo))

            campo_x = self.config.ANCHO_PANTALLA // 2 - 180
            campo_y = y_campo + 35
            campo_ancho = 360
            campo_alto = 40

            if nombre_activo == i:
                pygame.draw.rect(pantalla, self.config.COLOR_BORDE,
                               (campo_x - 2, campo_y - 2, campo_ancho + 4, campo_alto + 4),
                               border_radius=8)
            pygame.draw.rect(pantalla, (40, 40, 60), (campo_x, campo_y, campo_ancho, campo_alto),
                           border_radius=6)

            texto_render = self.fuente_boton.render(nombres[i], True, (255, 255, 255))
            pantalla.blit(texto_render, (campo_x + 10, campo_y + campo_alto // 2 - texto_render.get_height() // 2))

            if nombre_activo == i and int(self.tiempo_animacion * 2) % 2 == 0:
                cursor_x = campo_x + 10 + texto_render.get_width() + 2
                pygame.draw.line(pantalla, (255, 255, 255), (cursor_x, campo_y + 8),
                               (cursor_x, campo_y + campo_alto - 8), 2)

        texto_hint = self.fuente_pequena.render("TAB: cambiar campo  |  ENTER: jugar", True, self.config.COLOR_PLATA)
        pantalla.blit(texto_hint, (self.config.ANCHO_PANTALLA // 2 - texto_hint.get_width() // 2, 470))

        hover = mouse_pos and self._dentro_boton(mouse_pos, self.config.ANCHO_PANTALLA // 2 - 140, 520, 280, 50)
        self.dibujar_boton(pantalla, "Jugar", self.config.ANCHO_PANTALLA // 2 - 140, 520, 280, 50, hover)

    def obtener_accion_menu(self, mouse_pos, click):
        """Obtiene la acción del menú según la posición del mouse y el click.

        Args:
            mouse_pos (tuple): Posición del mouse.
            click (bool): True si se hizo click.

        Returns:
            str: Acción seleccionada ("jugar", "ayuda", "salir") o None.
        """
        if not click:
            return None
        botones = [
            (self.config.ANCHO_PANTALLA // 2 - 140, 280, 280, 50, "jugar"),
            (self.config.ANCHO_PANTALLA // 2 - 140, 355, 280, 50, "ayuda"),
            (self.config.ANCHO_PANTALLA // 2 - 140, 430, 280, 50, "ranking"),
            (self.config.ANCHO_PANTALLA // 2 - 140, 505, 280, 50, "salir")
        ]
        for x, y, ancho, alto, accion in botones:
            if self._dentro_boton(mouse_pos, x, y, ancho, alto):
                return accion
        return None

    def dibujar_ayuda(self, pantalla, mouse_pos=None):
        """Dibuja la pantalla de ayuda con instrucciones del juego.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            mouse_pos (tuple, optional): Posición del mouse para efectos hover.
        """
        pantalla.fill(self.config.COLOR_FONDO)
        self.dibujar_particulas_menu(pantalla)

        titulo = self.fuente_grande.render("Como Jugar", True, self.config.COLOR_DORADO)
        pantalla.blit(titulo, (self.config.ANCHO_PANTALLA // 2 - titulo.get_width() // 2, 40))

        self.dibujar_panel(pantalla, 60, 100, 904, 540, 190)

        secciones = [
            ("Objetivo:", self.config.COLOR_DORADO, 130),
            ("Ser el ultimo en ser tocado cuando expira el tiempo.", (255, 255, 255), 165),
            ("", None, 195),
            ("Reglas:", self.config.COLOR_DORADO, 210),
            ("- Un jugador es 'La Lleva' (rojo) y debe tocar a otro.", (255, 255, 255), 245),
            ("- Al tocar, el tocado pasa a ser 'La Lleva'.", (255, 255, 255), 277),
            ("- Gana quien menos tiempo sea 'La Lleva'.", (255, 255, 255), 309),
            ("", None, 340),
            ("Controles:", self.config.COLOR_DORADO, 355),
            ("Jugador 1: W (arriba), A (izq), S (abajo), D (der)", self.config.COLOR_JUGADOR_1, 390),
            ("Jugador 2: Flechas del teclado", self.config.COLOR_JUGADOR_2, 422),
            ("", None, 453),
            ("Consejos:", self.config.COLOR_DORADO, 465),
            ("- El que es 'La Lleva' se mueve un poco mas rapido.", (255, 255, 255), 500),
        ]

        for texto, color, y in secciones:
            if texto and color:
                render = self.fuente_boton.render(texto, True, color)
                pantalla.blit(render, (100, y))

        hover = mouse_pos and self._dentro_boton(mouse_pos, self.config.ANCHO_PANTALLA // 2 - 100, 670, 200, 50)
        self.dibujar_boton(pantalla, "Volver", self.config.ANCHO_PANTALLA // 2 - 100, 670, 200, 50, hover)

    def dibujar_countdown(self, pantalla, numero):
        """Dibuja el countdown antes de iniciar la partida.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            numero (int): Número del countdown a mostrar.
        """
        pantalla.fill(self.config.COLOR_FONDO)
        self.dibujar_particulas_menu(pantalla)

        escala = 1.0 + abs(math.sin(self.tiempo_animacion * 4)) * 0.1
        texto = self.fuente_countdown.render(str(numero), True, self.config.COLOR_DORADO)
        texto_escalado = pygame.transform.rotozoom(texto, 0, escala)

        sombra = self.fuente_countdown.render(str(numero), True, (0, 0, 0))
        sombra_escalada = pygame.transform.rotozoom(sombra, 0, escala)
        pantalla.blit(sombra_escalada, (self.config.ANCHO_PANTALLA // 2 - sombra_escalada.get_width() // 2 + 4,
                                        self.config.ALTO_PANTALLA // 2 - sombra_escalada.get_height() // 2 + 4))
        pantalla.blit(texto_escalado, (self.config.ANCHO_PANTALLA // 2 - texto_escalado.get_width() // 2,
                                       self.config.ALTO_PANTALLA // 2 - texto_escalado.get_height() // 2))

        texto_preparado = self.fuente_subtitulo.render("Preparate...", True, self.config.COLOR_PLATA)
        pantalla.blit(texto_preparado, (self.config.ANCHO_PANTALLA // 2 - texto_preparado.get_width() // 2,
                                        self.config.ALTO_PANTALLA // 2 + 80))

    def dibujar_fin_ronda(self, pantalla, ganador, puntajes, mouse_pos=None, jugadores=None):
        """Dibuja la pantalla de fin de ronda con resultados.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            ganador (int): ID del jugador ganador.
            puntajes (dict): Diccionario con tiempos de cada jugador.
            mouse_pos (tuple, optional): Posición del mouse para efectos hover.
            jugadores (list, optional): Lista de jugadores.
        """
        overlay = pygame.Surface((self.config.ANCHO_PANTALLA, self.config.ALTO_PANTALLA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        pantalla.blit(overlay, (0, 0))

        self.dibujar_panel(pantalla, self.config.ANCHO_PANTALLA // 2 - 260, 130, 520, 450, 230)

        texto_titulo = self.fuente_grande.render("Fin de Ronda", True, self.config.COLOR_DORADO)
        pantalla.blit(texto_titulo, (self.config.ANCHO_PANTALLA // 2 - texto_titulo.get_width() // 2, 160))

        if ganador is not None and jugadores:
            ganador_nombre = next((j.nombre for j in jugadores if j.id == ganador), f"Jugador {ganador + 1}")
            texto_ganador = self.fuente_grande.render(f"{ganador_nombre} Gana!", True, (255, 255, 255))
        else:
            texto_ganador = self.fuente_grande.render("Empate!", True, (255, 255, 255))
        pantalla.blit(texto_ganador, (self.config.ANCHO_PANTALLA // 2 - texto_ganador.get_width() // 2, 250))

        self.dibujar_panel(pantalla, self.config.ANCHO_PANTALLA // 2 - 190, 320, 380, 130, 160)
        texto_titulo_tabla = self.fuente_boton.render("Tabla de Tiempos", True, self.config.COLOR_PLATA)
        pantalla.blit(texto_titulo_tabla, (self.config.ANCHO_PANTALLA // 2 - texto_titulo_tabla.get_width() // 2, 330))

        y = 370
        for id_j, tiempo in sorted(puntajes.items(), key=lambda x: x[1]):
            nombre = next((j.nombre for j in jugadores if j.id == id_j), f"J{id_j + 1}") if jugadores else f"J{id_j + 1}"
            color = self.config.COLOR_DORADO if id_j == ganador else (255, 255, 255)
            texto = self.fuente_boton.render(f"{nombre}: {int(tiempo)}s", True, color)
            pantalla.blit(texto, (self.config.ANCHO_PANTALLA // 2 - texto.get_width() // 2, y))
            y += 35

        hover_revancha = mouse_pos and self._dentro_boton(mouse_pos, self.config.ANCHO_PANTALLA // 2 - 210, 510, 190, 50)
        hover_menu = mouse_pos and self._dentro_boton(mouse_pos, self.config.ANCHO_PANTALLA // 2 + 20, 510, 190, 50)

        self.dibujar_boton(pantalla, "Revancha", self.config.ANCHO_PANTALLA // 2 - 210, 510, 190, 50, hover_revancha)
        self.dibujar_boton(pantalla, "Menu", self.config.ANCHO_PANTALLA // 2 + 20, 510, 190, 50, hover_menu)

    def obtener_accion_fin_ronda(self, mouse_pos, click):
        """Obtiene la acción de fin de ronda según la posición del mouse y el click.

        Args:
            mouse_pos (tuple): Posición del mouse.
            click (bool): True si se hizo click.

        Returns:
            str: Acción seleccionada ("revancha", "menu") o None.
        """
        if not click:
            return None
        if self._dentro_boton(mouse_pos, self.config.ANCHO_PANTALLA // 2 - 210, 510, 190, 50):
            return "revancha"
        if self._dentro_boton(mouse_pos, self.config.ANCHO_PANTALLA // 2 + 20, 510, 190, 50):
            return "menu"
        return None

    def dibujar_ranking(self, pantalla, entradas, mouse_pos=None):
        """Dibuja la pantalla de ranking con las mejores partidas.

        Args:
            pantalla: Superficie de pygame donde dibujar.
            entradas (list): Lista de entradas del ranking ordenadas por tiempo.
            mouse_pos (tuple, optional): Posición del mouse para efectos hover.
        """
        pantalla.fill(self.config.COLOR_FONDO)
        self.dibujar_particulas_menu(pantalla)

        titulo = self.fuente_grande.render("Ranking", True, self.config.COLOR_DORADO)
        pantalla.blit(titulo, (self.config.ANCHO_PANTALLA // 2 - titulo.get_width() // 2, 40))

        subtitulo = self.fuente_subtitulo.render("Mejores Tiempos", True, self.config.COLOR_PLATA)
        pantalla.blit(subtitulo, (self.config.ANCHO_PANTALLA // 2 - subtitulo.get_width() // 2, 100))

        panel_y = 150
        panel_alto = 400
        self.dibujar_panel(pantalla, self.config.ANCHO_PANTALLA // 2 - 280, panel_y, 560, panel_alto, 180)

        if not entradas:
            texto_vacio = self.fuente_boton.render("No hay partidas registradas", True, self.config.COLOR_PLATA)
            pantalla.blit(texto_vacio, (self.config.ANCHO_PANTALLA // 2 - texto_vacio.get_width() // 2, panel_y + 180))
        else:
            encabezado_y = panel_y + 15
            col_pos_x = self.config.ANCHO_PANTALLA // 2 - 250
            col_nom_x = self.config.ANCHO_PANTALLA // 2 - 180
            col_tiempo_x = self.config.ANCHO_PANTALLA // 2 + 120

            texto_pos_h = self.fuente_pequena.render("#", True, self.config.COLOR_DORADO)
            texto_nom_h = self.fuente_pequena.render("Jugador", True, self.config.COLOR_DORADO)
            texto_tiem_h = self.fuente_pequena.render("Tiempo", True, self.config.COLOR_DORADO)
            pantalla.blit(texto_pos_h, (col_pos_x, encabezado_y))
            pantalla.blit(texto_nom_h, (col_nom_x, encabezado_y))
            pantalla.blit(texto_tiem_h, (col_tiempo_x, encabezado_y))

            pygame.draw.line(pantalla, self.config.COLOR_BORDE,
                           (col_pos_x, encabezado_y + 22),
                           (col_tiempo_x + 100, encabezado_y + 22), 1)

            for i, entrada in enumerate(entradas):
                y = encabezado_y + 35 + i * 34
                if y > panel_y + panel_alto - 40:
                    break

                if i == 0:
                    color_pos = self.config.COLOR_DORADO
                elif i == 1:
                    color_pos = (192, 192, 192)
                elif i == 2:
                    color_pos = (205, 127, 50)
                else:
                    color_pos = (255, 255, 255)

                texto_pos = self.fuente_boton.render(f"{i + 1}", True, color_pos)
                texto_nom = self.fuente_boton.render(entrada["ganador"], True, (255, 255, 255))
                texto_tiem = self.fuente_boton.render(f'{entrada["tiempo"]:.1f}s', True, color_pos)

                pantalla.blit(texto_pos, (col_pos_x + 10, y))
                pantalla.blit(texto_nom, (col_nom_x, y))
                pantalla.blit(texto_tiem, (col_tiempo_x + 20, y))

        hover_volver = mouse_pos and self._dentro_boton(mouse_pos, self.config.ANCHO_PANTALLA // 2 - 100, 580, 200, 50)
        self.dibujar_boton(pantalla, "Volver", self.config.ANCHO_PANTALLA // 2 - 100, 580, 200, 50, hover_volver)

    def obtener_accion_ranking(self, mouse_pos, click):
        """Obtiene la acción de la pantalla de ranking.

        Args:
            mouse_pos (tuple): Posición del mouse.
            click (bool): True si se hizo click.

        Returns:
            str: Acción seleccionada ("volver") o None.
        """
        if not click:
            return None
        if self._dentro_boton(mouse_pos, self.config.ANCHO_PANTALLA // 2 - 100, 580, 200, 50):
            return "volver"
        return None
