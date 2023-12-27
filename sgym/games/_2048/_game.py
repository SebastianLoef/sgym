import random
from typing import Callable, Optional

import numpy as np
import numpy.typing as npt
import torch
from tensordict import TensorDict, TensorDictBase
from torchrl.data import BoundedTensorSpec, CompositeSpec, UnboundedContinuousTensorSpec
from torchrl.envs import EnvBase

from ._game_logic import calc_step, reset
from ._render import Renderer


def make_composite_from_td(td: TensorDictBase):
    # custom function to convert a ``tensordict`` in a similar spec structure
    # of unbounded values.
    composite = CompositeSpec(
        {
            key: make_composite_from_td(tensor)
            if isinstance(tensor, TensorDictBase)
            else UnboundedContinuousTensorSpec(
                dtype=tensor.dtype, device=tensor.device, shape=tensor.shape
            )
            for key, tensor in td.items()
        },
        shape=td.shape,
    )
    return composite


def _make_spec(self, td_params: TensorDictBase):
    # Under the hood, this will populate self.output_spec["observation"]
    self.observation_spec = CompositeSpec(
        board=BoundedTensorSpec(
            low=-0,
            high=20,
            shape=torch.Size([1]),
            dtype=torch.int8,
        ),
        # we need to add the ``params`` to the observation specs, as we want
        # to pass it at each step during a rollout
        params=make_composite_from_td(td_params["params"]),
        shape=(),
    )
    # since the environment is stateless, we expect the previous output as input.
    # For this, ``EnvBase`` expects some state_spec to be available
    self.state_spec = self.observation_spec.clone()
    # action-spec will be automatically wrapped in input_spec when
    # `self.action_spec = spec` will be called supported
    self.action_spec = BoundedTensorSpec(
        low=1,
        high=4,
        shape=1,
        dtype=torch.int8,
    )
    self.reward_spec = UnboundedContinuousTensorSpec(
        shape=torch.Size((*td_params.shape, 1))
    )


def _gen_params(self, batch_size: int | torch.Size | None = None) -> TensorDictBase:
    """Returns a ``tensordict`` containing the physical parameters such as
    gravitational force and torque or speed limits."""
    batch_size = torch.Size([1])
    td = TensorDict(
        {
            "params": TensorDict(
                {},
                [1],
            )
        },
        [1],
    )
    if batch_size:
        td = td.expand(batch_size).contiguous()
    return td


def _step(self, tensordict: TensorDictBase) -> TensorDictBase:
    board: npt.NDArray[np.int8] = tensordict["board"]
    action: int = tensordict["action"]

    self.state.board = board
    self.state.action = action
    self.state = calc_step(self.state, action)
    out = self.state.to_tensordict(tensordict.shape)
    return out


def _reset(self, tensordict: Optional[TensorDictBase]) -> TensorDictBase:
    """Resets the environment and returns the initial observation."""
    if tensordict is None or tensordict.is_empty():
        # if no ``tensordict`` is passed, we generate a single set of hyperparameters
        # Otherwise, we assume that the input ``tensordict`` contains all the relevant
        # parameters to get started.
        tensordict = self.gen_params(batch_size=self.batch_size)
    self.state = reset()
    return self.state.to_tensordict(tensordict.shape)


def _set_seed(self, seed: Optional[int]):
    rng = torch.manual_seed(seed)
    self.rng = rng


class Environment(EnvBase):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 30,
    }
    batch_locked: bool = False
    batch_size: torch.Size = torch.Size([1])
    _make_spec = _make_spec
    gen_params = _gen_params

    def __init__(self, td_params=None, seed: int | None = None, device="cpu"):
        if td_params is None:
            td_params = self.gen_params()

        super().__init__(device=device, batch_size=td_params.batch_size)
        self._make_spec(td_params)
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
        self.set_seed(seed)

    # Mandatory methods: _step, _reset and _set_seed
    _reset = _reset
    _step: Callable = _step
    _set_seed = _set_seed

    def render(self):
        # check if self.render_logic is defined
        if not hasattr(self, "renderer"):
            self.renderer = Renderer()
        self.renderer.render(self.state)
