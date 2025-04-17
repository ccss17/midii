"""messages"""

import string

import mido
from rich.console import Console

from .note import (
    Note_all,
    Rest_all,
)
from .config import (
    DEFAULT_TICKS_PER_BEAT,
    DEFAULT_TEMPO,
    DEFAULT_TIME_SIGNATURE,
    COLOR,
)
from .utilities import tick2beat, note_number_to_name, tempo2bpm


class MidiMessageAnalyzer:
    """MidiMessageAnalyzer"""

    def __init__(
        self,
        msg,
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
    ):
        self.msg = msg
        self.ticks_per_beat = ticks_per_beat
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
                ticks_per_beat=self.ticks_per_beat,
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
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        time_signature=DEFAULT_TIME_SIGNATURE,
    ):
        super().__init__(
            msg, ticks_per_beat, tempo=tempo, idx=idx, length=length
        )
        self.time_signature = time_signature

    def analysis(self, blind_time=False):
        bpm = tempo2bpm(self.msg.tempo, time_signature=self.time_signature)
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
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        encoding="latin-1",
    ):
        super().__init__(
            msg, ticks_per_beat, tempo=tempo, idx=idx, length=length
        )
        self.encoded_text = self.msg.bin()[3:]
        self.encoding = encoding

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
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        note_queue=None,
    ):
        super().__init__(
            msg,
            ticks_per_beat,
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
        beat = tick2beat(tick, self.ticks_per_beat)
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
                tick2beat(self.msg.time, self.ticks_per_beat),
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
                tick2beat(self.msg.time, self.ticks_per_beat),
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
                tick2beat(self.msg.time, self.ticks_per_beat),
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
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        encoding="latin-1",
    ):
        self.msg = msg
        self.ticks_per_beat = ticks_per_beat
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.length = length
        self.encoded_text = self.msg.bin()[3:]
        self.encoding = encoding
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
                tick2beat(self.msg.time, self.ticks_per_beat),
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
