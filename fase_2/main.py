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
GRAY = (80, 80, 80)
GREEN = (60, 180, 75)
YELLOW = (255, 215, 0)

WIN = pygame.display.set_mode((900, 600))
pygame.display.set_caption("Autorama - Fase 2")

FONT_BIG = pygame.font.SysFont("arial", 54, bold=True)
FONT_MED = pygame.font.SysFont("arial", 34, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 24)

TRACK_BORDER_MASK = None


def load_image(filename: str, scale: float = 1.0, fallback: str | None = None) -> pygame.Surface:
    path = os.path.join(IMG_PATH, filename)
    if not os.path.exists(path):
        if fallback is None:
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        path = os.path.join(IMG_PATH, fallback)
    image = pygame.image.load(path)
    return scale_image(image, scale)


def load_assets():
    grass = load_image("grass2.jpg", 2.5, fallback="grass.jpg")
    track = load_image("track2.png", 1.0, fallback="track.png")
    border = load_image("track2-border.png", 1.0, fallback="track-border.png")
    red_car = load_image("red-car.png", 0.55)
    green_car = load_image("green-car.png", 0.55)
    return grass, track, border, red_car, green_car


class AbstractCar:
    def __init__(self, image, start_pos, max_vel, rotation_vel):
        self.img = image
        self.max_vel = max_vel
        self.vel = 0.0
        self.rotation_vel = rotation_vel
        self.angle = 0.0
        self.x, self.y = start_pos
        self.acceleration = 0.1
        self.laps = 0
        self.inside_finish = False

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        return blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def get_rotated_mask(self):
        rotated_image = pygame.transform.rotate(self.img, self.angle)
        return pygame.mask.from_surface(rotated_image), rotated_image

    def collide(self, mask, x=0, y=0):
        car_mask, rotated_image = self.get_rotated_mask()
        rotated_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        offset = (int(rotated_rect.left - x), int(rotated_rect.top - y))
        return mask.overlap(car_mask, offset)

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal

    def move_forward(self):
        old_x, old_y = self.x, self.y
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()
        if self.collide(TRACK_BORDER_MASK) is not None:
            self.x, self.y = old_x, old_y
            self.vel = 0

    def move_backward(self):
        old_x, old_y = self.x, self.y
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()
        if self.collide(TRACK_BORDER_MASK) is not None:
            self.x, self.y = old_x, old_y
            self.vel = 0

    def reduce_speed(self):
        old_x, old_y = self.x, self.y
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration / 2, 0)
        elif self.vel < 0:
            self.vel = min(self.vel + self.acceleration / 2, 0)
        self.move()
        if self.collide(TRACK_BORDER_MASK) is not None:
            self.x, self.y = old_x, old_y
            self.vel = 0


class PlayerCar(AbstractCar):
    pass


class GreenCar(AbstractCar):
    pass


def finish_zone_for_track(track):
    width = track.get_width()
    return pygame.Rect(max(0, width // 2 - 120), 35, 240, 90)


def create_cars(red_car, green_car):
    car1 = PlayerCar(red_car, (430, 75), 4, 4)
    car2 = GreenCar(green_car, (520, 75), 4, 4)
    return car1, car2


def update_car(car, keys, forward_key, backward_key, left_key, right_key):
    if keys[left_key]:
        car.rotate(left=True)
    if keys[right_key]:
        car.rotate(right=True)

    if keys[forward_key]:
        car.move_forward()
    elif keys[backward_key]:
        car.move_backward()
    else:
        car.reduce_speed()


def center_text(surface, text, font, color, y):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(rendered, rect)


def show_message(title, lines):
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

        center_text(WIN, "Pressione ENTER para continuar", FONT_SMALL, YELLOW, 520)
        pygame.display.update()


def run_phase_2(player1_name, player2_name):
    global WIN, TRACK_BORDER_MASK

    grass, track, border, red_car_img, green_car_img = load_assets()
    WIN = pygame.display.set_mode(track.get_size())
    TRACK_BORDER_MASK = pygame.mask.from_surface(border)
    finish_zone = finish_zone_for_track(track)

    car1, car2 = create_cars(red_car_img, green_car_img)
    clock = pygame.time.Clock()
    winner = None

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        keys = pygame.key.get_pressed()
        update_car(car1, keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
        update_car(car2, keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)

        temp_surface = pygame.Surface(track.get_size(), pygame.SRCALPHA)
        rect1 = car1.draw(temp_surface)
        rect2 = car2.draw(temp_surface)

        inside1 = finish_zone.colliderect(rect1)
        inside2 = finish_zone.colliderect(rect2)

        if inside1 and not car1.inside_finish:
            car1.laps += 1
            if car1.laps >= 5 and winner is None:
                winner = 1
        car1.inside_finish = inside1

        if inside2 and not car2.inside_finish:
            car2.laps += 1
            if car2.laps >= 5 and winner is None:
                winner = 2
        car2.inside_finish = inside2

        WIN.blit(grass, (0, 0))
        WIN.blit(track, (0, 0))
        WIN.blit(border, (0, 0))
        WIN.blit(temp_surface, (0, 0))

        pygame.draw.rect(WIN, YELLOW, finish_zone, 2)

        laps_1 = FONT_SMALL.render(f"{player1_name}: {car1.laps}/5", True, WHITE)
        laps_2 = FONT_SMALL.render(f"{player2_name}: {car2.laps}/5", True, WHITE)
        WIN.blit(laps_1, (20, 18))
        WIN.blit(laps_2, (20, 46))

        pygame.display.update()

        if winner is not None:
            return winner, car1.laps, car2.laps


def main():
    player1_name = "Corredor 1"
    player2_name = "Corredor 2"

    show_message(
        "FASE 2",
        [
            "Essa é a segunda pista do jogo.",
            f"{player1_name} vs {player2_name}",
            "O primeiro a fazer 5 voltas vence.",
        ],
    )

    winner, laps1, laps2 = run_phase_2(player1_name, player2_name)

    show_message(
        "Resultado da Fase 2",
        [
            f"Vencedor: {'Carro vermelho' if winner == 1 else 'Carro verde'}",
            f"{player1_name}: {laps1} voltas",
            f"{player2_name}: {laps2} voltas",
        ],
    )

    pygame.quit()


if __name__ == "__main__":
    main()