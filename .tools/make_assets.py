"""
make_assets.py — генерация PNG-спрайтов для игры Star Wars Maze.
Запусти один раз: python make_assets.py
Создаст папку assets/ с файлами персонажей.

ВНИМАНИЕ: assets/stormtrooper.png — художественный ассет, его игра
загружает как спрайт игрока. Здесь он НЕ перезаписывается: процедурная
версия сохраняется отдельно в stormtrooper_proc.png.
"""
import pygame
import os

TILE = 40
OUT_DIR = "assets"
os.makedirs(OUT_DIR, exist_ok=True)

pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)  # скрытое окно для рендера


def new_surface():
    """Прозрачный холст TILE x TILE."""
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    return s


# ==================== ШТУРМОВИК (процедурная версия) ====================
def make_stormtrooper_proc():
    s = new_surface()
    # Шлем (белый овал)
    pygame.draw.ellipse(s, (240, 240, 240), (4, 3, 32, 34))
    pygame.draw.ellipse(s, (30, 30, 30), (4, 3, 32, 34), 2)
    # Тени по бокам
    pygame.draw.ellipse(s, (200, 200, 210), (4, 3, 8, 34))
    pygame.draw.ellipse(s, (200, 200, 210), (28, 3, 8, 34))
    # Глаза (чёрные "очки")
    pygame.draw.ellipse(s, (10, 10, 10), (9, 14, 9, 7))
    pygame.draw.ellipse(s, (10, 10, 10), (22, 14, 9, 7))
    # Блик в глазах
    pygame.draw.circle(s, (180, 180, 200), (12, 16), 1)
    pygame.draw.circle(s, (180, 180, 200), (25, 16), 1)
    # Маска-респиратор (чёрная решётка)
    pygame.draw.rect(s, (20, 20, 20), (14, 24, 12, 8), border_radius=2)
    for i in range(3):
        pygame.draw.line(s, (60, 60, 60),
                         (15, 26 + i * 2), (25, 26 + i * 2), 1)
    # "Рот" — вертикальные линии
    pygame.draw.line(s, (15, 15, 15), (18, 23), (18, 33), 1)
    pygame.draw.line(s, (15, 15, 15), (22, 23), (22, 33), 1)
    pygame.image.save(s, os.path.join(OUT_DIR, "stormtrooper_proc.png"))
    return s


# ==================== ПОВСТАНЕЦ ====================
def make_rebel():
    s = new_surface()
    # Лицо
    pygame.draw.circle(s, (230, 190, 150), (20, 18), 10)
    pygame.draw.circle(s, (60, 30, 20), (20, 18), 10, 1)
    # Оранжевый шлем-жилет повстанца
    pygame.draw.arc(s, (200, 90, 40), (6, 4, 28, 28), 0.2, 3.0, 4)
    # Глаза
    pygame.draw.circle(s, (20, 20, 20), (16, 16), 2)
    pygame.draw.circle(s, (20, 20, 20), (24, 16), 2)
    # Улыбка (дерзкая)
    pygame.draw.arc(s, (120, 40, 40), (15, 20, 10, 6), 3.5, 6.0, 1)
    # Тело (оранжевый комбинезон)
    pygame.draw.rect(s, (210, 110, 40), (12, 28, 16, 10), border_radius=3)
    pygame.draw.rect(s, (150, 70, 20), (12, 28, 16, 10), 1, border_radius=3)
    # Бластер
    pygame.draw.rect(s, (40, 40, 40), (26, 30, 10, 4))
    pygame.draw.rect(s, (80, 80, 80), (30, 29, 3, 6))
    pygame.image.save(s, os.path.join(OUT_DIR, "rebel.png"))
    return s


# ==================== ДАРТ ВЕЙДЕР ====================
def make_vader():
    s = new_surface()
    # Плащ/шлем (чёрный)
    pygame.draw.ellipse(s, (15, 5, 25), (4, 2, 32, 36))
    # Купол шлема
    pygame.draw.ellipse(s, (30, 15, 40), (7, 3, 26, 18))
    # Маска (более светлая)
    pygame.draw.ellipse(s, (50, 30, 60), (11, 12, 18, 20))
    # Глаза-визоры
    pygame.draw.ellipse(s, (200, 40, 40), (12, 16, 7, 5))
    pygame.draw.ellipse(s, (200, 40, 40), (21, 16, 7, 5))
    # Блик
    pygame.draw.circle(s, (255, 180, 180), (14, 17), 1)
    pygame.draw.circle(s, (255, 180, 180), (23, 17), 1)
    # Респиратор
    pygame.draw.polygon(s, (20, 10, 25),
                        [(16, 26), (24, 26), (22, 32), (18, 32)])
    pygame.draw.line(s, (60, 30, 70), (18, 26), (18, 32), 1)
    pygame.draw.line(s, (60, 30, 70), (20, 26), (20, 32), 1)
    pygame.draw.line(s, (60, 30, 70), (22, 26), (22, 32), 1)
    # Световой меч (красный, справа)
    pygame.draw.rect(s, (30, 30, 30), (34, 22, 3, 10))  # рукоять
    pygame.draw.rect(s, (255, 40, 40), (35, 2, 2, 20))   # клинок
    pygame.draw.rect(s, (255, 150, 150), (35, 2, 1, 20)) # блик
    pygame.image.save(s, os.path.join(OUT_DIR, "vader.png"))
    return s


# ==================== ДРУГ-ШТУРМОВИК ====================
def make_friend():
    s = new_surface()
    # Такой же шлем, но с синим акцентом
    pygame.draw.ellipse(s, (225, 235, 255), (4, 3, 32, 34))
    pygame.draw.ellipse(s, (40, 60, 120), (4, 3, 32, 34), 2)
    # Синие "погоны"
    pygame.draw.ellipse(s, (90, 140, 220), (4, 3, 8, 34))
    pygame.draw.ellipse(s, (90, 140, 220), (28, 3, 8, 34))
    # Глаза
    pygame.draw.ellipse(s, (10, 10, 30), (9, 14, 9, 7))
    pygame.draw.ellipse(s, (10, 10, 30), (22, 14, 9, 7))
    pygame.draw.circle(s, (120, 180, 255), (12, 16), 1)
    pygame.draw.circle(s, (120, 180, 255), (25, 16), 1)
    # Маска
    pygame.draw.rect(s, (20, 20, 40), (14, 24, 12, 8), border_radius=2)
    for i in range(3):
        pygame.draw.line(s, (80, 100, 180),
                         (15, 26 + i * 2), (25, 26 + i * 2), 1)
    # Значок "плюс" (друг/аптечка) в углу
    pygame.draw.rect(s, (0, 200, 100), (30, 30, 8, 3))
    pygame.draw.rect(s, (0, 200, 100), (32, 28, 3, 8))
    pygame.image.save(s, os.path.join(OUT_DIR, "friend.png"))
    return s


# ==================== ВЫХОД ====================
def make_exit():
    s = new_surface()
    # Зелёный портал-стрелка вверх
    pygame.draw.circle(s, (0, 80, 40), (20, 20), 16)
    pygame.draw.circle(s, (0, 255, 120), (20, 20), 16, 2)
    # Стрелка вверх
    pygame.draw.polygon(s, (0, 255, 120), [(20, 8), (30, 22), (10, 22)])
    pygame.draw.rect(s, (0, 255, 120), (16, 22, 8, 10))
    # Пульсация — внутренний круг
    pygame.draw.circle(s, (0, 180, 90), (20, 20), 8, 1)
    pygame.image.save(s, os.path.join(OUT_DIR, "exit.png"))
    return s


# ==================== СТЕНА и ПОЛ ====================
def make_wall():
    s = pygame.Surface((TILE, TILE))
    s.fill((60, 60, 80))
    # Панельки как на Звезде Смерти
    pygame.draw.rect(s, (80, 80, 105), (2, 2, TILE-4, TILE-4), 1)
    pygame.draw.line(s, (45, 45, 60), (0, TILE//2), (TILE, TILE//2), 1)
    pygame.draw.circle(s, (90, 90, 120), (TILE//2, TILE//2), 3, 1)
    for cx, cy in [(8, 8), (32, 8), (8, 32), (32, 32)]:
        pygame.draw.circle(s, (70, 70, 90), (cx, cy), 2)
    pygame.image.save(s, os.path.join(OUT_DIR, "wall.png"))
    return s


def make_floor():
    s = pygame.Surface((TILE, TILE))
    s.fill((20, 20, 30))
    pygame.draw.rect(s, (28, 28, 40), (0, 0, TILE, TILE), 1)
    pygame.draw.circle(s, (25, 25, 38), (TILE//2, TILE//2), 1)
    pygame.image.save(s, os.path.join(OUT_DIR, "floor.png"))
    return s


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    make_stormtrooper_proc()
    make_rebel()
    make_vader()
    make_friend()
    make_exit()
    make_wall()
    make_floor()
    print(f"✅ Готово! Все спрайты в папке '{OUT_DIR}/'")
    print("Файлы:", os.listdir(OUT_DIR))
    pygame.quit()