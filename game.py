import copy
import uuid

import loader
from world_config import World, Person, Facility, Area, Object, Substance, Sex, Skill, Temperament, Nation, Faction, \
    Comm, CommKind, MessageKind



class Game:
    def __init__(self):
        self.world = None
        self.script = loader.load_script()


    def create(self, og_obj: Object, qty: int):
        if qty > 1:
            objects = []
            for i in range(qty):
                objects.append(self.create(og_obj,1 ))
            return objects
        created_obj = copy.deepcopy(og_obj)
        created_obj.oid += f"_{str(uuid.uuid4())}"
        self.world.objects[created_obj.oid] = created_obj
        return created_obj

    def tick(self, dt): #gameworld seconds
        if self.world:
            if self.world.time_stop:
                return
            self.world.time += dt

    def new_game(self):
        data = loader.load_default()
        self.world = self.build_world(data)

    def load_game(self, filename: str):
        pass

    def save_game(self, filename: str):
        pass

    def build_world(self, data):
        world=World()
        script={}

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
                        name=area["name"],
                        level=area["level"],
                        area=area["area"],
                        inventory=[
                            world.objects[oid] for oid in area["inventory"]
                        ],
                        staff_max=area["staff_max"],
                        staff=[] #first pass
                        ) for area in facility["areas"].values()
                },
                power=facility["power"],
                owner=None, #first pass
            )

        for person in data["people"].values():
            world.people[person["pid"]]=Person(
                pid=person["pid"],
                name=person["name"],
                age=person["age"],
                sex=Sex[person["sex"]],
                facility=world.facilities[person["facility"]] if person["facility"] else None,
                area=world.facilities[person["facility"]].areas[person["area"]] if person["facility"] else None,
                nation=Nation[person["nation"]],
                faction=Faction[person["faction"]],
                temperament=Temperament[person["temperament"]] or None,
                skills={Skill[skill]: qty for skill, qty in person["skills"].items()}
            )

        for facility in data["facilities"].values(): #second passes
            f=world.facilities[facility["fid"]]
            f.owner=world.people[facility["owner"]]
            if f.owner == world.people[data["states"]["player"]]:
                world.owned_facilities.append(f)
            for area in f.areas.values():
                area.staff=[
                    world.people[pid] for pid in facility["areas"][area.aid]["staff"]
                ]

        for message in self.script["messages"].values():
            self.script["messages"][message["mid"]] = {
                "mid": message["mid"],
                "kind": MessageKind[message["kind"]],
                "text": message["text"],
                "sender": world.people[message["sender"]] if message["sender"] and message["sender"] != "hai" else None,
                "recipient": world.people[message["recipient"]] if message["recipient"] else None
            }

        for comm in data["comms"].values():
            world.comms[comm["cid"]]=Comm(
                cid=comm["cid"],
                kind=CommKind[comm["kind"]],
                sender=world.people[comm["sender"]],
                recipient=world.people[comm["recipient"]],
                history=[
                    (
                        message["mid"],
                        message["received"],
                        message["timestamp"]
                    ) for message in comm["history"]
                ],
                ping=comm["ping"]
            )

        self.script = script
        return world

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

game = Game()

