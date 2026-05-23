import os
import sys
import importlib.util
import pygame

pygame.init()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

FASE1_DIR = os.path.join(ROOT_DIR, "fase_1")
FASE2_DIR = os.path.join(ROOT_DIR, "fase_2")

FASE1_PATH = os.path.join(FASE1_DIR, "mainfase1.py")
FASE2_PATH = os.path.join(FASE2_DIR, "mainfase2.py")

WIDTH, HEIGHT = 1200, 900
FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autorama Arcade - Menu Principal")

IMG_PATH = os.path.abspath(os.path.join(ROOT_DIR, "img"))


def load_module(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar o módulo em: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fase1_module = load_module("mainfase1", FASE1_PATH)
fase2_module = load_module("mainfase2", FASE2_PATH)


def tela_capa_jogo():
    """Desenha a capa do jogo e aguarda ENTER ou clique no botão iniciar."""
    clock = pygame.time.Clock()

    fundo_capa = pygame.image.load(os.path.join(IMG_PATH, "capa-jogo.png"))
    fundo_capa = pygame.transform.scale(fundo_capa, (WIDTH, HEIGHT))

    x_original, y_original = 365, 460
    largura_original, altura_original = 470, 105

    x_ajustado = int(x_original * (WIDTH / 1200))
    y_ajustado = int(y_original * (HEIGHT / 900))
    largura_ajustada = int(largura_original * (WIDTH / 1200))
    altura_ajustada = int(altura_original * (HEIGHT / 900))

    retangulo_iniciar = pygame.Rect(
        x_ajustado, y_ajustado, largura_ajustada, altura_ajustada
    )

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


def chamar_resultado_modulo(modulo, fase, vencedor, nome1, nome2, voltas1, voltas2):
    """
    Chama a função de resultado do módulo da fase.
    Aceita nomes diferentes de função para evitar erro de compatibilidade.
    """
    if hasattr(modulo, "show_results"):
        modulo.show_results(fase, vencedor, nome1, nome2, voltas1, voltas2)
    elif hasattr(modulo, "show_phase_result"):
        modulo.show_phase_result(fase, vencedor, nome1, nome2, voltas1, voltas2)
    elif hasattr(modulo, "show_message"):
        texto_vencedor = nome1 if vencedor == 1 else nome2
        modulo.show_message(
            f"Resultado da Fase {fase}",
            [
                f"Vencedor: {texto_vencedor}",
                f"{nome1}: {voltas1} voltas",
                f"{nome2}: {voltas2} voltas",
            ],
        )
    else:
        print(f"Fase {fase} encerrada. Vencedor: {'carro 1' if vencedor == 1 else 'carro 2'}")


def main_geral():
    tela_capa_jogo()

    if not hasattr(fase1_module, "ask_player_names"):
        raise AttributeError("mainfase1.py precisa ter a função ask_player_names()")
    if not hasattr(fase1_module, "run_phase"):
        raise AttributeError("mainfase1.py precisa ter a função run_phase()")
    if not hasattr(fase2_module, "run_phase_2"):
        raise AttributeError("mainfase2.py precisa ter a função run_phase_2()")

    player1_name, player2_name = fase1_module.ask_player_names()

    # Fase 1
    phase1_winner, laps1_p1, laps1_p2 = fase1_module.run_phase(
        1, player1_name, player2_name
    )
    chamar_resultado_modulo(
        fase1_module,
        1,
        phase1_winner,
        player1_name,
        player2_name,
        laps1_p1,
        laps1_p2,
    )

    # Fase 2
    phase2_winner, laps2_p1, laps2_p2 = fase2_module.run_phase_2(
        player1_name, player2_name
    )
    chamar_resultado_modulo(
        fase2_module,
        2,
        phase2_winner,
        player1_name,
        player2_name,
        laps2_p1,
        laps2_p2,
    )

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_geral()