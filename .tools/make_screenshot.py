"""
make_screenshot.py — снимок экрана игры для README.
Запусти из корня проекта: python .tools/make_screenshot.py
Создаст .stems/screenshot.png (окно не открывается — рендер в скрытом режиме).
"""
import os
import sys

# Скрипт лежит в .tools/, а игра — в корне проекта: правим путь и рабочую папку,
# чтобы импорты и папки sounds/ + sounds_event/ находились как при обычном запуске.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

# Скрытый (headless) рендер: не открываем окно и не требуем аудиоустройство
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from starwars import Game  # noqa: E402

OUT_DIR = ".stems"
OUT_FILE = os.path.join(OUT_DIR, "screenshot.png")
TICKS_BEFORE_SHOT = 30


def main():
    game = Game()

    # Прокручиваем несколько кадров, чтобы ожили анимации (Вейдер, выход)
    for _ in range(TICKS_BEFORE_SHOT):
        game.update()

    game.draw()
    pygame.display.flip()

    os.makedirs(OUT_DIR, exist_ok=True)
    pygame.image.save(game.screen, OUT_FILE)
    print(f"✅ Скриншот сохранён: {OUT_FILE} "
          f"({game.screen.get_width()}x{game.screen.get_height()})")

    pygame.quit()


if __name__ == "__main__":
    main()
