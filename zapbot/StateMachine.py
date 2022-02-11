from zapbot.State import State
import io
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class StateMachine:

    state: str
    target_state: str
    name: str
    states: dict[str, State]

    def __init__(self, name:str=None, states:dict=None, state: str='begin') -> None:
        self.name = name
        self.states = {k:State(k, **v) for k, v in states.items()}
        self.target_state = state
        self.state = None

    def start(self, target_state, **variables):
        self.state = target_state
        return self.states[self.state].start(**variables)

    def send(self, **variables):
        message = []
        if self.state == None:
            payload = self.start(self.target_state, **variables)
        else:
            payload = self.states[self.state].eval(**variables)
            message.append(payload.message)
            if payload.state is not None:
                payload = self.start(payload.state, **variables)
            else:
                payload = self.start(self.state, **variables)
        message.append(payload.message)
        return message


if __name__=='__main__':
    from datetime import datetime

    yaml = yaml.load(io.FileIO('test/fsm.yaml'), Loader)

    machine = StateMachine(**yaml)

    while True:
        now = datetime.now()
        machine.send(sender="Thales", message=input("mensage: "), h=now.hour, m=now.min, s=now.second, D=now.day, M=now.month, A=now.year)