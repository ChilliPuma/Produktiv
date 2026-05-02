import copy
import random
import uuid
from functools import partial

import loader
from world_config import World, Person, Facility, Area, Object, Substance, Sex, Skill, Temperament, Nation, Faction, \
    Comm, CommKind, MessageKind, format_time_short


class Game:
    def __init__(self):
        self.world=None
        self.script=loader.load_script()
        self.plot={}
        print("[game] script loaded")

    def comm_react(self, comm: Comm, kind: MessageKind):
        kind_chosen="ERROR"

        if comm.kind==CommKind.HAI:
            if kind.name=="TASK_ADD":
                kind_chosen="TASK_REQUEST"


        kind_chosen=MessageKind[kind_chosen]
        self.comm_receive(comm, kind_chosen, self.world.time)

    def comm_responses(self, comm:Comm):
        kinds = []

        if comm.kind==CommKind.HAI:
            if comm.history:
                if comm.history[0]["received"]: #if last was received
                    last=comm.history[0]["message"]
                    if last["kind"].name=="GREETING":
                        kinds.extend([
                            "GREETING",
                            "TASK_ADD"
                        ])

        kinds = list(set(kinds))
        candidates=[]
        for kind in kinds:
            chosen=self.build_message(comm, MessageKind[kind], False)
            candidates.append(chosen)
        print(f"[game] {comm.cid} responses updated")
        comm.responses=candidates

    def comm_send(self, comm:Comm, message:dict):
        timestamp = self.world.time

        comm.history.insert(
            0, {"message": message, "received": False, "timestamp": timestamp}
        )
        comm.transcribe(message, False, timestamp)

        print(f"[game] message sent in {comm.cid}: {message['kind']} {format_time_short(timestamp)}")

        self.world.processes.append((
            partial(self.comm_react, comm, message["kind"]),
            comm.ping
        ))
        game.comm_responses(comm)
        comm.new_message=True

    def comm_receive(self, comm:Comm, kind: MessageKind, timestamp: float):

        chosen=self.build_message(comm, kind, True)

        comm.history.insert(
            0, {"message": chosen, "received": True, "timestamp": timestamp}
        )
        comm.transcribe(chosen, True, timestamp)
        game.comm_responses(comm)
        comm.new_message = True
        print(f"[game] message received in {comm.cid}: {kind.name} {format_time_short(timestamp)}")


    def format_message(self, message: dict, comm: Comm, received: bool):
        text=message["text"]

        if "{sender_name}" in text:
            text=text.replace("{sender_name}", comm.sender.name if not received else comm.recipient.name)
        if "{recipient_name}" in text:
            text=text.replace("{recipient_name}", comm.recipient.name if not received else comm.sender.name)

        message["text"]=text
        return message



    def build_message(self, comm:Comm, kind: MessageKind, received: bool) -> dict:
        templates=self.script["messages"].get(kind, [])
        candidates=[]
        message_sender=comm.sender if not received else comm.recipient
        message_recipient=comm.recipient if not received else comm.sender

        for message in templates:
            points=0
            sender, recipient=message["sender"], message["recipient"]
            if sender:
                if sender!=message_sender:
                    continue
                points+=1
            if recipient:
                if recipient!=message_recipient:
                    continue
                points+=1



            candidates.append((message, points))
        candidates.sort(key=lambda x: x[1], reverse=True)
        candidates=candidates[:3]
        chosen=random.choice(
            candidates
        )[0] if candidates else {
            "text": kind.name,
            "kind": kind
        }

        chosen=self.format_message(chosen, comm, received)

        return chosen

    def process_check(self, dt: float):
        processes=[]
        for process in self.world.processes:
            function, time=process
            time-=dt
            if time<=0:
                function()
                continue
            processes.append((function, time))

        self.world.processes=processes

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
            self.process_check(dt)

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

        new_messages={}
        for kind, messages in self.script["messages"].items():
            new_messages[MessageKind[kind]]=[
                {
                    "kind": MessageKind[kind],
                    "text": message["text"],
                    "sender": world.people[message["sender"]] if message.get("sender") else None,
                    "recipient": world.people[message["recipient"]] if message.get("recipient") else None
                } for message in messages
            ]
        self.script["messages"]=new_messages

        for comm in data["comms"].values():
            world.comms[comm["cid"]]=Comm(
                cid=comm["cid"],
                kind=CommKind[comm["kind"]],
                sender=world.people[comm["sender"]],
                recipient=world.people[comm["recipient"]],
                history=[
                    {
                        "message": self.script["messages"][message["mid"]],
                        "received": message["received"],
                        "timestamp": message["timestamp"]
                    } for message in comm["history"]
                ],
                ping=comm["ping"]
            )
            for message in comm["history"]:
                world.comms[comm["cid"]].transcribe(
                    message["message"], message["received"], message["timestamp"]
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