import pygame

pygame.init()

import logging
from logging_config import setup_logging
setup_logging()
log = logging.getLogger("main")

from visual_config import init_display
init_display()
from visual_config import OFFSET_X, OFFSET_Y, SQUARE_SIZE, game_surface, screen

from world_config import world, TIME_SCALE, format_time

from ui_config import ui_manager

from data.ui_design import (ui_back_button, ui_start_continue,
                            ui_start_saves, ui_saves_new_save_button, ui_new_save_button, ui_start_new_game,
                            ui_main_facilities, ui_facilities_inventory_up, ui_facilities_inventory_down, ui_main_comms,
                            ui_item_contents_up, ui_item_contents_down, ui_time_bar)

#UI functionality-----------------------------------------------------------------------------

ui_back_button.function = lambda: ui_manager.menu_back()

ui_start_saves.function = lambda: ui_manager.menu_switch("saves")
ui_start_continue.function = lambda: ui_manager.continue_game()
ui_start_new_game.function = lambda: ui_manager.new_game()

ui_saves_new_save_button.function = lambda: ui_manager.menu_switch("new_save")

ui_new_save_button.function = lambda: ui_manager.new_save(ui_manager.input_text)

ui_main_facilities.function = lambda: ui_manager.menu_switch("facilities")
ui_main_comms.function = lambda: ui_manager.menu_switch("comms")

ui_facilities_inventory_up.function = lambda: ui_manager.facilities_inventory_scroll(-1)
ui_facilities_inventory_down.function = lambda: ui_manager.facilities_inventory_scroll(1)

ui_item_contents_up.function = lambda: ui_manager.item_contents_scroll(-1)
ui_item_contents_down.function = lambda: ui_manager.item_contents_scroll(1)

for i in range (4):
    ui_manager.ui_lookup(f"facilities_inventory_grid_cell_{
        i + 1}").function = lambda: ui_manager.menu_switch("item")
    ui_manager.ui_lookup(f"item_contents_grid_cell_{
        i + 1}").function = lambda: ui_manager.item_display()



#main loop------------------------------------------------------------------------------------

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
    world.tick(dt*TIME_SCALE)
    ui_time_bar.text[0].text = format_time(world.time)
    ui_time_bar.old = True


