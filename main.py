from evoengine import SimConfig, RngBundle, World, Env, Agent, view_simulation

cfg = SimConfig(world_size=75, seed=0)
rng = RngBundle(cfg.seed)
world = World(cfg, rng)
env = Env(cfg, rng, world)

cord=world.size//2
for i in range(6):
    env.add_agent(Agent(cfg, rng, x=cord+i, y=cord))

headless = False

if headless:
    while True:
        agents_count = len(env.agents)
        if agents_count > 0:
            env.step()
            print(agents_count, env.world.time)
        else: break
else:
    view_simulation(env, zoom=8, speed=1)
