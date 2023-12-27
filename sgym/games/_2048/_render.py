import math

import numpy as np
import numpy.typing as npt
import pygame

from ._game_logic import GameState

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


class Renderer:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self._init_fonts()

    def _init_fonts(self) -> None:
        """Initializes the fonts."""
        self._font_score_text = pygame.font.Font(FONT, 50)
        self._font_score = pygame.font.Font(FONT, 40)
        self._font_tiles = pygame.font.Font(FONT, 32)

    def render(self, gamestate: GameState) -> None:
        self._render_board(gamestate, self.clock)

    def _render_board(self, gamestate: GameState, clock: pygame.time.Clock):
        """Renders the board to the screen."""
        board = gamestate.board
        score = gamestate.score
        for step in range(ANIMATION_STEPS_MOVE):
            self._render_background(score)
            self._render_move(gamestate, step)
            pygame.display.flip()
            clock.tick(60)

        for step in range(ANIMATION_STEPS_MERGE):
            self._render_background(score)
            self._render_tiles(board)
            render_merge(
                board,
                gamestate.merged,
                gamestate.new_tiles,
                step,
                self.screen,
            )
            pygame.display.flip()
            clock.tick(60)

    def _render_background_tiles(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        for i in range(4):
            for j in range(4):
                pygame.draw.rect(
                    self.screen,
                    EMPTY_TILE_COLOR,
                    rect_tuple(i, j),
                    border_radius=BORDER_RADIUS,
                )

    def _render_score(self, score: int) -> None:
        """Renders the score to the screen."""
        text = self._font_score_text.render("Score: ", True, TEXT_COLOR)
        textRect = text.get_rect()
        textRect.center = (100, 45)
        self.screen.blit(text, textRect)
        pygame.draw.rect(self.screen, EMPTY_TILE_COLOR, (200, 20, 200, 60))
        text = self._font_score.render(str(score), True, TEXT_COLOR)
        textRect = text.get_rect()
        setattr(textRect, "topright", (380, 40))
        self.screen.blit(text, textRect)

    def _render_background(self, score: int) -> None:
        """Renders the background to the screen."""
        self._render_background_tiles()
        self._render_score(score)

    def _render_tile_text(self, number: int, i: float | int, j: float | int) -> None:
        text = self._font_tiles.render(str(2**number), True, "black")
        textRect = text.get_rect()
        textRect.center = (
            int(i * (TILE_SIZE + GAP) + 90),
            int(j * (TILE_SIZE + GAP) + 90 + TOP_GAP),
        )
        self.screen.blit(text, textRect)

    def _render_tile(self, number: int, i: int | float, j: int | float) -> None:
        pygame.draw.rect(
            self.screen,
            TILE_COLORS[number],
            rect_tuple(i, j),
            border_radius=BORDER_RADIUS,
        )

    def _render_tiles(self, board: npt.NDArray[np.int8]):
        """Renders the tiles to the screen."""
        for i in range(4):
            for j in range(4):
                if board[i][j] != 0:
                    self._render_tile(board[i][j], i, j)
                    self._render_tile_text(board[i][j], i, j)

    def _render_move(self, gamestate: GameState, step: int) -> None:
        column, direction = get_move_direction(gamestate.action)
        for i in range(4):
            for j in range(4):
                if gamestate.board[i][j] == 0:
                    continue
                i_pos, j_pos = get_float_pos(
                    i, j, gamestate.move_map[i][j], step, gamestate.action
                )
                self._render_tile(gamestate.board[i][j], i_pos, j_pos)
                self._render_tile_text(gamestate.board[i][j], i_pos, j_pos)


def get_float_pos(
    i: int | float, j: int | float, orig_pos, step: float, action: int
) -> tuple[float, float]:
    column, direction = get_move_direction(action)
    i_pos = float(i) + column * direction * orig_pos * step / ANIMATION_STEPS_MOVE
    j_pos = float(j) + (1 - column) * direction * orig_pos * step / ANIMATION_STEPS_MOVE
    return i_pos, j_pos


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


def get_move_direction(action: int) -> tuple[int, int]:
    if action == 0:
        return 0, -1
    if action == 1:
        return 1, -1
    if action == 2:
        return 0, 1
    return 1, 1
