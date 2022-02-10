def fstr(text: str, **variables):
    return eval(f"f'{text}'", {**variables})