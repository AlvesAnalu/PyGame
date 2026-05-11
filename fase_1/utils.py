"""Funções utilitárias para o jogo de Pygame."""

import pygame


def scale_image(image: pygame.Surface, scale_factor: float) -> pygame.Surface:
    """Escala uma imagem por um fator e retorna a nova superfície."""
    width = int(image.get_width() * scale_factor)
    height = int(image.get_height() * scale_factor)
    return pygame.transform.scale(image, (width, height))


def blit_rotate_center(surface: pygame.Surface, image: pygame.Surface, top_left: tuple[int, int], angle: float) -> pygame.Rect:
    """Rotaciona uma imagem em torno de seu centro e desenha na superfície."""
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    surface.blit(rotated_image, new_rect.topleft)
    return new_rect
