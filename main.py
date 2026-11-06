from evoengine import SimConfig, RngBundle, World, Env, Agent, view_simulation

headless = True

def simulate(headless, cfg):
    rng = RngBundle(cfg.seed)
    world = World(cfg, rng)
    env = Env(cfg, rng, world)

    cord=world.size//2
    for i in range(6):
        env.add_agent(Agent(cfg, rng, x=cord+i, y=cord))

    if headless:
        while True:
            agents_count = len(env.agents)
            if agents_count > 0:
                env.step()
            else:
                print(f"=== SEED: {cfg.seed} --- MAX_TIME: {env.world.time} ===") 
                break
    else:
        view_simulation(env)

for s in range(101):
    cfg = SimConfig(seed=s)
    simulate(headless, cfg)