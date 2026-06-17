# config.py
import pygame
import os
pygame.init()
# 屏幕
SCREEN_WIDTH = 1380
SCREEN_HEIGHT = 900
FPS = 60

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_BLUE = (20, 20, 50)
LIGHT_BLUE = (180, 180, 255)
LIGHT_RED = (255, 180, 180)
ORANGE = (255, 165, 0)

# 卡牌尺寸
CARD_WIDTH = 100
CARD_HEIGHT = 140
HAND_MAX = 10

# 字体
_font_cache = {}

def get_font(size):
    if size in _font_cache:
        return _font_cache[size]
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "assets/font.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = pygame.font.Font(path, size)
                _font_cache[size] = font
                return font
            except Exception:
                continue
    font = pygame.font.Font(None, size)
    _font_cache[size] = font
    return font

# 字体常量
FONT_SMALL = get_font(18)
FONT_MID = get_font(28)
FONT_BIG = get_font(50)

# 资源路径
ASSETS_DIR = "assets"
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")
IMAGE_DIR = os.path.join(ASSETS_DIR, "images")