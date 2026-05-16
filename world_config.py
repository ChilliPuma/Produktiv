from enum import Enum, auto
from zoneinfo import available_timezones


# Enums‐-----------------------------------------

class Action(Enum):
    SURFACE_NORMAL = auto()

    CUT = auto()
    HAMMER = auto()

    CARRY = auto()

class CommKind(Enum):
    HAI = auto()
    STAFF = auto()
    NPC = auto()

class Faction(Enum):
    INDEPENDENT = auto()

    MORMON = auto()

class Intent(Enum):
    NONE = auto()
    CANCEL = auto()

    GREETING = auto()
    ACKNOWLEDGE = auto()
    THANKS = auto()
    WELCOME = auto()

    ADVICE_ASK = auto()
    ADVICE_GIVE = auto()
    ADVICE_MORE = auto()

    STATUS = auto()
    PROBLEM = auto()

    TASK_ADD = auto()
    TASK_REPEAT = auto()
    TASK_PRODUCE_RECIPE = auto()
    TASK_PRODUCE_METHOD = auto()

    TASK_REQUEST = auto()
    TASK_CAN_PRODUCE = auto()
    TASK_HOW_PRODUCE = auto()

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

class StorageKind(Enum):
    NONE = auto()

    AMMO_9MM = auto()

    OBJECT = auto()
    GRAIN = auto()
    LIQUID = auto()
    GAS = auto()

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
            lines.append(line)
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
                 actions: dict[Action, float] = None, #Action: rank 0-10
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
        self.actions = actions or {}

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

class Recipe:
    def __init__(
        self,
        name: str,
        product: tuple[Object, int],
        inputs: dict[Object, int],
        surfaces: list[Action], #SURFACE_ Actions
        method: list[tuple[Action, float]], #step by step of action and normal time
        byproducts: list[tuple[Object, int]] = None
    ):
        self.name = name
        self.product = product
        self.inputs = inputs
        self.surfaces = surfaces
        self.method = method
        self.byproducts = byproducts if byproducts is not None else []

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

    def can_produce(self, person: "Person"):
        can_produce = {}
        inventory = self.all_inventory()
        useless_objs = []
        for surface_candidate in inventory:

            for recipe in person.recipes:
                how_produce = []
                for surface in recipe.surfaces:
                    if surface not in surface_candidate.actions:
                        continue

                    surface_storage = surface_candidate.all_storage()
                    used_inputs = []
                    matched_inputs = {}
                    no_inputs = False
                    for input_candidate in surface_storage:
                        if input_candidate in used_inputs:
                            continue
                        for input_obj in recipe.inputs.keys():
                            if not input_candidate.is_instance(input_obj):
                                continue
                            used_inputs.append(input_candidate)
                            matched_inputs.setdefault(input_obj, []).append(input_candidate)
                    for matched_input, obj_list in matched_inputs.items():
                        if recipe.inputs[matched_input] > len(obj_list):
                            no_inputs = True
                            break
                    if no_inputs:
                        continue

                    matched_tools = {}
                    no_tools = False
                    for tool_candidate in surface_storage:
                        if tool_candidate in used_inputs:
                            continue
                        for i, (action, time) in enumerate(recipe.method):
                            if action not in tool_candidate.actions:
                                if action not in surface_candidate.actions:
                                    continue
                                tool_candidate = surface_candidate
                            if matched_tools.get(i):
                                if tool_candidate.actions[action] > matched_tools.get(i):
                                    matched_tools[i] = tool_candidate
                            else:
                                matched_tools[i] = tool_candidate

                    if len(matched_tools) < len(recipe.method):
                        no_tools = True
                    if no_tools:
                        continue

                    how_produce.append(
                        {
                            "surface": surface_candidate,
                            "inputs": matched_inputs,
                            "tools": matched_tools,
                        }
                    )


        return can_produce

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
        recipes: list[Recipe] = None,
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
        self.skills = skills
        self.temperament = temperament
        self.recipes = recipes if recipes is not None else []
        self.facility = facility
        self.area = area
        self.nation = nation
        self.faction = faction
        self.title = title

class Message:
    def __init__(self,
        intent: Intent,
        text: str,
        sender: Person = None,
        recipient: Person = None,
        comm: "Comm" = None,
        incoming: bool = None,
        timestamp: float = None,
        data: dict = None #for formatting and game_logic
    ):
        self.intent = intent
        self.text = text
        self.sender = sender
        self.recipient = recipient
        self.comm = comm
        self.incoming = incoming
        self.timestamp = timestamp
        self.data = data

class Comm:
    def __init__(self,
        cid: str,
        kind: CommKind,
        sender: Person,
        recipient: Person,
        trust: float, #max 10
        history: list[Message] = None,
        transcript: list[tuple[str, Message]] = None, #message text, message source
        responses: list[Message] = None,
        ping: float = 2.0
        ):

        self.cid = cid
        self.kind = kind
        self.sender = sender
        self.recipient = recipient
        self.trust = trust

        self.history: list[Message] = history if history is not None else []
        self.transcript: list[tuple[str, Message]] = transcript if transcript is not None else []
        self.responses: list[dict] = responses if responses is not None else []

        self.ping = ping
        self.new_message = False

        self.char = 81

    def transcribe(self, message: Message):
        lines=text_lines(message.text, self.char)
        for line in lines:
                self.transcript.insert(
                    0, (line, message)
                )

    def names(self) -> dict[str, str]:
        r_name = self.recipient.name
        r_first_name = r_name.split()[0]

        s_name = self.sender.name
        s_first_name = s_name.split()[0]

        names_dict = {
            "recipient_name": r_name,
            "recipient_first_name": r_first_name,
            "sender_name": s_name,
            "sender_first_name": s_first_name,
        }
        return names_dict
