import numpy as np

from .agents import Agent
from .rng import RngBundle
from .actions import Action, ACTION_DELTAS
from .config import SimConfig
from .cells import CellType

class FoodCluster:
    def __init__(self, cx, cy, radius, capacity):
            self.cx = cx
            self.cy = cy
            self.radius = radius
            self.capacity = capacity

    def set_capacity(self,delta):
        self.capacity += delta

    def set_center(self, new_cx, new_cy):
        self.cx = new_cx
        self.cy = new_cy

    def is_active(self):
        return self.capacity > 0

    def food_spawn(self, rng: RngBundle):
        x = self.cx + rng.foods_spawn.integers(-self.radius, self.radius + 1)
        y = self.cy + rng.foods_spawn.integers(-self.radius, self.radius + 1)
        return x,y

class World:
    def __init__(self, cfg: SimConfig, rng: RngBundle):
        self.cfg = cfg
        self.rng = rng
        self.size = cfg.world_size
        self.time = 0
        self.grid = np.zeros((self.size, self.size), dtype=int)
        self.food_clusters = []
        self._create_world_assets()

    def set_cell(self, cell: tuple[int,int], value: CellType | int):
        x, y = cell
        self.grid[x,y] = value

    def _create_world_assets(self):
        self._create_walls()
        self._create_food_clusters()

    def _create_walls(self):
        for _ in range(self.cfg.wall_count):
            x = self.rng.env_wall.integers(1, self.size-1)
            y = self.rng.env_wall.integers(1, self.size-1)
            self.grid[x, y] = CellType.WALL

    def _create_food_clusters(self):
        for _ in range(self.cfg.food_cluster_count):
            # Центр кластера может быть внутри стены, просто еда не будет расти в этой клете, будто бы дерево растет из под асфальта
            cx = self.rng.food_clusters_spawn.integers(1, self.size-1)
            cy = self.rng.food_clusters_spawn.integers(1, self.size-1)
            self.food_clusters.append(FoodCluster(cx, cy, self.cfg.food_cluster_radius, self.cfg.food_cluster_capacity))


    def update_food_clusters(self):
        for food_cluster in self.food_clusters:
            if food_cluster.is_active():
                for _ in range(self.cfg.food_per_spawn):
                    x,y = food_cluster.food_spawn(self.rng)
                    if (0 < x < self.size-1) and (0 < y < self.size-1) and (self.grid[x, y] == CellType.EMPTY):
                        self.grid[x, y] = CellType.FOOD
                        food_cluster.set_capacity(-1)
            else:
                cx = self.rng.food_clusters_set_spawn.integers(1, self.size-1)
                cy = self.rng.food_clusters_set_spawn.integers(1, self.size-1)
                food_cluster.set_center(cx,cy)
                food_cluster.set_capacity(self.cfg.food_cluster_capacity)


class Env:
    def __init__(self, cfg: SimConfig, rng: RngBundle, world: World):
        self.cfg = cfg
        self.rng = rng
        self.world = world
        self.agents = {}
        self.id_for_agent = 0 # ID следующего агента в среде

    def set_agent_id(self, agent: Agent):
        agent.set_id(self.id_for_agent)
        self.id_for_agent += 1 

    def set_agent_coords(self, agent: Agent, target: tuple[int,int]):
        old_coords = (agent.x, agent.y)
        if old_coords in self.agents:
            del self.agents[old_coords]
            agent.move_to(target)
            self.agents[target] = agent

    def add_agent(self, agent: Agent):
        cell = (agent.x, agent.y)
        if not(cell in self.agents):
            self.set_agent_id(agent)
            self.agents[(agent.x, agent.y)] = agent
    
    def del_agent(self, agent: Agent):
        cell = (agent.x, agent.y)
        if cell in self.agents:
            del self.agents[(agent.x, agent.y)]

    def cell_type(self, cell: tuple[int,int], agents_map = None, grid = None) -> CellType:
            x, y = cell

            if agents_map is None: agents_map = self.agents
            if grid is None: grid = self.world.grid

            if (x, y) in agents_map:
                return CellType.AGENT
            if 0 <= x < self.world.size and 0 <= y < self.world.size:
                return CellType(int(grid[x, y]))
            return CellType.WALL

    def arround_cell(self, cell: tuple[int,int], dist: int) -> list[int]:
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        cells = []
        for dx, dy in directions:
            for d in range(1, dist + 1):
                cells.append(self.cell_type((cell[0] + dx * d, cell[1] + dy * d)))
        return cells

    def find_random_free_cell_in_arround(self, cell: tuple[int,int]):
        x,y = cell
        free_cells = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                # проверка границ карты и доступности клетки
                if (0 <= new_x < self.world.size) and (0 <= new_y < self.world.size) and self.cell_type((new_x, new_y)) == CellType.EMPTY:
                        free_cells.append((new_x, new_y))
    
        if len(free_cells) > 0:
            new_x, new_y = self.rng.offspring_spawn.choice(free_cells)
            return (new_x, new_y)
        else:
            return None

    def _intentions_to_move(self, intentions: dict[Agent, Action]) -> dict[tuple[int,int], list[Agent]]:
        targets = {}
        
        for agent, act in intentions.items():
            if act == Action.STAY:
                continue
            dx, dy = ACTION_DELTAS[act]
            cell = (agent.x + dx, agent.y + dy)
            targets.setdefault(cell, []).append(agent)

        return targets

    def _act_if_wall(self, agents_list: list[Agent]):
        for agent in agents_list:
            agent.take_damage(self.cfg.wall_hit_cost)

    def _act_if_agent(self, agent_list: list[Agent]):
        return

    def _act_if_food(self, cell: tuple[int,int], agents_list: list[Agent]):
        # Выбор случайного агента из кандидатов
        candidates = []
        for agent in agents_list:
            if agent.hp < self.cfg.max_hp: candidates.append(agent)
        if not candidates:
            return
        winner = candidates[self.rng.food_move.integers(0, len(candidates))]

        # Смена позиции
        self.set_agent_coords(winner, cell)
        self.world.set_cell(cell, CellType.EMPTY)
        winner.add_hp(self.cfg.food_value)
        winner.take_damage(self.cfg.damage_per_move)

    def _act_if_empty(self, cell: tuple[int,int], agents_list: list[Agent]):
        winner = agents_list[self.rng.empty_move.integers(0, len(agents_list))]

        self.set_agent_coords(winner, cell)
        winner.take_damage(self.cfg.damage_per_move)

    def _act(self, intentions: dict[Agent, Action]):
        targets = self._intentions_to_move(intentions)
        occupied_t = set(self.agents.keys()) # Снимок до действия

        for cell in targets:
            agents_list = targets[cell]
            cell_type = self.cell_type(cell, occupied_t)
            match cell_type:
                case CellType.EMPTY: self._act_if_empty(cell, agents_list)
                case CellType.FOOD: self._act_if_food(cell, agents_list)
                case CellType.WALL: self._act_if_wall(agents_list)
                case CellType.AGENT: self._act_if_agent(agents_list)

    def step(self):
        if self.world.time % self.cfg.food_respawn_period == 0:
                    self.world.update_food_clusters()

        intentions = {
            agent: agent.decide(self.arround_cell((agent.x,agent.y),self.cfg.vision_range))
            for agent in self.agents.values()
        }

        self._act(intentions)

        # рождение
        newborns = []
        for agent in self.agents.values():
            if agent.hp >= self.cfg.reproduction_threshold:
                free_cell = self.find_random_free_cell_in_arround((agent.x, agent.y))
                if free_cell is not None:
                    offspring = agent.create_offspring(free_cell)
                    agent.take_damage(self.cfg.offspring_cost)
                    newborns.append(offspring)

        # старение
        for agent in self.agents.values():
            agent.up_age()
            agent.take_damage(self.cfg.damage_per_step)

        # смерть
        dead = [pos for pos, agent in self.agents.items()
                if agent.hp <= 0 or agent.age >= self.cfg.age_limit]
        for pos in dead:
            del self.agents[pos]

        # новорождённые
        for child in newborns:
            self.add_agent(child)

        self.world.time += 1
