from world_config import MssgType, world


class Script:
    def __init__(self,
        sid: str,
        text: str,
        mssg_type: MssgType,
        sender: str = None,
        recipient: str = None
        ):

        self.sid = sid
        self.text = text
        self.mssg_type = mssg_type
        self.sender = sender
        self.recipient = recipient

def build_scripts():

    world.scripts["GREETING_1"] = Script(
        sid = "GREETING_1",
        text = "Hello",
        mssg_type = MssgType.GREETING
    )
    world.scripts["GREETING_s:hai_1"] = Script(
        sid = "GREETING_s:hai_1",
        text = "Greetings, how may I assist you today?",
        mssg_type = MssgType.GREETING,
        sender = "hai"
    )

    world.scripts["TASK_NEW_r:hai"] = Script(
        sid = "TASK_NEW_r:hai",
        text = "Set up a new task",
        mssg_type = MssgType.TASK_NEW,
        recipient = "hai"
    )