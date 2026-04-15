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

class CommType(Enum):
    AUTO = auto()
    STAFF = auto()
    NPC = auto()

class MssgType(Enum):
    GREETING = auto()
    ACKNOWLEDGEMENT = auto()

    REQUEST_TASK = auto()

    STATUS = auto()
    PROBLEM = auto()

    TASK_NEW = auto()
    TASK_THEN = auto()
    TASK_ONLY_THEN = auto()

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
        nation: str = "",
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

class Mssg:
    def __init__(self,
        mid: str,
        comm: "Comm",
        sender: str, #pid
        recipient: str, #pid
        mssg_type: MssgType,
        text: str,
        timestamp: float = 0.0
        ):

        self.mid = mid
        self.sender = sender
        self.recipient = recipient
        self. mssg_type = mssg_type
        self.text = text
        self.timestamp = timestamp

class Comm:
    def __init__(self,
        cid: str,
        comm_type: CommType,
        sender: str, #pid
        recipient: str #pid
        ):

        self.cid = cid
        self.comm_type = comm_type
        self.sender = sender
        self.recipient = recipient

        self.history: list[Mssg] = []
        self.transcript: list = [] #text, "left" or "right"

        self.ping: list[float] = [0.0, 2.0] #elapsed, req
        self.scripted: list = [] #Mssg, t-

        world.comms[self.cid] = self

    def personalize(self, mssg_type: MssgType, sender: str, recipient: str) -> str:
        possibilities = []

        for script in world.scripts.values():
            points = 0

            if script.mssg_type != mssg_type:
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
        if self.comm_type == CommType.AUTO:
            if self.history[-1].mssg_type in (MssgType.ACKNOWLEDGEMENT, MssgType.GREETING):

                mssgs["new_task"] = Mssg(
                    mid = "new_task",
                    comm = self,
                    sender = self.sender,
                    recipient = self.recipient,
                    mssg_type = MssgType.TASK_NEW,
                    text = self.personalize(MssgType.TASK_NEW, self.sender, self.recipient)
                )

        return mssgs

    def send(self, mssg: Mssg):
        mssg.timestamp = world.time
        self.history.append(mssg)
        for line in text_lines(mssg.text, 81):
            self.transcript.append((line, mssg.timestamp, "right"))
        self.ping[0] = 0.0
        world.processes.append(self)

    def receive(self, mssg: Mssg):
        self.history.append(mssg)
        for line in text_lines(mssg.text, 81):
            self.transcript.append((line, mssg.timestamp, "left"))

    def response(self, mssg: Mssg):
        pass

    def script(self, script: "Script", time: float):
        mssg = Mssg(
            mid = script.sid,
            mssg_type = script.mssg_type,
            comm = self,
            sender = self.recipient,
            recipient = self.sender,
            text = script.text
        )
        self.scripted.append((mssg, time))
        world.processes.append(self) if self not in world.processes else None

    def tick(self, dt: float):#seconds
        print(self.scripted)
        if self.ping[0] < self.ping[1]:
            self.ping[0] += dt

        elif self.scripted:
            new_scripted = []
            for mssg, time in self.scripted:
                if time - dt <= 0:
                    self.receive(mssg)
                else:
                    time -= dt
                    new_scripted.append((mssg, time))
            self.scripted = new_scripted

        else:
            world.processes.remove(self)
            self.response(self.history[-1]) if self.history[-1].sender == self.sender else None

def build_comms():

    world.comms["hai"] = Comm(
        cid = "hai",
        comm_type = CommType.AUTO,
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

