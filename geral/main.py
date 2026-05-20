import sys
import os
import importlib.util
import pygame

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

FASE1_DIR = os.path.join(ROOT_DIR, "fase_1")
FASE1_PATH = os.path.join(FASE1_DIR, "mainfase1.py")

spec = importlib.util.spec_from_file_location("mainfase1", FASE1_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load module from {FASE1_PATH}")

fase1_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fase1_module)

pygame.init()

WIDTH, HEIGHT = 1200, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autorama Arcade - Menu Principal")

IMG_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "img"))
FPS = 60

def tela_capa_jogo():
    """Desenha a capa do jogo e aguarda o botão INICIAR ou a tecla ENTER."""
    clock = pygame.time.Clock()

    fundo_capa = pygame.image.load(os.path.join(IMG_PATH, "capa-jogo.png"))
    fundo_capa = pygame.transform.scale(fundo_capa, (WIDTH, HEIGHT))
    x_original, y_original = 365, 460
    largura_original, altura_original = 470, 105

    x_ajustado = int(x_original * (WIDTH / 1200))
    y_ajustado = int(y_original * (HEIGHT / 900))
    largura_ajustada = int(largura_original * (WIDTH / 1200))
    altura_ajustada = int(altura_original * (HEIGHT / 900))

    retangulo_iniciar = pygame.Rect(x_ajustado, y_ajustado, largura_ajustada, altura_ajustada)

    while True:
        clock.tick(FPS)
        WIN.blit(fundo_capa, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    return
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retangulo_iniciar.collidepoint(event.pos):
                    return

        pygame.display.update()

def main_geral():

    tela_capa_jogo()
    player1_name, player2_name= fase1_module.ask_player_names()
    phase1_winner, laps1_p1, laps1_p2= fase1_module.run_phase(1, player1_name, player2_name)
    fase1_module.show_results(1, phase1_winner, player1_name, player2_name, laps1_p1, laps1_p2)

    pygame.quit()

if __name__ == "__main__":
    main_geral()