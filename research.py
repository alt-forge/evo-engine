from evoengine import SimConfig, RngBundle, World, Env, Agent, CellType
import pandas as pd
from itertools import product
import os

def simulate(cfg, MAX_STEPS):
    rng = RngBundle(cfg.seed)
    world = World(cfg, rng)
    env = Env(cfg, rng, world)

    for _ in range(cfg.initial_population):
        x = int(rng.gui_spawn.integers(1, world.size - 1))
        y = int(rng.gui_spawn.integers(1, world.size - 1))
        if world.grid[x, y] == CellType.EMPTY:
            env.add_agent(Agent(cfg, rng, x=x, y=y))

    while True:
        agents_count = len(env.agents)
        if agents_count > 0 and (env.world.time <= MAX_STEPS):
            env.step()
        else:
            return {
            "death_time": env.world.time,
            "agents_in_env_for_all_time": env.id_for_agent
        }

def experiment(settings: dict, seeds: list[int], max_steps: int = 20000,
               out: str = "experiments") -> pd.DataFrame:
    
    if not os.path.isdir(out):
        os.mkdir("experiments")

    names = list(settings)
    rows = []
    for combo in product(*settings.values()):
        grid = dict(zip(names, combo))
        for seed in seeds:
            cfg = SimConfig(**grid, seed=seed)
            rows.append({**grid, "seed": seed, **simulate(cfg, max_steps)})

    df = pd.DataFrame(rows)
    df.to_csv(f'{out}/experiment_1.csv', index=False)
    return df


# В setting нужно указывать какую настройку и на каком диапозоне мы изменяем
setting_1 = {
    "vision_range": [3,5],
    "hidden_size_1": [16,32]
}

# На каких сидах мы проверяем
seeds = list(range(5))

df = experiment(setting_1,seeds)
