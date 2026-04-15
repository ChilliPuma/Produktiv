import loader
from world_config import World, Person, Facility, Area


class Game:
    def __init__(self):
        self.world = None

    def new_game(self):
        data = loader.load_default()
        self.world = self.build_world(data)

        self.world.facilities["shed_backyard"].add_objects("exterior", "bicycle", 1)

    def load_game(self, filename: str):
        pass

    def save_game(self, filename: str):
        loader.new_save(filename)

    def build_world(self, data):
        world=World()

        for facility in data["facilities"].values():
            world.facilities[facility["fid"]] = Facility(
                fid=facility["fid"],
                name=facility["name"],
                location=facility["location"],
                staff_max=facility["staff_max"],
                areas={
                    area["aid"]: Area(
                        aid=area["aid"],
                        name=area["area_name"],
                        level=area["level"],
                        area=area["area"]
                        ) for area in facility["areas"]
                }
            )

        for person in data["people"].values():
            pass

        return world