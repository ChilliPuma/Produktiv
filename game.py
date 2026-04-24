import copy
import random
import uuid

import loader
from world_config import World, Person, Facility, Area, Object, Substance, Sex, Skill, Temperament, Nation, Faction, \
    Comm, CommKind, MessageKind



class Game:
    def __init__(self):
        self.world = None
        self.script = loader.load_script()
        self.plot = {}
        print("[game] script loaded")

    def comm_receive(self, comm:Comm, kind: MessageKind, timestamp: float):
        candidates = []
        for message in self.script["messages"].values():
            points = 0
            if message["kind"] != kind:
                continue
            else:
                if message["sender"] and message["sender"] != comm.recipient:
                    continue
                elif message["sender"] == comm.recipient:
                    points += 1

                if message["recipient"] and message["recipient"] != comm.sender:
                    continue
                elif message["recipient"] == comm.sender:
                    points += 1

            candidates.append((message, points))
        candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = candidates[:7]
        chosen = random.choice(candidates)[0]

        comm.history.append((chosen, True, timestamp))
        comm.transcribe(chosen, True, timestamp)
        print(f"[game] message received in {comm.cid}: {chosen['mid']} at {timestamp:.2f}")
        comm.new_message = True

    def plot_check(self):
        for story_id, story in self.plot["stories"].items():
            if story["state"] == "untriggered":
                if all (
                    self.plot[check][key] >= value if (check, key) in GTE_check
                    else self.plot[check][key] == value
                    for check in story["trigger"].keys()
                    for key, value in story["trigger"][check].items()
                ):
                    print(f"[game] story triggered: {story_id}")
                    try:
                        story["state"] = "triggered"
                        for effect, content in story["on_trigger"].items():
                            if effect == "message":
                                comm = self.world.comms[content["cid"]]
                                kind = MessageKind[content["kind"]]
                                self.comm_receive(
                                    comm,
                                    kind,
                                    self.world.time
                                )
                    except Exception as e:
                        print(f"Trigger error: {e}")


    def object_in_object(self, obj: Object, content: Object):
        if obj.can_store(content):
            obj.storage["content"].append(content)
            return True
        else:
            print(f"FAILED: {content.oid} too large for {obj.oid}")
            return False

    def object_in_area(self, area: Area, obj: Object):
        if area.can_add(obj.area):
            area.inventory.append(obj)
            return True
        else:
            print(f"FAILED: {obj.oid} too large for {area.aid}")
            return False


    def create(self, og_oid: str, qty: int):
        if qty > 1:
            objects = []
            for i in range(qty):
                objects.append(self.create(og_oid,1 ))
            return objects
        created_obj = copy.deepcopy(self.world.objects[og_oid])
        created_obj.oid += f"_{str(uuid.uuid4())}"
        self.world.objects[created_obj.oid] = created_obj
        return created_obj

    def tick(self, dt): #gameworld seconds
        if self.world:
            if self.world.time_stop:
                return
            self.world.time += dt
            self.plot["states"]["time"] = self.world.time

            self.plot_check()

    def new_game(self):
        data = loader.load_default()
        self.world = self.build_world(data)
        print("[game] new world created")

        #new game design:

        shed = self.world.facilities["shed_backyard"]
        shed_int, shed_ext = shed.areas["interior"], shed.areas["exterior"]
        main_table = self.create("table_wood", 1)
        for i in range (4):
            self.object_in_object(main_table, self.create("plank_wood", 1))
        self.object_in_area(shed_int, main_table)
        print("[game] new game setup complete")


    def load_game(self, filename: str):
        pass

    def save_game(self, filename: str):
        pass

    def build_world(self, data):
        world=World()
        print("[game] building world objects")

        world.time = data["states"]["time"]
        plot = {
            "flags": data["flags"],
            "states": data["states"],
            "stories": data["stories"]
        }

        for obj in data["objects"].values():
            world.objects[obj["oid"]] = Object(
                oid=obj["oid"],
                name=obj["name"],
                description=obj["description"],
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
                location=(facility["location"][0], facility["location"][1]),
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
                title=person["title"],
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

        new_messages = {}
        for message in self.script["messages"].values():
            new_messages[message["mid"]] = {
                "mid": message["mid"],
                "kind": MessageKind[message["kind"]],
                "text": message["text"],
                "sender": world.people[message["sender"]] if message["sender"] else None,
                "recipient": world.people[message["recipient"]] if message["recipient"] else None
            }
        self.script["messages"] = new_messages

        for comm in data["comms"].values():
            world.comms[comm["cid"]]=Comm(
                cid=comm["cid"],
                kind=CommKind[comm["kind"]],
                sender=world.people[comm["sender"]],
                recipient=world.people[comm["recipient"]],
                history=[
                    (
                        self.script["messages"][message["mid"]],
                        message["received"],
                        message["timestamp"]
                    ) for message in comm["history"]
                ],
                ping=comm["ping"]
            )

        self.plot = plot
        print(
            f"[game] world ready: {len(world.facilities)} facilities, "
            f"{len(world.people)} people, {len(world.objects)} objects, {len(world.comms)} comms"
        )
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

GTE_check = [
    ("states", "time")
]
