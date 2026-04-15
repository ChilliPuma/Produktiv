from data.ui_design import ui_time_bar
from world_config import world, format_time


class Event:
    def __init__(self,
        eid: str,
        function,
        time: float
        ):
        self.eid = eid
        self.function = function
        self.time = time

class Change:
    def __init__(self):

        self.asap: list = []
        self.queue: list = []

    def tick(self, dt: float): #seconds
        world.tick(dt)
        ui_time_bar.text[0].text, ui_time_bar.old = format_time(world.time), True
        if self.asap:
            for event in self.asap:
                event.function()
            self.asap = []
        if self.queue:
            new_queue = []
            for event in self.queue:
                event.time -= dt
                if event.time <= 0:
                    self.asap.append(event)
                elif event.time > 0:
                    new_queue.append(event)
            self.queue = new_queue



change = Change()

story = {}

def build_story():
    global story
    story = {
        "hai_intro": Event(
        eid="hai_intro",
        function=world.comms["hai"].receive(world.scripts["GREETING_s:hai_1"]),
        time=60.0
        )
    }

