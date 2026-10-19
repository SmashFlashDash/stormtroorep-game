"""
Star Wars: Stormtrooper Maze — версия для pygame-ce
Установка:  pip install pygame-ce
Запуск:     python main.py
"""
import pygame
import pygame.freetype          # ✅ импорт на уровне модуля (фикс UnboundLocalError)
import random
import sys
import math
from collections import deque

# ==================== НАСТРОЙКИ ====================
TILE_SIZE = 40
MAZE_COLS = 21
MAZE_ROWS = 17
HUD_HEIGHT = 64
SCREEN_WIDTH = MAZE_COLS * TILE_SIZE
SCREEN_HEIGHT = MAZE_ROWS * TILE_SIZE + HUD_HEIGHT
FPS = 60

# Палитра
BLACK        = (0, 0, 0)
WHITE        = (255, 255, 255)
DARK_BG      = (10, 10, 18)
FLOOR_COLOR  = (22, 22, 34)
FLOOR_EDGE   = (30, 30, 46)
WALL_COLOR   = (58, 58, 82)
WALL_HI      = (88, 88, 120)
WALL_LO      = (38, 38, 55)
STORM_COLOR  = (235, 235, 245)
STORM_SHADOW = (185, 185, 200)
REBEL_COLOR  = (210, 90, 55)
VADER_COLOR  = (35, 15, 45)
FRIEND_COLOR = (100, 160, 235)
EXIT_COLOR   = (0, 240, 120)
YELLOW       = (255, 220, 0)
HUD_BG       = (14, 14, 24)
HUD_LINE     = (60, 60, 90)
RED          = (230, 60, 60)


# ==================== ГЕНЕРАЦИЯ ЛАБИРИНТА ====================
def generate_maze(cols, rows):
    """Recursive backtracker. Размеры приводятся к нечётным."""
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
    return maze


# ==================== ПРОЦЕДУРНЫЕ СПРАЙТЫ ====================
def _surface(size=TILE_SIZE):
    return pygame.Surface((size, size), pygame.SRCALPHA)


def make_stormtrooper_sprite(frame=0):
    """Штурмовик. frame: 0..3 — для анимации ходьбы (покачивание)."""
    s = _surface()
    sway = [0, -1, 0, 1][frame % 4]
    # Шлем
    pygame.draw.ellipse(s, STORM_COLOR, (4, 3 + sway, 32, 34))
    pygame.draw.ellipse(s, (30, 30, 30), (4, 3 + sway, 32, 34), 2)
    # Боковые тени
    pygame.draw.ellipse(s, STORM_SHADOW, (4, 3 + sway, 8, 34))
    pygame.draw.ellipse(s, STORM_SHADOW, (28, 3 + sway, 8, 34))
    # Визоры
    pygame.draw.ellipse(s, (10, 10, 10), (9, 14 + sway, 9, 7))
    pygame.draw.ellipse(s, (10, 10, 10), (22, 14 + sway, 9, 7))
    pygame.draw.circle(s, (200, 200, 220), (12, 16 + sway), 1)
    pygame.draw.circle(s, (200, 200, 220), (25, 16 + sway), 1)
    # Респиратор
    pygame.draw.rect(s, (20, 20, 20), (14, 24 + sway, 12, 8), border_radius=2)
    for i in range(3):
        pygame.draw.line(s, (60, 60, 60),
                         (15, 26 + i * 2 + sway),
                         (25, 26 + i * 2 + sway), 1)
    pygame.draw.line(s, (15, 15, 15), (18, 23 + sway), (18, 33 + sway), 1)
    pygame.draw.line(s, (15, 15, 15), (22, 23 + sway), (22, 33 + sway), 1)
    return s


def make_rebel_sprite():
    s = _surface()
    # Лицо
    pygame.draw.circle(s, (230, 190, 150), (20, 18), 10)
    pygame.draw.circle(s, (60, 30, 20), (20, 18), 10, 1)
    # Оранжевый шлем
    pygame.draw.arc(s, REBEL_COLOR, (6, 4, 28, 28), 0.2, 3.0, 4)
    # Глаза
    pygame.draw.circle(s, (20, 20, 20), (16, 16), 2)
    pygame.draw.circle(s, (20, 20, 20), (24, 16), 2)
    # Улыбка
    pygame.draw.arc(s, (120, 40, 40), (15, 20, 10, 6), 3.5, 6.0, 1)
    # Тело
    pygame.draw.rect(s, (210, 110, 40), (12, 28, 16, 10), border_radius=3)
    pygame.draw.rect(s, (150, 70, 20), (12, 28, 16, 10), 1, border_radius=3)
    # Бластер
    pygame.draw.rect(s, (40, 40, 40), (26, 30, 10, 4))
    pygame.draw.rect(s, (80, 80, 80), (30, 29, 3, 6))
    return s


def make_vader_sprite(pulse=0):
    """Дарт Вейдер. pulse — для мерцания меча (0..7)."""
    s = _surface()
    # Плащ
    pygame.draw.ellipse(s, VADER_COLOR, (4, 2, 32, 36))
    # Купол шлема
    pygame.draw.ellipse(s, (30, 15, 40), (7, 3, 26, 18))
    # Маска
    pygame.draw.ellipse(s, (50, 30, 60), (11, 12, 18, 20))
    # Глаза
    pygame.draw.ellipse(s, (200, 40, 40), (12, 16, 7, 5))
    pygame.draw.ellipse(s, (200, 40, 40), (21, 16, 7, 5))
    pygame.draw.circle(s, (255, 180, 180), (14, 17), 1)
    pygame.draw.circle(s, (255, 180, 180), (23, 17), 1)
    # Респиратор
    pygame.draw.polygon(s, (20, 10, 25),
                        [(16, 26), (24, 26), (22, 32), (18, 32)])
    for x in (18, 20, 22):
        pygame.draw.line(s, (60, 30, 70), (x, 26), (x, 32), 1)
    # Световой меч с пульсацией
    glow = 20 + pulse * 4
    pygame.draw.rect(s, (30, 30, 30), (34, 22, 3, 10))          # рукоять
    pygame.draw.rect(s, (255, 40, 40), (35, 2, 2, 20))          # клинок
    glow_surf = pygame.Surface((8, 26), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (255, 60, 60, glow), (0, 0, 8, 26))
    s.blit(glow_surf, (32, 0), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.rect(s, (255, 200, 200), (35, 2, 1, 20))        # блик
    return s


def make_friend_sprite():
    s = _surface()
    pygame.draw.ellipse(s, (225, 235, 255), (4, 3, 32, 34))
    pygame.draw.ellipse(s, (40, 60, 120), (4, 3, 32, 34), 2)
    pygame.draw.ellipse(s, FRIEND_COLOR, (4, 3, 8, 34))
    pygame.draw.ellipse(s, FRIEND_COLOR, (28, 3, 8, 34))
    pygame.draw.ellipse(s, (10, 10, 30), (9, 14, 9, 7))
    pygame.draw.ellipse(s, (10, 10, 30), (22, 14, 9, 7))
    pygame.draw.circle(s, (120, 180, 255), (12, 16), 1)
    pygame.draw.circle(s, (120, 180, 255), (25, 16), 1)
    pygame.draw.rect(s, (20, 20, 40), (14, 24, 12, 8), border_radius=2)
    for i in range(3):
        pygame.draw.line(s, (80, 100, 180),
                         (15, 26 + i * 2), (25, 26 + i * 2), 1)
    # Значок "+"
    pygame.draw.rect(s, (0, 220, 100), (30, 30, 8, 3))
    pygame.draw.rect(s, (0, 220, 100), (32, 28, 3, 8))
    return s


def make_exit_sprite(frame=0):
    s = _surface()
    radius = 14 + (frame % 4)
    alpha  = 60 + (frame % 4) * 40
    # Внешнее свечение
    glow = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(glow, (0, 255, 120, alpha), (20, 20), 18)
    s.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Кольца
    pygame.draw.circle(s, (0, 80, 40), (20, 20), radius)
    pygame.draw.circle(s, EXIT_COLOR, (20, 20), radius, 2)
    # Стрелка вверх
    pygame.draw.polygon(s, EXIT_COLOR, [(20, 8), (30, 22), (10, 22)])
    pygame.draw.rect(s, EXIT_COLOR, (16, 22, 8, 10))
    return s


def make_wall_surface():
    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
    s.fill(WALL_COLOR)
    pygame.draw.rect(s, WALL_HI, (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 1)
    pygame.draw.line(s, WALL_LO, (0, TILE_SIZE // 2),
                     (TILE_SIZE, TILE_SIZE // 2), 1)
    pygame.draw.circle(s, WALL_HI, (TILE_SIZE // 2, TILE_SIZE // 2), 3, 1)
    for cx, cy in [(8, 8), (32, 8), (8, 32), (32, 32)]:
        pygame.draw.circle(s, (70, 70, 95), (cx, cy), 2)
    return s


def make_floor_surface():
    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
    s.fill(FLOOR_COLOR)
    pygame.draw.rect(s, FLOOR_EDGE, (0, 0, TILE_SIZE, TILE_SIZE), 1)
    pygame.draw.circle(s, (26, 26, 40), (TILE_SIZE // 2, TILE_SIZE // 2), 1)
    return s


# ==================== ЗВУКИ (процедурные beep) ====================
def make_beep(freq=440, duration_ms=80, volume=0.25):
    """Генерирует короткий beep без внешних файлов."""
    if not pygame.mixer.get_init():
        return None
    try:
        sample_rate = pygame.mixer.get_init()[0]
        n_samples = int(sample_rate * duration_ms / 1000)
        buf = bytearray()
        for i in range(n_samples):
            env = 1.0 - i / n_samples
            val = int(127 + 100 * env *
                      math.sin(2 * math.pi * freq * i / sample_rate))
            val = max(0, min(255, val))
            buf.append(val)
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception:
        return None


# ==================== КЛАССЫ ====================
class Entity:
    __slots__ = ("x", "y", "alive")
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True


class Stormtrooper(Entity):
    __slots__ = ("hp", "score", "friends", "walk_frame", "moving")
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 5
        self.score = 0
        self.friends = 0
        self.walk_frame = 0
        self.moving = False


class Rebel(Entity):
    __slots__ = ()


class Vader(Entity):
    __slots__ = ("move_counter",)
    def __init__(self, x, y):
        super().__init__(x, y)
        self.move_counter = 0


class Friend(Entity):
    __slots__ = ()


class Exit(Entity):
    __slots__ = ()


# ==================== ИГРА ====================
class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=256)
        except pygame.error:
            pass  # без звука тоже работает

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Star Wars: Stormtrooper Maze (pygame-ce)")
        self.clock = pygame.time.Clock()

        # Шрифты через freetype
        try:
            pygame.freetype.init()
            self.font        = pygame.freetype.SysFont("Arial", 18, bold=True)
            self.font_small  = pygame.freetype.SysFont("Arial", 14, bold=True)
            self.big_font    = pygame.freetype.SysFont("Arial", 46, bold=True)
            self.use_freetype = True
        except Exception:
            self.font        = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_small  = pygame.font.SysFont("Arial", 14, bold=True)
            self.big_font    = pygame.font.SysFont("Arial", 46, bold=True)
            self.use_freetype = False

        # Спрайты
        self.storm_frames  = [make_stormtrooper_sprite(i) for i in range(4)]
        self.rebel_sprite  = make_rebel_sprite()
        self.vader_frames  = [make_vader_sprite(i) for i in range(8)]
        self.friend_sprite = make_friend_sprite()
        self.exit_frames   = [make_exit_sprite(i) for i in range(4)]
        self.wall_surface  = make_wall_surface()
        self.floor_surface = make_floor_surface()

        # Звуки
        self.snd_step   = make_beep(660, 40, 0.10)
        self.snd_pickup = make_beep(880, 80, 0.30)
        self.snd_hit    = make_beep(180, 150, 0.35)
        self.snd_vader  = make_beep(90, 250, 0.40)
        self.snd_win    = make_beep(1046, 300, 0.35)

        self.tick = 0
        self.reset()

    def reset(self):
        self.maze = generate_maze(MAZE_COLS, MAZE_ROWS)
        self.rows = len(self.maze)
        self.cols = len(self.maze[0])

        free = [(x, y) for y in range(self.rows) for x in range(self.cols)
                if self.maze[y][x] == 0]
        random.shuffle(free)

        # Игрок
        px, py = free.pop()
        self.player = Stormtrooper(px, py)

        # Выход — подальше от старта
        free.sort(key=lambda p: -(abs(p[0] - px) + abs(p[1] - py)))
        ex, ey = free.pop(0)
        self.exit = Exit(ex, ey)

        self.rebels = []
        self.friends = []
        for _ in range(min(6, len(free))):
            x, y = free.pop()
            self.rebels.append(Rebel(x, y))
        for _ in range(min(4, len(free))):
            x, y = free.pop()
            self.friends.append(Friend(x, y))

        self.vader = None
        if free:
            free.sort(key=lambda p: -(abs(p[0] - px) + abs(p[1] - py)))
            vx, vy = free.pop(0)
            self.vader = Vader(vx, vy)

        self.state = "playing"
        self.message = ""
        self.vader_pulse = 0

        # Кэш фона
        self._bg_cache = self._build_bg()

    def _build_bg(self):
        bg = pygame.Surface((SCREEN_WIDTH, self.rows * TILE_SIZE))
        for y in range(self.rows):
            for x in range(self.cols):
                surf = self.wall_surface if self.maze[y][x] == 1 else self.floor_surface
                bg.blit(surf, (x * TILE_SIZE, y * TILE_SIZE))
        return bg.convert()

    # ---------- Ввод ----------
    def is_wall(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.maze[y][x] == 1
        return True

    def try_move(self, dx, dy):
        nx = self.player.x + dx
        ny = self.player.y + dy
        if not self.is_wall(nx, ny):
            self.player.x = nx
            self.player.y = ny
            self.player.walk_frame = (self.player.walk_frame + 1) % 4
            self.player.moving = True
            return True
        return False

    # ---------- Логика ----------
    def update(self):
        self.tick += 1
        if self.state != "playing":
            return

        # Столкновение с повстанцами
        for r in list(self.rebels):
            if r.alive and (r.x, r.y) == (self.player.x, self.player.y):
                r.alive = False
                self.rebels.remove(r)
                self.player.score += 100
                self._play(self.snd_hit)

        # Друзья
        for f in list(self.friends):
            if (f.x, f.y) == (self.player.x, self.player.y):
                self.friends.remove(f)
                self.player.friends += 1
                self.player.score += 50
                self.player.hp = min(5, self.player.hp + 1)
                self._play(self.snd_pickup)

        # Вейдер
        if self.vader and (self.vader.x, self.vader.y) == (self.player.x, self.player.y):
            self.player.hp -= 2
            self.player.score = max(0, self.player.score - 50)
            self._play(self.snd_vader)
            # Отброс назад на 3 клетки
            for _ in range(3):
                for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    if not self.is_wall(self.player.x + ddx, self.player.y + ddy):
                        self.player.x += ddx
                        self.player.y += ddy
                        break
            if self.player.hp <= 0:
                self.state = "lose"
                self.message = "Дарт Вейдер победил тебя..."

        # Движение Вейдера (BFS, раз в 8 кадров)
        if self.vader:
            self.vader.move_counter += 1
            if self.vader.move_counter >= 8:
                self.vader.move_counter = 0
                self._move_vader()

        # Проверка выхода
        if (self.exit.x, self.exit.y) == (self.player.x, self.player.y):
            self.state = "win"
            self.message = f"ПОБЕДА! Счёт: {self.player.score}"
            self._play(self.snd_win)

    def _play(self, snd):
        if snd is not None:
            try:
                snd.play()
            except Exception:
                pass

    def _move_vader(self):
        """BFS-преследование."""
        start = (self.vader.x, self.vader.y)
        goal = (self.player.x, self.player.y)
        if start == goal:
            return
        queue = deque([start])
        parents = {start: None}
        found = False

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == goal:
                found = True
                break
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = cx + dx, cy + dy
                if not self.is_wall(nx, ny) and (nx, ny) not in parents:
                    parents[(nx, ny)] = (cx, cy)
                    queue.append((nx, ny))

        if found:
            path = []
            cur = goal
            while parents[cur] is not None:
                path.append(cur)
                cur = parents[cur]
            path.reverse()
            if path:
                self.vader.x, self.vader.y = path[0]

    # ---------- Отрисовка ----------
    def draw(self):
        # Фон-лабиринт из кэша
        self.screen.blit(self._bg_cache, (0, 0))

        # Выход
        self.screen.blit(self.exit_frames[(self.tick // 6) % 4],
                         (self.exit.x * TILE_SIZE, self.exit.y * TILE_SIZE))

        # Друзья
        for f in self.friends:
            self.screen.blit(self.friend_sprite,
                             (f.x * TILE_SIZE, f.y * TILE_SIZE))

        # Повстанцы
        for r in self.rebels:
            self.screen.blit(self.rebel_sprite,
                             (r.x * TILE_SIZE, r.y * TILE_SIZE))

        # Вейдер
        if self.vader:
            self.vader_pulse = (self.vader_pulse + 1) % 8
            self.screen.blit(self.vader_frames[self.vader_pulse],
                             (self.vader.x * TILE_SIZE, self.vader.y * TILE_SIZE))

        # Игрок
        frame_idx = self.player.walk_frame if self.player.moving else 0
        self.screen.blit(self.storm_frames[frame_idx],
                         (self.player.x * TILE_SIZE, self.player.y * TILE_SIZE))
        self.player.moving = False

        # HUD
        self._draw_hud()
        if self.state != "playing":
            self._draw_game_over()

    def _draw_hud(self):
        y0 = self.rows * TILE_SIZE
        pygame.draw.rect(self.screen, HUD_BG, (0, y0, SCREEN_WIDTH, HUD_HEIGHT))
        pygame.draw.line(self.screen, YELLOW, (0, y0), (SCREEN_WIDTH, y0), 2)

        hearts = "♥" * max(0, self.player.hp)
        items = [
            (f"HP: {hearts}", WHITE),
            (f"Счёт: {self.player.score}", YELLOW),
            (f"Друзья: {self.player.friends}", FRIEND_COLOR),
            (f"Врагов: {len(self.rebels)}", REBEL_COLOR),
        ]
        for i, (text, color) in enumerate(items):
            self._text(text, color, (15 + i * 190, y0 + 18))

        self._text("Стрелки/WASD — движение | R — рестарт | ESC — выход",
                   (150, 150, 170), (SCREEN_WIDTH - 420, y0 + 18), small=True)

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        color = EXIT_COLOR if self.state == "win" else RED
        self._text(self.message, color,
                   (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40),
                   big=True, center=True)
        self._text("Нажми R для новой игры", WHITE,
                   (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30),
                   center=True)

    def _text(self, text, color, pos, big=False, small=False, center=False):
        if self.use_freetype:
            font = self.big_font if big else (self.font_small if small else self.font)
            surf, rect = font.render(text, color)
            if center:
                rect.center = pos
                self.screen.blit(surf, rect)
            else:
                self.screen.blit(surf, pos)
        else:
            font = self.big_font if big else (self.font_small if small else self.font)
            surf = font.render(text, True, color)
            rect = surf.get_rect()
            if center:
                rect.center = pos
            else:
                rect.topleft = pos
            self.screen.blit(surf, rect)

    # ---------- Главный цикл ----------
    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif self.state == "playing":
                        if event.key in (pygame.K_LEFT, pygame.K_a):
                            self.try_move(-1, 0)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.try_move(1, 0)
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            self.try_move(0, -1)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.try_move(0, 1)

            self.update()
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    Game().run()