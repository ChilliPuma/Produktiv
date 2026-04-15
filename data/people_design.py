from data.facilities_design import add_person, update_ownership
from world_config import world, Person, Sex, Skill, Temperament

def build_people():

    world.people["smith_guy"] = Person(
        name = "Guy Smith",
        pid = "smith_guy",
        sex = Sex.MALE,
        age = 27,
        nation = "Tiffin - Ohio, USA",
        skills = {
            Skill.FIT: 3.0,
            Skill.VIT: 4.2,
            Skill.SOC: 1.4,
            Skill.INT: 2.5
        },
        temperament = Temperament.PHLEGMATIC,
        title = "Dropout Engineer"
    )
    add_person("shed_backyard", "interior", world.people["smith_guy"])

    world.player = world.people["smith_guy"]

    update_ownership()