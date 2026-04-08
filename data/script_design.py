from world_config import Temperament, MssgType, Skill, Sex


class Script:
    scripts = {}
    def __init__(self,
        text: str,
        mssg_type: MssgType,
        sender: str = None,
        recipient: str = None,
        s_sex: Sex = None,
        r_sex: Sex = None,
        temperament: list[Temperament] = None,
        age: tuple[int] = None,
        skills: dict[Skill, list[float]] = None
        ):

        self.text = text
        self.mssg_type = mssg_type
        self.sender = sender
        self.recipient = recipient
        self.s_sex = s_sex
        self.r_sex = r_sex
        self.temperament = temperament if temperament else []
        self.age = age if age else ()
        self.skills = skills if skills else {}

        self.sid = f"{self.mssg_type.name}"
        self.sid_no = 1

        if self.sender:
            self.sid += f"_s:{self.sender}"
        elif self.s_sex:
            self.sid += f"_s:{self.s_sex}"
        if self.recipient:
            self.sid += f"_r:{self.recipient}"
        elif self.r_sex:
            self.sid += f"_r:{self.r_sex}"
        if self.temperament:
            for t in temperament:
                self.sid += f"_t:{t.name}"
        if self.age:
            self.sid += f"_a:{self.age[0]}-{self.age[1]}"
        if self.skills:
            for skill, value in skills.items():
                self.sid += f"_sk:{skill.name}:{value[0]}-{value[1]}"

        for script in Script.scripts:
            self.sid_no += 1
            self.sid += f"_{self.sid_no}"

        Script.scripts[self.sid_no] = self
