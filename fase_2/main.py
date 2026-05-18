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
YELLOW = (255, 215, 0)

WIN = pygame.display.set_mode((900, 600))
pygame.display.set_caption("Autorama - Fase 2")

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


def load_assets():
    grass = load_image("grass2.jpg", 2.5, fallback="gramado.png")
    track = load_image("track2.png", 1.0, fallback="pista.png")
    border = load_image("track2-border.png", 1.0, fallback="contorno.png")
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


def show_message(title, lines, footer="Pressione ENTER para continuar"):
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
        center_text(WIN, title, FONT_BIG, WHITE, 120)

        y = 240
        for line in lines:
            center_text(WIN, line, FONT_MED, WHITE, y)
            y += 50

        center_text(WIN, footer, FONT_SMALL, YELLOW, 520)
        pygame.display.update()


def make_control_points(track: pygame.Surface):
    w, h = track.get_width(), track.get_height()

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

    path_1 = build_path(base, density=18)
    path_2 = build_path(base, density=18)

    path_1 = offset_path(path_1, -10, -8)
    path_2 = offset_path(path_2, 10, 8)
    return path_1, path_2


def create_cars(red_car, green_car, path_1, path_2):
    car1 = SlotCar(red_car, path_1, 4.2)
    car2 = SlotCar(green_car, path_2, 4.2)
    return car1, car2


def run_phase_2(player1_name="Corredor 1", player2_name="Corredor 2"):
    global WIN

    grass, track, border, red_car_img, green_car_img = load_assets()
    WIN = pygame.display.set_mode(track.get_size())
    path_1, path_2 = make_control_points(track)
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

        car1.draw(WIN)
        car2.draw(WIN)

        laps_1 = FONT_SMALL.render(f"{player1_name}: {car1.laps}/5", True, WHITE)
        laps_2 = FONT_SMALL.render(f"{player2_name}: {car2.laps}/5", True, WHITE)
        WIN.blit(laps_1, (20, 18))
        WIN.blit(laps_2, (20, 46))

        pygame.display.update()

        if winner is not None:
            return winner, car1.laps, car2.laps


def main():
    show_message(
        "FASE 2",
        [
            "Segunda pista do autorama.",
            "O carro anda em um trilho fixo.",
            "Quem fizer 5 voltas primeiro vence.",
        ],
    )

    winner, laps1, laps2 = run_phase_2()

    show_message(
        "Resultado da Fase 2",
        [
            f"Vencedor: {'Carro vermelho' if winner == 1 else 'Carro verde'}",
            f"Voltas do carro vermelho: {laps1}",
            f"Voltas do carro verde: {laps2}",
        ],
        footer="Pressione ENTER para sair",
    )

    pygame.quit()


if __name__ == "__main__":
    main()