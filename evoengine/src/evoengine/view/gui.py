import pygame
import numpy as np

from ..core import Agent, CellType
from . import theme

PANEL_WIDTH = 380

class Gui:
    def __init__(self, env, zoom: int, speed: int = 1):
        pygame.font.init()
        self.font = theme.font(theme.FONT_BODY)
        self.font_bold = theme.font(theme.FONT_HEADER, bold=True)
        self.font_small = theme.font(theme.FONT_SMALL)

        self.env = env
        self.zoom = zoom
        self.selected = None
        self.paused = False
        self.weights_scroll = 0
        self.speed = speed

    def change_speed(self, delta: int):
        self.speed += delta

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._on_key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._on_mouse(event.button, event.pos)
        elif event.type == pygame.MOUSEWHEEL:
            self._on_wheel(event.y)

    def _on_wheel(self, dy):
        surface = pygame.display.get_surface()
        if surface is None:
            return
        if pygame.mouse.get_pos()[0] < surface.get_width() - PANEL_WIDTH:
            return
        self.weights_scroll = max(0, self.weights_scroll - dy * 40)

    def _cell(self, pos):
        x = pos[0] // self.zoom
        y = (self.env.world.size - 1) - pos[1] // self.zoom
        return x, y

    def _on_key(self, key):
        if key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_a:
            self._spawn_agent(pygame.mouse.get_pos())
        elif key == pygame.K_r:
            self._remove_agent(pygame.mouse.get_pos())
        elif key == pygame.K_ESCAPE:
            self.selected = None
            self.weights_scroll = 0

    def _on_mouse(self, button, pos):
        world = self.env.world
        if pos[0] >= world.size * self.zoom:
            return

        x, y = self._cell(pos)
        if not (0 <= x < world.size and 0 <= y < world.size):
            return

        agent = self.env.agents.get((x, y))

        if button == 1:
            if agent is not None:
                self.selected = agent
                self.weights_scroll = 0
            elif world.grid[x, y] in (CellType.EMPTY, CellType.FOOD):
                world.grid[x, y] = CellType.EMPTY if world.grid[x, y] == CellType.FOOD else CellType.FOOD
        elif button == 3:
            if agent is None and world.grid[x, y] in (CellType.EMPTY, CellType.WALL):
                world.grid[x, y] = CellType.EMPTY if world.grid[x, y] == CellType.WALL else CellType.WALL

    def _spawn_agent(self, mouse_pos):
        world = self.env.world
        x, y = self._cell(mouse_pos)

        for _ in range(200):
            if (1 <= x < world.size - 1 and 1 <= y < world.size - 1
                    and world.grid[x, y] != CellType.WALL
                    and (x, y) not in self.env.agents):
                break
            x = np.random.randint(1, world.size - 1)
            y = np.random.randint(1, world.size - 1)

        agent = Agent(self.env.cfg, self.env.rng, x=x, y=y)
        self.env.add_agent(agent)

    def _remove_agent(self, mouse_pos):
        x, y = self._cell(mouse_pos)
        agent = self.env.agents.get((x, y))

        if agent is None:
            agent = self.selected

        if agent is not None and agent in self.env.agents.values():
            self.env.del_agent(agent)
            if self.selected is agent:
                self.selected = None

    def draw(self, surface):
        panel_x = surface.get_width() - PANEL_WIDTH
        panel = pygame.Surface((PANEL_WIDTH, surface.get_height()))
        panel.fill(theme.BG_COLOR)

        y = 10
        y = self._draw_stats(panel, y)
        y = self._draw_help(panel, y)

        agent = self.selected
        if agent is not None:
            y = self._draw_agent_info(panel, agent, y)
            y = self._draw_agent_weights(panel, agent, y)

        surface.blit(panel, (panel_x, 0))
        pygame.draw.line(surface, theme.BORDER_COLOR, (panel_x, 0), (panel_x, surface.get_height()))

    def _text(self, surface, text, x, y, color=theme.TEXT_COLOR, font=None):
        img = (font or self.font).render(text, True, color)
        surface.blit(img, (x, y))
        return img.get_height()

    def _draw_stats(self, panel, y):
        lines = [
            f"Время:    {self.env.world.time}",
            f"Агентов:  {len(self.env.agents)}",
            f"Еды:      {int((self.env.world.grid == 1).sum())}",
            f"Пауза:    {'ДА' if self.paused else 'нет'}",
            f"Скорость: {self.speed}x",
        ]
        for line in lines:
            y += self._text(panel, line, 12, y)
        return y + 8

    def _draw_help(self, panel, y):
        y += self._text(panel, "--- Управление: ---", 12, y, theme.ACCENT_COLOR)
        for line in [
            "ЛКМ по агенту - выбрать",
            "ЛКМ - еда вкл/выкл",
            "ПКМ - стена вкл/выкл",
            "A - агент на курсор",
            "R - удалить агента",
            "SPACE - пауза",
            "N/ENTER - один шаг",
            "+ / - - скорость",
            "ESC - снять выбор",
            "КОЛЕСО - прокрутка весов",
        ]:
            y += self._text(panel, line, 12, y, font=self.font_small)
        return y + 10

    def _draw_agent_info(self, panel, agent, y):
        if agent not in self.env.agents.values():
            y += self._text(panel, f"=== АГЕНТ {agent.agent_id} (МЁРТВ) ===", 12, y, theme.NEGATIVE_COLOR, self.font_bold)
            return y + 8

        y += self._text(panel, f"=== АГЕНТ {agent.agent_id} ===", 12, y, theme.ACCENT_COLOR, self.font_bold)
        max_hp = agent.cfg.max_hp
        for line in [
            f"HP: {agent.hp:.1f} / {max_hp}",
            f"Возраст: {agent.age} шагов",
            f"Позиция: ({agent.x}, {agent.y})",
        ]:
            y += self._text(panel, line, 12, y)

        bar_w, bar_h = 150, 10
        ratio = max(0.0, min(1.0, agent.hp / max_hp))
        pygame.draw.rect(panel, theme.BORDER_COLOR, (12, y, bar_w, bar_h))
        if ratio > 0:
            color = theme.POSITIVE_COLOR if ratio > 0.4 else theme.NEGATIVE_COLOR
            pygame.draw.rect(panel, color, (12, y, int(bar_w * ratio), bar_h))
        y += bar_h + 8
        return y

    def _draw_agent_weights(self, panel, agent, y):
        start_y = y
        y += self._text(panel, "--- Веса нейросети: ---", 12, y, theme.ACCENT_COLOR)

        sections = [("W1 (вход->скрытый1)", agent.nn.W1),
                    ("W2 (скрытый1->скрытый2)", agent.nn.W2),
                    ("W3 (скрытый2->выход)", agent.nn.W3)]

        max_cols = max(W.shape[1] for _, W in sections)
        cell = min(16, (PANEL_WIDTH - 24 - (max_cols - 1) * 2) // max_cols)

        body_h = sum(self.font_small.get_height() + 2 + W.shape[0] * (cell + 2) + 6
                     for _, W in sections)
        max_scroll = max(0, body_h - (panel.get_height() - y))
        self.weights_scroll = min(self.weights_scroll, max_scroll)

        viewport = pygame.Rect(0, y, PANEL_WIDTH, panel.get_height() - y)
        old_clip = panel.get_clip()
        panel.set_clip(viewport)
        panel.fill(theme.BG_COLOR, viewport)

        yy = y - self.weights_scroll
        for name, W in sections:
            yy += self._text(panel, name, 12, yy, font=self.font_small)
            rows, cols = W.shape
            for r in range(rows):
                for c in range(cols):
                    pygame.draw.rect(panel, self._weight_color(W[r, c]),
                                     (12 + c * (cell + 2), yy + r * (cell + 2), cell, cell))
            yy += rows * (cell + 2) + 6
        panel.set_clip(old_clip)
        return start_y

    @staticmethod
    def _weight_color(value):
        t = max(-1.0, min(1.0, value / 3.0))
        level = int(185 * abs(t))
        if t >= 0:
            return (70, 70 + level, 70)
        return (70 + level, 70, 70)