from world_config import Object, Substance, CanContain, world

def build_objects():

    world.objects["box_cardboard_s"] = Object(
        oid = "box_cardboard_s",
        name = "Cbd. box (S)",
        weight = 0.4,
        volume = 4.0,
        area = 0.02,
        substance = Substance.CARDBOARD,
        can_contain = {CanContain.OBJECT: (15, 4)},
        description = "A small cardboard box. Versatile but relatively fragile."
    )

    world.objects["box_cardboard_m"] = Object(
        oid = "box_cardboard_m",
        name = "Cbd. box (M)",
        weight = 0.9,
        volume = 40,
        area = 0.12,
        substance = Substance.CARDBOARD,
        can_contain = {CanContain.OBJECT: (50, 40)},
        description = "A medium size cardboard box. Versatile but relatively fragile."
    )

    world.objects["box_cardboard_l"] = Object(
        oid = "box_cardboard_l",
        name = "Cbd. box (L)",
        weight = 1.2,
        volume = 60,
        area = 0.7,
        substance = Substance.CARDBOARD,
        can_contain = {CanContain.OBJECT: (120, 60)},
        description = "A big cardboard box. Versatile but relatively fragile. Someone could even fit inside..."
    )

    world.objects["bit_rivet"] = Object(
        oid = "bit_rivet",
        name = "Rivet",
        weight = 0.06,
        volume = 0.004,
        area = 0.00001,
        substance = Substance.STEEL,
        description = "A rivet. Essential for binding metal pieces together."
    )

    world.objects["knife_handle"] = Object(
        oid = "knife_handle",
        name = "Knife Handle",
        weight = 0.6,
        volume = 0.3,
        area = 0.02,
        substance = Substance.WOOD_PINE,
        description = "A pinewood knife handle."
    )


    world.objects["knife_blade"] = Object(
        oid = "knife_blade",
        name = "Knife Blade",
        weight = 1.1,
        volume = 0.4,
        area = 0.01,
        substance = Substance.STEEL,
        description = "A steel knife blade."
    )

    world.objects["knife"] = Object(
        oid = "knife",
        name = "Knife",
        weight = 2.0,
        volume = 0.5,
        area = 0.03,
        components = {
            "bit_rivet": 2,
            "knife_handle": 1,
            "knife_blade": 1
        },
        description = "A knife. Can be used as a tool or a weapon, so choose wisely."
    )

    world.objects["bench_work"] = Object(
        oid = "bench_work",
        name = "Workbench",
        weight = 30.0,
        volume = 1600.0,
        area = 2.0,
        can_contain = {
            CanContain.OBJECT: (600.0, 1100.0)
        },
        can_produce = {
            "knife": 60.0
        },
        description = "A starter workbench. It has space for storage and can be used to create new objects."
    )



