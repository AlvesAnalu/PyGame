import math
import os
import sys
import pygame

# --- CONFIGURAÇÃO DE DIRETÓRIOS ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
IMG_PATH = os.path.join(ROOT_DIR, "img")
FASE1_DIR = os.path.join(ROOT_DIR, "fase_1")

# Adiciona a pasta fase_1 ao path para podermos importar o utils.py de lá
if FASE1_DIR not in sys.path:
    sys.path.insert(0, FASE1_DIR)

from utils import scale_image, blit_rotate_center

pygame.init()
pygame.font.init()

# --- CONSTANTES ---
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 221, 0)
GREEN = (0, 200, 0)
CYAN = (0, 200, 200)
AJUSTE_ANGULO = 90

FONT_SMALL = pygame.font.SysFont("arial", 24)
FONT_MED = pygame.font.SysFont("arial", 34, bold=True)

def load_image(filename: str, scale: float = 1.0, fallback: str | None = None) -> pygame.Surface:
    path = os.path.join(IMG_PATH, filename)
    if not os.path.exists(path):
        if fallback is None:
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        path = os.path.join(IMG_PATH, fallback)
    image = pygame.image.load(path)
    return scale_image(image, scale)

def load_phase2_assets():
    # Carrega especificamente a pista2.png. Usa gramado e contorno normais como base/fallback
    grass = load_image("grass2.jpg", 2.5, fallback="gramado.png")
    track = load_image("pista2.png", 1.0)
    border = load_image("contorno2.png", 1.0, fallback="contorno.png")
    red_car = load_image("mazda.png", 0.070, fallback="red-car.png")
    green_car = load_image("lfa.png", 0.070, fallback="green-car.png")
    return grass, track, border, red_car, green_car

def pct(w: int, h: int, x: float, y: float) -> tuple[int, int]:
    return int(w * x), int(h * y)

def build_path(points: list[tuple[int, int]], density: int = 18) -> list[tuple[float, float]]:
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

def normalize(x: float, y: float) -> tuple[float, float]:
    dist = math.hypot(x, y)
    if dist == 0:
        return 0.0, 0.0
    return x / dist, y / dist

def offset_closed_polyline(points: list[tuple[int, int]], offset: float) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    n = len(points)
    for i in range(n):
        x, y = points[i]
        px, py = points[i - 1]
        nx, ny = points[(i + 1) % n]

        v1x, v1y = normalize(x - px, y - py)
        v2x, v2y = normalize(nx - x, ny - y)

        n1x, n1y = -v1y, v1x
        n2x, n2y = -v2y, v2x

        ox, oy = normalize(n1x + n2x, n1y + n2y)
        if ox == 0 and oy == 0:
            ox, oy = n1x, n1y

        dot = ox * n1x + oy * n1y

        if dot > 0.1:
            length = offset / dot
            length = min(length, offset * 1.5)
        else:
            length = offset

        result.append((int(x + ox * length), int(y + oy * length)))
    return result

def centerline_points_phase2(track: pygame.Surface) -> list[tuple[int, int]]:
    w, h = track.get_width(), track.get_height()

    # ========================================================================
    # ATENÇÃO: USAR O MAPEADOR2.PY NA pista2.png =======================================================================
    # raw = [
    #     (0.12, 0.06), (0.42, 0.06), (0.54, 0.16), (0.54, 0.34),
    #     (0.80, 0.34), (0.88, 0.50), (0.81, 0.66), (0.60, 0.66),
    #     (0.60, 0.83), (0.43, 0.91), (0.18, 0.84), (0.09, 0.66),
    #     (0.09, 0.38), (0.18, 0.20),
    # ]
    raw = [
        (0.80, 0.84),
        (0.77, 0.84),
        (0.41, 0.84),
        (0.39, 0.84),
        (0.38, 0.84),
        (0.37, 0.83),
        (0.35, 0.83),
        (0.34, 0.82),
        (0.33, 0.80),
        (0.32, 0.78),
        (0.30, 0.76),
        (0.28, 0.74),
        (0.27, 0.74),
        (0.25, 0.74),
        (0.23, 0.74),
        (0.22, 0.75),
        (0.21, 0.76),
        (0.18, 0.79),
        (0.16, 0.82),
        (0.13, 0.84),
        (0.12, 0.84),
        (0.10, 0.84),
        (0.08, 0.83),
        (0.06, 0.81),
        (0.05, 0.78),
        (0.05, 0.76),
        (0.05, 0.35),
        (0.05, 0.32),
        (0.05, 0.29),
        (0.06, 0.26),
        (0.07, 0.24),
        (0.09, 0.22),
        (0.11, 0.20),
        (0.13, 0.19),
        (0.15, 0.19),
        (0.17, 0.21),
        (0.19, 0.23),
        (0.19, 0.26),
        (0.19, 0.53),
        (0.20, 0.58),
        (0.21, 0.60),
        (0.23, 0.61),
        (0.25, 0.62),
        (0.39, 0.62),
        (0.41, 0.61),
        (0.43, 0.58),
        (0.43, 0.56),
        (0.43, 0.54),
        (0.41, 0.53),
        (0.40, 0.52),
        (0.31, 0.52),
        (0.29, 0.51),
        (0.28, 0.50),
        (0.28, 0.48),
        (0.28, 0.24),
        (0.28, 0.22),
        (0.29, 0.20),
        (0.30, 0.19),
        (0.32, 0.18),
        (0.89, 0.18),
        (0.91, 0.19),
        (0.92, 0.21),
        (0.93, 0.23),
        (0.93, 0.25),
        (0.91, 0.27),
        (0.89, 0.28),
        (0.57, 0.28),
        (0.55, 0.29),
        (0.53, 0.31),
        (0.51, 0.33),
        (0.51, 0.37),
        (0.52, 0.39),
        (0.54, 0.42),
        (0.57, 0.43),
        (0.59, 0.43),
        (0.61, 0.45),
        (0.61, 0.48),
        (0.61, 0.49),
        (0.60, 0.51),
        (0.59, 0.52),
        (0.57, 0.53),
        (0.54, 0.53),
        (0.52, 0.54),
        (0.50, 0.57),
        (0.50, 0.60),
        (0.51, 0.62),
        (0.53, 0.63),
        (0.58, 0.64),
        (0.54, 0.63),
        (0.55, 0.64),
        (0.54, 0.64),
        (0.60, 0.64),
        (0.62, 0.64),
        (0.64, 0.64),
        (0.66, 0.65),
        (0.68, 0.68),
        (0.69, 0.70),
        (0.72, 0.71),
        (0.73, 0.71),
        (0.89, 0.71),
        (0.91, 0.72),
        (0.93, 0.73),
        (0.94, 0.76),
        (0.93, 0.78),
        (0.93, 0.81),
        (0.92, 0.82),
        (0.90, 0.84),
        (0.89, 0.84),
        (0.81, 0.84),
    ]

    return [pct(w, h, x, y) for x, y in raw]

def build_lane_paths_phase2(track: pygame.Surface, lane_offset: int = 24):
    center = centerline_points_phase2(track)
    left_lane = build_path(offset_closed_polyline(center, -lane_offset), density=18)
    right_lane = build_path(offset_closed_polyline(center, lane_offset), density=18)
    return left_lane, right_lane, center

class SlotCarPhase2:
    def __init__(self, image: pygame.Surface, path: list[tuple[float, float]]):
        self.img = image
        self.path = path

        self.max_vel = 6.0
        self.derail_vel = 4.3
        self.crashed = False
        self.crash_timer = 0
        self.PENALTY_FRAMES = 90

        self.vel = 0.0
        self.acceleration = 0.08
        self.angle = 0.0
        self.path_index = 0
        self.laps = 0
        self.locked = False

        if self.path:
            self.x, self.y = self.path[0]
            self.sync_angle()

    def sync_angle(self):
        if len(self.path) > 1:
            nx, ny = self.path[1]
            self.angle = -math.degrees(math.atan2(ny - self.y, nx - self.x)) + AJUSTE_ANGULO

    def draw(self, win: pygame.Surface):
        if self.crashed:
            if (self.crash_timer // 5) % 2 == 0:
                return
        blit_rotate_center(win, self.img, (int(self.x), int(self.y)), self.angle)
        if self.crashed:
            aviso = FONT_MED.render("!", True, RED)
            win.blit(aviso, (int(self.x) - 10, int(self.y) - 40))

    def manage_penalty(self) -> bool:
        if self.crashed:
            self.crash_timer -= 1
            if self.crash_timer <= 0:
                self.crashed = False
            return True
        return False

    def advance(self, distance: float):
        remaining = distance
        while remaining > 0 and not self.locked:
            next_index = (self.path_index + 1) % len(self.path)
            next_x, next_y = self.path[next_index]
            dx = next_x - self.x
            dy = next_y - self.y
            dist = math.hypot(dx, dy)

            if dist < 0.001:
                self.x, self.y = next_x, next_y
                self.path_index = next_index
                if self.path_index == 0:
                    self.laps += 1
                    if self.laps >= 5:
                        self.locked = True; self.vel = 0.0; return
                continue

            step = min(remaining, dist)
            self.angle = -math.degrees(math.atan2(dy, dx)) + AJUSTE_ANGULO
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
            remaining -= step

            if step >= dist - 0.001:
                self.path_index = next_index
                if self.path_index == 0:
                    self.laps += 1
                    if self.laps >= 5:
                        self.locked = True; self.vel = 0.0; return
            else:
                break

    def accelerate(self):
        if self.locked or self.manage_penalty():
            return
        self.vel += self.acceleration
        if self.vel > self.derail_vel:
            self.crashed = True
            self.crash_timer = self.PENALTY_FRAMES
            self.vel = 0.0
            return
        self.advance(self.vel)

    def brake(self):
        if self.locked or self.manage_penalty():
            return
        self.vel = max(self.vel - self.acceleration * 2, 0.0)
        if self.vel > 0:
            self.advance(self.vel)

    def coast(self):
        if self.locked or self.manage_penalty():
            return
        self.vel = max(self.vel - self.acceleration * 0.35, 0.0)
        if self.vel > 0:
            self.advance(self.vel)


def run_phase_2(player1_name: str, player2_name: str):
    """
    Função principal da Fase 2.
    É chamada automaticamente pelo main.py da Fase 1 quando a primeira corrida termina.
    """
    DEBUG_PATHS = True # Mantenha True até alinhar a nova pista perfeitamente

    grass, track, border, red_car_img, green_car_img = load_phase2_assets()

    # Usa a janela já existente gerada pelo Pygame na Fase 1
    WIN = pygame.display.get_surface()
    if WIN.get_size() != track.get_size():
        WIN = pygame.display.set_mode(track.get_size())

    # Distância das faixas. Ajuste se as faixas saírem do asfalto
    lane_offset = 22

    lane_left, lane_right, center_raw = build_lane_paths_phase2(track, lane_offset)
    center_path = build_path(center_raw, density=18)

    car1 = SlotCarPhase2(red_car_img, lane_left)
    car2 = SlotCarPhase2(green_car_img, lane_right)

    clock = pygame.time.Clock()
    winner = None

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]: car1.accelerate()
        elif keys[pygame.K_s]: car1.brake()
        else: car1.coast()

        if keys[pygame.K_UP]: car2.accelerate()
        elif keys[pygame.K_DOWN]: car2.brake()
        else: car2.coast()

        if car1.laps >= 5 and winner is None: winner = 1
        if car2.laps >= 5 and winner is None: winner = 2

        WIN.blit(grass, (0, 0))
        WIN.blit(track, (0, 0))
        WIN.blit(border, (0, 0))

        if DEBUG_PATHS:
            if len(center_path) > 1:
                pygame.draw.lines(WIN, YELLOW, True, center_path, 2)
            if len(lane_left) > 1:
                pygame.draw.lines(WIN, RED, True, lane_left, 2)
            if len(lane_right) > 1:
                pygame.draw.lines(WIN, GREEN, True, lane_right, 2)

        car1.draw(WIN)
        car2.draw(WIN)

        laps_1 = FONT_SMALL.render(f"{player1_name}: {car1.laps}/5", True, WHITE)
        laps_2 = FONT_SMALL.render(f"{player2_name}: {car2.laps}/5", True, WHITE)
        phase_label = FONT_SMALL.render("Fase 2", True, CYAN)

        WIN.blit(laps_1, (20, 18))
        WIN.blit(laps_2, (20, 46))
        WIN.blit(phase_label, (WIN.get_width() - 110, 18))

        pygame.display.update()

        if winner is not None:
            return winner, car1.laps, car2.laps

if __name__ == "__main__":
    # Teste rápido apenas da Fase 2 (opcional)
    pygame.display.set_mode((900, 600))
    run_phase_2("Corredor 1", "Corredor 2")
    pygame.quit()