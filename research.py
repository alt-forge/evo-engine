from evoengine import SimConfig, RngBundle, World, Env, Agent, view_simulation, CellType
import pandas as pd
import numpy as np

headless = True

def simulate(headless, cfg):
    MAX_STEPS = 20000
    rng = RngBundle(cfg.seed)
    world = World(cfg, rng)
    env = Env(cfg, rng, world)

    for _ in range(cfg.initial_population):
        x = int(rng.gui_spawn.integers(1, world.size - 1))
        y = int(rng.gui_spawn.integers(1, world.size - 1))
        if world.grid[x, y] == CellType.EMPTY:
            env.add_agent(Agent(cfg, rng, x=x, y=y))

    if headless:
        while True:
            agents_count = len(env.agents)
            if agents_count > 0 and (env.world.time < MAX_STEPS):
                env.step()
            else:
                return env.world.time
    else:
        view_simulation(env)

results = []

vr_l = [3,5,7,10]
h1_l = [8,16,32,64,128]
h2_l = [8,16,32,64,128]

for vr in vr_l:
    for h1 in h1_l:
        for h2 in h2_l:
            print(f"SIMULATION: vision_range={vr}, hidden_size_1={h1}, hidden_size_2={h2}")
            for s in range(1):
                cfg = SimConfig(seed=s, vision_range=vr, hidden_size_1=h1, hidden_size_2=h2)
                max_time = simulate(headless, cfg)
                results.append({
                    "seed": s,
                    "vision_range": vr,
                    "hidden_size_1": h1,
                    "hidden_size_2": h2,
                    "max_time": max_time
                })

df = pd.DataFrame(results)
df.to_csv("experiments.csv", index=False)