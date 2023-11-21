import numpy as np
import pygame
from ._render import render_board
import sys
import random


class Environment:
    def __init__(self, render: bool) -> None:
        self.engine = Engine()
        self.reset()
        self.render = render
        if render:
            # pygame setup
            pygame.init()
            self.screen = pygame.display.set_mode((720, 720))
            self.clock = pygame.time.Clock()
            self.running = True
            render_board(self.engine, self.screen, self.clock, None)

    def quit_rendering(self):
        if self.render:
            pygame.quit()
            sys.exit()
            self.render = False

    def reset(self):
        self.engine.reset()
        return self.engine.board

    def step(self, action):
        if action is None:
            return
        self.engine.step(action)

        if self.render:
            anim_complete = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_rendering()
            self.screen, anim_complete = render_board(
                self.engine,
                self.screen,
                self.clock,
                action
            )

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

    def step(self, action: int):
        self.old_board = self.board
        board = self.board.copy()
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

        if np.array_equal(board, self.board):
            self.just_merged = np.zeros((4, 4), dtype=int)
            self.move_map = np.zeros((4, 4), dtype=int)
            self.new_tiles = np.zeros((4, 4), dtype=int)
            return

        self.board = board
        self.move_map = move_map
        self.just_merged = just_merged

        loc_new_tile = self._get_empty_tile()
        self.board[*loc_new_tile] = self._get_new_number()

        self.new_tiles = np.zeros((4, 4), dtype=int)
        self.new_tiles[*loc_new_tile] = 1

