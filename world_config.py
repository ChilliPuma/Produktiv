import logging

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

class World:
    def __init__(self,
                 facilities: dict[str, "Facility"] = None,
                 objects: dict[str, "Object"] = None,
                 people: dict[str, "Person"] = None,
                 player: "Person" = None,
                 comms: dict[str, "Comm"] = None,
                 time: float = 0):
        self.facilities = facilities if facilities else {}
        self.owned_facilities = []
        self.objects = objects if objects else {}
        self.people = people if people else {}
        self.player = player
        self.comms = comms if comms else {}

        self.time = time  # seconds
        self.time_stop = True

        self.comms_lag: tuple[bool, float, float] = (False, 0.0, 2.0)

    def tick(self, dt: float):
        if self.time_stop:
            return
        self.time += dt
        self.comms_lag += dt

        for f in self.owned_facilities:
            for a in f.areas.values():
                pass

    def wait



world = World()

#Objects--------------------------------------------------------------------

class Object:
    def __init__(self,
                 oid: str,
                 name: str,
                 weight: float,  # kg
                 volume: float,  # L (dcm^3)
                 area: float, # m²
                 substance: Substance = None,
                 components: dict[str, int] = None,
                 can_contain: dict[CanContain, tuple[
                     float, float]] = None,  # weight, volume
                 contents: dict[Substance, float] = None,
                 storage: list["Object"] = None,
                 can_produce: dict[
                     str, float] = None,
                 description: str = ""):  # ingame secs

        self.oid = oid
        self.name = name

        self.weight = weight
        self.volume = volume
        self.area = area
        self.substance = (
                substance or Substance.COMPOSITE)
        self.components = components or {}

        self.can_contain = can_contain or {
            CanContain.NONE: (0.0, 0.0)}
        self.contents = contents or {}
        self.storage = storage or []

        self.can_produce = can_produce or {}

        self.description = description

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
        inventory: list[Object] = None,
        ):

        self.name = name
        self.aid = aid
        self.level = level
        self.area = area
        self.inventory = inventory or []

        self.staff: dict[str, "Person"] = {} # pid, person

#Facilities-------------------------------------------------------

class Facility:
    def __init__(self, *,
        fid: str,
        name: str,
        areas: dict[str, Area],  # area name, m²]
        staff_max: int,
        power: float, # W
        location: tuple[tuple, str],  # (x,y), (City, Country)
        owner: str = None):

        self.fid = fid
        self.name = name
        self.areas = areas
        self.staff_capacity = staff_max
        self.power = power
        self.location = location
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

    def total_staff(self) -> int:
        total = 0
        for a in self.areas.values():
            s = len(a.staff)
            total += s
        return total

#staff---------------------------------------------------------------------------------------------

class Person:
    def __init__(self,
        name: str,
        pid: str,
        sex: Sex,
        age: int,
        homeland: str,
        skills: dict[Skill, float], # max 10
        temperament: Temperament,
        location: Area = None
        ):

        self.name = name
        self.pid = pid
        self.sex = sex
        self.age = age
        self.homeland = homeland
        self.skills = skills
        self.temperament = temperament
        self.location = location

        world.people[pid] = self

class Task:
    def __init__(self,
        name: str,
        tid: str,
        ):

        self.name = name

class Mssg:
    def __init__(self,
        mid: str,
        sender: str, #pid
        recipient: str, #pid
        mssg_type: MssgType,
        text: str
        ):

        self.mid = mid
        self.sender = sender
        self.recipient = recipient
        self. mssg_type = mssg_type
        self.text = text

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
        self.ping: tuple[float, float] = (0.0, 2.0) #elapsed, req

        world.comms[self.cid] = self

    def can_send(self) -> dict:
        mssgs = {}
        if self.comm_type == CommType.AUTO:
            if self.history[-1].mssg_type in (MssgType.ACKNOWLEDGEMENT, MssgType.GREETING):

                mssgs["new_task"] = Mssg(
                    mid = "new_task",
                    sender = self.sender,
                    mssg_type = MssgType.TASK_NEW,
                    text = self.personalize(MssgType.TASK_NEW, self.sender)
                )

        return mssgs

    def send(self, mssg: Mssg):
        self.history.append(mssg)
        self.ping[0] = 0.0
        world.processes.append(self)

    def response(self, mssg: Mssg):
        self.history.append(mssg)

    def tick(self, dt: float): #seconds
        if ping[0] < ping[1]:
            ping += dt
            else:
                self.response(self.history[-1])
        else:
            return

#build world---------------------------------------------------------------------------------------

from data.facilities_design import build_facilities
from data.objects_design import build_objects
from data.people_design import build_people

def build_default_world():
    world.facilities = {}
    world.objects = {}
    world.people = {}
    world.time = 0

    build_objects()
    build_facilities()
    build_people()

