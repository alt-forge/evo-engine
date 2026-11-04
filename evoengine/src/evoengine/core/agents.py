import numpy as np

from .actions import Action
from .config import SimConfig
from .rng import RngBundle

class NeuralNetwork:
    @staticmethod
    def softmax(x):
        e = np.exp(x - np.max(x))
        return e / e.sum()

    def __init__(self, cfg: SimConfig, rng: RngBundle):
        self.cfg = cfg
        self.rng = rng
        self.W1 = rng.init_weight.standard_normal((cfg.input_size, cfg.hidden_size_1))
        self.W2 = rng.init_weight.standard_normal((cfg.hidden_size_1, cfg.hidden_size_2))
        self.W3 = rng.init_weight.standard_normal((cfg.hidden_size_2, Action.size()))

    def forward(self, x: np.ndarray):
        h1 = np.tanh(x @ self.W1)
        h2 = np.tanh(h1 @ self.W2)
        return h2 @ self.W3

    def choice_action(self, vision: np.ndarray):
        logits = self.forward(vision)
        probs = self.softmax(logits)
        return self.rng.action.choice(len(probs), p=probs)
    
    def mutate(self):
        for W in [self.W1, self.W2, self.W3]:
            mutation_rate = 1 / W.size
            mutation_mask = self.rng.mutation.random(size=W.shape) < mutation_rate
            W += mutation_mask * self.rng.mutation.standard_normal(size=W.shape)

class Agent:
    def __init__(self, cfg: SimConfig, rng: RngBundle, x: int, y: int, hp: float | None = None):
        self.cfg = cfg
        self.rng = rng
        self.x = x
        self.y = y
        self.hp = cfg.starting_hp if hp is None else hp
        self.age = 0
        self.agent_id = 0
        self.nn = NeuralNetwork(cfg, rng)
    
    def decide(self, observation: list[int]):
        vision = np.array(observation + [self.hp / self.cfg.max_hp, self.age / self.cfg.age_limit]) # Набор чувств агента (observation из env и самоощущение)
        return Action(self.nn.choice_action(vision))

    def move_to(self, coordinates: tuple[int,int]):
        self.x, self.y = coordinates[0], coordinates[1]

    def take_damage(self, value: int | float):
        self.hp -= value

    def add_hp(self, value: int | float):
        self.hp = min(self.hp + value, self.cfg.max_hp)

    def set_id(self, id: int):
        self.agent_id = id

    def up_age(self):
        self.age += 1

    def create_offspring(self, cell: tuple[int,int]):
        x,y = cell
        offspring = Agent(self.cfg, self.rng, x, y, hp=self.cfg.offspring_starting_hp)
        offspring.nn.W1 = np.copy(self.nn.W1)
        offspring.nn.W2 = np.copy(self.nn.W2)
        offspring.nn.W3 = np.copy(self.nn.W3)
        offspring.nn.mutate()
        return offspring