import numpy as np

class RngBundle:
    def __init__(self, seed: int):
        self.reseed(seed)

    def reseed(self, seed: int):
        self.env_wall = np.random.default_rng(seed)
        self.env_food_spawn = np.random.default_rng(seed + 1)
        self.env_food_respawn = np.random.default_rng(seed + 2)
        self.init_weight = np.random.default_rng(seed + 3)
        self.action = np.random.default_rng(seed + 4)
        self.mutation = np.random.default_rng(seed + 5)
        self.offspring_spawn = np.random.default_rng(seed + 6)
        self.food_move = np.random.default_rng(seed + 7)
        self.empty_move = np.random.default_rng(seed + 8)
        self.gui_spawn = np.random.default_rng(seed + 9)