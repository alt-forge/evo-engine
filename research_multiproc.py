from evoengine import SimConfig, RngBundle, World, Env, Agent, CellType
import pandas as pd
from itertools import product
import os, time
import numpy as np
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

    if env.agents:
        agents_list = list(env.agents.values())
        
        w1_norms = [np.linalg.norm(a.nn.W1) for a in agents_list]
        w2_norms = [np.linalg.norm(a.nn.W2) for a in agents_list]
        w3_norms = [np.linalg.norm(a.nn.W3) for a in agents_list]

        mean_w1 = float(np.mean(w1_norms))
        mean_w2 = float(np.mean(w2_norms))
        mean_w3 = float(np.mean(w3_norms))
        
        std_w1 = float(np.std(w1_norms))
        std_w2 = float(np.std(w2_norms))
        std_w3 = float(np.std(w3_norms))

    else:
        mean_w1 = mean_w2 = mean_w3 = 0.0
        std_w1 = std_w2 = std_w3 = 0.0

    return {
        **grid,
        "seed": seed,
        "death_time": env.world.time,
        "agents_in_env_for_all_time": env.id_for_agent,
        "mean_W1": mean_w1,
        "mean_W2": mean_w2,
        "mean_W3": mean_w3,
        "std_W1": std_w1,
        "std_W2": std_w2,
        "std_W3": std_w3
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
    df.to_csv(f"{out}/experiment_3.csv", index=False)
    print(f"Saved: {out}/experiment_3.csv")
    return df

if __name__ == "__main__":
    setting_1 = {}
    seeds = [32,36,44,82]
    df = experiment(setting_1, seeds, max_steps=50000, processes=(os.cpu_count()))