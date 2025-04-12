import string

import mido

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


class MessageAnalyzer:
    def __init__(
        self,
        msg,
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        blind_time=False,
    ):
        self.msg = msg
        self.ticks_per_beat = ticks_per_beat
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.length = length
        self.blind_time = blind_time

    def str_type(self):
        return f"[black on white]\\[{self.msg.type}][/black on white]"

    def str_time(self):
        if not self.msg.time:
            return ""
        style_main = "bold"
        style_sub = "white"
        time = mido.tick2second(
            self.msg.time,
            ticks_per_beat=self.ticks_per_beat,
            tempo=self.tempo,
        )
        return " ".join(
            [
                f"[{style_main}]{time:4.2f}[/{style_main}]"
                + f"[{style_sub}]/{self.length:6.2f}[/{style_sub}]",
                f"[{style_sub}]time=[/{style_sub}]"
                + f"[{style_main}]{self.msg.time:<3}[/{style_main}]",
            ]
        )

    def str_format(self, head="", body=""):
        time_info = "" if self.blind_time else self.str_time()
        _result = [self.idx_info, head, time_info, body]
        return " ".join([s for s in _result if s])

    def __str__(self):
        return self.str_format(
            head=self.str_type(),
            body=f"[color(250)]{self.msg}[/color(250)]",
        )


class MessageAnalyzer_set_tempo(MessageAnalyzer):
    def __init__(
        self,
        msg,
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        blind_time=False,
        time_signature=DEFAULT_TIME_SIGNATURE,
    ):
        super().__init__(
            msg,
            ticks_per_beat,
            tempo=tempo,
            idx=idx,
            length=length,
            blind_time=blind_time,
        )
        self.time_signature = time_signature

    def __str__(self):
        bpm = tempo2bpm(self.msg.tempo, time_signature=self.time_signature)
        return self.str_format(
            head=self.str_type(),
            body=f"[white]BPM=[/white][color(190)]{bpm}({self.msg.tempo})[/color(190)]",
        )


class MessageAnalyzer_key_signature(MessageAnalyzer):
    def __str__(self):
        return self.str_format(head=self.str_type(), body=self.msg.key)


class MessageAnalyzer_end_of_track(MessageAnalyzer):
    def __str__(self):
        return self.str_format(head=self.str_type())


class MessageAnalyzer_time_signature(MessageAnalyzer):
    def __str__(self):
        result = self.str_format(
            head=self.str_type(),
            body=f"{self.msg.numerator}/{self.msg.denominator}",
        )
        return result


class MessageAnalyzer_text(MessageAnalyzer):
    def __init__(
        self,
        msg,
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        blind_time=False,
        encoding="latin-1",
    ):
        super().__init__(
            msg,
            ticks_per_beat,
            tempo=tempo,
            idx=idx,
            length=length,
            blind_time=blind_time,
        )
        self.text = self.decode(encoding=encoding)

    def decode(self, encoding):
        return self.msg.bin()[3:].decode(encoding).strip()

    def __str__(self):
        return self.str_format(head=self.str_type(), body=self.text)


class MessageAnalyzer_SoundUnit(MessageAnalyzer):
    def __init__(
        self,
        msg,
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        blind_time=False,
        blind_note=False,
        blind_note_info=False,
        note_queue=None,
    ):
        super().__init__(
            msg,
            ticks_per_beat,
            tempo=tempo,
            idx=idx,
            length=length,
            blind_time=blind_time,
        )
        if note_queue is None:
            self.note_queue = {}
        else:
            self.note_queue = note_queue
        self.blind_note = blind_note
        self.blind_note_info = blind_note_info

    def note_queue_find(self, value):
        for k, v in self.note_queue.items():
            if v == value:
                return k
        return None

    def note_queue_alloc(self):
        address = 0
        while True:
            try:
                self.note_queue[address]
                address += 1
            except KeyError:
                return address

    def closest_note(self, tick, as_rest=False):
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

    def str_quantization(
        self, error, real_beat, quantized_note, quantization_color="color(85)"
    ):
        if error is None:
            return ""
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

    def str_note(self, note):
        return f"{note_number_to_name(note):>3}({note:2})"


class MessageAnalyzer_note_on(MessageAnalyzer_SoundUnit):
    def __init__(
        self,
        msg,
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        blind_time=False,
        blind_note=False,
        blind_note_info=False,
        note_queue=None,
    ):
        super().__init__(
            msg,
            ticks_per_beat,
            tempo=tempo,
            idx=idx,
            length=length,
            blind_time=blind_time,
            blind_note=blind_note,
            blind_note_info=blind_note_info,
            note_queue=note_queue,
        )
        self.addr = self.alloc_note(self.msg.note)

    def alloc_note(self, note):
        note_address = self.note_queue_alloc()
        self.note_queue[note_address] = note
        return note_address

    def __str__(self):
        error, quantized_note = self.closest_note(self.msg.time, as_rest=True)
        _str_quantization = ""
        if error is not None and not self.blind_note_info:
            _str_quantization = self.str_quantization(
                round(error, 3),
                tick2beat(self.msg.time, self.ticks_per_beat),
                quantized_note,
            )
        color = f"color({COLOR[self.addr % len(COLOR)]})"
        note_msg = f"[{color}]┌{self.str_note(self.msg.note)}┐[/{color}]"
        result = ""
        if not self.blind_note:
            result = self.str_format(head=note_msg, body=_str_quantization)
        return result


class MessageAnalyzer_note_off(MessageAnalyzer_SoundUnit):
    def __init__(
        self,
        msg,
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        blind_time=False,
        blind_note=False,
        blind_note_info=False,
        note_queue=None,
    ):
        super().__init__(
            msg,
            ticks_per_beat,
            tempo=tempo,
            idx=idx,
            length=length,
            blind_time=blind_time,
            blind_note=blind_note,
            blind_note_info=blind_note_info,
            note_queue=note_queue,
        )
        self.addr = self.free_note(self.msg.note)

    def free_note(self, note):
        addr = self.note_queue_find(note)
        if addr is not None:
            del self.note_queue[addr]
        return addr

    def __str__(self):
        color = (
            None
            if self.addr is None
            else f"color({COLOR[self.addr % len(COLOR)]})"
        )
        error, quantized_note = self.closest_note(
            self.msg.time, as_rest=True if self.addr is None else False
        )
        if color:
            _note_info = self.str_note(self.msg.note)
            _str_note_off_info = f"[{color}]└{_note_info}┘[/{color}]"
        else:
            symbol = quantized_note.symbol if quantized_note else "0"
            _str_note_off_info = f"[#ffffff]{symbol:^9}[/#ffffff]"
        _str_quantization = ""
        if error is not None and not self.blind_note_info:
            _str_quantization = self.str_quantization(
                round(error, 3),
                tick2beat(self.msg.time, self.ticks_per_beat),
                quantized_note,
            )
        result = ""
        if not self.blind_note:
            result = self.str_format(
                head=_str_note_off_info,
                body=_str_quantization,
            )
        return result


class MessageAnalyzer_lyrics(MessageAnalyzer_SoundUnit, MessageAnalyzer_text):
    def __init__(
        self,
        msg,
        ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        blind_time=False,
        blind_note=False,
        blind_note_info=False,
        encoding="latin-1",
        note_address=0,
    ):
        self.msg = msg
        self.ticks_per_beat = ticks_per_beat
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.length = length
        self.blind_time = blind_time
        self.blind_note = blind_note
        self.blind_note_info = blind_note_info
        self.lyric = self.decode(encoding=encoding)
        if not self.lyric:
            self.lyric = " "
        self.note_address = note_address

    def is_alnumpunc(self, s):
        candidate = (
            string.ascii_letters + string.digits + string.punctuation + " "
        )
        for c in s:
            if c not in candidate:
                return False
        return True

    def __str__(self):
        style_lyric = "#98ff29"
        style_border = f"color({COLOR[self.note_address % len(COLOR)]})"

        border = f"[{style_border}]│[/{style_border}]"
        _str_lyric = (
            f"{self.lyric:^7}"
            if self.is_alnumpunc(self.lyric)
            else f"{self.lyric:^6}"
        )

        error, quantized_note = self.closest_note(self.msg.time)
        info_quantization = ""
        if error is not None and not self.blind_note_info:
            info_quantization = self.str_quantization(
                round(error, 3),
                tick2beat(self.msg.time, self.ticks_per_beat),
                quantized_note,
            )
        head = (
            border
            + f"[{style_lyric}]"
            + _str_lyric
            + f"[/{style_lyric}]"
            + border
        )
        result = ""
        if not self.blind_note:
            result = self.str_format(
                head=head,
                body=info_quantization,
            )
        return result
