import os, io, re
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from fsm.state import State
from fsm.exception import *
from fsm.util import date_parser


class FunctionDef:
    @staticmethod
    def fstr(value: str, variables) -> str:
        regex = r'{.+}'
        rep = re.search(regex, value)
        while rep:
            value = value[:rep.span(0)[0]]+str(eval(rep.group(0)[1:-1], variables))+value[rep.span(0)[1]:]
            rep = re.search(regex, value)
        return value

    def goto(fsm: 'FSM', state: str) -> bool:
        fsm.state = state

    def call(fsm: 'FSM', state: str) -> bool:
        pass
        # fsm._exec_state(state)

    def define(fsm: 'FSM', _dict: str) -> bool:
        fsm._current_variables.update({k:FunctionDef.fstr(v, fsm._current_variables) for k ,v in _dict.items()})

    def condition(fsm: 'FSM', content: dict) -> bool:
        block = 'then' if eval(content['eval'], fsm._current_variables) else 'else'
        if block in content:
            for function, body in State(block, content[block]):
                fsm._exec_function(function, body)

    def input(fsm: 'FSM', content) -> None:
        fsm._current_variables.update({n:input(f'{n}: ') for n in content})
        print(fsm._current_variables)
        fsm.pause()
        
    def say(fsm: 'FSM', value) -> None:
        print(FunctionDef.fstr(value, fsm._current_variables))


class FSM:

    name: str
    __state: str
    __states: list[State]
    _interrupt: bool = False
    _pause: bool = False
    _halt: bool = False
    _current_variables: dict[str, any] = {'DATE': date_parser}
    _function_def: type = FunctionDef
    #  __state_index: int

    @staticmethod
    def loadYAML(path:str=None) -> 'FSM':
        path = os.path.normpath(path)
        yaml_dict = yaml.load(io.FileIO(path), Loader)
        return FSM(**yaml_dict)

    def __init__(self, name:str=None, states:dict=None, state: str='begin', **variables) -> None:
        self.name = name
        self.__state = state
        self.__states = {n:State(n, states[n]) for n in states}
        self._current_variables.update(variables)

    def __setattr__(self, __name: str, __value: any) -> None:
        if __name == 'state':
            self.interrupt()
            self.__state=__value
        super().__setattr__(__name, __value)

    def pause(self):
        self._interrupt=True

    def interrupt(self):
        self._interrupt=True
        self.__states[self.__state].i=0

    def set_state(self, state):
        self.__states = state

    def _exec_function(self, function: str, body: dict) -> None:
        if function in self._function_def.__dict__:
            self._function_def.__dict__[function](self, body)
        else:
            raise InvalidKeywordException(function)

    def _exec_state(self, state_name: str) -> None:
        if state_name not in self.__states:
            raise InvalidStateException(state_name)
        state = self.__states[state_name]
        if len(state) == 0:
            self._halt = True
        for function, body in state:
            self._exec_function(function, body)
            if self._interrupt:
                break

    def execute(self, **variables):
        self._pause = False
        self._interrupt = False
        while not self._pause and not self._halt:
            self._current_variables.update(variables)
            self._exec_state(self.__state)
        
    def __str__(self):
        string = f'FSM({self.name}, {self.__states})'
        return string