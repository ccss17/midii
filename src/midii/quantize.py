import numpy as np
from numba import njit


@njit(cache=True, fastmath=True)
def _quantize_w_error_forward(targets, unit):
    """
    Sequential quantization with error forwarding.
    Returns quantized targets array + final accumulated error.
    """
    quantized_targets = np.empty_like(targets)
    err = 0
    for i in range(targets.size):
        if targets[i] + err >= 0:
            # compensating for synchronization distortion with the original
            targets[i] += err
            err = 0
        r = targets[i] % unit
        if r * 2 < unit:  # round down
            err += r
            quantized_targets[i] = targets[i] - r
        else:  # round up
            err += r - unit
            quantized_targets[i] = targets[i] + (unit - r)
    return quantized_targets, err


def _quantize_wo_error_forward(targets, unit):
    """
    Vectorised midpoint–round-half-up (no error carry).
    """
    q = targets // unit
    r = targets - q * unit
    up = r * 2 >= unit
    quantized = (q + up.astype(np.int64)) * unit
    errors = np.where(up, r - unit, r)
    return quantized, errors.sum()


def quantize(target_list, unit, error_forwarding=True):
    if unit <= 0:
        raise ValueError
    target_list = np.asarray(target_list)

    print("unit", unit)
    if error_forwarding:
        q, err = _quantize_w_error_forward(target_list, unit)
    else:
        q, err = _quantize_wo_error_forward(target_list, unit)

    return q.tolist(), err
