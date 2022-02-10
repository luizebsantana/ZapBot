
from abc import abstractmethod
from zapbot.Conditions import Condition
from zapbot.util import fstr

class Action:

    name: str

    def __init__(self, name: str) -> None:
        self.name: str = name

    def __call__(self,**kwds: any) -> str:
        return self.exec(**kwds)

    @abstractmethod
    def exec(self, **variables) -> str:
        pass

    def __str__(self) -> str:
        return f'Action({self.name})'

class Evaluate(Action):

    def __init__(self, condition: Condition, _then: list[Action], _else: list[Action]) -> None:
        super().__init__('evaluate')
        self.codition = condition
        self._then: list[Action] = _then
        self._else: list[Action] = _else

    def exec(self, **variables) -> str:
        if self.codition(**variables):
            return self._then
        else:
            return self._else

class Say(Action):

    template_messages: list[str]

    def __init__(self, template_messages: list[str]) -> None:
        super().__init__('say')
        self.template_messages: list[str] =  template_messages

    def exec(self, **variables) -> str:
        if type(self.template_messages) == list:
            return [fstr(msg, **variables) for msg in self.template_messages]
        else:
            return [fstr(self.template_messages, **variables)]

class Goto(Action):

    def __init__(self, state: str) -> None:
        super().__init__('goto')
        self.state: str = state

    def exec(self, **variables) -> str:
        return fstr(self.state, **variables)

ACTIONS = {
    'say': Say,
    'goto': Goto,
}