import copy
import random
import uuid
from functools import partial

import loader
from world_config import World, Person, Facility, Area, Object, Substance, Sex, Skill, Temperament, Nation, Faction, \
    Comm, CommKind, Intent, format_time_short, Message, Action


class Game:
    def __init__(self):
        self.world=None
        self.script=loader.load_script()
        self.plot={}
        print("[game] script loaded")

    def comm_react(self, comm: Comm, message: Message):
        response = self.build_message(
            comm, Intent.NONE, {}, True
        )
        intent = message.intent.name
        if comm.kind.name=="HAI":
            if intent == "GREETING":
                response = self.build_message(
                    comm, Intent.GREETING, {}, True
                )
            elif intent in ["CANCEL"]:
                response = self.build_message(
                    comm, Intent.ACKNOWLEDGE, {}, True
                )
            elif intent in ["THANKS"]:
                response = self.build_message(
                    comm, Intent.WELCOME, {}, True
                )

            elif intent in ["ADVICE_ASK", "ADVICE_MORE"]:
                response = self.build_message(
                    comm, Intent.ADVICE_GIVE, {}, True
                )

            elif intent == "TASK_ADD":
                response = self.build_message(
                    comm, Intent.TASK_REQUEST, {}, True
                )

            elif intent == "TASK_PRODUCE":
                facility = comm.sender.facility
                can_produce = facility.can_produce(comm.sender)
                response = self.build_message(
                    comm, Intent.TASK_CAN_PRODUCE, {"can_produce": can_produce}, True
                )
            elif intent == "TASK_RECON":
                response = self.build_message(
                    comm, Intent.ACKNOWLEDGE, {}, True
                )


        self.comm_new_message(comm, response)

    def comm_responses(self, comm:Comm):
        messages = []

        if comm.kind == CommKind.HAI:
            if comm.history:
                if comm.history[0].incoming: #if last was received
                    intent = comm.history[0].intent
                    data = comm.history[0].data
                    if intent in [
                        Intent.GREETING, Intent.WELCOME, Intent.ACKNOWLEDGE
                    ]:
                        messages = [
                            self.build_message(
                                comm, Intent.GREETING, comm.names(), False
                            ),
                            self.build_message(
                                comm, Intent.ADVICE_ASK, {}, False
                            ),
                            self.build_message(
                                comm, Intent.TASK_ADD, {}, False
                            )
                        ]
                    elif intent == Intent.ADVICE_GIVE:
                        messages = [
                            self.build_message(
                                comm, Intent.THANKS, {}, False
                            ),
                            self.build_message(
                                comm, Intent.ADVICE_MORE, {}, False
                            )
                        ]

                    elif intent == Intent.TASK_REQUEST:
                        messages = [
                            self.build_message(
                                comm, Intent.CANCEL, {}, False
                            ),
                            self.build_message(
                                comm, Intent.TASK_PRODUCE, {}, False
                            ),
                            self.build_message(
                                comm, Intent.TASK_RECON, {}, False
                            )
                        ]
                    elif intent == Intent.TASK_CAN_PRODUCE:
                        can_produce = data["can_produce"]
                        messages = [
                            self.
                        ]


        print(f"[game] {comm.cid} responses updated")
        comm.responses=messages

    def comm_send(self, comm: Comm, message: Message):

        self.comm_new_message(comm, message)

        print(f"[game] message sent in {comm.cid}: {message.intent} {format_time_short(message.timestamp)}")

        self.world.processes.append((
            partial(self.comm_react, comm, message),
            comm.ping
        ))

    def comm_new_message(self, comm:Comm, message: Message):

        comm.history.insert(0, message)
        comm.transcribe(message)
        self.comm_responses(comm)
        comm.new_message = True
        print(f"[game] message received in {comm.cid}: {message.intent.name} {format_time_short(message.timestamp)}")


    def format_message(self, template: dict, comm: Comm, incoming: bool, data: dict):
        text = template["text"]
        intent = template["intent"]
        sender = comm.sender if not incoming else comm.recipient
        recipient = comm.recipient if not incoming else comm.sender
        data["sender_name"], data["sender_first_name"]  = sender.name, sender.name.split()[0]
        data["recipient_name"], data["recipient_first_name"] = recipient.name, recipient.name.split()[0]

        for key, value in data.items():
            target = "{" + key + "}"
            text = text.replace(target, value)

        message = Message(
            intent = intent,
            text = text,
            sender = sender,
            recipient = recipient,
            comm = comm,
            incoming = incoming,
            timestamp = self.world.time,
            data = data
        )

        return message

    def build_message(self, comm:Comm, intent: Intent, data: dict, incoming: bool) -> Message:

        templates = self.script["messages"].get(intent, [])
        candidates = []

        message_sender = comm.sender if not incoming else comm.recipient
        message_recipient = comm.recipient if not incoming else comm.sender
        for message in templates:
            points = 0
            sender, recipient = message["sender"], message["recipient"]

            if sender:
                if sender != message_sender:
                    continue
                points += 1
            if recipient:
                if recipient != message_recipient:
                    continue
                points += 1

            candidates.append((message, points))
        candidates.sort(key = lambda x: x[1], reverse = True)
        candidates = candidates[:3]
        chosen = random.choice(
            candidates
        )[0] if candidates else {
            "text": intent.name,
            "intent": intent
        }

        chosen=self.format_message(chosen, comm, incoming, data)

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
                                intent = Intent[content["intent"]]
                                data = content.get("data", {})
                                incoming = content["incoming"]
                                self.comm_new_message(
                                    comm,
                                    self.build_message(comm, intent, data, incoming)
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

        shed = self.world.facilities["abode_small"]
        shed_int, shed_ext = shed.areas["interior"], shed.areas["exterior"]
        main_table = self.create("table_wood", 1)
        for i in range (4):
            self.object_in_object(main_table, self.create("plank_4x16_wood", 1))
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
                oid = obj["oid"],
                name = obj["name"],
                description = obj["description"],
                weight = obj["weight"],
                volume = obj["volume"],
                area = obj["area"],
                substance = Substance[obj["substance"]],
                storage = {}, #nested builds after
                actions = {}
            )
            for action, qty in obj["actions"].items():
                world.objects[obj["oid"]].actions[Action[action]] = qty

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
        for intent, messages in self.script["messages"].items():
            new_messages[Intent[intent]]=[
                {
                    "intent": Intent[intent],
                    "text": message["text"],
                    "sender": world.people[message["sender"]] if message.get("sender") else None,
                    "recipient": world.people[message["recipient"]] if message.get("recipient") else None,
                } for message in messages
            ]
        self.script["messages"]=new_messages

        for comm in data["comms"].values():
            world.comms[comm["cid"]]=Comm(
                cid = comm["cid"],
                kind = CommKind[comm["kind"]],
                sender = world.people[comm["sender"]],
                recipient = world.people[comm["recipient"]],
                trust = comm["trust"],
                history = [
                    Message(
                        intent = Intent[message["intent"]],
                        text = message["text"],
                        sender = world.people[message["sender"]],
                        recipient = world.people[message["recipient"]],
                        comm = world.comms[message["comm"]],
                        timestamp = message["timestamp"],
                        data = message["data"],
                    ) for message in comm["history"]
                ],
                ping = comm["ping"]
            )
            for message in world.comms[comm["cid"]].history:
                world.comms[comm["cid"]].transcribe(
                    message
                )

        self.plot = plot
        print(
            f"[game] world ready: {len(world.facilities)} facilities, "
            f"{len(world.people)} people, {len(world.objects)} objects, {len(world.comms)} comms"
        )
        return world

def rank(value: float) -> str:
    global RANKS
    grade = "?"
    value = max(0.0, (min(10.0, value)))
    for threshold, label in RANKS:
        if value < threshold:
            grade = label
    return grade



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

RANKS = [
    (2, "F"),
    (3, "E"),
    (4, "D"),
    (5, "C"),
    (6, "C+"),
    (7, "B"),
    (8, "B+"),
    (9, "A"),
    (10, "A+"),
    (float("inf"), "S"),
]