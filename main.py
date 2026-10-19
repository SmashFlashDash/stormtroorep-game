"""main.py — Star Wars: Stormtrooper Maze v5 (pygame-ce)."""
import pygame
import pygame.freetype
import random
import sys
from collections import deque

from assets_gen import (
    TILE_SIZE, THEMES, generate_maze,
    make_stormtrooper_sprite, make_rebel_sprite, make_vader_sprite,
    make_friend_sprite, make_exit_sprite,
    make_wall_surface, make_floor_surface,
)
from audio import SoundManager, SAMPLE_RATE

# ==================== НАСТРОЙКИ ====================
MAZE_COLS = 21
MAZE_ROWS = 17
HUD_HEIGHT = 64
SCREEN_WIDTH  = MAZE_COLS * TILE_SIZE
SCREEN_HEIGHT = MAZE_ROWS * TILE_SIZE + HUD_HEIGHT
FPS = 60

VADER_SPEED        = 14
EXTRA_PASSAGES     = 12
RESTARTS_PER_THEME = 3


# ==================== СУЩНОСТИ ====================
class Entity:
    __slots__ = ("x", "y", "alive")
    def __init__(self, x, y):
        self.x, self.y, self.alive = x, y, True


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
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16,
                              channels=2, buffer=512)
        except pygame.error as e:
            print("⚠️  Аудио недоступно:", e)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Star Wars: Stormtrooper Maze (pygame-ce) v5")
        self.clock = pygame.time.Clock()

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

        self.sounds = SoundManager()

        self.tick = 0
        self.restart_count = 0
        self.theme_index = 0
        self._apply_theme(0)
        self.reset()

    def _apply_theme(self, idx):
        theme = THEMES[idx % len(THEMES)]
        self.theme = theme
        self.wall_surface  = make_wall_surface(theme)
        self.floor_surface = make_floor_surface(theme)

    def reset(self):
        new_idx = (self.restart_count // RESTARTS_PER_THEME) % len(THEMES)
        if new_idx != self.theme_index:
            self.theme_index = new_idx
            self._apply_theme(self.theme_index)

        self.maze = generate_maze(MAZE_COLS, MAZE_ROWS, EXTRA_PASSAGES)
        self.rows, self.cols = len(self.maze), len(self.maze[0])

        free = [(x, y) for y in range(self.rows) for x in range(self.cols)
                if self.maze[y][x] == 0]
        random.shuffle(free)

        px, py = free.pop()
        self.player = Stormtrooper(px, py)

        free.sort(key=lambda p: -(abs(p[0] - px) + abs(p[1] - py)))
        ex, ey = free.pop(0)
        self.exit = Exit(ex, ey)

        self.rebels, self.friends = [], []
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
        self._bg_cache = self._build_bg()

        self.sounds.resume_music()

    def _build_bg(self):
        bg = pygame.Surface((SCREEN_WIDTH, self.rows * TILE_SIZE))
        for y in range(self.rows):
            for x in range(self.cols):
                surf = self.wall_surface if self.maze[y][x] == 1 else self.floor_surface
                bg.blit(surf, (x * TILE_SIZE, y * TILE_SIZE))
        return bg.convert()

    def is_wall(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.maze[y][x] == 1
        return True

    def try_move(self, dx, dy):
        nx, ny = self.player.x + dx, self.player.y + dy
        if not self.is_wall(nx, ny):
            self.player.x, self.player.y = nx, ny
            self.player.walk_frame = (self.player.walk_frame + 1) % 4
            self.player.moving = True
            if random.random() < 0.5:
                self.sounds.play("step")
            return True
        return False

    # ---------- Логика ----------
    def update(self):
        self.tick += 1
        self.sounds.update_music()

        # Обработка отложенных звуков (см. SoundManager.play_fall)
        for _ in pygame.event.get(pygame.USEREVENT + 1):
            self.sounds.play("breath")
        for _ in pygame.event.get(pygame.USEREVENT + 2):
            self.sounds.play("laugh")
        for _ in pygame.event.get(pygame.USEREVENT + 3):
            if self.sounds.event_fall:
                try:
                    self.sounds.event_fall.play()
                except Exception:
                    pass

        if self.state != "playing":
            return

        # Повстанцы
        for r in list(self.rebels):
            if r.alive and (r.x, r.y) == (self.player.x, self.player.y):
                r.alive = False
                self.rebels.remove(r)
                self.player.score += 100
                self.sounds.play("blaster")

                # 🎉 Все повстанцы уничтожены — играем rebels.mp3
                if not self.rebels:
                    self.sounds.play_rebels()

        # Друзья
        for f in list(self.friends):
            if (f.x, f.y) == (self.player.x, self.player.y):
                self.friends.remove(f)
                self.player.friends += 1
                self.player.score += 50
                self.player.hp = min(5, self.player.hp + 1)
                self.sounds.play("pickup")

        # Столкновение с Вейдером
        if self.vader and (self.vader.x, self.vader.y) == (self.player.x, self.player.y):
            self.player.hp -= 2
            self.player.score = max(0, self.player.score - 50)
            self.sounds.play("swing")
            for _ in range(3):
                for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    if not self.is_wall(self.player.x + ddx, self.player.y + ddy):
                        self.player.x += ddx
                        self.player.y += ddy
                        break
            if self.player.hp <= 0:
                self.state = "lose"
                self.message = "Дарт Вейдер победил тебя..."
                self.sounds.play_fall()

        # Движение Вейдера
        if self.vader:
            self.vader.move_counter += 1
            if self.vader.move_counter >= VADER_SPEED:
                self.vader.move_counter = 0
                self._move_vader()

        # Выход
        if (self.exit.x, self.exit.y) == (self.player.x, self.player.y):
            self.state = "win"
            self.message = f"ПОБЕДА! Счёт: {self.player.score}"
            self.sounds.play_win()

    def _move_vader(self):
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
        self.screen.blit(self._bg_cache, (0, 0))

        self.screen.blit(self.exit_frames[(self.tick // 6) % 4],
                         (self.exit.x * TILE_SIZE, self.exit.y * TILE_SIZE))

        for f in self.friends:
            self.screen.blit(self.friend_sprite,
                             (f.x * TILE_SIZE, f.y * TILE_SIZE))

        for r in self.rebels:
            self.screen.blit(self.rebel_sprite,
                             (r.x * TILE_SIZE, r.y * TILE_SIZE))

        if self.vader:
            self.vader_pulse = (self.vader_pulse + 1) % 8
            self.screen.blit(self.vader_frames[self.vader_pulse],
                             (self.vader.x * TILE_SIZE, self.vader.y * TILE_SIZE))

        frame_idx = self.player.walk_frame if self.player.moving else 0
        self.screen.blit(self.storm_frames[frame_idx],
                         (self.player.x * TILE_SIZE, self.player.y * TILE_SIZE))
        self.player.moving = False

        self._draw_hud()
        if self.state != "playing":
            self._draw_game_over()

    def _draw_hud(self):
        y0 = self.rows * TILE_SIZE
        pygame.draw.rect(self.screen, (14, 14, 24),
                         (0, y0, SCREEN_WIDTH, HUD_HEIGHT))
        pygame.draw.line(self.screen, (255, 220, 0),
                         (0, y0), (SCREEN_WIDTH, y0), 2)

        hearts = "♥" * max(0, self.player.hp)
        items = [
            (f"HP: {hearts}", (255, 255, 255)),
            (f"Счёт: {self.player.score}", (255, 220, 0)),
            (f"Друзья: {self.player.friends}", (100, 160, 235)),
            (f"Врагов: {len(self.rebels)}", (210, 90, 55)),
        ]
        for i, (text, color) in enumerate(items):
            self._text(text, color, (15 + i * 165, y0 + 12))

        self._text(f"Карта: {self.theme['name']}", (200, 200, 220),
                   (15, y0 + 38), small=True)
        self._text(f"Рестартов: {self.restart_count}", (200, 200, 220),
                   (200, y0 + 38), small=True)
        self._text("Стрелки/WASD | R — рестарт | ESC — выход",
                   (150, 150, 170), (SCREEN_WIDTH - 380, y0 + 12), small=True)

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        color = (0, 240, 120) if self.state == "win" else (230, 60, 60)
        self._text(self.message, color,
                   (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40),
                   big=True, center=True)
        self._text("Нажми R для новой игры", (255, 255, 255),
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
                        self.sounds.stop_all()      # ← ✅ стоп win/fall/музыки
                        self.restart_count += 1
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