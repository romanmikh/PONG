from ..utils.settings import *
from .sprites import *
import time

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


class Game:
    def __init__(self):
        pygame.init() 
        pygame.font.init()
        pygame.display.set_caption('Pong Game')
        self.clock = pygame.time.Clock()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)
        self.scores = {"player1": 0, "player2": 0}
        self.running = True
        self.ball = None

        # make pads & ball
        self.all_sprites = pygame.sprite.Group()
        pad_left  = PlayerPad(POS['padl_start'], "player1", None, self.all_sprites)
        pad_right = PlayerPad(POS['padr_start'], "player2", None, self.all_sprites)
        # pad_right = DumbOpponentPad(POS['padr_start'], "DumbBot", None, self.all_sprites)
        # pad_right = FollowOpponentPad(POS['padr_start'], "KeenBot", None, self.all_sprites)
        # pad_right = SmartOpponentPad(POS['padr_start'], "SmartBot", None, self.all_sprites)
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
                            
            # draw the screen
            self.display_surface.fill(BG_COLOR)
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