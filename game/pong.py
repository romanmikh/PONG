import pygame


# constants
WINDOW_WIDTH, WINDOW_HEIGHT     = 1000, 600
PAD_WIDTH, PAD_HEIGHT           = WINDOW_WIDTH//40, WINDOW_HEIGHT//4
BALL_SIZE                       = PAD_WIDTH
BALL_SPEED, PAD_SPEED           = 0.5, 0.2
BG_COLOR, FG_COLOR, TEXT_COLOR  = "orange", "blue", "black"


# helper functions
def make_shape(topleft, width, height):
    surf = pygame.Surface((width, height))
    surf.fill(FG_COLOR)
    return surf, surf.get_frect(topleft=topleft)


def pad_hit(pad_rect, ball_rect):
    return pad_rect.top <= ball_rect.centery <= pad_rect.bottom


def main():

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Pong Game')
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # make pads & ball
    pad_y = WINDOW_HEIGHT//2 - PAD_HEIGHT//2
    pad_left , padl_rect = make_shape((0, pad_y), PAD_WIDTH, PAD_HEIGHT)
    pad_right, padr_rect = make_shape((WINDOW_WIDTH-PAD_WIDTH, pad_y), PAD_WIDTH, PAD_HEIGHT)

    ball_moving_up = True
    ball_moving_right = True
    ball_x = PAD_WIDTH
    ball_y = pad_y + PAD_HEIGHT//2 - BALL_SIZE//2
    ball, ball_rect = make_shape((ball_x, ball_y), BALL_SIZE, BALL_SIZE)

    my_font = pygame.font.Font("game/Pokemon_GB.ttf", 50)
    player1_score, player2_score = 0, 0
    running = True
    while running:
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ball movement
        ball_rect.move_ip(BALL_SPEED if ball_moving_right else -BALL_SPEED,
                         -BALL_SPEED if ball_moving_up else BALL_SPEED)

        if ball_rect.top < 0:
            ball_moving_up = False
        elif ball_rect.bottom > WINDOW_HEIGHT:
            ball_moving_up = True

        if ball_rect.left < PAD_WIDTH:
            if not pad_hit(padl_rect, ball_rect):
                player2_score += 1
            ball_moving_right = True
        elif ball_rect.right > WINDOW_WIDTH - PAD_WIDTH:
            if not pad_hit(padr_rect, ball_rect):
                player1_score += 1
            ball_moving_right = False
        text_surface = my_font.render(f"{player1_score}:{player2_score}", False, TEXT_COLOR)
        
        # pad movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and padl_rect.top > 0:
            padl_rect.move_ip(0, -PAD_SPEED)
        if keys[pygame.K_s] and padl_rect.bottom < WINDOW_HEIGHT:
            padl_rect.move_ip(0, PAD_SPEED)
        if keys[pygame.K_UP] and padr_rect.top > 0:
            padr_rect.move_ip(0, -PAD_SPEED)
        if keys[pygame.K_DOWN] and padr_rect.bottom < WINDOW_HEIGHT:
            padr_rect.move_ip(0, PAD_SPEED)

        # draw the screen
        display_surface.fill(BG_COLOR)
        display_surface.blit(pad_left, padl_rect)
        display_surface.blit(pad_right, padr_rect)
        display_surface.blit(ball, ball_rect)
        display_surface.blit(text_surface, (WINDOW_WIDTH//2 - text_surface.get_width()//2, 20))
        
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()