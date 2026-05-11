"""
Jogo de autorama para dois jogadores feito em Pygame.

O jogo simula uma pista vista de cima, com dois carros controlados pelo teclado
e colisão precisa com a borda da pista usando máscaras.
"""

import os
import pygame
import math
from utils import scale_image, blit_rotate_center

pygame.init()

FILE_PATH = os.path.dirname(__file__)
IMG_PATH = os.path.join(FILE_PATH, "imgs")

GRASS = scale_image(pygame.image.load(os.path.join(IMG_PATH, "grass.jpg")), 2.5)
TRACK = scale_image(pygame.image.load(os.path.join(IMG_PATH, "track.png")), 1)

# Imagem da borda da pista, usada para detectar colisões.
# Ela deve ter o mesmo fator de escala da pista.
TRACK_BORDER = scale_image(pygame.image.load(os.path.join(IMG_PATH, "track-border.png")), 1)

RED_CAR = scale_image(pygame.image.load(os.path.join(IMG_PATH, "red-car.png")), 0.55)
GREEN_CAR = scale_image(pygame.image.load(os.path.join(IMG_PATH, "green-car.png")), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autorama 2 Jogadores")

FPS = 60