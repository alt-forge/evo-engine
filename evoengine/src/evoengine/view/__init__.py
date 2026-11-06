import pygame

from ..core import Env
from .rendering import PygameRenderer
from .gui import Gui, PANEL_WIDTH

def view_simulation(env: Env, zoom: int = 8, speed: int = 1):
    renderer = PygameRenderer(env, zoom=zoom, panel_width=PANEL_WIDTH)
    gui = Gui(env, zoom=zoom, speed=speed)

    clock = pygame.time.Clock()
    running = True
    FPS = 30

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if gui.selected is not None:
                        gui.selected = None
                        gui.weights_scroll = 0
                    else:
                        running = False
                elif event.key in (pygame.K_n, pygame.K_RETURN, pygame.K_KP_ENTER):
                    if gui.paused:
                        env.step()
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    gui.change_speed(+1)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    gui.change_speed(-1)
                else:
                    gui.handle_event(event)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEWHEEL):
                gui.handle_event(event)

        if not gui.paused and env.agents:
            for _ in range(gui.speed):
                if not env.agents:
                    break
                env.step()

        renderer.draw(selected=gui.selected)
        gui.draw(renderer.screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.display.quit()