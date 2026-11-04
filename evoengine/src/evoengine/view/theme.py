from pathlib import Path
import sys
import pygame

# Цвета интерфейса
BG_COLOR = (22, 24, 30) # Фон окон и панели
SURFACE_COLOR = (45, 47, 58) # Фон полей и блоков
SURFACE_DIM_COLOR = (34, 36, 44) # Фон неактивных полей
BORDER_COLOR = (70, 72, 85) # Рамки, разделители, фон шкал
TEXT_COLOR = (230, 230, 230) # Обычный текст
DIM_TEXT_COLOR = (140, 142, 152) # Приглушённый текст
ACCENT_COLOR = (255, 200, 60) # Акцент: заголовки, активные элементы
ACCENT_HOVER_COLOR = (255, 215, 100) # Акцент при наведении
DARK_TEXT_COLOR = (30, 30, 30) # Текст на акцентном фоне
NEGATIVE_COLOR = (220, 80, 80) # Ошибки и критическое здоровье
POSITIVE_COLOR = (60, 200, 90) # Нормальное здоровье

# Цвета карты мира
MAP_BG_COLOR = (30, 30, 30) # Пустая клетка
WALL_COLOR = (80, 80, 80) # Стена
FOOD_COLOR = (0, 255, 0) # Еда
AGENT_COLOR = (255, 255, 255) # Агент

# Шрифты
FONT_TITLE  = 22
FONT_HEADER = 17
FONT_BODY   = 15
FONT_SMALL  = 13

if getattr(sys, 'frozen', False):
    _ASSETS_DIR = Path(sys._MEIPASS) / "assets" / "fonts"  # type: ignore[attr-defined]
else:
    _ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "fonts"

FONT_REGULAR_PATH = _ASSETS_DIR / "JetBrainsMono-Regular.ttf"
FONT_BOLD_PATH    = _ASSETS_DIR / "JetBrainsMono-Bold.ttf"

_font_cache: dict[tuple[int, bool], pygame.font.Font] = {}


def font(size=FONT_BODY, bold=False):
    if not pygame.font.get_init():
        pygame.font.init()

    key = (size, bold)
    cached = _font_cache.get(key)
    if cached is not None:
        return cached

    path = FONT_BOLD_PATH if bold else FONT_REGULAR_PATH
    fnt = pygame.font.Font(str(path), size)

    _font_cache[key] = fnt
    return fnt