import logging

log = logging.getLogger(__name__)

import pygame
pygame.init()

from datetime import datetime
import json

from world_config import Object, Facility, world, build_default_world, Area, Person

from visual_config import BASE_DIR

saves_dir = BASE_DIR / "saves"

def new_save(save_file_name: str):
    if not save_file_name:
        save_file_name = f"{datetime.now():%Y%m%d_%H%M%S}"

    save_file = {
        "time": world.time,
        "objects": {oid: serialize_object(obj)
                    for oid, obj in world.objects.items()
                    },
        "facilities": {fid: serialize_facility(facility)
                       for fid, facility in world.facilities.items()
                       },
        "people": {pid: serialize_person(person)
                   for pid, person in world.people.items()}
    }

    saves_dir.mkdir(exist_ok=True)
    path = saves_dir / f"{save_file_name}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(save_file, f, indent=4)

def serialize_object(obj: Object) -> dict:
    return {
        "id": obj.oid,
        "name": obj.name,
        "weight": obj.weight,
        "volume": obj.volume,
        "substance": obj.substance.name,
        "components": {
            component_oid: qty
            for component_oid, qty in obj.components.items()
        },
        "can_contain": {
            content_type.name: qty
            for content_type, qty in obj.can_contain.items()
        },
        "contents": {
            substance.name: volume
            for substance, volume in obj.contents.items()
        },
        "storage": [
            stored_obj.oid for stored_obj in obj.storage
        ],
        "can_produce": {
            oid: prod_duration
            for oid, prod_duration in obj.can_produce.items()
        }
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
        "homeland": p.homeland,
        "skills": {
            skill.name: value for skill, value in p.skills.items()
        },
        "temperament": p.temperament.name,
    }

