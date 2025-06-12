import pygame
from os.path import join


# constants
WINDOW_WIDTH, WINDOW_HEIGHT     = 1000, 600

BALL_SPEED, PAD_SPEED           = 300, 300
PAD_WIDTH, PAD_HEIGHT           = WINDOW_WIDTH//40, WINDOW_HEIGHT//4
RAY_LENGTH, RAY_SHRINK_SPEED    = WINDOW_WIDTH//50, WINDOW_WIDTH//15
TEXT_SIZE, FONT_PATH            = WINDOW_HEIGHT//15, join('game','utils','Pokemon_GB.ttf')
BALL_SIZE                       = PAD_WIDTH
BG_COLOR, FG_COLOR, TEXT_COLOR  = "orange", "blue", "black"
CLICK_SOUND_PATH                = join('game','utils','3b1b_clack.wav')
MISS_SOUND_PATH                 = join('game','utils','fart.wav')
WIN_SOUND_PATH                  = join('game','utils','win.wav')
