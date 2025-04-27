__all__ = [
    "tick2beat",
    "beat2tick",
    "note_number_to_name",
    "duration_secs_to_frames",
]

import numpy as np

from .config import DEFAULT_HOP_LENGTH, DEFAULT_SAMPLING_RATE


# Adapted from . (.py)
# Source: https://github.com/././blob/main/..py
# Original License: MIT
def duration_secs_to_frames(
    note_duration_sec, sr=DEFAULT_SAMPLING_RATE, hop_length=DEFAULT_HOP_LENGTH
):
    """
    If the unit of the note duration is "seconds", the unit should be converted to "frames"
    Furthermore, it should be rounded to integer and this causes rounding error
    This function includes error handling process that alleviates the rounding error
    """
    note_duration_sec = np.asarray(note_duration_sec)
    frames_per_sec = sr / hop_length
    note_duration_frame = note_duration_sec * frames_per_sec
    note_duration_frame_int = note_duration_frame.copy().astype(np.int64)
    errors = (
        note_duration_frame - note_duration_frame_int
    )  # rounding error per each note
    errors_sum = int(np.sum(errors))
    if errors_sum:
        top_k_errors_idx = errors.argsort()[-errors_sum:][::-1]
        if note_duration_frame_int.shape:
            for i in top_k_errors_idx:
                note_duration_frame_int[i] += 1

    return note_duration_frame_int


def tick2beat(tick, ticks_per_beat):
    return tick / ticks_per_beat


def beat2tick(beat, ticks_per_beat):
    return int(beat * ticks_per_beat)


# Adapted from pretty_midi (utilities.py)
# Source: https://github.com/craffel/pretty-midi/blob/main/pretty_midi/utilities.py
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
