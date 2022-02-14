class State:

    name: str
    functions: list[tuple[str, dict]]
    i: int = 0

    def __init__(self, name: str, functions: list[dict] or dict[str, dict]) -> None:
        self.name = name
        if functions:
            self.functions = [tuple(f.items())[0] for f in functions] if type(functions)==list\
                else list(functions.items())
        else:
            self.functions = []

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < len(self.functions):
            function = self.functions[self.i]
            self.i += 1
            return function
        self.i = 0
        raise StopIteration

    def __len__(self) -> int:
        return len(self.functions)

    def __str__(self):
        return f'State({self.name.upper()}, actions={self.functions})'

    def __repr__(self) -> str:
        return str(self)
