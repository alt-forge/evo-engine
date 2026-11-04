import pygame

from ..core import CellType
from . import theme


class PygameRenderer:
    def __init__(self, env, zoom: int, panel_width: int = 0):
        self.env = env
        self.zoom = zoom
        self.panel_width = panel_width

        pygame.init()
        pygame.display.set_caption("Evo Engine")
        self.screen = pygame.display.set_mode(
            (env.world.size * zoom + panel_width, env.world.size * zoom)
        )

    def draw(self, selected=None):
        self.screen.fill(theme.BG_COLOR)

        size = self.env.world.size
        grid = self.env.world.grid
        agents = self.env.agents

        for i in range(size):
            for j in range(size):
                x = i * self.zoom
                y = (size - 1 - j) * self.zoom

                if (i, j) in agents:
                    color = theme.AGENT_COLOR
                    if selected is not None and agents[(i, j)] is selected:
                        color = theme.ACCENT_COLOR
                elif grid[i, j] == CellType.FOOD:
                    color = theme.FOOD_COLOR
                elif grid[i, j] == CellType.WALL:
                    color = theme.WALL_COLOR
                else:
                    color = theme.MAP_BG_COLOR

                pygame.draw.rect(self.screen, color, (x, y, self.zoom, self.zoom))