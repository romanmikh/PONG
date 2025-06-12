from ..utils.settings import *

# helper functions
def make_shape(topleft, width, height):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, width, height)
    pygame.draw.rect(surf, FG_COLOR, rect, border_radius=12)        
    pygame.draw.rect(surf, "black", rect, width=2, border_radius=12)
    return surf, surf.get_frect(topleft=topleft)


class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, pads, scores):
        super().__init__(groups)
        start_x = PAD_WIDTH
        start_y = WINDOW_HEIGHT//2 - PAD_HEIGHT//2 + PAD_HEIGHT//2 - BALL_SIZE//2
        self.image, self.rect = make_shape((start_x, start_y), BALL_SIZE, BALL_SIZE)
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
                    self._spawn_rays(pygame.math.Vector2(1, 0))
                else:
                    self.scores["player2"] += 1
                    self.reset_position()

            elif self.rect.right >= WINDOW_WIDTH - PAD_WIDTH:
                if self._pad_hit(self.pad_right.rect, self.rect):
                    self.direction.x = -abs(self.direction.x)
                    self._spawn_rays(pygame.math.Vector2(-1, 0))
                else:
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


class Text(pygame.sprite.Sprite):
    """Text prompt & score display"""
    def __init__(self, pos, color, scores, ball, groups):
        super().__init__(groups)
        self.x, self.y  = pos
        self.color      = color
        self.scores     = scores
        self.ball       = ball
        self.font  = pygame.font.Font(FONT_PATH, TEXT_SIZE)
        self.image = self.font.render("PRESS SPACE", True, self.color)
        self.rect  = self.image.get_rect(center=(self.x, self.y))

    def update(self, *_):
        if self.ball.game_active_ever:
            text = f"{self.scores['player1']}:{self.scores['player2']}"
            self.image = self.font.render(text, True, self.color)
            self.rect  = self.image.get_rect(center=(WINDOW_WIDTH // 2, self.y))


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
        self._update_image()


def main():

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Pong Game')
    clock = pygame.time.Clock()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    scores = {"player1": 0, "player2": 0}

    # make pads & ball & text
    all_sprites = pygame.sprite.Group()
    pad_start_y = WINDOW_HEIGHT//2 - PAD_HEIGHT//2
    padl_start_x, padr_start_x = 0, WINDOW_WIDTH - PAD_WIDTH
    
    pad_left  = Pad(padl_start_x, pad_start_y, "player1", all_sprites)
    pad_right = Pad(padr_start_x, pad_start_y, "player2", all_sprites)
    ball      = Ball(all_sprites, (pad_left, pad_right), scores)
    Text((WINDOW_WIDTH // 2, WINDOW_HEIGHT//10), TEXT_COLOR, scores, ball, all_sprites)

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
        
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()