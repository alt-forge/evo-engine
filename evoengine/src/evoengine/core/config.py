from dataclasses import dataclass

@dataclass(frozen=True)
class SimConfig:
    # Мир
    world_size: int = 100
    seed: int = 100
    wall_count: int = 250

    # Еда
    food_cluster_count: int = 5
    food_per_spawn: int = 10
    food_cluster_radius: int = 3
    food_respawn_period: int = 15
    food_cluster_capacity: int = 100

    # Агенты
    starting_hp: float = 100.0
    max_hp: float = 200.0
    age_limit: int = 500
    initial_population: int = 100

    # Нейросеть
    vision_range: int = 5
    hidden_size_1: int = 21
    hidden_size_2: int = 12

    # Метаболизм
    damage_per_step: float = 0.25
    damage_per_move: float = 0.15
    food_value: float = 10.0

    # Размножение
    offspring_cost: float = 60.0
    offspring_starting_hp: float = 40.0
    reproduction_threshold: float = 100.0

    # Производные поля
    input_size: int = 0
    wall_hit_cost: float = 0.0

    def __post_init__(self):
        object.__setattr__(self, "input_size", self.vision_range * 4 + 2)
        object.__setattr__(self, "wall_hit_cost", self.damage_per_move * 2)