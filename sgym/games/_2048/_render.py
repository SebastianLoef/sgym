import math
import random

import pygame

BACKGROUND_COLOR = "#d8c8b9"
EMPTY_TILE_COLOR = "#cdc1b4"
TILE_COLORS = {
    1: "#eee4da",
    2: "#ede0c8",
    3: "#f2b179",
    4: "#f59563",
    5: "#f67c5f",
    6: "#f65e3b",
    7: "#edcf72",
    8: "#edcc61",
    9: "#edc850",
    10: "#edc53f",
    11: "#edc22e",
}
FONT = "freesansbold.ttf"
TEXT_COLOR = "#776e65"

ANIMATION_STEPS_MOVE = 10
ANIMATION_STEPS_MERGE = 20

BORDER_RADIUS = 15
WIDTH = 720
HEIGHT = 800
GAP = 20
TOP_GAP = 80
TILE_SIZE = int((WIDTH - 5 * GAP) / 4)


def rect_tuple(i, j):
    """Returns the rectangle tuple for the square at (i, j)."""
    return (
        int(i * (TILE_SIZE + GAP) + GAP),
        int(j * (TILE_SIZE + GAP) + GAP + TOP_GAP),
        TILE_SIZE,
        TILE_SIZE,
    )


def render_background(screen, score):
    """Renders the background to the screen."""
    screen.fill(BACKGROUND_COLOR)
    for i in range(4):
        for j in range(4):
            pygame.draw.rect(
                screen,
                EMPTY_TILE_COLOR,
                rect_tuple(i, j),
                border_radius=BORDER_RADIUS,
            )

    font = pygame.font.Font(FONT, 50)
    text = font.render("Score: ", True, TEXT_COLOR)
    textRect = text.get_rect()
    textRect.center = (100, 45)
    screen.blit(text, textRect)
    pygame.draw.rect(screen, EMPTY_TILE_COLOR, (200, 20, 200, 60))
    font = pygame.font.Font(FONT, 40)
    text = font.render(str(score), True, TEXT_COLOR)
    textRect = text.get_rect()
    setattr(textRect, "topright", (380, 342))
    screen.blit(text, textRect)
    return screen


def render_tiles(board, screen):
    """Renders the tiles to the screen."""
    for i in range(4):
        for j in range(4):
            if board[i][j] != 0:
                render_tile(board[i][j], screen, i, j)
    return screen


def render_tile(number: int, screen, i, j):
    pygame.draw.rect(
        screen,
        TILE_COLORS[number],
        rect_tuple(i, j),
        border_radius=BORDER_RADIUS,
    )
    font = pygame.font.Font(FONT, 32)
    text = font.render(str(2**number), True, "black")
    textRect = text.get_rect()
    textRect.center = (
        i * (TILE_SIZE + GAP) + 90,
        j * (TILE_SIZE + GAP) + 90 + TOP_GAP,
    )
    screen.blit(text, textRect)


def get_move_direction(action):
    if action == 0:
        return 0, -1
    if action == 1:
        return 1, -1
    if action == 2:
        return 0, 1
    return 1, 1


def render_move(board, move_map, screen, step, action):
    column, direction = get_move_direction(action)
    for i in range(4):
        for j in range(4):
            if board[i][j] != 0:
                i_pos = float(i) + column * direction * (
                    move_map[i][j] * step / ANIMATION_STEPS_MOVE
                )
                j_pos = (
                    float(j)
                    + (1 - column)
                    * direction
                    * move_map[i][j]
                    * step
                    / ANIMATION_STEPS_MOVE
                )
                # print(i_pos, j_pos, move_map[i][j])
                render_tile(board[i][j], screen, i_pos, j_pos)


def size_func(step):
    return 1.0 + 0.2 * math.sin(step * math.pi / ANIMATION_STEPS_MERGE)


def render_merge(board, just_merged, new_tiles, step, screen):
    new_tile_size = TILE_SIZE * size_func(step)
    diff = new_tile_size - TILE_SIZE
    for i in range(4):
        for j in range(4):
            if just_merged[i][j] != 1 and new_tiles[i][j] != 1:
                continue
            number = board[i][j]
            if number == 0:
                print(f"ERROR: missing tile {i}, {j} during merge")
                continue
            pygame.draw.rect(
                screen,
                TILE_COLORS[number],
                (
                    i * (TILE_SIZE + GAP) + GAP - diff / 2,
                    j * (TILE_SIZE + GAP) + GAP + TOP_GAP - diff / 2,
                    new_tile_size,
                    new_tile_size,
                ),
                border_radius=int(BORDER_RADIUS + diff / 2),
            )
            font = pygame.font.Font("freesansbold.ttf", 32)
            text = font.render(str(2 ** board[i][j]), True, "black")
            textRect = text.get_rect()
            textRect.center = (
                i * (TILE_SIZE + GAP) + 90,
                j * (TILE_SIZE + GAP) + 90 + TOP_GAP,
            )
            screen.blit(text, textRect)


def render_board(engine, screen, clock, action, score):
    """Renders the board to the screen."""
    board = engine.board
    old_board = engine.old_board
    move_map = engine.move_map
    for step in range(ANIMATION_STEPS_MOVE):
        render_background(screen, score)
        render_move(old_board, move_map, screen, step, action)
        pygame.display.flip()
        clock.tick(60)

    for step in range(ANIMATION_STEPS_MERGE):
        render_background(screen, score)
        render_tiles(board, screen)
        render_merge(
            board,
            engine.just_merged,
            engine.new_tiles,
            step,
            screen,
        )
        pygame.display.flip()
        clock.tick(60)

    return screen, random.random() > 0.99
