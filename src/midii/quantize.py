import numpy as np
from numba import njit
from typing import Sequence, Tuple

from .config import DEFAULT_TICKS_PER_BEAT
from .utilities import beat2tick
from .note import Note

_STR2BEAT = {n.value.name_short.split("/")[-1]: n.value.beat for n in Note}


@njit(cache=True, fastmath=True)
def _quantize_w_error_forward(
    ticks: np.ndarray, unit: int
) -> Tuple[np.ndarray, int]:
    """
    Sequential quantization with error forwarding.
    Returns quantized ticks array + final accumulated error.
    """
    quantized_ticks = np.empty_like(ticks)
    err = 0
    for i in range(ticks.size):
        if ticks[i] + err >= 0:
            ticks[i] += err
            err = 0
        r = ticks[i] % unit
        if r * 2 < unit:  # round down
            err += r
            quantized_ticks[i] = ticks[i] - r
        else:  # round up
            err += r - unit
            quantized_ticks[i] = ticks[i] + (unit - r)
    return quantized_ticks, err


def _quantize_wo_error_forward(
    ticks: np.ndarray, unit: int
) -> Tuple[np.ndarray, int]:
    """
    Vectorised midpoint–round-half-up (no error carry).
    """
    q = ticks // unit
    r = ticks - q * unit
    up = r * 2 >= unit
    quantized = (q + up.astype(np.int64)) * unit
    errors = np.where(up, r - unit, r)
    return quantized, int(errors.sum())


def quantize(
    ticks: Sequence[int] | np.ndarray,
    unit: str = "32",
    ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT,
    error_forwarding: bool = True,
) -> Tuple[list[int], int]:
    """
    Parameters
    ----------
    ticks            : iterable of int  –  input delta-ticks
    unit             : e.g. "32"  or numeric beat  or explicit int-ticks
    ticks_per_beat   : resolution (default 480)
    error_forwarding : if True propagate rounding error to next note

    Returns
    -------
    quantized_ticks  : list[int]
    final_error      : int   (may be negative)
    """

    try:
        unit_beat = _STR2BEAT[unit]
    except KeyError:
        raise ValueError(f"unknown unit string {unit!r}")
    unit_tick = beat2tick(unit_beat, ticks_per_beat)
    ticks_arr = np.asarray(ticks, dtype=np.int64)

    if error_forwarding:
        q, err = _quantize_w_error_forward(ticks_arr, unit_tick)
    else:
        q, err = _quantize_wo_error_forward(ticks_arr, unit_tick)

    return q.tolist(), err
