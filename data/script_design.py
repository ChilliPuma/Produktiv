from world_config import MssgType, world


class Script:
    def __init__(self,
        text: str,
        mssg_type: MssgType,
        sender: str = None,
        recipient: str = None
        ):

        self.text = text
        self.mssg_type = mssg_type
        self.sender = sender
        self.recipient = recipient

def build_scripts():

    world.scripts["GREETING_1"] = Script(
        text = "Hello",
        mssg_type = MssgType.GREETING
    )
    world.scripts["GREETING_s:AI_1"] = Script(
        text = "Greetings, how may I assist you today?",
        mssg_type = MssgType.GREETING,
        sender = "hai"
    )

    world.scripts["TASK_NEW_r:AI"] = Script(
        text = "Set up a new task",
        mssg_type = MssgType.TASK_NEW,
        recipient = "hai"
    )