import pygame
import os

pygame.init()

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
FONDOS_DIR = os.path.join(ASSETS_DIR, "fondos")

os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(FONDOS_DIR, exist_ok=True)

def crear_sprite_jugador(ruta, color, color_oscuro, tamano=32):
    surface = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
    pygame.draw.rect(surface, color_oscuro, (2, 2, tamano - 2, tamano - 2), border_radius=6)
    pygame.draw.rect(surface, color, (0, 0, tamano, tamano), border_radius=5)
    brillo = pygame.Surface((tamano - 6, tamano // 2 - 2), pygame.SRCALPHA)
    brillo.fill((255, 255, 255, 50))
    pygame.draw.rect(brillo, (255, 255, 255, 50), (0, 0, tamano - 6, tamano // 2 - 2), border_radius=4)
    surface.blit(brillo, (3, 3))
    pygame.image.save(surface, ruta)

def crear_sprite_lleva(ruta, tamano=32):
    surface = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
    pygame.draw.rect(surface, (180, 30, 30), (2, 2, tamano - 2, tamano - 2), border_radius=6)
    pygame.draw.rect(surface, (255, 50, 50), (0, 0, tamano, tamano), border_radius=5)
    pygame.draw.rect(surface, (255, 255, 255), (3, 3, tamano - 6, tamano - 6), border_radius=4)
    pygame.image.save(surface, ruta)

def crear_fondo(ruta, ancho=1024, alto=768):
    surface = pygame.Surface((ancho, alto))
    for y in range(alto):
        r = 25 + int(15 * (y / alto))
        g = 25 + int(10 * (y / alto))
        b = 45 + int(20 * (y / alto))
        pygame.draw.line(surface, (r, g, b), (0, y), (ancho, y))
    for i in range(50):
        x = (i * 73) % ancho
        y = (i * 47) % alto
        alpha = 20 + (i % 30)
        punto = pygame.Surface((2, 2), pygame.SRCALPHA)
        punto.fill((100, 100, 140, alpha))
        surface.blit(punto, (x, y))
    pygame.image.save(surface, ruta)

crear_sprite_jugador(
    os.path.join(SPRITES_DIR, "jugador1.png"),
    (0, 180, 255), (0, 90, 128)
)
print("Creado: sprites/jugador1.png")

crear_sprite_jugador(
    os.path.join(SPRITES_DIR, "jugador2.png"),
    (255, 100, 50), (128, 50, 25)
)
print("Creado: sprites/jugador2.png")

crear_sprite_lleva(
    os.path.join(SPRITES_DIR, "lleva.png")
)
print("Creado: sprites/lleva.png")

crear_fondo(
    os.path.join(FONDOS_DIR, "campo.png")
)
print("Creado: fondos/campo.png")

print("\nPlaceholders creados! Ejecuta el juego normalmente.")
