"""note rest information dictionary"""

from collections import namedtuple
from enum import Enum

DEFAULT_BPM = 120
DEFAULT_TEMPO = 500000
DEFAULT_TIME_SIGNATURE = (4, 4)
DEFAULT_PPQN = 480
DEFAULT_MEASURE_SPACE = 4

NoteNamedTuple = namedtuple(
    "NoteNamedTuple", ["beat", "name_eng", "name_kor", "symbol", "name_short"]
)


class Rest(Enum):
    """Rest Enum"""

    WHOLE_REST = NoteNamedTuple(4, "whole rest", "온쉼표", "𝄻", "r/1")
    HALF_REST = NoteNamedTuple(2, "half rest", "2분쉼표", "𝄼", "r/2")
    QUARTER_REST = NoteNamedTuple(1, "quarter rest", "4분쉼표", "𝄽", "r/4")
    EIGHTH_REST = NoteNamedTuple(0.5, "eighth rest", "8분쉼표", "𝄾", "r/8")
    SIXTEENTH_REST = NoteNamedTuple(
        0.25, "sixteenth rest", "16분쉼표", "𝄿", "r/16"
    )
    THIRTY_SECOND_REST = NoteNamedTuple(
        0.125, "thirty-second rest", "32분쉼표", "𝅀", "r/32"
    )
    SIXTY_FOURTH_REST = NoteNamedTuple(
        0.0625, "sixty-fourth rest", "64분쉼표", "𝅁", "r/64"
    )
    HUNDRED_TWENTY_EIGHTH_REST = NoteNamedTuple(
        0.03125, "hundred twenty-eighth rest", "128분쉼표", "𝅂", "r/128"
    )
    TWO_HUNDRED_FIFTY_SIXTH_REST = NoteNamedTuple(
        0.015625, "two hundred fifty-sixth rest", "256분쉼표", "𝅂", "r/256"
    )


class Note(Enum):
    """Note Enum"""

    WHOLE_NOTE = NoteNamedTuple(4, "whole note", "온음표", "𝅝", "n/1")
    HALF_NOTE = NoteNamedTuple(2, "half note", "2분음표", "𝅗𝅥", "n/2")
    QUARTER_NOTE = NoteNamedTuple(1, "quarter note", "4분음표", "♩", "n/4")
    EIGHTH_NOTE = NoteNamedTuple(0.5, "eighth note", "8분음표", "♪", "n/8")
    SIXTEENTH_NOTE = NoteNamedTuple(
        0.25, "sixteenth note", "16분음표", "𝅘𝅥𝅯", "n/16"
    )
    THIRTY_SECOND_NOTE = NoteNamedTuple(
        0.125, "thirty-second note", "32분음표", "𝅘𝅥𝅰", "n/32"
    )
    SIXTY_FOURTH_NOTE = NoteNamedTuple(
        0.0625, "sixty-fourth note", "64분음표", "𝅘𝅥𝅱", "n/64"
    )
    HUNDRED_TWENTY_EIGHTH_NOTE = NoteNamedTuple(
        0.03125, "hundred twenty-eighth note", "128분음표", "𝅘𝅥𝅲", "n/128"
    )
    TWO_HUNDRED_FIFTY_SIXTH_NOTE = NoteNamedTuple(
        0.015625, "two hundred fifty-sixth note", "256분음표", "𝅘𝅥𝅲", "n/256"
    )


class Rest_all(Enum):
    """Rest Enum"""

    DOTTED_OCTUPLE_WHOLE_REST = NoteNamedTuple(
        48, "dotted octuple whole rest", "점8온쉼표", "𝆶.", "r*8."
    )
    OCTUPLE_WHOLE_REST = NoteNamedTuple(
        32, "octuple whole rest", "8온쉼표", "𝆶", "r*8"
    )
    DOTTED_QUADRUPLE_WHOLE_REST = NoteNamedTuple(
        24, "dotted quadruple whole rest", "점4온쉼표", "𝅜𝅥.", "r*4."
    )
    QUADRUPLE_WHOLE_REST = NoteNamedTuple(
        16, "quadruple whole rest", "4온쉼표", "𝅜", "r*4"
    )
    DOTTED_DOUBLE_REST = NoteNamedTuple(
        12, "dotted double whole rest", "점겹온쉼표", "𝄺.", "r*2."
    )
    DOUBLE_WHOLE_REST = NoteNamedTuple(
        8, "double whole rest", "겹온쉼표", "𝄺", "r*2"
    )
    DOTTED_WHOLE_REST = NoteNamedTuple(
        6, "dotted whole rest", "점온쉼표", "𝄻.", "r/1."
    )
    WHOLE_REST = NoteNamedTuple(4, "whole rest", "온쉼표", "𝄻", "r/1")
    DOTTED_HALF_REST = NoteNamedTuple(
        3, "dotted half rest", "점2분쉼표", "𝄼.", "r/2."
    )
    HALF_REST = NoteNamedTuple(2, "half rest", "2분쉼표", "𝄼", "r/2")
    DOTTED_QUARTER_REST = NoteNamedTuple(
        1.5, "dotted quarter rest", "점4분쉼표", "𝄽.", "r/4."
    )
    QUARTER_REST = NoteNamedTuple(1, "quarter rest", "4분쉼표", "𝄽", "r/4")
    DOTTED_EIGHTH_REST = NoteNamedTuple(
        0.75, "dotted eighth rest", "점8분쉼표", "𝄾.", "r/8."
    )
    EIGHTH_REST = NoteNamedTuple(0.5, "eighth rest", "8분쉼표", "𝄾", "r/8")
    DOTTED_SIXTEENTH_REST = NoteNamedTuple(
        0.375, "dotted sixteenth rest", "점16분쉼표", "𝄿.", "r/16."
    )
    SIXTEENTH_REST = NoteNamedTuple(
        0.25, "sixteenth rest", "16분쉼표", "𝄿", "r/16"
    )
    DOTTED_THIRTY_SECOND_REST = NoteNamedTuple(
        0.1875, "dotted thirty-second rest", "점32분쉼표", "𝅀.", "r/32."
    )
    THIRTY_SECOND_REST = NoteNamedTuple(
        0.125, "thirty-second rest", "32분쉼표", "𝅀", "r/32"
    )
    DOTTED_SIXTY_FOURTH_REST = NoteNamedTuple(
        0.09375, "dotted sixty-fourth rest", "점64분쉼표", "𝅁.", "r/64."
    )
    SIXTY_FOURTH_REST = NoteNamedTuple(
        0.0625, "sixty-fourth rest", "64분쉼표", "𝅁", "r/64"
    )
    DOTTED_HUNDRED_TWENTY_EIGHTH_REST = NoteNamedTuple(
        0.046875,
        "dotted hundred twenty-eighth rest",
        "점128분쉼표",
        "𝅂.",
        "r/128.",
    )
    HUNDRED_TWENTY_EIGHTH_REST = NoteNamedTuple(
        0.03125, "hundred twenty-eighth rest", "128분쉼표", "𝅂", "r/128"
    )
    DOTTED_TWO_HUNDRED_FIFTY_SIXTH_REST = NoteNamedTuple(
        0.0234375,
        "dotted two hundred fifty-sixth rest",
        "점256분쉼표",
        "𝅂.",
        "r/256.",
    )
    TWO_HUNDRED_FIFTY_SIXTH_REST = NoteNamedTuple(
        0.015625, "two hundred fifty-sixth rest", "256분쉼표", "𝅂", "r/256"
    )


class Note_all(Enum):
    """Note_all Enum"""

    DOTTED_OCTUPLE_WHOLE_NOTE = NoteNamedTuple(
        48, "dotted octuple whole note", "점8온음표", "𝆶.", "n*8."
    )
    OCTUPLE_WHOLE_NOTE = NoteNamedTuple(
        32, "octuple whole note", "8온음표", "𝆶", "n*8"
    )
    DOTTED_QUADRUPLE_WHOLE_NOTE = NoteNamedTuple(
        24, "dotted quadruple whole note", "점4온음표", "𝅜𝅥.", "n*4."
    )
    QUADRUPLE_WHOLE_NOTE = NoteNamedTuple(
        16, "quadruple whole note", "4온음표", "𝅜", "n*4"
    )
    DOTTED_DOUBLE_WHOLE_NOTE = NoteNamedTuple(
        12, "dotted double whole note", "점겹온음표", "𝅜.", "n*2."
    )
    DOUBLE_WHOLE_NOTE = NoteNamedTuple(
        8, "double whole note", "겹온음표", "𝅜", "n*2"
    )
    DOTTED_WHOLE_NOTE = NoteNamedTuple(
        6, "dotted whole note", "점온음표", "𝅝.", "n/1."
    )
    WHOLE_NOTE = NoteNamedTuple(4, "whole note", "온음표", "𝅝", "n/1")
    DOTTED_HALF_NOTE = NoteNamedTuple(
        3, "dotted half note", "점2분음표", "♩.", "n/2."
    )
    HALF_NOTE = NoteNamedTuple(2, "half note", "2분음표", "𝅗𝅥", "n/2")
    DOTTED_QUARTER_NOTE = NoteNamedTuple(
        1.5, "dotted quarter note", "점4분음표", "♩.", "n/4."
    )
    QUARTER_NOTE = NoteNamedTuple(1, "quarter note", "4분음표", "♩", "n/4")
    DOTTED_EIGHTH_NOTE = NoteNamedTuple(
        0.75, "dotted eighth note", "점8분음표", "♪.", "n/8."
    )
    EIGHTH_NOTE = NoteNamedTuple(0.5, "eighth note", "8분음표", "♪", "n/8")
    DOTTED_SIXTEENTH_NOTE = NoteNamedTuple(
        0.375, "dotted sixteenth note", "점16분음표", "𝅘𝅥𝅯.", "n/16."
    )
    SIXTEENTH_NOTE = NoteNamedTuple(
        0.25, "sixteenth note", "16분음표", "𝅘𝅥𝅯", "n/16"
    )
    DOTTED_THIRTY_SECOND_NOTE = NoteNamedTuple(
        0.1875, "dotted thirty-second note", "점32분음표", "𝅘𝅥𝅰.", "n/32."
    )
    THIRTY_SECOND_NOTE = NoteNamedTuple(
        0.125, "thirty-second note", "32분음표", "𝅘𝅥𝅰", "n/32"
    )
    DOTTED_SIXTY_FOURTH_NOTE = NoteNamedTuple(
        0.09375, "dotted sixty-fourth note", "점64분음표", "𝅘𝅥𝅱.", "n/64."
    )
    SIXTY_FOURTH_NOTE = NoteNamedTuple(
        0.0625, "sixty-fourth note", "64분음표", "𝅘𝅥𝅱", "n/64"
    )
    DOTTED_HUNDRED_TWENTY_EIGHTH_NOTE = NoteNamedTuple(
        0.046875,
        "dotted hundred twenty-eighth note",
        "점128분음표",
        "𝅘𝅥𝅲.",
        "n/128.",
    )
    HUNDRED_TWENTY_EIGHTH_NOTE = NoteNamedTuple(
        0.03125, "hundred twenty-eighth note", "128분음표", "𝅘𝅥𝅲", "n/128"
    )
    DOTTED_TWO_HUNDRED_FIFTY_SIXTH_NOTE = NoteNamedTuple(
        0.0234375,
        "dotted two hundred fifty-sixth note",
        "점256분음표",
        "𝅘𝅥𝅲.",
        "n/256.",
    )
    TWO_HUNDRED_FIFTY_SIXTH_NOTE = NoteNamedTuple(
        0.015625, "two hundred fifty-sixth note", "256분음표", "𝅘𝅥𝅲", "n/256"
    )


COLOR = (
    15,
    165,
    47,
    87,
    121,
    9,
    27,
    190,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    9,
    11,
    30,
    33,
    37,
    39,
    51,
    46,
    63,
    57,
    87,
    121,
    91,
    104,
    123,
    118,
    129,
    159,
    124,
    127,
    157,
    159,
    135,
    162,
    194,
    201,
    226,
    230,
    217,
)
