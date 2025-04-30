__all__ = [
    "tick2beat",
    "beat2tick",
    "note_number_to_name",
    "second2frame",
    "frame2second",
]

import numpy as np

from .config import DEFAULT_HOP_LENGTH, DEFAULT_SAMPLING_RATE


def tick2beat(tick, ticks_per_beat):
    return tick / ticks_per_beat


def beat2tick(beat, ticks_per_beat):
    return int(beat * ticks_per_beat)


# Adapted from pretty_midi (utilities.py)
# Source: https://github.com/craffel/pretty-midi
# Copyright (c) 2014 Colin Raffel
# Original License: MIT
def note_number_to_name(note_number):
    """Convert a MIDI note number to its name, in the format
    ``'(note)(accidental)(octave number)'`` (e.g. ``'C#4'``).

    Parameters
    ----------
    note_number : int
        MIDI note number.  If not an int, it will be rounded.

    Returns
    -------
    note_name : str
        Name of the supplied MIDI note number.

    Notes
    -----
        Thanks to Brian McFee.

    """

    # Note names within one octave
    semis = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # Ensure the note is an int
    note_number = int(round(note_number))

    # Get the semitone and the octave, and concatenate to create the name
    return semis[note_number % 12] + str(note_number // 12 - 1)


def second2frame(
    seconds, sr=DEFAULT_SAMPLING_RATE, hop_length=DEFAULT_HOP_LENGTH
):
    """
    If the unit of the note duration is "seconds", the unit should be
    converted to "frames" Furthermore, it should be rounded to integer
    and this causes rounding error This function includes error handling
    process that alleviates the rounding error
    """
    is_scalar_input = np.isscalar(seconds)
    seconds_arr = np.atleast_1d(seconds)
    frames_per_sec = sr / hop_length
    frames = seconds_arr * frames_per_sec
    frames_int = np.floor(frames).astype(np.int64)
    errors = frames - frames_int
    errors_sum = int(np.round(np.sum(errors)))
    if errors_sum > 0 and not is_scalar_input:
        top_k_errors_idx = np.argpartition(errors, -errors_sum)[-errors_sum:]
        frames_int[top_k_errors_idx] += 1
    if is_scalar_input:
        return frames_int[0]
    else:
        return frames_int


def frame2second(
    frames, sr=DEFAULT_SAMPLING_RATE, hop_length=DEFAULT_HOP_LENGTH
):
    return hop_length / sr * frames
