import mido
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

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
from .quantize import quantize
from .utilities import beat2tick
from .note import NOTE


class MidiFile(mido.MidiFile):
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
            self.type = 0

    def quantize(
        self,
        unit="32",
        error_forwarding=True,
        targets=["note_on", "note_off", "lyrics"],
    ):
        try:
            unit_beat = NOTE["n/" + unit].beat
        except KeyError:
            raise ValueError(f"unknown unit string {unit!r}")
        unit_tick = beat2tick(unit_beat, self.ticks_per_beat)
        if self.type == 0:
            quantized_ticks, error = quantize(
                ticks=self.times,
                unit=unit_tick,
                error_forwarding=error_forwarding,
            )
            quantized_ticks_iter = iter(quantized_ticks)
            for msg in self.tracks[0]:
                if msg.type in targets:
                    msg.time = next(quantized_ticks_iter)
        elif self.type == 1:
            for track, track_times in zip(self.tracks, self.times):
                quantized_ticks, error = quantize(
                    ticks=track_times,
                    unit=unit_tick,
                    error_forwarding=error_forwarding,
                )
                quantized_ticks_iter = iter(quantized_ticks)
                for msg in track:
                    if msg.type in targets:
                        msg.time = next(quantized_ticks_iter)
        else:  # type == 2
            raise NotImplementedError

    def _print_note_num(self, note_num, tempo, time_signature):
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
    ):
        tempo = DEFAULT_TEMPO
        time_signature = DEFAULT_TIME_SIGNATURE
        current_time = 0
        note_address = 0
        note_num = 0
        first_tempo = True
        prev_tempo = None
        note_queue = {}
        if track_limit is None:
            track_limit = float("inf")
        total_time = 0
        for i, msg in enumerate(track):
            if i > track_limit:
                break
            total_time += msg.time
            current_time += mido.tick2second(
                msg.time,
                ticks_per_beat=self.ticks_per_beat,
                tempo=tempo,
            )
            kwarg = {
                "msg": msg,
                "ticks_per_beat": self.ticks_per_beat,
                "tempo": tempo,
                "index": i,
                "current_time": current_time,
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
            elif msg.type == "text" or msg.type == "track_name":
                ma = MessageAnalyzer_text(
                    **kwarg,
                    encoding=self.lyric_encoding,
                )
            elif msg.type == "set_tempo":
                if not first_tempo and self.convert_1_to_0:
                    self._print_note_num(note_num, tempo, time_signature)
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
            elif msg.type == "end_of_track":
                if self.convert_1_to_0:
                    self._print_note_num(note_num, tempo, time_signature)
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

        current_time = mido.tick2second(
            total_time,
            ticks_per_beat=self.ticks_per_beat,
            tempo=tempo,
        )
        rprint("Total secs/time: " + f"{current_time}/{total_time}")

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
    ):
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
                    print_note_info=print_note_info,
                )

    def _get_note_data(
        self, msg, note_map, time_current, tempo, lyric, time_format
    ):
        note_data = {
            "start": None,
            "end": None,
            "duration": None,
            "pitch": None,
            "lyric": None,
        }
        note_data = note_data.copy()
        try:
            time_note_on = note_map[msg.note]
        except KeyError:
            note_data["pitch"] = 0
            time_note_on = time_current - msg.time
        else:
            note_data["pitch"] = msg.note
            del note_map[msg.note]
        duration = time_current - time_note_on
        if time_format == "ticks":
            note_data["start"] = time_note_on
            note_data["end"] = time_current
            note_data["duration"] = duration
        elif time_format == "seconds":
            note_data["start"] = mido.tick2second(
                time_note_on,
                ticks_per_beat=self.ticks_per_beat,
                tempo=tempo,
            )
            note_data["end"] = mido.tick2second(
                time_current,
                ticks_per_beat=self.ticks_per_beat,
                tempo=tempo,
            )
            note_data["duration"] = mido.tick2second(
                duration,
                ticks_per_beat=self.ticks_per_beat,
                tempo=tempo,
            )
        else:
            raise ValueError
        note_data["lyric"] = lyric
        return note_data

    def to_json(
        self,
        time_format="ticks",  # "seconds", "ticks"
    ):
        if self.type == 1 and not self.convert_1_to_0:
            raise RuntimeError
        tempo = DEFAULT_TEMPO
        time_current = 0
        lyric = ""
        result = []
        note_map = {}
        for msg in self.tracks[0]:
            time_current += msg.time
            if msg.type == "set_tempo":
                tempo = msg.tempo
            elif msg.type == "lyrics":
                lyric += MessageAnalyzer_lyrics(
                    msg=msg,
                    encoding=self.lyric_encoding,
                ).lyric
            elif msg.type == "note_on":
                note_map[msg.note] = time_current
            elif msg.type == "note_off":
                result.append(
                    self._get_note_data(
                        msg, note_map, time_current, tempo, lyric, time_format
                    )
                )
                lyric = ""

        return result

    @property
    def times(self):
        if self.type == 0:
            return [
                msg.time
                for msg in self.tracks[0]
                if msg.type in ["note_on", "note_off", "lyrics"]
            ]
        elif self.type == 1:
            return [
                [
                    msg.time
                    for msg in track
                    if msg.type in ["note_on", "note_off", "lyrics"]
                ]
                for track in self.tracks
            ]
        else:  # type == 2
            raise NotImplementedError

    @property
    def lyrics(self):
        lyrics = ""
        if self.type == 0:
            for msg in self.tracks[0]:
                if msg.type == "lyrics":
                    lyrics += MessageAnalyzer_lyrics(
                        msg=msg,
                        encoding=self.lyric_encoding,
                    ).lyric
        elif self.type == 1:
            for track in self.tracks:
                for msg in track:
                    if msg.type == "lyrics":
                        lyrics += MessageAnalyzer_lyrics(
                            msg=msg,
                            encoding=self.lyric_encoding,
                        ).lyric
        elif self.type == 2:
            raise NotImplementedError
        return lyrics
