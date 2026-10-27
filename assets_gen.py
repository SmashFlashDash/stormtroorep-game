"""assets_gen.py — спрайты, лабиринт, цветовые схемы."""
import os
import random
from functools import lru_cache

import pygame

from audio import resource_path

TILE_SIZE = 40

# ==================== ТЕМЫ ====================
THEMES = [
    {"name": "Космический корабль",
     "floor": (22, 22, 34), "floor_edge": (30, 30, 46),
     "wall": (58, 58, 82), "wall_hi": (88, 88, 120),
     "wall_lo": (38, 38, 55), "bolt": (70, 70, 95),
     "floor_dot": (26, 26, 40)},
    {"name": "Татуин",
     "floor": (60, 45, 28), "floor_edge": (75, 58, 38),
     "wall": (180, 140, 80), "wall_hi": (220, 180, 110),
     "wall_lo": (120, 90, 50), "bolt": (90, 65, 35),
     "floor_dot": (80, 60, 38)},
    {"name": "Лес Эндора",
     "floor": (20, 45, 22), "floor_edge": (28, 60, 30),
     "wall": (60, 120, 60), "wall_hi": (100, 170, 90),
     "wall_lo": (35, 80, 35), "bolt": (40, 90, 45),
     "floor_dot": (25, 55, 28)},
    {"name": "Дантуин",
     "floor": (35, 40, 55), "floor_edge": (45, 52, 70),
     "wall": (110, 125, 150), "wall_hi": (160, 175, 200),
     "wall_lo": (75, 88, 110), "bolt": (90, 105, 130),
     "floor_dot": (50, 58, 78)},
]


# ==================== ЛАБИРИНТ ====================
def generate_maze(cols, rows, extra_passages=0):
    if cols % 2 == 0: cols += 1
    if rows % 2 == 0: rows += 1
    maze = [[1] * cols for _ in range(rows)]

    def carve(cx, cy):
        maze[cy][cx] = 0
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < cols - 1 and 0 < ny < rows - 1 and maze[ny][nx] == 1:
                maze[cy + dy // 2][cx + dx // 2] = 0
                carve(nx, ny)

    carve(1, 1)
    for _ in range(extra_passages):
        cands = []
        for y in range(1, rows - 1):
            for x in range(1, cols - 1):
                if maze[y][x] != 1:
                    continue
                if (maze[y][x-1] == 0 and maze[y][x+1] == 0) or \
                   (maze[y-1][x] == 0 and maze[y+1][x] == 0):
                    cands.append((x, y))
        if not cands:
            break
        x, y = random.choice(cands)
        maze[y][x] = 0
    return maze


# ==================== СПРАЙТЫ ====================
def _surface(size=TILE_SIZE):
    return pygame.Surface((size, size), pygame.SRCALPHA)


# ---------- PNG-ассеты персонажа ----------
ASSETS_DIR      = "assets"
STORM_FILE_NAME = "stormtrooper.png"
STORM_MARGIN    = 2          # отступ картинки от края тайла (пиксели)


@lru_cache(maxsize=1)
def _load_stormtrooper_png():
    """assets/stormtrooper.png, обрезанный и сглаженно вписанный в тайл.

    Прозрачные поля исходника обрезаются (иначе персонаж выглядит мелким),
    пропорции сохраняются. Картинка читается и масштабируется один раз
    за запуск (кэш lru_cache).
    Возвращает None, если PNG нет или он битый — тогда используется
    процедурный спрайт _draw_stormtrooper().
    """
    path = resource_path(ASSETS_DIR, STORM_FILE_NAME)
    if not os.path.isfile(path):
        print(f"⚠️  Нет файла {path} — штурмовик рисуется кодом")
        return None
    try:
        img = pygame.image.load(path)
    except pygame.error as e:
        print(f"⚠️  Не удалось прочитать {path}: {e}")
        return None
    try:
        img = img.convert_alpha()
    except pygame.error:
        pass                     # видеорежим ещё не создан — это не критично

    # Обрезаем прозрачные поля вокруг шлема
    if img.get_flags() & pygame.SRCALPHA:
        bounds = img.get_bounding_rect(min_alpha=8)
        if bounds.width > 0 and bounds.height > 0:
            img = img.subsurface(bounds).copy()

    # Вписываем в тайл с сохранением пропорций
    max_side = TILE_SIZE - STORM_MARGIN * 2
    w, h = img.get_size()
    scale = min(max_side / w, max_side / h)
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    return pygame.transform.smoothscale(img, size)


def make_stormtrooper_sprite(frame=0):
    """Кадр штурмовика из PNG-ассета с покачиванием при ходьбе."""
    base = _load_stormtrooper_png()
    if base is None:
        return _draw_stormtrooper(frame)

    s = _surface()
    sway = [0, -1, 0, 1][frame % 4]      # вверх-вниз
    lean = [1, 0, -1, 0][frame % 4]      # влево-вправо — «шаг»
    x = (TILE_SIZE - base.get_width()) // 2 + lean
    y = (TILE_SIZE - base.get_height()) // 2 + sway
    s.blit(base, (x, y))
    return s


def make_stormtrooper_frames(count=4):
    """Набор кадров ходьбы штурмовика для игрока."""
    return [make_stormtrooper_sprite(i) for i in range(count)]


def _draw_stormtrooper(frame=0):
    """Процедурный штурмовик — фолбэк, если PNG-ассета нет."""
    s = _surface()
    sway = [0, -1, 0, 1][frame % 4]
    pygame.draw.ellipse(s, (235, 235, 245), (4, 3 + sway, 32, 34))
    pygame.draw.ellipse(s, (30, 30, 30), (4, 3 + sway, 32, 34), 2)
    pygame.draw.ellipse(s, (185, 185, 200), (4, 3 + sway, 8, 34))
    pygame.draw.ellipse(s, (185, 185, 200), (28, 3 + sway, 8, 34))
    pygame.draw.ellipse(s, (10, 10, 10), (9, 14 + sway, 9, 7))
    pygame.draw.ellipse(s, (10, 10, 10), (22, 14 + sway, 9, 7))
    pygame.draw.circle(s, (200, 200, 220), (12, 16 + sway), 1)
    pygame.draw.circle(s, (200, 200, 220), (25, 16 + sway), 1)
    pygame.draw.rect(s, (20, 20, 20), (14, 24 + sway, 12, 8), border_radius=2)
    for i in range(3):
        pygame.draw.line(s, (60, 60, 60),
                         (15, 26 + i * 2 + sway), (25, 26 + i * 2 + sway), 1)
    pygame.draw.line(s, (15, 15, 15), (18, 23 + sway), (18, 33 + sway), 1)
    pygame.draw.line(s, (15, 15, 15), (22, 23 + sway), (22, 33 + sway), 1)
    return s


def make_rebel_sprite():
    s = _surface()
    pygame.draw.circle(s, (230, 190, 150), (20, 18), 10)
    pygame.draw.circle(s, (60, 30, 20), (20, 18), 10, 1)
    pygame.draw.arc(s, (210, 90, 55), (6, 4, 28, 28), 0.2, 3.0, 4)
    pygame.draw.circle(s, (20, 20, 20), (16, 16), 2)
    pygame.draw.circle(s, (20, 20, 20), (24, 16), 2)
    pygame.draw.arc(s, (120, 40, 40), (15, 20, 10, 6), 3.5, 6.0, 1)
    pygame.draw.rect(s, (210, 110, 40), (12, 28, 16, 10), border_radius=3)
    pygame.draw.rect(s, (150, 70, 20), (12, 28, 16, 10), 1, border_radius=3)
    pygame.draw.rect(s, (40, 40, 40), (26, 30, 10, 4))
    pygame.draw.rect(s, (80, 80, 80), (30, 29, 3, 6))
    return s


def make_vader_sprite(pulse=0):
    s = _surface()
    pygame.draw.ellipse(s, (35, 15, 45), (4, 2, 32, 36))
    pygame.draw.ellipse(s, (30, 15, 40), (7, 3, 26, 18))
    pygame.draw.ellipse(s, (50, 30, 60), (11, 12, 18, 20))
    pygame.draw.ellipse(s, (200, 40, 40), (12, 16, 7, 5))
    pygame.draw.ellipse(s, (200, 40, 40), (21, 16, 7, 5))
    pygame.draw.circle(s, (255, 180, 180), (14, 17), 1)
    pygame.draw.circle(s, (255, 180, 180), (23, 17), 1)
    pygame.draw.polygon(s, (20, 10, 25),
                        [(16, 26), (24, 26), (22, 32), (18, 32)])
    for x in (18, 20, 22):
        pygame.draw.line(s, (60, 30, 70), (x, 26), (x, 32), 1)
    glow = 20 + pulse * 4
    pygame.draw.rect(s, (30, 30, 30), (34, 22, 3, 10))
    pygame.draw.rect(s, (255, 40, 40), (35, 2, 2, 20))
    glow_surf = pygame.Surface((8, 26), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (255, 60, 60, glow), (0, 0, 8, 26))
    s.blit(glow_surf, (32, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.rect(s, (255, 200, 200), (35, 2, 1, 20))
    return s


def make_friend_sprite():
    s = _surface()
    pygame.draw.ellipse(s, (225, 235, 255), (4, 3, 32, 34))
    pygame.draw.ellipse(s, (40, 60, 120), (4, 3, 32, 34), 2)
    pygame.draw.ellipse(s, (100, 160, 235), (4, 3, 8, 34))
    pygame.draw.ellipse(s, (100, 160, 235), (28, 3, 8, 34))
    pygame.draw.ellipse(s, (10, 10, 30), (9, 14, 9, 7))
    pygame.draw.ellipse(s, (10, 10, 30), (22, 14, 9, 7))
    pygame.draw.circle(s, (120, 180, 255), (12, 16), 1)
    pygame.draw.circle(s, (120, 180, 255), (25, 16), 1)
    pygame.draw.rect(s, (20, 20, 40), (14, 24, 12, 8), border_radius=2)
    for i in range(3):
        pygame.draw.line(s, (80, 100, 180),
                         (15, 26 + i * 2), (25, 26 + i * 2), 1)
    pygame.draw.rect(s, (0, 220, 100), (30, 30, 8, 3))
    pygame.draw.rect(s, (0, 220, 100), (32, 28, 3, 8))
    return s


def make_exit_sprite(frame=0):
    s = _surface()
    radius = 14 + (frame % 4)
    alpha  = 60 + (frame % 4) * 40
    glow = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(glow, (0, 255, 120, alpha), (20, 20), 18)
    s.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(s, (0, 80, 40), (20, 20), radius)
    pygame.draw.circle(s, (0, 240, 120), (20, 20), radius, 2)
    pygame.draw.polygon(s, (0, 240, 120), [(20, 8), (30, 22), (10, 22)])
    pygame.draw.rect(s, (0, 240, 120), (16, 22, 8, 10))
    return s


def make_wall_surface(theme):
    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
    s.fill(theme["wall"])
    pygame.draw.rect(s, theme["wall_hi"], (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 1)
    pygame.draw.line(s, theme["wall_lo"], (0, TILE_SIZE // 2),
                     (TILE_SIZE, TILE_SIZE // 2), 1)
    pygame.draw.circle(s, theme["wall_hi"], (TILE_SIZE // 2, TILE_SIZE // 2), 3, 1)
    for cx, cy in [(8, 8), (32, 8), (8, 32), (32, 32)]:
        pygame.draw.circle(s, theme["bolt"], (cx, cy), 2)
    return s


def make_floor_surface(theme):
    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
    s.fill(theme["floor"])
    pygame.draw.rect(s, theme["floor_edge"], (0, 0, TILE_SIZE, TILE_SIZE), 1)
    pygame.draw.circle(s, theme["floor_dot"], (TILE_SIZE // 2, TILE_SIZE // 2), 1)
    return s