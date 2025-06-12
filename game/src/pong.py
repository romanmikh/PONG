from ..utils.settings import *
import time

# helper functions
def make_shape(topleft, width, height):
    border_radius = WINDOW_WIDTH // 10
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, width, height)
    pygame.draw.rect(surf, FG_COLOR, rect, border_radius=border_radius)        
    pygame.draw.rect(surf, TEXT_COLOR, rect, width=2, border_radius=border_radius)
    return surf, surf.get_frect(topleft=topleft)


def display_text(display_surface, text, pos, color=TEXT_COLOR, size=TEXT_SIZE):
    font = pygame.font.Font(FONT_PATH, size)
    text_surf = font.render(text, False, color)
    text_rect = text_surf.get_frect(center=pos)
    display_surface.blit(text_surf, text_rect)


def display_score(display_surface, scores, pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 10)):
    text = f"{scores['player1']} : {scores['player2']}"
    display_text(display_surface, text, pos, color=TEXT_COLOR, size=TEXT_SIZE)


def display_winner(display_surface, winner, pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 10)):
    text = f"{winner} WINS!"
    display_text(display_surface, text, pos, color=TEXT_COLOR, size=TEXT_SIZE)


def display_instructions(display_surface, pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 10)):
    offset_x = WINDOW_WIDTH // 50
    offset_y = WINDOW_HEIGHT // 40
    display_text(display_surface, "PRESS SPACE", pos, color=TEXT_COLOR, size=TEXT_SIZE)
    display_text(display_surface, "W", (PAD_WIDTH + offset_x, WINDOW_HEIGHT // 2 - PAD_HEIGHT // 2 + offset_y), color=TEXT_COLOR, size=TEXT_SIZE // 2)
    display_text(display_surface, "S", (PAD_WIDTH + offset_x, WINDOW_HEIGHT // 2 + PAD_HEIGHT // 2 - offset_y), color=TEXT_COLOR, size=TEXT_SIZE // 2)
    display_text(display_surface, "UP", (WINDOW_WIDTH - PAD_WIDTH - offset_x, WINDOW_HEIGHT // 2 - PAD_HEIGHT // 2 + offset_y), color=TEXT_COLOR, size=TEXT_SIZE // 2)
    display_text(display_surface, "DN", (WINDOW_WIDTH - PAD_WIDTH - offset_x, WINDOW_HEIGHT // 2 + PAD_HEIGHT // 2 - offset_y), color=TEXT_COLOR, size=TEXT_SIZE // 2)



class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, pads, scores):
        super().__init__(groups)
        start_x = PAD_WIDTH
        start_y = WINDOW_HEIGHT//2 - PAD_HEIGHT//2 + PAD_HEIGHT//2 - BALL_SIZE//2
        self.image, self.rect = make_shape((start_x, start_y), BALL_SIZE, BALL_SIZE)
        self.pad_hit_sound = pygame.mixer.Sound(CLICK_SOUND_PATH)
        self.miss_sound = pygame.mixer.Sound(MISS_SOUND_PATH)
        self.miss_sound.set_volume(0.5)
        self.direction = pygame.math.Vector2(1, -1)
        self.pad_left, self.pad_right = pads
        self.game_active_ever = False
        self.game_active = False
        self.scores = scores
        self.collisions = 0

    def _pad_hit(self, pad_rect, ball_rect):
        self.collisions += 1
        return pad_rect.top <= ball_rect.centery <= pad_rect.bottom
    
    def _spawn_rays(self, normal):
        for angle in (75, 25, -25, -75):
            Ray(self.rect.center,
                normal.rotate(angle),
                self.groups())
            
    def reset_position(self):
        self.rect.midleft = (PAD_WIDTH, WINDOW_HEIGHT // 2)
        self.direction = pygame.math.Vector2(1, -1)
        self.pad_left.reset_position()
        self.pad_right.reset_position()
        self.game_active = False
        self.collisions = 0
        
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.game_active = True
            self.game_active_ever = True

        if self.game_active:
            if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT:
                self.direction.y *= -1

            if self.rect.left <= PAD_WIDTH:
                if self._pad_hit(self.pad_left.rect, self.rect):
                    self.direction.x = abs(self.direction.x)
                    self.pad_hit_sound.play()
                    self._spawn_rays(pygame.math.Vector2(1, 0))
                else:
                    self.miss_sound.play()
                    self.scores["player2"] += 1
                    self.reset_position()

            elif self.rect.right >= WINDOW_WIDTH - PAD_WIDTH:
                if self._pad_hit(self.pad_right.rect, self.rect):
                    self.direction.x = -abs(self.direction.x)
                    self.pad_hit_sound.play()
                    self._spawn_rays(pygame.math.Vector2(-1, 0))
                else:
                    self.miss_sound.play()
                    self.scores["player1"] += 1
                    self.reset_position()

            self.rect.center += self.direction * BALL_SPEED * dt * (1 + self.collisions / 10)


class Pad(pygame.sprite.Sprite):
    def __init__(self, x, y, player, groups):
        super().__init__(groups)
        self.start_x   = x
        self.start_y   = y
        self.player    = player
        self.direction = pygame.math.Vector2(0, 1)
        self.image, self.rect = make_shape((x, y), PAD_WIDTH, PAD_HEIGHT)

    def reset_position(self):
        self.rect.topleft = (self.start_x, self.start_y)

    def update(self, dt):
        
        keys = pygame.key.get_pressed()
        if self.player == "player1":
            self.direction = -int(keys[pygame.K_w])  + int(keys[pygame.K_s])
        else:
            self.direction = -int(keys[pygame.K_UP]) + int(keys[pygame.K_DOWN])
        self.rect.y += self.direction * PAD_SPEED * dt
        self.rect.y = max(0, min(WINDOW_HEIGHT - PAD_HEIGHT, self.rect.y))


class Ray(pygame.sprite.Sprite):
    """A blue line animation that moves away from the ball cntre until it vanishes"""
    def __init__(self, pos, normal, groups):
        super().__init__(groups)
        self.normal   = normal.normalize()
        self.radius   = BALL_SIZE
        self.length   = RAY_LENGTH
        size          = (self.radius + self.length) * 2
        self.image    = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect     = self.image.get_rect(center=pos)
        self._update_image()

    def _update_image(self):
        self.image.fill((0, 0, 0, 0))
        remain = max(0, self.length)
        if remain == 0:
            return
        cx, cy = self.image.get_width() // 2, self.image.get_height() // 2
        start  = (cx + self.normal.x * (self.radius + (RAY_LENGTH - self.length)),
                  cy + self.normal.y * (self.radius + (RAY_LENGTH - self.length)))
        end    = (cx + self.normal.x * (self.radius + RAY_LENGTH),
                  cy + self.normal.y * (self.radius + RAY_LENGTH))
        pygame.draw.line(self.image, FG_COLOR, start, end, 2)

    def update(self, dt):
        self.length -= RAY_SHRINK_SPEED * dt
        if self.length <= 0:
            self.kill()
        else:
            self._update_image()


def main():

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Pong Game')
    clock = pygame.time.Clock()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    scores = {"player1": 0, "player2": 0}
    win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)

    # make pads & ball & text
    pad_start_y = WINDOW_HEIGHT//2 - PAD_HEIGHT//2
    padl_start_x, padr_start_x = 0, WINDOW_WIDTH - PAD_WIDTH
    
    all_sprites = pygame.sprite.Group()
    pad_left    = Pad(padl_start_x, pad_start_y, "player1", all_sprites)
    pad_right   = Pad(padr_start_x, pad_start_y, "player2", all_sprites)
    ball        = Ball(all_sprites, (pad_left, pad_right), scores)

    running = True
    while running:

        # event loop
        delta_time = clock.tick() / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                        
        # draw the screen
        display_surface.fill(BG_COLOR)
        all_sprites.update(delta_time)
        all_sprites.draw(display_surface)
        if not ball.game_active_ever:
            display_instructions(display_surface)
        elif scores["player1"] >= 5 or scores["player2"] >= 5:
            winner = "Player 1" if scores["player1"] > scores["player2"] else "Player 2"
            display_winner(display_surface, winner)
            win_sound.play()
            pygame.display.update()
            time.sleep(5)
            running = False
        else:
            display_score(display_surface, scores)
        
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()