import loader
from world_config import World, Person, Facility, Area, Object, Substance, Sex, Skill, Temperament


def build_storage(data, world):
    if not data:
        return {}

    elif data["kind"] == "OBJECT":
        return {
            "kind": data["kind"],
            "max": data["max"],
            "content": [
                world.objects[oid] for oid in data["content"]
            ]
        }
    elif data["kind"] == "AMMO":
        return {
            "kind": data["kind"],
            "max": data["max"],
            "content": [
                world.objects[oid] for oid in data["content"]
            ]
        }
    else:
        return {}

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

        for obj in data["objects"].values():
            world.objects[obj["oid"]] = Object(
                oid=obj["oid"],
                name=obj["name"],
                weight=obj["weight"],
                volume=obj["volume"],
                area=obj["area"],
                substance=Substance[obj["substance"]],
                storage={}, #nested builds after
                production=obj["production"]
            )
        for obj in data["objects"].values():
            world.objects[obj["oid"]].storage=build_storage(obj["storage"], world)

        for facility in data["facilities"].values():
            world.facilities[facility["fid"]] = Facility(
                fid=facility["fid"],
                name=facility["name"],
                location=facility["location"],
                areas={
                    area["aid"]: Area(
                        aid=area["aid"],
                        name=area["area_name"],
                        level=area["level"],
                        area=area["area"],
                        staff_max=area["staff_max"],
                        staff=[
                            world.people[pid] for pid in area["staff"]
                        ]
                        ) for area in facility["areas"]
                },
                power=facility["power"],
                owner=world.people[facility["owner"]],
            )

        for person in data["people"].values():
            world.people[person["pid"]]=Person(
                pid=person["pid"],
                name=person["name"],
                age=person["age"],
                sex=Sex[person["sex"]],
                skills={Skill[skill]: qty for skill, qty in person["skills"].items()},
                temperament=Temperament[person["temperament"]],
            )

        for facility in data["facilities"].values():
            f=world.facilities[facility["fid"]]
            f.staff=[
                world.people[pid] for pid in facility["staff"]
            ]
            for area in f:
                area.staff=[
                    world.people[pid] for pid in area["staff"]
                ]

        return world