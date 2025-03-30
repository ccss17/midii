"""midii"""

import string

import numpy as np
import mido

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from .note import (
    Note,
    Note_all,
    Rest_all,
    COLOR,
)

DEFAULT_TICKS_PER_BEAT = 480
DEFAULT_TIME_SIGNATURE = (4, 4)
DEFAULT_TEMPO = 500000
DEFAULT_BPM = 120
DEFAULT_MEASURE_SPACE = 4


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
    note_number = int(np.round(note_number))

    # Get the semitone and the octave, and concatenate to create the name
    return semis[note_number % 12] + str(note_number // 12 - 1)


def tick2beat(tick, ppqn):
    """tick2beat"""
    return tick / ppqn


def beat2tick(beat, ppqn):
    """beat2tick"""
    return int(beat * ppqn)


class MidiFile(mido.MidiFile):
    """Class for analysis midi file"""

    def __init__(
        self,
        filename=None,
        file=None,
        type=1,
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        charset="latin1",
        debug=False,
        clip=False,
        tracks=None,
        convert_1_to_0=False,
        lyric_encoding="utf-8",
    ):
        super().__init__(
            filename=filename,
            file=file,
            type=type,
            ticks_per_beat=ticks_per_beat,
            charset=charset,
            debug=debug,
            clip=clip,
            tracks=tracks,
        )

        self.lyric_encoding = lyric_encoding
        self.convert_1_to_0 = convert_1_to_0

        if self.type == 1 and self.convert_1_to_0:
            self.tracks = [mido.merge_tracks(self.tracks)]

    def quantization(self, unit="32"):
        """quantization"""
        if not any(
            [unit == n.value.name_short.split("/")[-1] for n in list(Note)]
        ):
            raise ValueError

        for track in self.tracks:
            error = 0
            for msg in track:
                if msg.type in ["note_on", "note_off", "lyrics"]:
                    if not msg.time:
                        continue
                    if error:
                        msg.time += error
                        error = 0
                    error = self._quantization(msg, unit=unit)

    def analysis(
        self,
        track_bound=None,
        blind_note=False,
        blind_time=False,
        blind_lyric=True,
        track_list=None,
        blind_note_info=False,
    ):
        """method to analysis"""

        if track_bound is None:
            track_bound = float("inf")
        # meta information of midi file
        header_style = "black on white blink"
        header_info = "\n".join(
            [
                f"[{header_style}]mid file type: {self.type}",
                f"ticks per beat: {self.ticks_per_beat}",
                f"total duration: {self.length}[/{header_style}]",
            ]
        )
        header_panel = Panel(
            header_info,
            title="[MIDI File Header]",
            subtitle=f"{self.filename}",
            style=f"{header_style}",
            border_style=f"{header_style}",
        )
        rprint(header_panel)

        for i, track in enumerate(self.tracks):
            console = Console()
            console.rule(
                "[#ffffff on #4707a8]" + f'Track {i}: "{track.name}"'
                f"[/#ffffff on #4707a8]",
                style="#ffffff on #4707a8",
            )
            if track_list is None or track.name in track_list:
                self._analysis(
                    track,
                    track_bound=track_bound,
                    blind_note=blind_note,
                    blind_time=blind_time,
                    blind_lyric=blind_lyric,
                    blind_note_info=blind_note_info,
                )

    def _quantization(self, msg, unit="32"):
        q_time = None
        total_q_time = 0
        error = 0
        for note_item in list(Note):
            beat = tick2beat(msg.time, self.ticks_per_beat)
            q_beat = note_item.value.beat
            q_time = beat2tick(q_beat, self.ticks_per_beat)
            if beat > q_beat:
                msg.time -= q_time
                total_q_time += q_time
            elif beat == q_beat:  # msg is quantized
                msg.time += total_q_time
                return error
                # return msg, error
            if unit in note_item.value.name_short:
                beat_unit = note_item.value.beat  # beat_unit
                break

        # beat in [0, beat_unit), i.e. beat_unit=0.125
        beat = tick2beat(msg.time, self.ticks_per_beat)
        if beat < beat_unit / 2:  # beat in [0, beat_unit/2)
            error = msg.time
            msg.time = 0  # approximate to beat=0
        elif beat < beat_unit:  # beat in [beat_unit/2, beat_unit)
            error = msg.time - beat2tick(beat_unit, self.ticks_per_beat)
            # approximate to beat=beat_unit
            msg.time = beat2tick(beat_unit, self.ticks_per_beat)
        msg.time += total_q_time
        return error
        # return msg, error

    def print_note_num(self, note_num, tempo, time_signature):
        """print_note_num"""
        color = "color(240)" if note_num == 0 else "color(47)"
        bpm = round(mido.tempo2bpm(tempo, time_signature=time_signature))
        info = f"[bold {color}]Total item num of BPM({bpm}): " + f"{note_num}"
        Console().rule(info, style=f"{color}")

    def _analysis(
        self,
        track,
        track_bound=None,
        blind_note=False,
        blind_time=False,
        blind_lyric=True,
        blind_note_info=False,
    ):
        """analysis track"""
        tempo = DEFAULT_TEMPO
        time_signature = DEFAULT_TIME_SIGNATURE
        length = 0
        note_address = 0
        note_num = 0
        first_tempo = True
        prev_tempo = None
        note_queue = {}
        if track_bound is None:
            track_bound = float("inf")
        lyric = ""
        total_time = 0
        for i, msg in enumerate(track):
            if i > track_bound:
                break
            total_time += msg.time
            length += mido.tick2second(
                msg.time,
                ticks_per_beat=self.ticks_per_beat,
                tempo=tempo,
            )
            msg_kwarg = {
                "msg": msg,
                "ppqn": self.ticks_per_beat,
                "tempo": tempo,
                "idx": i,
                "length": length,
            }
            match msg.type:
                case "note_on":
                    result, note_address = MidiMessageAnalyzer_note_on(
                        **msg_kwarg, note_queue=note_queue
                    ).analysis(
                        blind_time=blind_time,
                        blind_note=blind_note,
                        blind_note_info=blind_note_info,
                    )
                case "note_off":
                    result = MidiMessageAnalyzer_note_off(
                        **msg_kwarg, note_queue=note_queue
                    ).analysis(
                        blind_time=blind_time,
                        blind_note=blind_note,
                        blind_note_info=blind_note_info,
                    )
                case "rest":
                    result = MidiMessageAnalyzer_rest(
                        **msg_kwarg, note_queue=note_queue
                    ).analysis(
                        blind_time=blind_time,
                        blind_note=blind_note,
                        blind_note_info=blind_note_info,
                    )
                case "lyrics":
                    mmal = MidiMessageAnalyzer_lyrics(
                        **msg_kwarg,
                        encoding=self.lyric_encoding,
                    )
                    if self.lyric_encoding != mmal.encoding:
                        self.lyric_encoding = mmal.encoding
                    result, _lyric = mmal.analysis(
                        note_address=note_address,
                        blind_time=blind_time,
                        blind_note=blind_note,
                        blind_note_info=blind_note_info,
                    )
                    lyric += _lyric
                case "measure":
                    result = MidiMessageAnalyzer_measure(
                        time_signature
                    ).analysis()
                case "text" | "track_name":
                    mmat = MidiMessageAnalyzer_text(
                        **msg_kwarg,
                        encoding=self.lyric_encoding,
                    )
                    if self.lyric_encoding != mmat.encoding:
                        self.lyric_encoding = mmat.encoding
                    result = mmat.analysis(blind_time=blind_time)
                case "set_tempo":
                    if not first_tempo and self.convert_1_to_0:
                        self.print_note_num(note_num, tempo, time_signature)
                    first_tempo = False
                    result, tempo = MidiMessageAnalyzer_set_tempo(
                        **msg_kwarg,
                        time_signature=time_signature,
                    ).analysis(blind_time=blind_time)
                    if prev_tempo is None:
                        prev_tempo = tempo
                    if note_num:
                        prev_tempo = tempo
                        note_num = 0
                    else:
                        tempo = prev_tempo
                case "end_of_track":
                    if self.convert_1_to_0:
                        self.print_note_num(note_num, tempo, time_signature)
                    result = MidiMessageAnalyzer_end_of_track(
                        **msg_kwarg
                    ).analysis(blind_time=blind_time)
                case "key_signature":
                    result = MidiMessageAnalyzer_key_signature(
                        **msg_kwarg
                    ).analysis(blind_time=blind_time)
                case "time_signature":
                    result, time_signature = (
                        MidiMessageAnalyzer_time_signature(
                            **msg_kwarg
                        ).analysis(blind_time=blind_time)
                    )
                case _:
                    result = MidiMessageAnalyzer(**msg_kwarg).analysis(
                        blind_time=blind_time
                    )

            if result:
                rprint(result)

            if msg.type in ["note_on", "note_off", "lyrics"]:
                note_num += 1

        rprint(f"Track lyric encode: {self.lyric_encoding}")
        length = mido.tick2second(
            total_time,
            ticks_per_beat=self.ticks_per_beat,
            tempo=tempo,
        )
        rprint("Track total secs/time: " + f"{self.length}/{total_time}")
        bpm = round(mido.tempo2bpm(tempo, time_signature=time_signature))
        rprint("bpm(tempo): " + f"{bpm}({tempo})")
        if not blind_lyric:
            print(f'LYRIC: "{lyric}"')


class MidiMessageAnalyzer:
    """MidiMessageAnalyzer"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
    ):
        self.msg = msg
        self.ppqn = ppqn
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.length = length

    def info_type(self):
        """info_type"""
        return f"[black on white]\\[{self.msg.type}][/black on white]"

    def info_time(self):
        """time_info"""
        if self.msg.time:
            main_color = "#ffffff"
            sub_color = "white"
            time = mido.tick2second(
                self.msg.time,
                ticks_per_beat=self.ppqn,
                tempo=self.tempo,
            )
            return " ".join(
                [
                    f"[{main_color}]{time:4.2f}[/{main_color}]"
                    + f"[{sub_color}]/{self.length:6.2f}[/{sub_color}]",
                    f"[{sub_color}]time=[/{sub_color}]"
                    + f"[{main_color}]{self.msg.time:<3}[/{main_color}]",
                ]
            )
        else:
            return ""

    def result(self, head="", body="", blind_time=False):
        """print strings"""
        time_info = "" if blind_time else self.info_time()
        _result = [self.idx_info, head, time_info, body]
        return " ".join([s for s in _result if s])

    def analysis(self, blind_time=False):
        """analysis"""
        return self.result(
            head=self.info_type(),
            body=f"[color(250)]{self.msg}[/color(250)]",
            blind_time=blind_time,
        )


class MidiMessageAnalyzer_set_tempo(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_set_tempo"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        time_signature=DEFAULT_TIME_SIGNATURE,
    ):
        super().__init__(msg, ppqn, tempo=tempo, idx=idx, length=length)
        self.time_signature = time_signature

    def analysis(self, blind_time=False):
        bpm = round(
            mido.tempo2bpm(self.msg.tempo, time_signature=self.time_signature)
        )
        result = self.result(
            head=self.info_type(),
            body=f"[white]BPM=[/white][color(190)]{bpm}({self.msg.tempo})[/color(190)]",
            blind_time=blind_time,
        )
        return result, self.msg.tempo


class MidiMessageAnalyzer_key_signature(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_key_signature"""

    def analysis(self, blind_time=False):
        return self.result(
            head=self.info_type(), body=self.msg.key, blind_time=blind_time
        )


class MidiMessageAnalyzer_end_of_track(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_end_of_track"""

    def analysis(self, blind_time=False):
        return self.result(head=self.info_type(), blind_time=blind_time)


class MidiMessageAnalyzer_time_signature(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_time_signature"""

    def analysis(self, blind_time=False):
        result = self.result(
            head=self.info_type(),
            body=f"{self.msg.numerator}/{self.msg.denominator}",
            blind_time=blind_time,
        )
        return result, (self.msg.numerator, self.msg.denominator)


class MidiMessageAnalyzer_measure(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_measure"""

    idx = 1

    def __init__(
        self,
        time_signature=DEFAULT_TIME_SIGNATURE,
    ):
        self.time_signature = time_signature

    @classmethod
    def inc_idx(cls):
        """inc_idx"""
        cls.idx += 1

    def analysis(self):
        """print measure"""
        Console(width=50).rule(
            f"[#ffffff]𝄞 {self.time_signature[0]}/{self.time_signature[1]} "
            + f"measure {self.idx}[/#ffffff]",
            style="#ffffff",
            characters="=",
        )
        self.inc_idx()
        return ""


class MidiMessageAnalyzer_text(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_text"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        encoding="utf-8",
        encoding_alternative="cp949",
    ):
        super().__init__(msg, ppqn, tempo=tempo, idx=idx, length=length)
        self._init_encoding(
            encoding=encoding, encoding_alternative=encoding_alternative
        )

    def _init_encoding(self, encoding="utf-8", encoding_alternative="cp949"):
        self.encoded_text = self.msg.bin()[3:]
        self.encoding = self.determine_encoding(encoding, encoding_alternative)

    def determine_encoding(self, *encoding_list):
        """determine_encoding"""
        for encoding in encoding_list:
            try:
                self.encoded_text.decode(encoding)
            except UnicodeDecodeError:
                continue
            else:
                return encoding
        raise UnicodeDecodeError

    def analysis(self, blind_time=False):
        """analysis text"""
        text = self.encoded_text.decode(self.encoding).strip()
        return self.result(
            head=self.info_type(), body=text, blind_time=blind_time
        )


class MidiMessageAnalyzer_SoundUnit(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_SoundUnit"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        note_queue=None,
    ):
        super().__init__(
            msg,
            ppqn,
            tempo=tempo,
            idx=idx,
            length=length,
        )
        if note_queue is None:
            self.note_queue = {}
        else:
            self.note_queue = note_queue

    def note_queue_find(self, value):
        """note_queue_find"""
        for k, v in self.note_queue.items():
            if v == value:
                return k
        return None

    def note_queue_alloc(self):
        """note_queue_alloc"""
        address = 0
        while True:
            try:
                self.note_queue[address]
                address += 1
            except KeyError:
                return address

    def closest_note(self, tick, as_rest=False):
        """select minimum error"""
        if tick == 0:
            return None, None
        beat = tick2beat(tick, self.ppqn)
        min_error = float("inf")
        quantized_note = None
        note_enum = Rest_all if as_rest else Note_all
        for note in note_enum:
            error = note.value.beat - beat
            if abs(error) < min_error:
                min_error = error
                quantized_note = note.value
        return min_error, quantized_note

    def quantization_info(
        self, error, real_beat, quantized_note, quantization_color="color(85)"
    ):
        """info_quantization"""
        if error is None:
            return ""
        else:
            if error == 0:
                err_msg = ""
            else:
                err_msg = (
                    f"[red]-{float(real_beat):.3}[/red]"
                    + f"[#ff0000]={error}[/#ff0000]"
                )
            return (
                f"[{quantization_color}]"
                + f"{quantized_note.symbol:2}{quantized_note.name_short}"
                + f"[/{quantization_color}] "
                + f"[color(249)]{float(quantized_note.beat):.3}b[/color(249)]"
                + err_msg
            )

    def note_info(self, note):
        """note_info"""
        return f"{note_number_to_name(note):>3}({note:2})"


class MidiMessageAnalyzer_note_on(MidiMessageAnalyzer_SoundUnit):
    """MidiMessageAnalyzer_note_on"""

    def alloc_note(self, note):
        """alloc_note"""
        note_address = self.note_queue_alloc()
        self.note_queue[note_address] = note
        return note_address

    def analysis(
        self, blind_time=False, blind_note=False, blind_note_info=False
    ):
        addr = self.alloc_note(self.msg.note)
        error, quantized_note = self.closest_note(self.msg.time, as_rest=True)
        info_quantization = ""
        if error is not None and not blind_note_info:
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        color = f"color({COLOR[addr % len(COLOR)]})"
        note_msg = f"[{color}]┌{self.note_info(self.msg.note)}┐[/{color}]"
        result = ""
        if not blind_note:
            result = self.result(
                head=note_msg, body=info_quantization, blind_time=blind_time
            )
        return result, addr


class MidiMessageAnalyzer_note_off(MidiMessageAnalyzer_SoundUnit):
    """MidiMessageAnalyzer_note_off"""

    def free_note(self, note):
        """alloc_note"""
        addr = self.note_queue_find(note)
        if addr is not None:
            del self.note_queue[addr]
        return addr

    def analysis(
        self,
        blind_time=False,
        blind_note=False,
        blind_note_info=False,
    ):
        addr = self.free_note(self.msg.note)
        color = None if addr is None else f"color({COLOR[addr % len(COLOR)]})"

        error, quantized_note = self.closest_note(
            self.msg.time, as_rest=True if addr is None else False
        )
        if color:
            _note_info = self.note_info(self.msg.note)
            info_note_off = f"[{color}]└{_note_info}┘[/{color}]"
        else:
            symbol = quantized_note.symbol if quantized_note else "0"
            info_note_off = f"[#ffffff]{symbol:^9}[/#ffffff]"
        info_quantization = ""
        if error is not None and not blind_note_info:
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        result = ""
        if not blind_note:
            result = self.result(
                head=info_note_off,
                body=info_quantization,
                blind_time=blind_time,
            )

        return result


class MidiMessageAnalyzer_rest(MidiMessageAnalyzer_SoundUnit):
    """MidiMessageAnalyzer_rest"""

    def analysis(
        self,
        blind_time=False,
        blind_note=False,
        blind_note_info=False,
    ):
        error, quantized_note = self.closest_note(self.msg.time, as_rest=True)
        info_quantization = ""
        if error is not None and not blind_note_info:
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        result = ""
        info_rest = f"[black on white]{quantized_note.symbol}[/black on white]"
        info_rest = f"{info_rest:^19}"
        info_rest = f"[#ffffff]{quantized_note.symbol:^9}[/#ffffff]"
        if not blind_note:
            result = self.result(
                head=info_rest,
                body=info_quantization,
                blind_time=blind_time,
            )

        return result


class MidiMessageAnalyzer_lyrics(
    MidiMessageAnalyzer_SoundUnit, MidiMessageAnalyzer_text
):
    """MidiMessageAnalyzer_lyrics"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        encoding="utf-8",
        encoding_alternative="cp949",
    ):
        self.msg = msg
        self.ppqn = ppqn
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.length = length
        self._init_encoding(
            encoding=encoding, encoding_alternative=encoding_alternative
        )
        self.lyric = self.encoded_text.decode(self.encoding).strip()
        if not self.lyric:
            self.lyric = " "

    def is_alnumpunc(self, s):
        """is_alnumpunc"""
        candidate = (
            string.ascii_letters + string.digits + string.punctuation + " "
        )
        for c in s:
            if c not in candidate:
                return False
        return True

    def analysis(
        self,
        note_address=0,
        blind_time=False,
        border_color="#ffffff",
        blind_note=False,
        blind_note_info=False,
    ):
        """analysis"""
        lyric_style = "#98ff29"
        border_color = f"color({COLOR[note_address % len(COLOR)]})"
        lyric = self.lyric
        if lyric == " ":
            lyric = "' '"

        border = f"[{border_color}]│[/{border_color}]"
        lyric_info = (
            f"{lyric:^7}" if self.is_alnumpunc(lyric) else f"{lyric:^6}"
        )

        error, quantized_note = self.closest_note(self.msg.time)
        info_quantization = ""
        if error is not None and not blind_note_info:
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        head = (
            border
            + f"[{lyric_style}]"
            + lyric_info
            + f"[/{lyric_style}]"
            + border
        )
        result = ""
        if not blind_note:
            result = self.result(
                head=head,
                body=info_quantization,
                blind_time=blind_time,
            )
        return result, self.lyric
