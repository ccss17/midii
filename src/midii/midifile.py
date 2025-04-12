"""midi file"""

import mido

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from .note import Note
from .messages import (
    MessageAnalyzer_text,
    MessageAnalyzer_set_tempo,
    MessageAnalyzer_end_of_track,
    MessageAnalyzer_key_signature,
    MessageAnalyzer_time_signature,
    MessageAnalyzer,
    MessageAnalyzer_note_on,
    MessageAnalyzer_note_off,
    MessageAnalyzer_lyrics,
)
from .config import (
    DEFAULT_TICKS_PER_BEAT,
    DEFAULT_TEMPO,
    DEFAULT_TIME_SIGNATURE,
)
from .utilities import tick2beat, beat2tick, tempo2bpm


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
        lyric_encoding="latin1",
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
            self.tracks = [self.merged_track]

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

    def quantization(self, unit="32"):
        """note duration quantization"""
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

    def print_note_num(self, note_num, tempo, time_signature):
        """print_note_num"""
        color = "color(240)" if note_num == 0 else "color(47)"
        bpm = round(mido.tempo2bpm(tempo, time_signature=time_signature))
        info = f"[bold {color}]Total item num of BPM({bpm}): " + f"{note_num}"
        Console().rule(info, style=f"{color}")

    def _print_tracks(
        self,
        track,
        track_limit=None,
        print_note=True,
        print_time=True,
        print_note_info=False,
        print_times=False,
        print_lyric=False,
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
        if track_limit is None:
            track_limit = float("inf")
        lyric = ""
        _str_times = [f"TEMPO=({DEFAULT_TEMPO})"]
        total_time = 0
        for i, msg in enumerate(track):
            if i > track_limit:
                break
            total_time += msg.time
            _str_times.append(f"{msg.time}")
            length += mido.tick2second(
                msg.time,
                ticks_per_beat=self.ticks_per_beat,
                tempo=tempo,
            )
            kwarg = {
                "msg": msg,
                "ticks_per_beat": self.ticks_per_beat,
                "tempo": tempo,
                "idx": i,
                "length": length,
                "print_time": print_time,
            }
            if msg.type == "note_on":
                ma = MessageAnalyzer_note_on(
                    **kwarg,
                    print_note=print_note,
                    print_note_info=print_note_info,
                    note_queue=note_queue,
                )
                note_address = ma.addr
            elif msg.type == "note_off":
                ma = MessageAnalyzer_note_off(
                    **kwarg,
                    print_note=print_note,
                    print_note_info=print_note_info,
                    note_queue=note_queue,
                )
            elif msg.type == "lyrics":
                ma = MessageAnalyzer_lyrics(
                    **kwarg,
                    print_note=print_note,
                    print_note_info=print_note_info,
                    encoding=self.lyric_encoding,
                    note_address=note_address,
                )
                lyric += ma.lyric
            elif msg.type == "text" or msg.type == "track_name":
                ma = MessageAnalyzer_text(
                    **kwarg,
                    encoding=self.lyric_encoding,
                )
            elif msg.type == "set_tempo":
                if not first_tempo and self.convert_1_to_0:
                    self.print_note_num(note_num, tempo, time_signature)
                first_tempo = False
                tempo = msg.tempo
                ma = MessageAnalyzer_set_tempo(
                    **kwarg,
                    time_signature=time_signature,
                )
                if prev_tempo is None:
                    prev_tempo = tempo
                if note_num:
                    prev_tempo = tempo
                    note_num = 0
                else:
                    tempo = prev_tempo
                _str_times.append(
                    f"TEMPO=({tempo2bpm(tempo, time_signature)})"
                )
            elif msg.type == "end_of_track":
                if self.convert_1_to_0:
                    self.print_note_num(note_num, tempo, time_signature)
                ma = MessageAnalyzer_end_of_track(**kwarg)
            elif msg.type == "key_signature":
                ma = MessageAnalyzer_key_signature(**kwarg)
            elif msg.type == "time_signature":
                time_signature = (msg.numerator, msg.denominator)
                ma = MessageAnalyzer_time_signature(**kwarg)
            else:
                ma = MessageAnalyzer(**kwarg)

            _str = str(ma)
            if _str:
                rprint(_str)

            if msg.type in ["note_on", "note_off", "lyrics"]:
                note_num += 1

        rprint(f"Track lyric encode: {self.lyric_encoding}")
        length = mido.tick2second(
            total_time,
            ticks_per_beat=self.ticks_per_beat,
            tempo=tempo,
        )
        rprint("Track total secs/time: " + f"{self.length}/{total_time}")
        if print_lyric:
            print(f'LYRIC: "{lyric}"')
        if print_times:
            print(f"TIMES: {' '.join(_str_times)}")

    def _panel(self):
        # meta information of midi file
        header_style = "black on white blink"
        header_info = "\n".join(
            [
                f"[{header_style}]mid file type: {self.type}",
                f"ticks per beat: {self.ticks_per_beat}",
                f"total duration: {self.length}[/{header_style}]",
            ]
        )
        return Panel(
            header_info,
            title="[MIDI File Header]",
            subtitle=f"{self.filename}",
            style=f"{header_style}",
            border_style=f"{header_style}",
        )

    def print_tracks(
        self,
        track_limit=None,
        print_note=True,
        print_time=True,
        print_note_info=False,
        track_list=None,
        print_times=False,
        print_lyric=False,
    ):
        """method to analysis"""

        if track_limit is None:
            track_limit = float("inf")
        rprint(self._panel())

        _style_track_line = "#ffffff on #4707a8"
        for i, track in enumerate(self.tracks):
            Console().rule(
                f'[{_style_track_line}]Track {i}: "{track.name}"'
                f"[/{_style_track_line}]",
                style=f"{_style_track_line}",
            )
            if track_list is None or track.name in track_list:
                self._print_tracks(
                    track,
                    track_limit=track_limit,
                    print_note=print_note,
                    print_time=print_time,
                    print_lyric=print_lyric,
                    print_note_info=print_note_info,
                    print_times=print_times,
                )
