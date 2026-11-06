from evoengine import SimConfig, RngBundle, World, Env, Agent, CellType
import pandas as pd
from itertools import product
import os
from multiprocessing import Pool, cpu_count


def simulate(args: tuple) -> dict:
    """Один прогон. args = (grid_dict, seed, max_steps)."""
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
        "extinct": len(env.agents) == 0,
        "survived": len(env.agents) > 0,
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

    with Pool(processes=processes) as pool:
        rows = []
        for i, res in enumerate(pool.imap_unordered(simulate, grid_runs, chunksize=1), 1):
            rows.append(res)
            if i % 10 == 0 or i == len(grid_runs):
                print(f"  {i}/{len(grid_runs)}")

    df = pd.DataFrame(rows)
    df.to_csv(f"{out}/experiment_1.csv", index=False)
    print(f"Saved: {out}/experiment_1.csv")
    return df


if __name__ == "__main__":
    setting_1 = {
        "vision_range": [3, 5],
        "hidden_size_1": [16, 32],
    }
    seeds = list(range(5))
    df = experiment(setting_1, seeds, max_steps=20_000, processes=os.cpu_count())