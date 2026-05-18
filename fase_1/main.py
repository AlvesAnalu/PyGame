import math
import os
import pygame

from utils import scale_image, blit_rotate_center

pygame.init()
pygame.font.init()

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_PATH = os.path.join(BASE_PATH, "img")

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (18, 18, 18)
GRAY = (90, 90, 90)
GREEN = (60, 180, 75)
RED = (220, 50, 50)
YELLOW = (255, 215, 0)
CYAN = (80, 200, 255)

TRACK_BORDER_MASK = None
WIN = pygame.display.set_mode((900, 600))
pygame.display.set_caption("Autorama 2 Jogadores")

FONT_BIG = pygame.font.SysFont("arial", 54, bold=True)
FONT_MED = pygame.font.SysFont("arial", 34, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 24)


def load_image(filename: str, scale: float = 1.0, fallback: str | None = None) -> pygame.Surface:
    path = os.path.join(IMG_PATH, filename)
    if not os.path.exists(path):
        if fallback is None:
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        path = os.path.join(IMG_PATH, fallback)
    image = pygame.image.load(path)
    return scale_image(image, scale)


def load_level_assets(level: int):
    if level == 2:
        grass = load_image("grass2.jpg", 2.5, fallback="gramado.png")
        track = load_image("track2.png", 1.0, fallback="pista.png")
        border = load_image("track2-border.png", 1.0, fallback="contorno.png")
    else:
        grass = load_image("gramado.png", 2.5, fallback="grass.jpg")
        track = load_image("pista.png", 1.0, fallback="track.png")
        border = load_image("contorno.png", 1.0, fallback="track-border.png")

    red_car = load_image("mazda.png", 0.070, fallback="red-car.png")
    green_car = load_image("lfa.png", 0.070, fallback="green-car.png")
    return grass, track, border, red_car, green_car


def pct(w: int, h: int, x: float, y: float) -> tuple[int, int]:
    return int(w * x), int(h * y)


def build_path(points: list[tuple[int, int]], density: int = 16) -> list[tuple[float, float]]:
    path: list[tuple[float, float]] = []
    for i in range(len(points)):
        a = points[i]
        b = points[(i + 1) % len(points)]
        for step in range(density):
            t = step / density
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            path.append((x, y))
    return path


def offset_path(path: list[tuple[float, float]], dx: float, dy: float) -> list[tuple[float, float]]:
    return [(x + dx, y + dy) for x, y in path]


class SlotCar:
    def __init__(self, image: pygame.Surface, path: list[tuple[float, float]], max_vel: float = 4.0):
        self.img = image
        self.path = path
        self.max_vel = max_vel
        self.vel = 0.0
        self.acceleration = 0.08
        self.angle = 0.0
        self.path_index = 0
        self.laps = 0
        self.locked = False

        self.x, self.y = self.path[0]

    def draw(self, win: pygame.Surface):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def rotate_to_next_point(self, next_x: float, next_y: float):
        dx = next_x - self.x
        dy = next_y - self.y
        self.angle = -math.degrees(math.atan2(dy, dx)) + 90

    def move_along_path(self):
        if self.locked or self.vel <= 0:
            return

        next_index = self.path_index + 1
        if next_index >= len(self.path):
            next_index = 0

        next_x, next_y = self.path[next_index]
        dx = next_x - self.x
        dy = next_y - self.y
        dist = math.hypot(dx, dy)

        if dist <= self.vel:
            self.x, self.y = next_x, next_y
            self.path_index = next_index

            if self.path_index == 0:
                self.laps += 1
                if self.laps >= 5:
                    self.locked = True
                    self.vel = 0.0
                    return

            next_index = self.path_index + 1
            if next_index >= len(self.path):
                next_index = 0
            self.rotate_to_next_point(*self.path[next_index])
        else:
            self.rotate_to_next_point(next_x, next_y)
            self.x += (dx / dist) * self.vel
            self.y += (dy / dist) * self.vel

    def accelerate(self):
        if self.locked:
            return
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move_along_path()

    def brake(self):
        if self.locked:
            return
        self.vel = max(self.vel - self.acceleration * 2, 0.0)
        if self.vel > 0:
            self.move_along_path()

    def coast(self):
        if self.locked:
            return
        self.vel = max(self.vel - self.acceleration * 0.35, 0.0)
        if self.vel > 0:
            self.move_along_path()


def center_text(surface, text, font, color, y):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(rendered, rect)


def draw_button(surface, rect, text, active=False):
    color = YELLOW if active else GRAY
    pygame.draw.rect(surface, color, rect, border_radius=14)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=14)
    label = FONT_SMALL.render(text, True, BLACK)
    surface.blit(label, label.get_rect(center=rect.center))


def start_screen():
    clock = pygame.time.Clock()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        WIN.fill(DARK)
        center_text(WIN, "AUTORAMA 2 JOGADORES", FONT_BIG, WHITE, 110)
        center_text(WIN, "P1: W acelera / S freia", FONT_MED, YELLOW, 220)
        center_text(WIN, "P2: UP acelera / DOWN freia", FONT_MED, YELLOW, 270)
        center_text(WIN, "Cada fase termina em 5 voltas", FONT_SMALL, WHITE, 330)
        center_text(WIN, "Pressione ENTER para começar", FONT_MED, GREEN, 420)
        pygame.display.update()


def ask_player_names():
    clock = pygame.time.Clock()
    name1 = ""
    name2 = ""
    active = 1

    box1 = pygame.Rect(120, 220, 560, 60)
    box2 = pygame.Rect(120, 330, 560, 60)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active = 2 if active == 1 else 1
                elif event.key == pygame.K_RETURN:
                    return name1.strip() or "Corredor 1", name2.strip() or "Corredor 2"
                elif event.key == pygame.K_BACKSPACE:
                    if active == 1:
                        name1 = name1[:-1]
                    else:
                        name2 = name2[:-1]
                else:
                    if event.unicode.isprintable() and len(event.unicode) == 1:
                        if active == 1 and len(name1) < 16:
                            name1 += event.unicode
                        elif active == 2 and len(name2) < 16:
                            name2 += event.unicode

        WIN.fill(DARK)
        center_text(WIN, "Digite o nome dos corredores", FONT_BIG, WHITE, 110)
        center_text(WIN, "TAB troca de campo | ENTER confirma", FONT_SMALL, YELLOW, 170)

        label1 = FONT_SMALL.render("Carro vermelho:", True, WHITE)
        label2 = FONT_SMALL.render("Carro verde:", True, WHITE)
        WIN.blit(label1, (120, 190))
        WIN.blit(label2, (120, 300))

        pygame.draw.rect(WIN, WHITE, box1, 2, border_radius=12)
        pygame.draw.rect(WIN, WHITE, box2, 2, border_radius=12)

        if active == 1:
            pygame.draw.rect(WIN, GREEN, box1, 4, border_radius=12)
        else:
            pygame.draw.rect(WIN, GREEN, box2, 4, border_radius=12)

        text1 = FONT_MED.render(name1 or "...", True, WHITE)
        text2 = FONT_MED.render(name2 or "...", True, WHITE)
        WIN.blit(text1, (140, 230))
        WIN.blit(text2, (140, 340))

        draw_button(WIN, pygame.Rect(120, 430, 220, 52), "ENTER para confirmar", True)
        pygame.display.update()


def show_message_screen(title, lines, footer="Pressione ENTER para continuar"):
    clock = pygame.time.Clock()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        WIN.fill(DARK)
        center_text(WIN, title, FONT_BIG, WHITE, 110)

        y = 240
        for line in lines:
            center_text(WIN, line, FONT_MED, WHITE, y)
            y += 50

        center_text(WIN, footer, FONT_SMALL, YELLOW, WIN.get_height() - 70)
        pygame.display.update()


def make_control_points(track: pygame.Surface, level: int):
    w, h = track.get_width(), track.get_height()

    if level == 2:
        base = [
            pct(w, h, 0.10, 0.05),
            pct(w, h, 0.42, 0.05),
            pct(w, h, 0.54, 0.17),
            pct(w, h, 0.54, 0.36),
            pct(w, h, 0.82, 0.36),
            pct(w, h, 0.88, 0.50),
            pct(w, h, 0.82, 0.66),
            pct(w, h, 0.60, 0.66),
            pct(w, h, 0.60, 0.83),
            pct(w, h, 0.42, 0.92),
            pct(w, h, 0.18, 0.85),
            pct(w, h, 0.09, 0.66),
            pct(w, h, 0.09, 0.38),
            pct(w, h, 0.18, 0.20),
        ]
    else:
        base = [
            pct(w, h, 0.08, 0.05),
            pct(w, h, 0.42, 0.05),
            pct(w, h, 0.55, 0.12),
            pct(w, h, 0.55, 0.30),
            pct(w, h, 0.75, 0.30),
            pct(w, h, 0.84, 0.45),
            pct(w, h, 0.79, 0.63),
            pct(w, h, 0.60, 0.63),
            pct(w, h, 0.60, 0.84),
            pct(w, h, 0.40, 0.92),
            pct(w, h, 0.16, 0.84),
            pct(w, h, 0.06, 0.63),
            pct(w, h, 0.06, 0.38),
            pct(w, h, 0.16, 0.18),
        ]

    path_1 = build_path(base, density=18)
    path_2 = build_path(base, density=18)

    path_1 = offset_path(path_1, -10, -8)
    path_2 = offset_path(path_2, 10, 8)

    return path_1, path_2


def create_cars(red_car: pygame.Surface, green_car: pygame.Surface, path_1, path_2):
    car1 = SlotCar(red_car, path_1, max_vel=4.2)
    car2 = SlotCar(green_car, path_2, max_vel=4.2)
    return car1, car2


def run_phase(level: int, player1_name: str, player2_name: str):
    global WIN

    grass, track, border, red_car_img, green_car_img = load_level_assets(level)
    WIN = pygame.display.set_mode(track.get_size())
    finish_zone = pygame.Rect(track.get_width() // 2 - 90, 20, 180, 80)

    path_1, path_2 = make_control_points(track, level)
    car1, car2 = create_cars(red_car_img, green_car_img, path_1, path_2)

    clock = pygame.time.Clock()
    winner = None

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            car1.accelerate()
        elif keys[pygame.K_s]:
            car1.brake()
        else:
            car1.coast()

        if keys[pygame.K_UP]:
            car2.accelerate()
        elif keys[pygame.K_DOWN]:
            car2.brake()
        else:
            car2.coast()

        if car1.laps >= 5 and winner is None:
            winner = 1
        if car2.laps >= 5 and winner is None:
            winner = 2

        WIN.blit(grass, (0, 0))
        WIN.blit(track, (0, 0))
        WIN.blit(border, (0, 0))
        pygame.draw.rect(WIN, YELLOW, finish_zone, 2)

        car1.draw(WIN)
        car2.draw(WIN)

        laps_1 = FONT_SMALL.render(f"{player1_name}: {car1.laps}/5", True, WHITE)
        laps_2 = FONT_SMALL.render(f"{player2_name}: {car2.laps}/5", True, WHITE)
        phase_label = FONT_SMALL.render(f"Fase {level}", True, CYAN)

        WIN.blit(laps_1, (20, 18))
        WIN.blit(laps_2, (20, 46))
        WIN.blit(phase_label, (WIN.get_width() - 110, 18))

        pygame.display.update()

        if winner is not None:
            return winner, car1.laps, car2.laps


def show_phase_result(phase, winner_id, player1_name, player2_name, laps_1, laps_2):
    winner_name = player1_name if winner_id == 1 else player2_name
    show_message_screen(
        f"Fase {phase} concluída",
        [
            f"Vencedor: {winner_name}",
            f"{player1_name}: {laps_1} voltas",
            f"{player2_name}: {laps_2} voltas",
        ],
    )


def show_final_screen(phase1_winner, phase2_winner, player1_name, player2_name):
    score1 = (1 if phase1_winner == 1 else 0) + (1 if phase2_winner == 1 else 0)
    score2 = (1 if phase1_winner == 2 else 0) + (1 if phase2_winner == 2 else 0)

    if score1 > score2:
        champ = f"Campeão geral: {player1_name}"
    elif score2 > score1:
        champ = f"Campeão geral: {player2_name}"
    else:
        champ = "Empate geral!"

    show_message_screen(
        "Resultado final",
        [
            champ,
            f"Fase 1: {'carro vermelho' if phase1_winner == 1 else 'carro verde'}",
            f"Fase 2: {'carro vermelho' if phase2_winner == 1 else 'carro verde'}",
        ],
        footer="Pressione ENTER para sair",
    )


def main():
    start_screen()
    player1_name, player2_name = ask_player_names()

    phase1_winner, laps1_p1, laps1_p2 = run_phase(1, player1_name, player2_name)
    show_phase_result(1, phase1_winner, player1_name, player2_name, laps1_p1, laps1_p2)

    phase2_winner, laps2_p1, laps2_p2 = run_phase(2, player1_name, player2_name)
    show_phase_result(2, phase2_winner, player1_name, player2_name, laps2_p1, laps2_p2)

    show_final_screen(phase1_winner, phase2_winner, player1_name, player2_name)
    pygame.quit()


if __name__ == "__main__":
    main()