from abc import abstractmethod
from zapbot.util import fstr

class Condition:
    @abstractmethod
    def eval(self, **variables):
        pass

    def __call__(self, **kwds: any) -> any:
        return self.eval(**kwds)


class MatchAll(Condition):

    template_text: str
    template_keywords: list[str]

    def __init__(self, text: str, keywords: list[str]) -> None:
        super().__init__()
        self.template_text = text
        self.template_keywords = keywords
    
    def eval(self, **variables):
        text = fstr(self.template_text, **variables)
        for key in self.template_keywords:
            if fstr(key, **variables) not in text:
                return False
        return True

class MatchAny(Condition):

    template_text: str
    template_keywords: list[str]

    def __init__(self, text: str, keywords: list[str]) -> None:
        super().__init__()
        self.template_text = text
        self.template_keywords = keywords
    
    def eval(self, **variables):
        text = fstr(self.template_text, **variables)
        for key in self.template_keywords:
            if fstr(key, **variables) in text:
                return True
        return False

class TRUE(Condition):

    def eval(self, **variables):
        return True
    
CONDITIONS = {
    'matchall': MatchAll,
    'matchany': MatchAny,
    'true': TRUE,
}