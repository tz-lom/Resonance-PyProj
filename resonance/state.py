from enum import Enum


class ExecMode(Enum):
    INTERPRETER = 0
    OFFLINE = 1
    ONLINE = 2


inputs = []
mode = ExecMode.INTERPRETER


def set_mode(new_mode: ExecMode):
    global mode
    if new_mode == ExecMode.INTERPRETER:
        mode = new_mode
    else:
        if mode != ExecMode.INTERPRETER:
            raise Exception("Can't switch to mode " + new_mode + " from mode " + mode +
                            ". Probably you are trying to mix online and offline modes in one run")
        mode = new_mode

