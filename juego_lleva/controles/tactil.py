"""Control táctil para jugar desde pantallas táctiles (móviles y tablets)."""

import pygame


class ControladorTactil:
    """Traduce los toques de pantalla en teclas virtuales y gestiona la pausa."""

    def __init__(self, ancho, alto, visible=False):
        """Inicializa las zonas táctiles del jugador 1 y 2.

        Args:
            ancho (int): Ancho lógico de la pantalla.
            alto (int): Alto lógico de la pantalla.
            visible (bool): Mostrar las cruces desde el inicio (web).
        """
        self.ancho = ancho
        self.alto = alto
        self.activo = visible
        self.dedos = {}
        self.pausa_pedida = False
        self._fuente_cache = None
        self.zona_pausa = pygame.Rect(ancho - 170, 24, 140, 60)
        self.zonas_j1 = self._crear_pad(190, alto - 190, "J1")
        self.zonas_j2 = self._crear_pad(ancho - 190, alto - 190, "J2")

    def _crear_pad(self, cx, cy, etiqueta):
        """Crea la cruz de control de un jugador.

        Args:
            cx (int): Centro horizontal de la cruz.
            cy (int): Centro vertical de la cruz.
            etiqueta (str): Nombre del jugador.

        Returns:
            dict: Rectángulos de cada dirección y su etiqueta.
        """
        return {
            "arriba": pygame.Rect(cx - 60, cy - 150, 120, 90),
            "abajo": pygame.Rect(cx - 60, cy + 60, 120, 90),
            "izquierda": pygame.Rect(cx - 150, cy - 45, 90, 90),
            "derecha": pygame.Rect(cx + 60, cy - 45, 90, 90),
            "etiqueta": etiqueta,
            "centro": (cx, cy),
        }

    def procesar_evento(self, evento):
        """Actualiza la posición de los dedos tras un evento táctil.

        Args:
            evento: Evento de pygame (FINGERDOWN, FINGERMOTION o FINGERUP).
        """
        if evento.type == pygame.FINGERDOWN:
            self.activo = True
            pos = (evento.x * self.ancho, evento.y * self.alto)
            self.dedos[evento.finger_id] = pos
            if self.zona_pausa.collidepoint(pos):
                self.pausa_pedida = True
        elif evento.type == pygame.FINGERMOTION:
            self.dedos[evento.finger_id] = (evento.x * self.ancho, evento.y * self.alto)
        elif evento.type == pygame.FINGERUP:
            self.dedos.pop(evento.finger_id, None)

    def teclas_activas(self):
        """Devuelve las teclas virtuales presionadas por los toques.

        Returns:
            list: Códigos de tecla (pygame.K_*) activos por el tacto.
        """
        direcciones = ["arriba", "abajo", "izquierda", "derecha"]
        pads = [
            (self.zonas_j1, [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]),
            (self.zonas_j2, [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]),
        ]
        activas = []
        for pos in self.dedos.values():
            for pad, codigos in pads:
                for nombre in direcciones:
                    if pad[nombre].collidepoint(pos):
                        activas.append(codigos[direcciones.index(nombre)])
        return activas

    def consumir_pausa(self):
        """Consume el pulso de pausa si el jugador tocó el botón.

        Returns:
            bool: True si hubo un toque pendiente sobre pausa.
        """
        valor = self.pausa_pedida
        self.pausa_pedida = False
        return valor

    def dibujar(self, pantalla):
        """Dibuja las zonas táctiles visibles sobre la pantalla.

        Args:
            pantalla: Superficie de pygame donde dibujar.
        """
        if not self.activo:
            return
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        for pad in (self.zonas_j1, self.zonas_j2):
            for nombre in ("arriba", "abajo", "izquierda", "derecha"):
                rect = pad[nombre]
                pygame.draw.rect(overlay, (45, 45, 75, 150), rect, border_radius=14)
                self._dibujar_flecha(overlay, rect, nombre)
            etiqueta = self._fuente().render(pad["etiqueta"], True, (220, 220, 220, 255))
            overlay.blit(etiqueta, etiqueta.get_rect(center=(pad["centro"][0], pad["centro"][1] + 130)))
        pygame.draw.rect(overlay, (70, 70, 110, 190), self.zona_pausa, border_radius=12)
        texto = self._fuente().render("PAUSA", True, (255, 255, 255, 255))
        overlay.blit(texto, texto.get_rect(center=self.zona_pausa.center))
        pantalla.blit(overlay, (0, 0))

    def _dibujar_flecha(self, overlay, rect, direccion):
        """Dibuja la flecha de una dirección dentro de su zona.

        Args:
            overlay: Superficie transparente del control.
            rect: Rect de la zona.
            direccion (str): Nombre de la dirección.
        """
        cx, cy = rect.center
        lado = 16
        if direccion == "arriba":
            puntos = [(cx, cy - lado), (cx - lado, cy + lado), (cx + lado, cy + lado)]
        elif direccion == "abajo":
            puntos = [(cx, cy + lado), (cx - lado, cy - lado), (cx + lado, cy - lado)]
        elif direccion == "izquierda":
            puntos = [(cx - lado, cy), (cx + lado, cy - lado), (cx + lado, cy + lado)]
        else:
            puntos = [(cx + lado, cy), (cx - lado, cy - lado), (cx - lado, cy + lado)]
        pygame.draw.polygon(overlay, (220, 220, 220, 220), puntos)

    def _fuente(self):
        """Devuelve una fuente pequeña (en caché) para las etiquetas."""
        if self._fuente_cache is None:
            self._fuente_cache = pygame.font.SysFont(None, 28)
        return self._fuente_cache