from world_config import Facility, world, Person, Area


def update_ownership():
    for facility in world.facilities.values():
        if facility in world.owned_facilities:
            if facility.owner != world.player.pid:
                world.owned_facilities.remove(facility)
            else:
                continue
        elif facility.owner == world.player.pid:
            world.owned_facilities.append(facility)


def design_space(objs:list[tuple[str, int, list]]):
    to_fill = []
    for obj in objs:
        for i in range(obj[1]):
            creature = world.objects[obj[0]].create()
            if obj[2]:
                creature.storage = design_space(obj[2])
            to_fill.append(creature)
    return to_fill

def add_person(f: str, a: str, person: Person):
    world.facilities[f].areas[a].staff[person.pid] = person
    person.location = world.facilities[f].areas[a]

def build_facilities():

    world.facilities["shed_backyard"] = Facility (
        fid = "shed_backyard",
        name = "Backyard shed",
        areas = {
            "interior": Area(
                name = "Interior",
                aid = "interior",
                area = 28,
                inventory = design_space([
                    ("bench_work", 1, []),
                    ("box_cardboard_m", 1, []),
                    ("box_cardboard_l", 1, []),
                    ("box_cardboard_s", 1, [
                        ("bit_rivet", 12, [])]),
                    ("box_cardboard_l", 1, [
                        ("knife", 2, []),
                        ("knife_blade", 5, []),
                        ("knife_handle", 3, [])
                    ])
    ])
            ),
            "exterior": Area(
                name = "Exterior",
                aid = "exterior",
                area = 110,
            )
        },
        staff_max = 7,
        power = 2000,
        location = ((41.139111, -83.143000), "Tiffin - Ohio, USA"),
        owner = "smith_guy"
    )

    world.facilities["warehouse_abandoned_airfield"] = Facility(
        fid = "warehouse_abandoned_airfield",
        name = "Abandoned airfield",
        areas = {
            "hangar": Area(
                name = "Hangar",
                aid = "hangar",
                area = 2000
            )
        },
        staff_max= 100,
        power = 0,
        location = ((41.09211, -83.20497), "Tiffin - Ohio, USA" ),
    )


