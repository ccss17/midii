__all__ = ["tick2beat, beat2tick, note_number_to_name"]


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
