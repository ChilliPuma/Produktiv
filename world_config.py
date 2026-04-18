import logging
import random

log = logging.getLogger(__name__)

import copy, uuid
from enum import Enum, auto



# Enums‐-----------------------------------------

class CanContain(Enum):
    NONE = auto()

    AMMO_9MM = auto()

    OBJECT = auto()
    GRAIN = auto()
    LIQUID = auto()
    GAS = auto()

class CommKind(Enum):
    AUTO = auto()
    STAFF = auto()
    NPC = auto()

class Faction(Enum):
    INDEPENDENT = auto()

    MORMON = auto()

class MessageKind(Enum):
    GREETING = auto()
    ACKNOWLEDGEMENT = auto()

    REQUEST_TASK = auto()

    STATUS = auto()
    PROBLEM = auto()

    TASK_NEW = auto()
    TASK_THEN = auto()
    TASK_ONLY_THEN = auto()

class Nation(Enum):
    AMERICAN_WHITE = auto()

class Sex(Enum):
    MALE = auto()
    FEMALE = auto()

class Skill(Enum):
    FIT = auto()
    VIT = auto()
    SOC = auto()
    INT = auto()

class Substance(Enum):
    COMPOSITE = auto()
    CARDBOARD = auto()
    STEEL = auto()
    WOOD_PINE = auto()

class Temperament(Enum):
    SANGUINE = auto()
    CHOLERIC = auto()
    MELANCHOLIC = auto()
    PHLEGMATIC = auto()

#time and space----------------------------------------------------------------------------------------

TIME_SCALE = 30

def format_time(seconds: float) -> str:
    seconds = int(seconds)
    minutes = (seconds // 60) % 60
    hours = (seconds // 3600) % 24
    day = 1 + seconds // 86400
    return f"Day {day}, {hours:02d}:{minutes:02d}"

def format_time_short(seconds: float) -> str:
    seconds = int(seconds)
    minutes = (seconds // 60) % 60
    hours = (seconds // 3600) % 24
    day = 1 + seconds // 86400
    return f"{day};{hours:02d}:{minutes:02d}"

def text_lines(text:str, char:int):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        if len(line) + len(word) + (1 if line else 0) < char:
            if line:
                line += " "
            line += word
        else:
            line = word

    if line:
        lines.append(line)

    return lines

class World:
    def __init__(self,
                 facilities: dict[str, "Facility"] = None,
                 objects: dict[str, "Object"] = None,
                 people: dict[str, "Person"] = None,
                 player: "Person" = None,
                 comms: dict[str, "Comm"] = None,
                 scripts: dict[str, "Script"] = None,
                 time: float = 0):
        self.facilities = facilities if facilities else {}
        self.owned_facilities = []
        self.objects = objects if objects else {}
        self.people = people if people else {}
        self.player = player
        self.comms = comms if comms else {}
        self.scripts = scripts if scripts else {}

        self.time = time  # seconds
        self.time_stop = True

        self.processes: list = []

    def tick(self, dt: float):

        if self.time_stop:
            return
        self.time += dt

        for process in self.processes:
            process.tick(dt)



world = World()

#Entities --------------------------------------------------------------------

class Object:
    def __init__(self,
                 oid: str,
                 name: str,
                 weight: float,  # kg
                 volume: float,  # L (dcm^3)
                 area: float, # m²
                 substance: Substance = None,
                 components: dict[str, int] = None,
                 storage: dict = None,
                 production: list[dict] = None,
                 description: str = ""):  # ingame secs

        self.oid = oid
        self.name = name
        self.description = description

        self.weight = weight
        self.volume = volume
        self.area = area
        self.substance = (
                substance or Substance.COMPOSITE)
        self.components = components or {}
        self.storage = storage or {}
        self.production = production or []

    def create(self, *kwargs):
        created_obj = copy.deepcopy(self)
        created_obj.oid += f"_{str(uuid.uuid4())}"
        world.objects[created_obj.oid] = created_obj
        return created_obj

    def total_weight(self):
        total = self.weight
        for content in self.storage:
            total += content.total_weight()
        return total

#Area----------------------------------------------------------

class Area:
    def __init__(self,
        name: str,
        aid: str,
        level: int = 0,
        area: float = 4.0, # m²
        staff: list["Person"] = None,
        staff_max: int = 1,
        inventory: list[Object] = None,
        ):

        self.name = name
        self.aid = aid
        self.level = level
        self.area = area
        self.staff = staff or []
        self.staff_max = staff_max
        self.inventory = inventory or []

#Facilities-------------------------------------------------------

class Facility:
    def __init__(self, *,
        fid: str,
        name: str,
        areas: dict[str, Area],  # area name, m²]
        power: float, # W
        location: tuple[tuple, str],  # (x,y), (City, Country)
        staff: list["Person"] = None,
        owner: str = None):

        self.fid = fid
        self.name = name
        self.areas = areas
        self.power = power
        self.location = location
        self.staff = staff or []
        self.owner = owner if owner else ""

        self.total_area: float = 0.0
        for area_name, area in self.areas.items():
            self.total_area += area.area

        self.tasks: list[Task] = []

        world.facilities[fid] = self

    def used_area(self) -> float:
        used_area = 0.0
        for a_name, area in self.areas.items():
            for obj in area.inventory:
                used_area += obj.area

        return used_area

    def staff_max(self) -> int:
        total = 0
        for a in self.areas.values():
            total += a.staff_max
        return total

    def total_staff(self) -> int:
        total = 0
        for a in self.areas.values():
            s = len(a.staff)
            total += s
        return total

class Person:
    def __init__(self,
        name: str,
        pid: str,
        sex: Sex,
        age: int,
        skills: dict[Skill, float], # max 10
        temperament: Temperament,
        facility: Facility = None,
        area: Area = None,
        nation: Nation = None,
        faction: Faction = None,
        title: str = "",
        ):

        self.name = name
        self.pid = pid
        self.sex = sex
        self.age = age
        self.facility = facility
        self.area = area
        self.nation = nation
        self.skills = skills
        self.temperament = temperament
        self.title = title

class Task:
    def __init__(self,
        name: str,
        tid: str,
        ):

        self.name = name

class Message:
    def __init__(self,
        sid: str,
        text: str,
        ):

        self.sid = sid
        self.text = text

class Comm:
    def __init__(self,
        cid: str,
        kind: CommKind,
        sender: str, #pid
        recipient: str, #pid
        history: list[tuple[str, bool, float]] = None, #mid, received, timestamp
        ping: float=2.0
        ):

        self.cid=cid
        self.kind=kind
        self.sender=sender
        self.recipient=recipient

        self.history: list[tuple[str, bool, float]]=history if history is not None else [] #mid, received, timestamp
        self.transcript: list=[] #text, "left" or "right", "timestamp"

        self.ping=ping

        self.char=81

    def transcribe(self, add: tuple[str, bool, float]):
        if add:
            lines = text_lines(add[0], self.char)
            if add[1]:
                for line in lines:
                    self.transcript.append((line, "left", add[2]))
            else:
                for line in lines:
                    self.transcript.append((line, "right", add[2]))
        elif self.history:
            self.transcript = []
            for message in self.history:
                self.transcribe(message)
        else:
            return

    def personalize(self, mssg_type: MessageKind, sender: str, recipient: str) -> str:
        possibilities=[]

        for script in world.scripts.values():
            points = 0

            if script.kind != mssg_type:
                continue

            else:
                if script.sender == sender:
                    points += 1
                elif script.sender and sender != script.sender:
                    continue
                if script.recipient == recipient:
                    points += 1
                elif script.recipient and recipient != script.recipient:
                    continue

            possibilities.append((script, points))

        possibilities.sort(key = lambda x: x[1], reverse = True)

        choice = random.choice(possibilities)[:3]
        return choice[0]

    def can_send(self) -> dict:
        mssgs = {}
        if self.kind == CommKind.AUTO:
            if self.history[-1].kind in (MessageKind.ACKNOWLEDGEMENT, MessageKind.GREETING):

                mssgs["new_task"] = Message(
                    mid = "new_task",
                    comm = self,
                    sender = self.sender,
                    recipient = self.recipient,
                    mssg_type = MessageKind.TASK_NEW,
                    text = self.personalize(MssgType.TASK_NEW, self.sender, self.recipient)
                )

        return mssgs

    def send(self, message: tuple[str, bool, float]):
        self.history.append(message)
        self.transcribe(message)
        game.send_message(self, message)

    def receive(self, message: tuple[str, bool, float]):
        self.history.append(message)
        self.transcribe(message)

    def response(self, message: tuple[str, bool, float]):
        pass

def build_comms():

    world.comms["hai"] = Comm(
        cid = "hai",
        comm_type = CommKind.AUTO,
        sender = world.player.pid,
        recipient = "hai",
    )

#build world---------------------------------------------------------------------------------------

from data.facilities_design import build_facilities
from data.objects_design import build_objects
from data.people_design import build_people
from data.script_design import Script, build_scripts

def build_default_world():
    world.facilities = {}
    world.objects = {}
    world.people = {}
    world.scripts = {}
    world.comms = {}
    world.time = 0

    build_objects()
    build_facilities()
    build_people()
    build_comms()
    build_scripts()

