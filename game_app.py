# Simple pygame program

# Import and initialize the pygame library
import pygame

from game_manager import GameManager
from game_object import GameStatus

gm = GameManager()
color_dict = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'purple': (255, 0, 255),
        'cyan': (0, 255, 255),
        'black': (0, 0, 0)
    }
pygame.init()

block_size = 80
panel_length = 300
# Set up the drawing window
screen = pygame.display.set_mode([block_size * 8 + panel_length, block_size * 8])

# Run until the user asks to quit
running = True
fps_clock = pygame.time.Clock()
debug = 0

def draw_swapping(gm: GameManager):
    pygame.draw.circle(
                screen,
                color_code,
                ((x * block_size + block_size//2), (y * block_size) + block_size//2),
                block_size//2)

while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            x = pos[0] // block_size
            y = pos[1] // block_size
            gm.set_selection(x, y)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                gm = GameManager()

    if gm.game_status == GameStatus.Idle:
        continue
    gm.process_frame()

    # Fill the background with white
    screen.fill((255, 255, 255))

    # Draw a solid blue circle in the center
    # pygame.draw.circle(screen, (0, 255, 255), (250, 250), 75)
    for y in range(0, gm.dimension_y):
        for x in range(0, gm.dimension_x):
            sprite = gm.sprite_map[y][x]
            color_key = sprite.color
            color_code = color_dict[color_key]
            pygame.draw.circle(
                screen,
                color_code,
                ((sprite.x * block_size + block_size//2), (sprite.y * block_size) + block_size//2),
                block_size//2)


    # Flip the display
    pygame.display.flip()
    fps_clock.tick(10)

# Done! Time to quit.
pygame.quit()