from evoengine import SimConfig, RngBundle, World, Env, Agent, CellType, view_simulation

def simulate(headless, cfg):
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
            if agents_count > 0 and (env.world.time < 10000):
                print(agents_count, env.world.time)
                env.step()
            else:
                break
    else:
        view_simulation(env)

headless = True
cfg = SimConfig(seed=82)
simulate(headless, cfg)