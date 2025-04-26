from .config import DEFAULT_TICKS_PER_BEAT
from .utilities import beat2tick
from .note import Note


def _quantize(tick, unit):
    q, r = divmod(tick, unit)
    quantized_tick = q * unit
    error = 0
    if r < unit / 2:
        error = r
        r = 0
    else:
        error = r - unit
        r = unit
    quantized_tick += r
    return quantized_tick, error


def quantize(
    ticks,
    unit="32",
    ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
    error_forwarding=True,
):
    if isinstance(unit, str):
        for note in list(Note):
            if unit == note.value.name_short.split("/")[-1]:
                unit = note.value.beat
                break
        else:
            raise ValueError
    if unit not in [note.value.beat for note in list(Note)]:
        raise ValueError
    unit = beat2tick(unit, ticks_per_beat)
    error = 0
    quantized_ticks = []
    for tick in ticks:
        if error_forwarding and error and tick + error >= 0:
            tick += error
            error = 0
        quantized_tick, _error = _quantize(tick, unit=unit)
        quantized_ticks.append(quantized_tick)
        error += _error
    return quantized_ticks, error
