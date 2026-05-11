"""
Jogo de autorama para dois jogadores feito em Pygame.

O jogo simula uma pista vista de cima, com dois carros controlados pelo teclado
e colisão precisa com a borda da pista usando máscaras.
"""

import os
import pygame
from utils import scale_image, blit_rotate_center

pygame.init()

FILE_PATH = os.path.dirname(__file__)
IMG_PATH = os.path.join(FILE_PATH, "img")

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

class AbstractCar:
    """
 self.vele baseself.img.get_heightm carro no autorama.

    Centraliza a lógica de movimento, rotação, aceleração e colisão,
    permitindo que diferentes carros compartilhem o mesmo comportamento.
    """
    def _init_(self, max_vel, rotation_vel):
        """Inicializa os atributos principais do carro."""
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def rotate(self, left=False, right=False):
        """
        Rotaciona o carro para a esquerda ou para a direita.

        No contexto do autorama, isso representa a mudança de direção
        enquanto o carrinho percorre a pista.
        """
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        """Desenha o carro na tela já considerando sua rotação atual."""
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)









class PlayerCar(AbstractCar):
    """
    Carro do jogador 1.

    Usa a imagem vermelha e começa em uma posição específica da pista.
    """
    IMG = RED_CAR
    START_POS = (430, 75)   # carro 1


class GreenCar(AbstractCar):
    """
    Carro do jogador 2.

    Usa a imagem verde e começa em uma posição específica da pista.
    """
    IMG = GREEN_CAR
    START_POS = (520, 75)   # carro 2
