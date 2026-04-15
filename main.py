import pygame

pygame.init()

import logging
from logging_config import setup_logging
setup_logging()
log = logging.getLogger("main")

from visual_config import init_display
init_display()
from visual_config import OFFSET_X, OFFSET_Y, SQUARE_SIZE, game_surface, screen

from world_config import TIME_SCALE

from ui_config import ui_manager

#main loop------------------------------------------------------------------------------------

from change import change

running = True
clock = pygame.time.Clock()

ui_manager.menu_switch("start")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            if OFFSET_X <= mouse_x <= OFFSET_X + SQUARE_SIZE and (
            OFFSET_Y <= mouse_y <= OFFSET_Y + SQUARE_SIZE):
                game_x = mouse_x - OFFSET_X
                game_y = mouse_y - OFFSET_Y
                ui_manager.click((game_x, game_y))

        if ui_manager.input_state:
            if event.type == pygame.TEXTINPUT:
                ui_manager.input_text += event.text
                ui_manager.input_ui.text[0].text = ui_manager.input_text
                ui_manager.input_ui.old = True


            elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                ui_manager.input_text = ui_manager.input_text[:-1]
                ui_manager.input_ui.text[0].text = ui_manager.input_text
                ui_manager.input_ui.old = True

    game_surface.fill((0, 0, 0))
    ui_manager.draw(game_surface)

    screen.fill((0, 0, 0))
    screen.blit(game_surface, (OFFSET_X, OFFSET_Y))
    pygame.display.flip()

    dt = clock.tick(60) / 1000  # seconds
    change.tick(dt*TIME_SCALE)


