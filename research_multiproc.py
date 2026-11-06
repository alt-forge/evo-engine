from evoengine import SimConfig, RngBundle, World, Env, Agent, CellType
import pandas as pd
from itertools import product
import os, time
from multiprocessing import Pool, cpu_count

def simulate(args: tuple) -> dict:
    grid, seed, max_steps = args
    cfg = SimConfig(**grid, seed=seed)

    rng = RngBundle(cfg.seed)
    world = World(cfg, rng)
    env = Env(cfg, rng, world)

    for _ in range(cfg.initial_population):
        x = int(rng.gui_spawn.integers(1, world.size - 1))
        y = int(rng.gui_spawn.integers(1, world.size - 1))
        if world.grid[x, y] == CellType.EMPTY:
            env.add_agent(Agent(cfg, rng, x=x, y=y))

    while env.agents and env.world.time < max_steps:
        env.step()

    return {
        **grid,
        "seed": seed,
        "death_time": env.world.time,
        "agents_in_env_for_all_time": env.id_for_agent,
    }


def experiment(settings: dict, seeds: list[int], max_steps: int = 20_000,
               out: str = "experiments",
               processes: int | None = None) -> pd.DataFrame:
    os.makedirs(out, exist_ok=True)

    names = list(settings)
    grid_runs = [
        (dict(zip(names, combo)), seed, max_steps)
        for combo in product(*settings.values())
        for seed in seeds
    ]

    processes = processes or max(1, cpu_count() - 1)
    print(f"Running {len(grid_runs)} sims on {processes} processes")

    start_time = time.time()
    with Pool(processes=processes) as pool:
        rows = []
        for i, res in enumerate(pool.imap_unordered(simulate, grid_runs, chunksize=1), 1):
            rows.append(res)
            if i % 10 == 0 or i == len(grid_runs):
                print(f"  {i}/{len(grid_runs)} ~{(len(grid_runs) - i) * (time.time() - start_time) / i / 60:.1f} minutes")

    df = pd.DataFrame(rows)
    df.to_csv(f"{out}/experiment_1.csv", index=False)
    print(f"Saved: {out}/experiment_1.csv")
    return df


if __name__ == "__main__":
    setting_1 = {
        "damage_per_step": [0.20, 0.15, 0.10, 0.05, 0.01],
        "damage_per_move": [0.15, 0.10, 0.05, 0.01],
        "food_cluster_count": [5,6,7,8,9,10],
        "food_per_spawn": [10,15,20],
        "food_cluster_capacity": [80,100,120],
        "food_respawn_period": [10,15,20]
    }
    seeds = list(range(25))
    df = experiment(setting_1, seeds, max_steps=20000, processes=os.cpu_count())