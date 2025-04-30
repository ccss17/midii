import numpy as np
from numba import njit


@njit(cache=True, fastmath=True)
def _quantize_w_error_forward(ticks, unit):
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


def _quantize_wo_error_forward(ticks, unit):
    """
    Vectorised midpoint–round-half-up (no error carry).
    """
    q = ticks // unit
    r = ticks - q * unit
    up = r * 2 >= unit
    quantized = (q + up.astype(np.int64)) * unit
    errors = np.where(up, r - unit, r)
    return quantized, errors.sum()


def quantize(ticks, unit, error_forwarding=True):
    if unit <= 0:
        raise ValueError
    ticks_arr = np.asarray(ticks)

    print("unit", unit)
    if error_forwarding:
        q, err = _quantize_w_error_forward(ticks_arr, unit)
    else:
        q, err = _quantize_wo_error_forward(ticks_arr, unit)

    return q.tolist(), err
