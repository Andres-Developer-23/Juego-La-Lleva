import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    ANCHO_PANTALLA = 1908
    ALTO_PANTALLA = 1080
    FPS = 60
    TAMAÑO_JUGADOR = 95
    VELOCIDAD_JUGADOR = 5
    DURACION_RONDA = 60
    MAX_JUGADORES = 2

    # Colores principales
    COLOR_FONDO = (25, 25, 45)
    COLOR_JUGADOR_1 = (0, 180, 255)
    COLOR_JUGADOR_2 = (255, 100, 50)
    COLOR_LLEVA = (255, 50, 50)
    COLOR_LIBRE = (0, 220, 100)

    # Acentos
    COLOR_DORADO = (255, 215, 0)
    COLOR_PLATA = (192, 192, 192)
    COLOR_OBSTACULO = (60, 60, 80)
    COLOR_ZONA_LENTO = (40, 120, 200)

    # Obstaculos
    CANTIDAD_OBSTACULOS_MIN = 3
    CANTIDAD_OBSTACULOS_MAX = 8
    TAMAÑO_CAJA = 100
    TAMAÑO_ZONA = 80
    FACTOR_RALENTIZACION = 0.4
    FUERZA_REBOTE = 5

    # UI
    COLOR_BOTON = (50, 50, 80)
    COLOR_BOTON_HOVER = (70, 70, 110)
    COLOR_BORDE = (100, 100, 140)
    COLOR_OVERLAY = (0, 0, 0, 180)

    # Assets
    ASSETS_DIR = os.path.join(_BASE_DIR, "assets")
    SPRITE_DIR = os.path.join(ASSETS_DIR, "sprites")
    FONDOS_DIR = os.path.join(ASSETS_DIR, "fondos")
    UI_DIR = os.path.join(ASSETS_DIR, "ui")

    SPRITE_J1 = os.path.join(SPRITE_DIR, "jugador1.png")
    SPRITE_J2 = os.path.join(SPRITE_DIR, "jugador2.png")
    SPRITE_LLEVA = os.path.join(SPRITE_DIR, "lleva.png")
    FONDO = os.path.join(FONDOS_DIR, "campo.png")
    FONDO_MENU = os.path.join(FONDOS_DIR, "menu_bg.jpg")

    # UI Sprites (9-slice panels)
    UI_PANEL_DARK = os.path.join(UI_DIR, "panel_dark.png")
    UI_PANEL_DARK_BORDER = os.path.join(UI_DIR, "panel_dark_border.png")
    UI_PANEL_DARK_CENTER = os.path.join(UI_DIR, "panel_dark_center.png")
    UI_BORDER_DARK = os.path.join(UI_DIR, "border_dark.png")
    UI_PANEL_BASE = os.path.join(UI_DIR, "panel_base.png")
    UI_BORDER = os.path.join(UI_DIR, "border.png")
    UI_PANEL_TRANSPARENT_BORDER = os.path.join(UI_DIR, "panel_transparent_border.png")
    UI_PANEL_TRANSPARENT_CENTER = os.path.join(UI_DIR, "panel_transparent_center.png")
