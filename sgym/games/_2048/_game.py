import random

import numpy as np
import numpy.typing as npt
import pygame

from ._render import HEIGHT, WIDTH, render_board


def added_function():
    print("Hello from added function!")


class Environment:
    def __init__(self, render: bool) -> None:
        self.engine = Engine()
        self.total_score = 0
        self.reset()
        self._render = render
        if render:
            self._init_render()

    def quit_rendering(self):
        pygame.quit()
        self._render = False

    def _init_render(self):
        if self._render:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
            self.running = True
            render_board(self.engine, self.screen, self.clock, None, 0)

    @property
    def render(self):
        return self._render

    @render.setter
    def render(self, render):
        self._render = render
        if render:
            self._init_render()
            self.screen, _ = render_board(self.engine, self.screen, self.clock, None, 0)
        else:
            self.quit_rendering()

    def _return_board(self):
        return tuple(tuple(row) for row in self.engine.board)

    def reset(self):
        self.engine.reset()
        self.total_score = 0
        return self._return_board()

    def get_actions(self):
        return [0, 1, 2, 3]

    def step(self, action):
        done = False
        if action is None:
            return done, -1
        done, score = self.engine.step(action)
        self.total_score += score

        if self._render:
            anim_complete = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_rendering()
            self.screen, anim_complete = render_board(
                self.engine, self.screen, self.clock, action, self.total_score
            )
        reward = score
        # observation, reward, terminated, truncated, info
        return self._return_board(), reward, done, False, {"score": self.total_score}


class Engine:
    def __init__(self):
        self.board = np.zeros((4, 4), dtype=int)
        self.old_board = np.zeros((4, 4), dtype=int)
        self.move_map = np.zeros((4, 4), dtype=int)
        self.just_merged = np.zeros((4, 4), dtype=int)
        self.new_tiles = np.zeros((4, 4), dtype=int)
        # pygame setup

    def _get_new_number(self):
        return 1 if random.random() < 0.9 else 2

    def _get_empty_tiles(self):
        return np.argwhere(self.board == 0)

    def _get_empty_tile(self):
        return random.choice(self._get_empty_tiles())

    def reset(self):
        self.board = np.zeros((4, 4), dtype=int)
        self.new_tiles = np.zeros((4, 4), dtype=int)
        loc = self._get_empty_tile()
        self.new_tiles[*loc] = 1
        self.board[*loc] = self._get_new_number()
        loc = self._get_empty_tile()
        self.board[*loc] = self._get_new_number()
        self.new_tiles[*loc] = 1
        self.old_board = self.board

        self.move_map = np.zeros((4, 4), dtype=int)
        self.just_merged = np.zeros((4, 4), dtype=int)
        self.new_tiles = np.zeros((4, 4), dtype=int)

    def _get_valid_moves(self):
        return [0, 1, 2, 3]

    def move_seq(self, row, dir):
        new_row = np.zeros(4, dtype=int)
        move_map_row = np.zeros(4, dtype=int)
        just_merged_row = np.zeros(4, dtype=int)

        last_i = 0
        new_row[0] = row[0]
        for i, val in enumerate(row[1:]):
            i += 1
            if val == 0:
                continue
            if new_row[last_i] == val:
                new_row[last_i] = val + 1
                move_map_row[i] = i - last_i
                just_merged_row[last_i] = 1
                last_i += 1
            elif new_row[last_i] == 0:
                new_row[last_i] = val
                move_map_row[i] = i - last_i
            else:
                new_row[last_i + 1] = val
                move_map_row[i] = i - last_i - 1
                last_i += 1
        return new_row, move_map_row, just_merged_row

    def _score(self):
        return np.sum(self.just_merged * 2**self.board).item()

    def _check_if_done(self):
        """Checks if done by trying all moves and seeing if any of them change
        the board."""
        for action in self._get_valid_moves():
            board, _, _, _ = self._step(action, self.board)
            if not np.array_equal(board, self.board):
                return False
        return True

    def _step(self, action: int, board: npt.NDArray):
        old_board = board
        board = board.copy()
        move_map = np.zeros((4, 4), dtype=int)
        just_merged = np.zeros((4, 4), dtype=int)

        board = np.rot90(board, action)
        for i in range(4):
            row = board[i]
            filled_row = sum(row != 0)
            if filled_row == 0:
                continue
            if filled_row > 0:
                new_row, move_map_row, just_merged_row = self.move_seq(row, action)
                board[i] = new_row
                move_map[i] = move_map_row
                just_merged[i] = just_merged_row

        board = np.rot90(board, -action)
        move_map = np.rot90(move_map, -action)
        just_merged = np.rot90(just_merged, -action)
        return board, old_board, move_map, just_merged

    def step(self, action: int):
        board, old_board, move_map, just_merged = self._step(action, self.board)
        self.old_board = old_board
        if np.array_equal(board, old_board):
            self.just_merged = np.zeros((4, 4), dtype=int)
            self.move_map = np.zeros((4, 4), dtype=int)
            self.new_tiles = np.zeros((4, 4), dtype=int)
            if len(self._get_empty_tiles()) == 0 and self._check_if_done():
                return True, self._score()
            return False, self._score()

        self.old_board = self.board
        self.board = board
        self.move_map = move_map
        self.just_merged = just_merged

        loc_new_tile = self._get_empty_tile()
        self.board[*loc_new_tile] = self._get_new_number()

        self.new_tiles = np.zeros((4, 4), dtype=int)
        self.new_tiles[*loc_new_tile] = 1

        return False, self._score()
