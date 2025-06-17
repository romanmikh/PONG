from ..utils.settings import *
from random import choice

# helper functions
def make_shape(center, width, height, shine_side=None):
    """Create a rounded rectangle, add a vertical shine if shine_side given."""
    border_radius = WINDOW_WIDTH // 10
    surf = pygame.Surface((width, height), pygame.SRCALPHA)

    # base shape + dark border
    rect = pygame.FRect(0, 0, width, height)
    pygame.draw.rect(surf, FG_COLOR, rect, border_radius=border_radius)
    pygame.draw.rect(surf, TEXT_COLOR, rect, width=2, border_radius=border_radius)

    # shine for pads
    if shine_side in ("left", "right"):
        shine_w = int(width * 0.15)
        shine_h = int(height * 0.8)
        shine_x = int(width * 0.2) if shine_side == "left" else int(width * 0.7)
        shine_y = (height - shine_h) // 2

        shine_rect = pygame.Rect(shine_x, shine_y, shine_w, shine_h)
        pygame.draw.rect(surf, "white", shine_rect, border_radius=WINDOW_WIDTH//10)

    return surf, surf.get_frect(center=center)



class Pad(pygame.sprite.Sprite):
    def __init__(self, pos, player, ball, groups):
        super().__init__(groups)
        self.start_x, self.start_y = pos
        self.player    = player
        self.ball      = ball
        self.direction = 0
        
        shine_side = "right" if self.start_x < WINDOW_WIDTH // 2 else "left"
        self.image, self.rect = make_shape(pos, PAD_WIDTH, PAD_HEIGHT, shine_side)

    def reset_position(self):
        self.rect.center = (self.start_x, self.start_y)

    def _move(self, dt):
        self.rect.y += self.direction * PAD_SPEED * dt
        self.rect.y = max(0, min(WINDOW_HEIGHT - PAD_HEIGHT, self.rect.y))

    def update(self, dt):
        if not self.ball.game_active:
            return
        self.set_direction()
        self._move(dt)


class PlayerPad(Pad):
    def __init__(seld, pos, player, ball, groups):
        super().__init__(pos, player, ball, groups)

    def set_direction(self):
        keys = pygame.key.get_pressed()
        if self.player == "player1":
            self.direction = -int(keys[pygame.K_w])  + int(keys[pygame.K_s])
        else:
            self.direction = -int(keys[pygame.K_UP]) + int(keys[pygame.K_DOWN])


class DumbOpponentPad(Pad):
    """Moves up and down cyclically, ignores the ball"""
    def __init__(self, pos, player, ball, groups):
        super().__init__(pos, player, ball, groups)

    def set_direction(self):
        if not self.ball.game_active:
            self.direction = 0
            return
        
        if self.rect.centery < self.ball.rect.centery:
            self.direction = 1
        elif self.rect.centery > self.ball.rect.centery:
            self.direction = -1
        else:
            self.direction = 0


class FollowOpponentPad(Pad):
    """Follows the ball"""
    def __init__(self, pos, player, ball, groups):
        super().__init__(pos, player, ball, groups)

    def set_direction(self):
        if not self.ball.game_active:
            self.direction = 0
            return

        if self.rect.centery < self.ball.rect.centery - PAD_HEIGHT // 2:
            self.direction = 1
        elif self.rect.centery > self.ball.rect.centery + PAD_HEIGHT // 2:
            self.direction = -1
        else:
            self.direction = 0


class SmartOpponentPad(Pad):
    """Predicts collision y coordinate & moves towards it. I haven't beaten it yet"""
    def __init__(self, pos, player, ball, groups):
        super().__init__(pos, player, ball, groups)

    def _predict_intercept_y(self) -> int:
        # x, y and t the ball will travel before pad hit
        dx_left = self.rect.centerx - self.ball.rect.centerx 
        t_left = abs(dx_left) / (abs(self.ball.direction.x) * BALL_SPEED)
        abs_y_left = self.ball.rect.centery + self.ball.direction.y * BALL_SPEED * t_left

        # adjust abs_y_left for bouncing off top/bottom, return remainder
        n = int(abs_y_left // WINDOW_HEIGHT)
        if n % 2 == 0:
            return int(abs_y_left % WINDOW_HEIGHT)
        else:
            return int(WINDOW_HEIGHT - (abs_y_left % WINDOW_HEIGHT))

    def set_direction(self):
        if not self.ball.game_active:
            self.direction = 0
            return

        target_y = self._predict_intercept_y()
        centre_y = self.rect.centery
        if centre_y < target_y:
            self.direction = 1
        elif centre_y > target_y:
            self.direction = -1
        else:
            self.direction = 0


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos, pads, scores, groups):
        super().__init__(groups)

        # keep BOTH surface and rect
        self.base_surf, self.rect = make_shape(pos, BALL_SIZE, BALL_SIZE)
        self.direction  = pygame.math.Vector2(choice([-1, 1]), choice([-1, 1]))
        self.image = self.base_surf.copy()
        self.pad_left, self.pad_right = pads
        self.game_active_ever = False
        self.game_active      = False
        self.scores     = scores
        self.collisions = 0
        self._update_spot()

        self.hit_sound  = pygame.mixer.Sound(CLICK_SOUND_PATH)
        self.miss_sound = pygame.mixer.Sound(MISS_SOUND_PATH)
        self.miss_sound.set_volume(0.5)

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
            self.rect.top = WINDOW_HEIGHT - 1
            self.direction.y = -1
        if self.rect.bottom <= 0:
            self.rect.bottom = 1
            self.direction.y = 1

    def _update_spot(self):
        """
        Draw a white spot on the ball that always faces the screen centre
        Spot slides within an invisible smaller circle
        """
        self.image.blit(self.base_surf, (0, 0))     # wipe the image
        spot_radius = int(BALL_SIZE * 0.1)
        max_offset  = BALL_SIZE * 0.25
        centre_x, centre_y = POS['ball_start']
        ball_x, ball_y     = self.rect.center

        # vector pointing to screen centre
        vec_x, vec_y = centre_x - ball_x, centre_y - ball_y
        dist = (vec_x**2 + vec_y**2) ** 0.5
        if dist != 0:
            scaled_vec_x, scaled_vec_y = vec_x / dist, vec_y / dist
        else:
            scaled_vec_x, scaled_vec_y = 0, 0

        # scale & clamp offset proportional to distance
        max_dist = (centre_x**2 + centre_y**2) ** 0.5
        clamp    = min(1.0, dist / max_dist)
        scaled_offset = clamp * max_offset

        # spot centre within the ball surface
        spot_x = BALL_SIZE // 2 + scaled_vec_x * scaled_offset
        spot_y = BALL_SIZE // 2 + scaled_vec_y * scaled_offset

        pygame.draw.circle(self.image, "white", (int(spot_x), int(spot_y)), spot_radius)
            
    def _set_direction(self):
        self._return_to_bounds()
        if self.rect.top <= 0:
            self.rect.top = 0 
            self.direction.y =  abs(self.direction.y)
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.direction.y = -abs(self.direction.y)

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
            self._update_spot()



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
        # wipe the image and draw a line
        self.image.fill((0, 0, 0, 0))
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
