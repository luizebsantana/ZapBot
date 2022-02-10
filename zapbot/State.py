from dataclasses import dataclass
from zapbot.Action import Evaluate, Say, Goto, ACTIONS
from zapbot.Conditions import CONDITIONS
from zapbot.Action import Action

@dataclass(frozen=True)
class Payload:
    message: str
    state: str

class State:

    name: str
    variables: list[str]
    actions: list[Action]
    timeout: int
    evaluate: list[Evaluate]

    def __init__(self, name: str, variables: list[str]=None, timeout: int=None, evaluate: list[any]=None, **kargs) -> None:
        self.name: str = name
        self.variables: list[str] = variables
        self.actions: list[Action] = [ACTIONS[k](v) for k, v in kargs.items()]
        self.timeout: int = timeout
        self.evaluate: list[Evaluate] = [Evaluate(CONDITIONS[str(e['type']).lower()](**e['args'] if 'args' in e else {}), e['then'], e['else'] if 'else' in e else None) for e in evaluate]

    def start(self, **variables) -> Payload:
        message:list[str] = []
        for action in self.actions:
            if type(action) == Say:
                message.extend(action(**variables))
        return Payload(state=None, message=message)
    
    def eval(self, **variables) -> Payload:
        message:list[str] = []
        for condtion in self.evaluate:
            conditon_evaluated = condtion(**variables)
            if conditon_evaluated:
                actions = [ACTIONS[k](v) for k, v in conditon_evaluated.items()]
                for action in actions:
                    if type(action) == Say:
                        message.extend(action(**variables))
                    elif type(action) == Goto:
                        goto = action(**variables)
                        if goto:    
                            return Payload(state=goto, message=message)
        return Payload(state=None, message=message)

    def __str__(self) -> str:
        string = f'State({self.name}'
        if self.variables:
            string += f', variables={self.variables}'
        if self.timeout:
            string += f', timeout={self.timeout}'
        return string+')'
