import os
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from .core import (
    SimConfig, RngBundle, Action, ACTION_DELTAS,
    Agent, NeuralNetwork, CellType, World, Env,
)
from .view import view_simulation

__all__ = [
    "SimConfig", "RngBundle", "Action", "ACTION_DELTAS",
    "CellType", "Agent", "NeuralNetwork", "World", "Env",
    "view_simulation",
]