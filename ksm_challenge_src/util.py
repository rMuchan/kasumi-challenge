class BiasedRandomFormat:
    def __init__(self, val):
        self._val = NumFormat(val[0])
        self._appraise = val[1]

    def __format__(self, format_spec: str):
        return format(self._val, format_spec) + f'({self._appraise})'


class NumFormat:
    def __init__(self, val: float):
        self._val = val

    def __format__(self, format_spec: str):
        if format_spec and format_spec[-1] == '%':
            format_spec = format_spec[:-1]
            return format(self._val * 100, format_spec or '.0f') + '%'

        return format(self._val, format_spec or '.0f')


def recurrence(a_1: float, k: float, m: float, n: int) -> float:
    return (a_1 - m) * k ** (n - 1) + m * ((k ** n - 1) / (k - 1) if k != 1 else n)
