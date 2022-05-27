# Simple pygame program

# Import and initialize the pygame library
import pygame
from sprite_manager import ColorBlockSprite

from game_manager import GameManager

gm = GameManager()
color_dict = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'purple': (255, 0, 255),
        'cyan': (0, 255, 255),
        'black': (0, 0, 0),
        'white': (255, 255, 255)
    }
pygame.init()

block_size = 80
panel_length = 300
# Set up the drawing window
screen = pygame.display.set_mode([block_size * 8 + panel_length, block_size * 8])

# Run until the user asks to quit
running = True
fps_clock = pygame.time.Clock()
debug_mode = False

def draw_block(block_sprite: ColorBlockSprite) -> None:
    if block_sprite.cleared:
        return
    color_key = block_sprite.color
    color_code = color_dict[color_key]
    pygame.draw.circle(
        screen,
        color_code,
        (
            (block_sprite.x * block_size + block_size//2),
            (block_sprite.y * block_size) + block_size//2
        ),
        block_size//2
    )

    if block_sprite.hilighted and not block_sprite.cleared:
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            pygame.Rect(
                block_sprite.x * block_size,
                block_sprite.y * block_size,
                10,
                10)
        )

def draw_text(text: str, x: int, y: int) -> None:
    myfont = pygame.font.SysFont("monospace", 20)
    label = myfont.render(text, 1, (0,0,0))
    screen.blit(label, (x, y))

debug_msg = ''
debug_coord = None

while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            x = pos[0] // block_size
            y = pos[1] // block_size
            if debug_mode:
                debug_msg = gm.sprite_map[x][y].get_sprite_info()
                debug_coord = (x, y)
            else:
                gm.set_selection(x, y)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                gm = GameManager()
            if event.key == pygame.K_d:
                debug_mode = not debug_mode

    gm.process_frame()

    # Fill the background with white
    screen.fill((255, 255, 255))
    draw_text(str(gm.game_status), 650, 100)
    draw_text(str(debug_coord), 650, 200)
    draw_text(debug_msg, 650, 300)

    # Draw a solid blue circle in the center
    # pygame.draw.circle(screen, (0, 255, 255), (250, 250), 75)
    for column in gm.sprite_map:
        for sprite in column:
            draw_block(sprite)


    # Flip the display
    pygame.display.flip()
    fps_clock.tick(30)

# Done! Time to quit.
pygame.quit()
