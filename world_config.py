from enum import Enum, auto



# Enums‐-----------------------------------------

class StorageKind(Enum):
    NONE = auto()

    AMMO_9MM = auto()

    OBJECT = auto()
    GRAIN = auto()
    LIQUID = auto()
    GAS = auto()

class CommKind(Enum):
    HAI = auto()
    STAFF = auto()
    NPC = auto()

class Faction(Enum):
    INDEPENDENT = auto()

    MORMON = auto()

class MessageKind(Enum):
    ERROR = auto()
    CANCEL = auto()

    GREETING = auto()
    ACKNOWLEDGE = auto()
    THANKS=auto()
    WELCOME=auto()

    ADVICE_ASK=auto()
    ADVICE_GIVE=auto()

    STATUS = auto()
    PROBLEM = auto()

    TASK_ADD = auto()
    TASK_REPEAT = auto()

    TASK_REQUEST = auto()

    TASK_RECON = auto()
    TASK_PRODUCE = auto()

class Nation(Enum):
    NONE = auto()
    AMERICAN_WHITE = auto()


class Sex(Enum):
    MALE = auto()
    FEMALE = auto()
    NONE = auto()

class Skill(Enum):
    FIT = auto()
    VIT = auto()
    SOC = auto()
    INT = auto()

class Substance(Enum):
    COMPOSITE = auto()

    CARDBOARD = auto()
    STEEL = auto()
    WOOD = auto()

class Temperament(Enum):
    AI = auto()
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
                 time: float = 0):
        self.facilities = facilities if facilities else {}
        self.owned_facilities = []
        self.objects = objects if objects else {}
        self.people = people if people else {}
        self.player = player
        self.comms = comms if comms else {}

        self.time = time  # seconds
        self.time_stop = True

        self.processes: list = []

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

    def total_weight(self):
        total = self.weight
        if self.storage and self.storage["kind"] == "OBJECT":
            for content in self.storage["content"]:
                total += content.total_weight()
        return total

    def used_storage(self) -> float:
        total = 0
        if self.storage["kind"] == "OBJECT":
            for obj in self.storage["content"]:
                total += obj.volume
        return total

    def can_store(self, obj: "Object"):
        if self.storage:
            if self.storage["kind"] == "OBJECT":
                if obj.volume + self.used_storage() <= self.storage["max"]:
                    return True
        return False

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
        self.staff = staff if staff is not None else []
        self.staff_max = staff_max
        self.inventory = inventory if inventory is not None else []

    def used_area(self) -> float:
        used_area = 0.0
        for obj in self.inventory:
            used_area += obj.area

        return used_area

    def can_add(self, obj_area: float) -> bool:
        if obj_area + self.used_area() > self.area:
            return False
        else:
            return True

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

class Comm:
    def __init__(self,
        cid: str,
        kind: CommKind,
        sender: Person,
        recipient: Person,
        history: list[dict] = None, #message dict, received, timestamp
        transcript: list[dict] = None, #message text, side, timestamp
        responses: list[dict] = None,
        ping: float=2.0
        ):

        self.cid=cid
        self.kind=kind
        self.sender=sender
        self.recipient=recipient

        self.history: list[dict]=history if history is not None else []
        self.transcript: list[dict]=transcript if transcript is not None else []
        self.responses: list[dict]=responses if responses is not None else []

        self.ping=ping
        self.new_message=False

        self.char=81

    def transcribe(self, message: dict, received: bool, timestamp: float):
        lines=text_lines(message["text"], self.char)
        if received:
            for line in lines:
                self.transcript.insert(
                    0, {"text": line, "side": "left", "timestamp": timestamp}
                )
        else:
            for line in lines:
                self.transcript.insert(
                    0, {"text": line, "side": "right", "timestamp": timestamp}
                )
