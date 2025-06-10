import pygame

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Pong Game')
running = True

# surfaces
PAD_WIDTH = WINDOW_WIDTH // 40
PAD_HEIGHT = WINDOW_HEIGHT // 4
pad_y = WINDOW_HEIGHT // 2 - 50
surf = pygame.Surface ((PAD_WIDTH, PAD_HEIGHT))

BALL_WIDTH = BALL_HEIGHT = WINDOW_WIDTH // 40
ball_x = PAD_WIDTH
ball_y = pad_y + PAD_HEIGHT // 2 - BALL_WIDTH // 2
ball_moving_up = True
ball_moving_right = True
ball_speed = 0.3
ball = pygame.Surface((BALL_WIDTH, BALL_WIDTH))

while running:
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # draw the screen
    display_surface.fill('orange')
    surf.fill('blue'), ball.fill('blue')
    display_surface.blit(surf, (0, pad_y))
    display_surface.blit(surf, (WINDOW_WIDTH - PAD_WIDTH, pad_y))
    display_surface.blit(ball, (ball_x, ball_y))
    # if (pad_y + PAD_HEIGHT < WINDOW_HEIGHT):
    #     pad_y += 0.0

    ball_x += ball_speed if ball_moving_right else -ball_speed
    ball_y -= ball_speed if ball_moving_up else -ball_speed

    if ball_y <= 0:
        ball_moving_up = False
    elif ball_y >= WINDOW_HEIGHT - BALL_WIDTH:
        ball_moving_up = True

    if ball_x <= PAD_WIDTH:
        if not (pad_y <= ball_y <= pad_y + PAD_HEIGHT):
            print("Missed! (Player 1)")
        ball_moving_right = True
    elif ball_x >= WINDOW_WIDTH - PAD_WIDTH * 2:
        if not (pad_y <= ball_y <= pad_y + PAD_HEIGHT):
            print("Missed! (Player 2)")
        ball_moving_right = False
    
    pygame.display.update()

pygame.quit()