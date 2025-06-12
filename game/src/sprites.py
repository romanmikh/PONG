from ..utils.settings import *
from random import choice

# helper functions
def make_shape(center, width, height):
    border_radius = WINDOW_WIDTH // 10
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, width, height)
    pygame.draw.rect(surf, FG_COLOR, rect, border_radius=border_radius)        
    pygame.draw.rect(surf, TEXT_COLOR, rect, width=2, border_radius=border_radius)
    return surf, surf.get_frect(center=center)


class PlayerPad(pygame.sprite.Sprite):
    def __init__(self, pos, player, ball, groups):
        super().__init__(groups)
        self.start_x, self.start_y = pos
        self.ball      = ball
        self.player    = player
        self.direction = 0
        self.image, self.rect = make_shape(pos, PAD_WIDTH, PAD_HEIGHT)

    def reset_position(self):
        self.rect.center = (self.start_x, self.start_y)

    def _set_direction(self):
        keys = pygame.key.get_pressed()
        if self.player == "player1":
            self.direction = -int(keys[pygame.K_w])  + int(keys[pygame.K_s])
        else:
            self.direction = -int(keys[pygame.K_UP]) + int(keys[pygame.K_DOWN])

    def _move(self, dt):
        self.rect.y += self.direction * PAD_SPEED * dt
        self.rect.y = max(0, min(WINDOW_HEIGHT - PAD_HEIGHT, self.rect.y))

    def update(self, dt):
        if not self.ball.game_active:
            return
        self._set_direction()
        self._move(dt)


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos, pads, scores, groups):
        super().__init__(groups)
        self.image, self.rect = make_shape(pos, BALL_SIZE, BALL_SIZE)
        self.hit_sound = pygame.mixer.Sound(CLICK_SOUND_PATH)
        self.miss_sound = pygame.mixer.Sound(MISS_SOUND_PATH)
        self.miss_sound.set_volume(0.5)
        self.direction = pygame.math.Vector2(choice([-1, 1]), choice([-1, 1]))
        self.pad_left, self.pad_right = pads
        self.game_active_ever = False
        self.game_active = False
        self.scores = scores
        self.collisions = 0

    def _reset_position(self):
        self.rect.midleft = POS['ball_start']
        self.direction = pygame.math.Vector2(choice([-1, 1]), choice([-1, 1]))
        self.pad_left.reset_position()
        self.pad_right.reset_position()
        self.game_active = False
        self.collisions = 0

    def _pad_hit(self, pad_rect, ball_rect):
        self.collisions += 1
        return pad_rect.top <= ball_rect.centery <= pad_rect.bottom
    
    def _spawn_rays(self, normal):
        for angle in (75, 25, -25, -75):
            Ray(self.rect.center,
                normal.rotate(angle),
                self.groups())
            
    def _return_to_bounds(self):
        if self.rect.top >= WINDOW_HEIGHT:
            self.rect.top = WINDOW_HEIGHT
            self.direction.y = -1
        if self.rect.bottom <= 0:
            self.rect.bottom = 0
            self.direction.y = 1
            
    def _set_direction(self):
        self._return_to_bounds()
        if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT:
            self.direction.y *= -1

        if self.rect.left <= PAD_WIDTH:
            if self._pad_hit(self.pad_left.rect, self.rect):
                self.direction.x = abs(self.direction.x)
                self.hit_sound.play()
                self._spawn_rays(pygame.math.Vector2(1, 0))
            else:
                self.miss_sound.play()
                self.scores["player2"] += 1
                self._reset_position()

        elif self.rect.right > WINDOW_WIDTH - PAD_WIDTH:
            if self._pad_hit(self.pad_right.rect, self.rect):
                self.direction.x = -abs(self.direction.x)
                self.hit_sound.play()
                self._spawn_rays(pygame.math.Vector2(-1, 0))
            else:
                self.miss_sound.play()
                self.scores["player1"] += 1
                self._reset_position()

    def _move(self, dt):
        self.rect.center += self.direction * BALL_SPEED * dt * (1 + self.collisions / 10)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.game_active = True
            self.game_active_ever = True

        if self.game_active:
            self._set_direction()
            self._move(dt)


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
