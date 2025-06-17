import pygame
from os.path import join


# constants
WINDOW_WIDTH, WINDOW_HEIGHT     = 1000, 600

BALL_SPEED, PAD_SPEED           = 300, 1500
MAX_SCORE                       = 5
PAD_WIDTH, PAD_HEIGHT           = WINDOW_WIDTH//40, WINDOW_HEIGHT//4
RAY_LENGTH, RAY_SHRINK_SPEED    = WINDOW_WIDTH//50, WINDOW_WIDTH//15
TEXT_SIZE                       = WINDOW_HEIGHT//15
BALL_SIZE                       = PAD_WIDTH
BG_COLOR, FG_COLOR, TEXT_COLOR  = "orange", "blue", "black"
FONT_PATH                       = join('game','utils','Pokemon_GB.ttf')
CLICK_SOUND_PATH                = join('game','utils','3b1b_clack.wav')
MISS_SOUND_PATH                 = join('game','utils','fart.wav')
WIN_SOUND_PATH                  = join('game','utils','win.wav')
SCORE_FILE_PATH                 = join('game','data','scores.json')

POS = {
    'padl_start': (PAD_WIDTH // 2, WINDOW_HEIGHT // 2),
    'padr_start': (WINDOW_WIDTH - PAD_WIDTH // 2, WINDOW_HEIGHT // 2),
    'ball_start': (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
    'text_center': (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 10),
}