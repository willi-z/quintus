units = {
    "A": 1,
    "mA": 1e-3,
    "h": 60 * 60,
    "s": 1,
    "kg": 1,
    "g": 1e-3,
    "mg": 1e-6,
    "m": 1,
    "dm": 1e-1,
    "cm": 1e-2,
    "mm": 1e-3,
    "µm": 1e-6,
    "%": 1e-2,
    "V": 1,
    "Pa": 1,
    "kPa": 1e3,
    "MPa": 1e6,
    "GPa": 1e9,
    "°C": "change system",
    "C": 1,
    "Wh": 60 * 60,
    "N": 1,
}

operators = {"^": "**"}


def sort_units_by_priority():
    def len_prio(unit: tuple):
        return len(unit[0])

    global units
    units = dict(sorted(units.items(), key=len_prio, reverse=True))


sort_units_by_priority()


def parse_unit(unit: str) -> float:
    """

    creates an numerical expression, wich can be evaluted in the end with eval
    """
    if unit is None:
        return 1

    for key in units:
        # check each unit in list
        index = unit.find(key)
        if index != -1:
            # if unit exists in expression
            # replace it with the value
            unit = unit.replace(key, str(units.get(key)))
            if index - 1 <= 0:
                continue
            if unit[index - 1].isalpha() or unit[index - 1].isnumeric():
                """ """
                unit = unit[:index] + "*" + unit[index:]

    for key in operators:
        unit = unit.replace(key, str(operators.get(key)))

    return eval(unit)


def parse_value(value_str: str) -> tuple[float, tuple[float, float]]:
    minimum = maximum = 0

    value_str = value_str.replace(" ", "")

    index_start = value_str.find("(")
    if index_start != -1:
        value = eval(value_str[:index_start])
        index_end = value_str.rfind(")")
        tol = value_str[index_start + 1 : index_end]
        if tol.startswith("+/-"):
            deviation = eval(tol[3:])
            maximum = +deviation
            minimum = -deviation
    else:
        value = eval(value_str)
        minimum = maximum = 0

    return value, (minimum, maximum)
