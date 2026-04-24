import pygame
pygame.init()

from datetime import datetime
import json

from world_config import Object, Facility, Area, Person

from data.visual_design import BASE_DIR

saves_dir = BASE_DIR / "saves"

def load_default():
    print("[loader] loading default save data")
    with open(BASE_DIR / "data/default_save.json") as f:
        return json.load(f)

def load_script():
    print("[loader] loading script data")
    with open(BASE_DIR / "data/script.json") as f:
        return json.load(f)

def new_save(save_file_name: str, save_data: dict):
    if not save_file_name:
        save_file_name = f"{datetime.now():%Y%m%d_%H%M%S}"

    saves_dir.mkdir(exist_ok=True)
    path = saves_dir / f"{save_file_name}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=4)
    print(f"[loader] saved game to {path.name}")

def serialize_object(obj: Object) -> dict:
    return {
        "id": obj.oid,
        "name": obj.name,
        "weight": obj.weight,
        "volume": obj.volume,
        "substance": obj.substance.name,
        "components": {
            oid: qty
            for oid, qty in obj.components.items()
        },
        "storage": [
            stored_obj.oid for stored_obj in obj.storage
        ],
        "production": {}
    }

def serialize_area(area: Area) -> dict:
    return {
        "name": area.name,
        "area": area.area,
        "inventory": [
            obj.oid for obj in area.inventory
        ]
    }

def serialize_facility(f: Facility) -> dict:
    return {
        "id": f.fid,
        "name": f.name,
        "areas": {
            a_name: serialize_area(area) for a_name, area in f.areas.items()
        },
        "power": f.power,
        "location": f.location,
    }

def serialize_person(p: Person) -> dict:
    return {
        "id": p.pid,
        "name": p.name,
        "age": p.age,
        "homeland": p.nation,
        "skills": {
            skill.name: value for skill, value in p.skills.items()
        },
        "temperament": p.temperament.name,
    }
