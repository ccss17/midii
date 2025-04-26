from .config import DEFAULT_TICKS_PER_BEAT
from .utilities import beat2tick
from .note import Note


def _quantize(tick, unit, quanta):
    quantized_tick = 0
    for quantum in quanta:
        while tick >= quantum:
            tick -= quantum
            quantized_tick += quantum
        if quantum == unit:
            break
    error = 0
    if tick < unit / 2:
        error = tick
        tick = 0
    else:
        error = tick - unit
        tick = unit
    quantized_tick += tick
    return quantized_tick, error


def quantize(
    ticks,
    unit="32",
    ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
    quanta=None,
    error_forwarding=True,
):
    if quanta is None:
        quanta = [x.value.beat for x in list(Note)]
        if isinstance(unit, str) and not any(
            [unit == n.value.name_short.split("/")[-1] for n in list(Note)]
        ):
            raise ValueError
        elif isinstance(unit, int) and unit not in quanta:
            raise ValueError
        if isinstance(unit, str):
            for n in list(Note):
                if unit == n.value.name_short.split("/")[-1]:
                    unit = n.value.beat
    elif unit not in quanta:
        raise ValueError

    quanta = sorted(quanta, reverse=True)
    quanta_ticks = []
    for quantum in quanta:
        quanta_ticks.append(beat2tick(quantum, ticks_per_beat))
    unit = beat2tick(unit, ticks_per_beat)

    error = 0
    quantized_ticks = []
    for tick in ticks:
        if error_forwarding and error and tick + error >= 0:
            tick += error
            error = 0
        quantized_tick, _error = _quantize(
            tick, unit=unit, quanta=quanta_ticks
        )
        quantized_ticks.append(quantized_tick)
        error += _error
    return quantized_ticks, error
