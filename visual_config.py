import logging

from pathlib import Path

log = logging.getLogger(__name__)

import pygame

BASE_DIR = Path(__file__).resolve().parent

def load_font(font: str, size: int) -> pygame.font.Font:
    path = BASE_DIR / "data" / font
    return pygame.font.Font(path, size)

# globals (declared, not initialized)

SCREEN_W = SCREEN_H = 0
SQUARE_SIZE = 0
OFFSET_X = OFFSET_Y = 0
scale_factor = 0

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
game_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))

FONTS = {}
COLORS = {}

BASE_RES = 720

frame_hi_h = 0
frame_lo_h = 0
frame_mid_h = 0
frame_hi_rect = (0, 0, 0, 0)
frame_mid_rect = (0, 0, 0, 0)
frame_lo_rect = (0, 0, 0, 0)

frame_border = 0

std_padding = 0
std_dist = 0

def s(n: int):
    global scale_factor, SQUARE_SIZE
    scale_factor = SQUARE_SIZE / BASE_RES
    return int(n * scale_factor)

def init_display():
    global screen, game_surface
    global SCREEN_W, SCREEN_H, SQUARE_SIZE
    global OFFSET_X, OFFSET_Y, scale_factor
    global FONTS, COLORS
    global frame_hi_h, frame_lo_h, frame_mid_h, frame_hi_rect, frame_mid_rect, \
        frame_lo_rect, frame_border, std_padding, std_dist

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    info = pygame.display.Info()
    print(info)
    SCREEN_W = info.current_w
    SCREEN_H = info.current_h
    print(SCREEN_W, SCREEN_H)

    SQUARE_SIZE = min(SCREEN_W, SCREEN_H)
    OFFSET_X = (SCREEN_W - SQUARE_SIZE) // 2
    OFFSET_Y = (SCREEN_H - SQUARE_SIZE) // 2

    game_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))

    std_padding = s(24)
    std_dist = s(91)

    frame_border = s(5)

    frame_hi_h = s(48)
    frame_lo_h = s(72)
    frame_mid_h = SQUARE_SIZE - (frame_hi_h + frame_lo_h)
    frame_hi_rect = (0, 0, SQUARE_SIZE, frame_hi_h)
    frame_mid_rect = (-frame_border, frame_hi_h, SQUARE_SIZE+2*frame_border, frame_mid_h)
    frame_lo_rect = (0, SQUARE_SIZE - frame_lo_h, SQUARE_SIZE, frame_lo_h)

    font_topaz_xs = load_font("topaz.ttf", s(9))
    font_topaz_s = load_font("topaz.ttf", s(16))
    font_topaz_m = load_font("topaz.ttf", s(21))
    font_topaz_xm = load_font("topaz.ttf", s(28))
    font_topaz_l = load_font("topaz.ttf", s(35))
    font_topaz_xl = load_font("topaz.ttf", s(56))
    font_topaz_xxl = load_font("topaz.ttf", s(72))

    FONTS = {
        "topaz_xs": font_topaz_xs,
        "topaz_s": font_topaz_s,
        "topaz_m": font_topaz_m,
        "topaz_xm": font_topaz_xm,
        "topaz_l": font_topaz_l,
        "topaz_xl": font_topaz_xl,
        "topaz_xxl": font_topaz_xxl,
    }

    COLORS = {
        "transparent": (0, 0, 0, 0),
        "opaque": (0, 0, 0, 120),

        "black": (0, 0, 0, 255),

        "gray_lo": (30, 30, 30, 255),
        "gray_mid": (60, 60, 60, 255),
        "gray_hi": (90, 90, 90, 255),
        "gray_border": (120, 120, 120, 255, frame_border),

        "white": (255, 255, 255, 255),
        "white_border": (255, 255, 255, 255, frame_border),

        "yellow_lo": (65, 50, 0, 255),
        "yellow_mid": (160, 130, 0, 255),
        "yellow_hi": (250, 250, 0, 255),
        "yellow_border": (220, 220, 0, 255, frame_border),

        "orange_dead": (30, 12, 0, 255),
        "orange_lo": (60, 25, 0, 255),
        "orange_mid": (130, 90, 0, 255),
        "orange_hi": (250, 160, 0, 255),
        "orange_border": (250, 160, 0, 255, frame_border),

        "red_lo": (60, 0, 0, 255),
        "red_mid": (170, 0, 0, 255),
        "red_hi": (250, 0, 0, 255),
        "red_border": (250, 0, 0, 255, frame_border),

        "blue_dead": (5, 10, 15, 255),
        "blue_lo": (10, 20, 30, 255),
        "blue_mid": (20, 30, 100, 255),
        "blue_hi": (20, 30, 250, 255),
        "blue_border": (70, 100, 220, 255, frame_border),

        "cyan_dead": (0, 20, 20, 255),
        "cyan_lo": (0, 40, 40, 255),
        "cyan_mid": (0, 110, 110, 255),
        "cyan_hi": (0, 200, 200, 255),
        "cyan_border": (0, 220, 220, 255, frame_border),

        "magenta_lo": (40, 0, 40, 255),
        "magenta_mid": (120, 0, 120, 255),
        "magenta_hi": (220, 0, 220, 255),
        "magenta_border": (220, 0, 220, 255, frame_border),

        "green_dead": (0, 20, 0, 255),
        "green_lo": (0, 40, 0, 255),
        "green_mid": (0, 120, 0, 255),
        "green_hi": (0, 200, 0, 255),
        "green_border": (0, 220, 0, 255, frame_border),

        "purple_lo": (30, 0, 50, 255),
        "purple_mid": (80, 20, 120, 255),
        "purple_hi": (150, 60, 200, 255),
        "purple_border": (170, 80, 220, 255, frame_border),

        "teal_lo": (0, 35, 30, 255),
        "teal_mid": (0, 90, 80, 255),
        "teal_hi": (0, 160, 140, 255),
        "teal_border": (0, 180, 160, 255, frame_border),
    }


