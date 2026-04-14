from data.ui_design import ui_time_bar
from world_config import world, format_time


class Change:
    def __init__(self):

        asap: list = []
        queue: list = []

    def tick(self, dt: float): #seconds
        world.tick(dt)
        ui_time_bar.text[0].text = format_time(world.time)
        ui_time_bar.old = True

        if self.asap:
            for


change = Change()