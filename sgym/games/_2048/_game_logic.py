import random
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import torch
from tensordict import TensorDict, TensorDictBase

VALID_MOVES = [0, 1, 2, 3]


@dataclass
class GameState:
    board: npt.NDArray[np.int8]
    old_board: npt.NDArray[np.int8]
    move_map: npt.NDArray[np.int8]
    merged: npt.NDArray[np.int8]
    new_tiles: npt.NDArray[np.int8]
    action: int
    score: int
    done: bool

    def to_tensordict(self, shape: int | torch.Size) -> TensorDictBase:
        out = TensorDict(
            {
                "board": self.board,
                "score": self.score,
                "done": self.done,
            },
            shape,
        )
        return out


def reset() -> GameState:
    board = np.zeros((4, 4), dtype=np.int8)
    score = 0
    done = False
    for _ in range(2):
        loc_new_tile = _get_empty_tile(board)
        board[*loc_new_tile] = _get_new_tile()
    return GameState(
        board=board,
        old_board=board,
        move_map=np.zeros((4, 4), dtype=int),
        merged=np.zeros((4, 4), dtype=int),
        new_tiles=np.zeros((4, 4), dtype=int),
        action=0,
        score=score,
        done=done,
    )


def _check_if_done(state: GameState) -> bool:
    """Checks if done by trying all moves and seeing if any of them change the
    board."""
    for action in VALID_MOVES:
        new_state = _do_step_action(state, action)
        if not np.array_equal(new_state.board, state.board):
            return False
    return True


def _score(state: GameState) -> int:
    return np.sum(state.merged * 2**state.board).astype(int)


def _get_new_tile() -> int:
    return 1 if random.random() < 0.9 else 2


def _get_empty_tiles(board: npt.NDArray[np.int8]) -> npt.NDArray[np.int8]:
    return np.argwhere(board == 0)


def _get_empty_tile(board: npt.NDArray[np.int8]) -> tuple[int, int]:
    return random.choice(_get_empty_tiles(board))


def _move_row(
    row: npt.NDArray[np.int8], action: int
) -> tuple[npt.NDArray[np.int8], npt.NDArray[np.int8], npt.NDArray[np.int8]]:
    """Moves a row to the left and returns the new row, the move map and the
    merge_map."""
    new_row = np.zeros(4, dtype=np.int8)
    move_map_row = np.zeros(4, dtype=np.int8)
    merged_row = np.zeros(4, dtype=np.int8)

    last_i = 0
    new_row[0] = row[0]
    for i, val in enumerate(row[1:]):
        i += 1
        if val == 0:
            continue
        if new_row[last_i] == val:
            new_row[last_i] = val + 1
            move_map_row[i] = i - last_i
            merged_row[last_i] = 1
            last_i += 1
        elif new_row[last_i] == 0:
            new_row[last_i] = val
            move_map_row[i] = i - last_i
        else:
            new_row[last_i + 1] = val
            move_map_row[i] = i - last_i - 1
            last_i += 1
    return new_row, move_map_row, merged_row


def _do_step_action(state: GameState, action: int) -> GameState:
    """Calculates the board after the action."""
    state.old_board = state.board.copy()
    board = np.rot90(state.board, action)
    move_map = np.zeros(state.board.shape, dtype=int)
    merged = np.zeros(state.board.shape, dtype=int)
    for i in range(4):
        row = state.board[i]
        filled_row = sum(row != 0)
        if filled_row == 0:
            continue
        if filled_row > 0:
            state.board[i], move_map[i], merged[i] = _move_row(row, action)
    state.board = np.rot90(board, -action)
    state.move_map = np.rot90(move_map, -action)
    state.merged = np.rot90(merged, -action)
    return state


def calc_step(state: GameState, action: int) -> GameState:
    """Performs one step of the game."""
    state = _do_step_action(state, action)

    if np.array_equal(state.board, state.old_board):
        state.merged = np.zeros((4, 4), dtype=int)
        state.move_map = np.zeros((4, 4), dtype=int)
        state.new_tiles = np.zeros((4, 4), dtype=int)
        state.done = len(_get_empty_tiles(state.board)) == 0 and _check_if_done(state)
    else:
        state.score = _score(state)
        loc_new_tile = _get_empty_tile(state.board)
        state.board[*loc_new_tile] = _get_new_tile()
        state.new_tiles[*loc_new_tile] = 1

    return state
