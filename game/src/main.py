from ..utils.settings import *
from .sprites import *
import time
import json

# helper functions
def display_text(display_surface, text, pos, color=TEXT_COLOR, size=TEXT_SIZE):
    font = pygame.font.Font(FONT_PATH, size)
    text_surf = font.render(text, False, color)
    text_rect = text_surf.get_frect(center=pos)
    display_surface.blit(text_surf, text_rect)


def display_score(display_surface, scores, pos=POS['text_center']):
    text = f"{scores['player1']} : {scores['player2']}"
    display_text(display_surface, text, pos, TEXT_COLOR, TEXT_SIZE)


def display_winner(display_surface, winner, pos=POS['text_center']):
    text = f"{winner} WINS!"
    display_text(display_surface, text, pos, TEXT_COLOR, TEXT_SIZE)


def display_instructions(display_surface, pos=POS['text_center']):
    offset_x = WINDOW_WIDTH // 50
    offset_y = WINDOW_HEIGHT // 40
    display_text(display_surface, "PRESS SPACE", pos, TEXT_COLOR, TEXT_SIZE)
    display_text(display_surface, "W", (PAD_WIDTH + offset_x, WINDOW_HEIGHT // 2 - PAD_HEIGHT // 2 + offset_y), TEXT_COLOR, TEXT_SIZE // 2)
    display_text(display_surface, "S", (PAD_WIDTH + offset_x, WINDOW_HEIGHT // 2 + PAD_HEIGHT // 2 - offset_y), TEXT_COLOR, TEXT_SIZE // 2)
    display_text(display_surface, "UP", (WINDOW_WIDTH - PAD_WIDTH - offset_x, WINDOW_HEIGHT // 2 - PAD_HEIGHT // 2 + offset_y), TEXT_COLOR, TEXT_SIZE // 2)
    display_text(display_surface, "DN", (WINDOW_WIDTH - PAD_WIDTH - offset_x, WINDOW_HEIGHT // 2 + PAD_HEIGHT // 2 - offset_y), TEXT_COLOR, TEXT_SIZE // 2)


def make_radial_bg(size, center_color, edge_color):
    w, h = size
    center_x, center_y = w / 2, h / 2
    surf = pygame.Surface(size)
    for y in range(h):
        for x in range(w):
            # radial distance from center
            dx = (x - center_x) / center_x
            dy = (y - center_y) / center_y
            r2 = dx*dx + dy*dy
            t = min(r2, 1.0)

            # blend colours
            r = center_color[0] + (edge_color[0]-center_color[0])*t
            g = center_color[1] + (edge_color[1]-center_color[1])*t
            b = center_color[2] + (edge_color[2]-center_color[2])*t
            surf.set_at((x, y), (int(r), int(g), int(b)))
    return surf


class Game:
    def __init__(self):
        pygame.init() 
        pygame.font.init()
        pygame.display.set_caption('Pong Game')
        self.clock = pygame.time.Clock()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)
        self.running = True
        self.ball = None
        self.bg_surface = make_radial_bg(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.Color(BG_COLOR)[:3],
            tuple(max(c-35, 0) for c in pygame.Color(BG_COLOR)[:3])
        )

        # load scores
        # with open(SCORE_FILE_PATH, 'r') as f:
        #     try:
        #         self.scores = json.load(f)
        #     except json.JSONDecodeError:
        #         self.scores = {"player1": 0, "player2": 0}
        self.scores = {"player1": 0, "player2": 0}

        # make pad & ball sprites
        self.all_sprites = pygame.sprite.Group()
        # pad_left  = PlayerPad(POS['padl_start'], "player1", None, self.all_sprites)
        # pad_right = PlayerPad(POS['padr_start'], "player2", None, self.all_sprites)
        # pad_right = DumbOpponentPad(POS['padr_start'], "DumbBot", None, self.all_sprites)
        # pad_right = FollowOpponentPad(POS['padr_start'], "KeenBot", None, self.all_sprites)
        pad_left = SmartOpponentPad(POS['padl_start'], "SmartBot", None, self.all_sprites)
        pad_right = SmartOpponentPad(POS['padr_start'], "SmartBot", None, self.all_sprites)
        self.ball = Ball(POS['ball_start'], (pad_left, pad_right), self.scores, self.all_sprites)
        pad_left.ball = pad_right.ball = self.ball

    def _check_win(self):
        return self.scores["player1"] >= MAX_SCORE or self.scores["player2"] >= MAX_SCORE

    def _handle_win(self):
        winner = "Player 1" if self.scores["player1"] > self.scores["player2"] else "Player 2"
        display_winner(self.display_surface, winner)
        self.win_sound.play()
        pygame.display.update()
        time.sleep(5)
        self.running = False

    def run(self):
        while self.running:

            # event loop
            delta_time = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    with open(SCORE_FILE_PATH, 'w') as f:
                        json.dump(self.scores, f)
                            
            # draw the screen
            self.display_surface.blit(self.bg_surface, (0, 0))
            self.all_sprites.update(delta_time)
            self.all_sprites.draw(self.display_surface)

            # handle game state
            if not self.ball.game_active_ever:
                display_instructions(self.display_surface)
            elif self._check_win():
                self._handle_win()
            else:
                display_score(self.display_surface, self.scores)
            
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()