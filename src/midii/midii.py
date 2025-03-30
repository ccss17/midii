"""midii"""

import sys
import string
import json
from pathlib import Path

import numpy as np
import mido as md
from mido import MidiFile, Message, MetaMessage

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from .note import (
    Note,
    Note_all,
    Rest_all,
    COLOR,
    DEFAULT_TEMPO,
    DEFAULT_TIME_SIGNATURE,
    DEFAULT_PPQN,
)


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


class MidiAnalyzer:
    """Class for analysis midi file"""

    def __init__(
        self,
        midi_path,
        convert_1_to_0=False,
        encoding="utf-8",
    ):
        sys.stdout.reconfigure(encoding="utf-8")  # printing encoding
        self.midi_path = midi_path
        self.mid = MidiFile(self.midi_path)
        self.ppqn = self.mid.ticks_per_beat
        self.convert_1_to_0 = convert_1_to_0

        if self.mid.type == 1 and self.convert_1_to_0:
            self.mid.tracks = [md.merge_tracks(self.mid.tracks)]

        self.track_analyzers = [
            MidiTrackAnalyzer(
                track,
                self.ppqn,
                encoding=encoding,
                convert_1_to_0=convert_1_to_0,
            )
            for track in self.mid.tracks
        ]

    def quantization(self, unit="32"):
        """quantization"""
        for i, track_analyzer in enumerate(self.track_analyzers):
            self.mid.tracks[i] = track_analyzer.quantization(unit=unit)

    def split_space_note(self, remove_silence_threshold=0.3):
        """split_space_note"""
        for i, track_analyzer in enumerate(self.track_analyzers):
            self.mid.tracks[i] = track_analyzer.split_space_note(
                remove_silence_threshold=remove_silence_threshold
            )

    def slice_chunks_time(self, chunks_time):
        """slice_chunks_time"""
        if self.mid.type == 1 and not self.convert_1_to_0:
            raise RuntimeError
        result = []
        for chunk_time in chunks_time:
            begin, end = chunk_time
            result.append(
                self.track_analyzers[0].slice(begin / 100, end / 100)
            )
        return result

    def slice_slience(self):
        """slice_slience"""
        if self.mid.type == 1 and not self.convert_1_to_0:
            raise RuntimeError
        return self.track_analyzers[0].slice_slience()

    def slice(self, begin, end):
        """slice"""
        if self.mid.type == 1 and not self.convert_1_to_0:
            raise RuntimeError
        return self.track_analyzers[0].slice(begin, end)

    def to_json(self, dir_path=None):
        """to_json"""
        if self.mid.type == 1 and not self.convert_1_to_0:
            raise RuntimeError
        return self.track_analyzers[0].to_json(
            file_path=self.mid.filename, dir_path=dir_path
        )

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
                f"[{header_style}]mid file type: {self.mid.type}",
                f"ticks per beat: {self.ppqn}",
                f"total duration: {self.mid.length}[/{header_style}]",
            ]
        )
        header_panel = Panel(
            header_info,
            title="[MIDI File Header]",
            subtitle=f"{self.mid.filename}",
            style=f"{header_style}",
            border_style=f"{header_style}",
        )
        rprint(header_panel)

        for i, track_analyzer in enumerate(self.track_analyzers):
            console = Console()
            console.rule(
                "[#ffffff on #4707a8]" + f'Track {i}: "{track_analyzer.name}"'
                f"[/#ffffff on #4707a8]",
                style="#ffffff on #4707a8",
            )
            if track_list is None or track_analyzer.name in track_list:
                track_analyzer.analysis(
                    track_bound=track_bound,
                    blind_note=blind_note,
                    blind_time=blind_time,
                    blind_lyric=blind_lyric,
                    blind_note_info=blind_note_info,
                )


class MidiTrackAnalyzer:
    """Class for analysis midi track"""

    def __init__(self, track, ppqn, encoding="utf-8", convert_1_to_0=False):
        self.track = track
        self.name = track.name
        self.ppqn = ppqn
        self.encoding = encoding
        self.convert_1_to_0 = convert_1_to_0
        self._init_values()

    def _init_values(self):
        self.time_signature = DEFAULT_TIME_SIGNATURE
        self.tempo = DEFAULT_TEMPO
        self.length = 0

    def _get_quantized_note(self, msg, beat):
        result = []
        if msg.type == "note_on":
            result.append(Message("note_off", time=beat2tick(beat, self.ppqn)))
        elif msg.type == "note_off":
            q_msg = msg.copy()
            q_msg.time = beat2tick(beat, self.ppqn)
            _msg_on = Message(
                "note_on", note=msg.note, velocity=msg.velocity, time=0
            )
            result.append(q_msg)
            result.append(_msg_on)
        return result

    def _quantization(self, msg, unit="32"):
        q_time = None
        total_q_time = 0
        error = 0
        for note_item in list(Note):
            beat = tick2beat(msg.time, self.ppqn)
            q_beat = note_item.value.beat
            q_time = beat2tick(q_beat, self.ppqn)
            if beat > q_beat:
                msg.time -= q_time
                total_q_time += q_time
            elif beat == q_beat:  # msg is quantized
                msg.time += total_q_time
                return msg, error
            if unit in note_item.value.name_short:
                beat_unit = note_item.value.beat  # beat_unit
                break

        # beat in [0, beat_unit), i.e. beat_unit=0.125
        beat = tick2beat(msg.time, self.ppqn)
        if beat < beat_unit / 2:  # beat in [0, beat_unit/2)
            error = msg.time
            msg.time = 0  # approximate to beat=0
        elif beat < beat_unit:  # beat in [beat_unit/2, beat_unit)
            error = msg.time - beat2tick(beat_unit, self.ppqn)
            # approximate to beat=beat_unit
            msg.time = beat2tick(beat_unit, self.ppqn)
        msg.time += total_q_time
        return msg, error

    def quantization(self, unit="32"):
        """quantization"""
        if not any(
            [unit == n.value.name_short.split("/")[-1] for n in list(Note)]
        ):
            raise ValueError

        error = 0
        last_note = 0
        for i, msg in enumerate(self.track):
            if msg.type in ["note_on", "note_off", "lyrics"]:
                if not msg.time:
                    continue
                if error:
                    msg.time += error
                    error = 0
                msg, error = self._quantization(msg, unit=unit)
                last_note = i

        if error:
            self.track[last_note].time += error
        return self.track

    def slice_slience(self):
        """slice_slience"""
        result = []
        chunk = []
        for msg in self.track:
            if msg.type == "lyrics":
                mmal = MidiMessageAnalyzer_lyrics(msg, encoding=self.encoding)
                if mmal.lyric == " ":
                    if chunk:
                        result.append(chunk)
                        chunk = []
                else:
                    chunk.append(mmal.lyric)
            if msg.type == "note_off":
                chunk.append(msg.note)

    def slice(self, begin, end):
        """slice"""
        pitchs = []
        durations = []
        lyrics = ""
        prev_lyric = ""
        lyric = ""
        total_time = 0
        total_secs = 0
        prev_total_secs = 0
        for msg in self.track:
            total_time += msg.time
            if msg.type == "note_off":
                prev_total_secs = total_secs
            if msg.type == "lyrics":
                prev_lyric = lyric
                mmal = MidiMessageAnalyzer_lyrics(msg, encoding=self.encoding)
                if self.encoding != mmal.encoding:
                    self.encoding = mmal.encoding
                lyric = mmal.lyric
            total_secs += md.tick2second(
                msg.time,
                ticks_per_beat=self.ppqn,
                tempo=self.tempo,
            )
            if msg.type == "set_tempo":
                self.tempo = msg.tempo
            if begin < total_secs < end:
                match msg.type:
                    case "lyrics":
                        if not lyrics:
                            lyrics += prev_lyric
                        lyrics += lyric
                    case "note_off":
                        pitchs.append(msg.note)
                        if not durations:
                            durations.append(total_secs - begin)
                        else:
                            duration = md.tick2second(
                                msg.time,
                                ticks_per_beat=self.ppqn,
                                tempo=self.tempo,
                            )
                            durations.append(duration)
            elif end < total_secs:
                match msg.type:
                    case "note_off":
                        pitchs.append(msg.note)
                        duration = md.tick2second(
                            msg.time,
                            ticks_per_beat=self.ppqn,
                            tempo=self.tempo,
                        )
                        durations.append(end - prev_total_secs)
                        rprint(len(pitchs), len(durations), len(lyrics))
                        rprint(pitchs, durations, lyrics)
                        if not len(pitchs) == len(durations) == len(lyrics):
                            raise ValueError
                        return np.array(pitchs), np.array(durations), lyrics
                    case "end_of_track":
                        return np.array(pitchs), np.array(durations), lyrics

        return None, None, None

    def split_space_note(self, remove_silence_threshold=0.3):
        """split_space_note"""
        modified_track = []
        error = 0
        note_in = False
        for msg in self.track:
            match msg.type:
                case "note_on":
                    note_in = True
                    time = md.tick2second(
                        msg.time,
                        ticks_per_beat=self.ppqn,
                        tempo=self.tempo,
                    )
                    if time > remove_silence_threshold:
                        modified_track += [
                            Message("note_on", time=0),
                            MetaMessage("lyrics", text=" "),
                            Message("note_off", time=msg.time),
                        ]
                    else:  # just remove time
                        error += time
                    msg.time = 0
                case "note_off":
                    note_in = False
                    if error:
                        msg.time += md.second2tick(
                            error, ticks_per_beat=self.ppqn, tempo=self.tempo
                        )
                        error = 0
                case "set_tempo":
                    time = md.tick2second(
                        msg.time,
                        ticks_per_beat=self.ppqn,
                        tempo=self.tempo,
                    )
                    if not note_in and time > remove_silence_threshold:
                        modified_track += [
                            Message("note_on", time=0),
                            MetaMessage("lyrics", text=" "),
                            Message("note_off", time=msg.time),
                        ]
                    else:
                        error += time
                    msg.time = 0
                    self.tempo = msg.tempo
                case _:
                    time = md.tick2second(
                        msg.time,
                        ticks_per_beat=self.ppqn,
                        tempo=self.tempo,
                    )
                    if not note_in and time > remove_silence_threshold:
                        modified_track += [
                            Message("note_on", time=0),
                            MetaMessage("lyrics", text=" "),
                            Message("note_off", time=msg.time),
                        ]
                    else:
                        error += time
                    msg.time = 0
            modified_track.append(msg)
        self.track = modified_track
        return self.track

    def print_note_num(self, note_num):
        """print_note_num"""
        color = "color(240)" if note_num == 0 else "color(47)"
        bpm = round(
            md.tempo2bpm(self.tempo, time_signature=self.time_signature)
        )
        info = f"[bold {color}]Total item num of BPM({bpm}): " + f"{note_num}"
        Console().rule(info, style=f"{color}")

    def to_json(self, file_path, dir_path=None):
        """to_json"""
        self._init_values()
        total_time = 0
        lyric = ""
        data = {"notes": []}
        note_data = {
            "start_time": None,
            "end_time": None,
            "length": None,
            "pitch": None,
            "lyric": None,
        }
        duration = 0
        for i, msg in enumerate(self.track):
            total_time += msg.time
            duration += msg.time
            self.length += md.tick2second(
                msg.time,
                ticks_per_beat=self.ppqn,
                tempo=self.tempo,
            )
            msg_kwarg = {
                "msg": msg,
                "ppqn": self.ppqn,
                "tempo": self.tempo,
                "idx": i,
                "length": self.length,
            }
            match msg.type:
                case "note_on":
                    note_on_time = self.length
                    duration = 0
                case "note_off":
                    _note_data = note_data.copy()
                    _note_data["start_time"] = note_on_time
                    _note_data["end_time"] = self.length
                    _note_data["length"] = md.tick2second(
                        duration,
                        ticks_per_beat=self.ppqn,
                        tempo=self.tempo,
                    )
                    _note_data["pitch"] = msg.note
                    if not lyric:
                        raise ValueError
                    _note_data["lyric"] = lyric
                    if None in _note_data.values():
                        raise ValueError
                    data["notes"].append(_note_data)
                case "lyrics":
                    mmal = MidiMessageAnalyzer_lyrics(
                        **msg_kwarg,
                        encoding=self.encoding,
                    )
                    if self.encoding != mmal.encoding:
                        self.encoding = mmal.encoding
                    _, lyric = mmal.analysis()
                case "set_tempo":
                    _, self.tempo = MidiMessageAnalyzer_set_tempo(
                        **msg_kwarg,
                        time_signature=self.time_signature,
                    ).analysis()
                case "time_signature":
                    _, self.time_signature = (
                        MidiMessageAnalyzer_time_signature(
                            **msg_kwarg
                        ).analysis()
                    )
        if dir_path is None:
            dir_path = Path("")
        else:
            dir_path = Path(dir_path)
            dir_path.mkdir(exist_ok=True, parents=True)
        file_path = dir_path / Path(file_path).with_suffix(".json").name
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def analysis(
        self,
        track_bound=None,
        blind_note=False,
        blind_time=False,
        blind_lyric=True,
        blind_note_info=False,
    ):
        """analysis track"""
        self._init_values()
        note_address = 0
        note_num = 0
        first_tempo = True
        prev_tempo = None
        note_queue = {}
        if track_bound is None:
            track_bound = float("inf")
        lyric = ""
        total_time = 0
        for i, msg in enumerate(self.track):
            if i > track_bound:
                break
            total_time += msg.time
            self.length += md.tick2second(
                msg.time,
                ticks_per_beat=self.ppqn,
                tempo=self.tempo,
            )
            msg_kwarg = {
                "msg": msg,
                "ppqn": self.ppqn,
                "tempo": self.tempo,
                "idx": i,
                "length": self.length,
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
                        encoding=self.encoding,
                    )
                    if self.encoding != mmal.encoding:
                        self.encoding = mmal.encoding
                    result, _lyric = mmal.analysis(
                        note_address=note_address,
                        blind_time=blind_time,
                        blind_note=blind_note,
                        blind_note_info=blind_note_info,
                    )
                    lyric += _lyric
                case "measure":
                    result = MidiMessageAnalyzer_measure(
                        self.time_signature
                    ).analysis()
                case "text" | "track_name":
                    mmat = MidiMessageAnalyzer_text(
                        **msg_kwarg,
                        encoding=self.encoding,
                    )
                    if self.encoding != mmat.encoding:
                        self.encoding = mmat.encoding
                    result = mmat.analysis(blind_time=blind_time)
                case "set_tempo":
                    if not first_tempo and self.convert_1_to_0:
                        self.print_note_num(note_num)
                    first_tempo = False
                    result, self.tempo = MidiMessageAnalyzer_set_tempo(
                        **msg_kwarg,
                        time_signature=self.time_signature,
                    ).analysis(blind_time=blind_time)
                    if prev_tempo is None:
                        prev_tempo = self.tempo
                    if note_num:
                        prev_tempo = self.tempo
                        note_num = 0
                    else:
                        self.tempo = prev_tempo
                case "end_of_track":
                    if self.convert_1_to_0:
                        self.print_note_num(note_num)
                    result = MidiMessageAnalyzer_end_of_track(
                        **msg_kwarg
                    ).analysis(blind_time=blind_time)
                case "key_signature":
                    result = MidiMessageAnalyzer_key_signature(
                        **msg_kwarg
                    ).analysis(blind_time=blind_time)
                case "time_signature":
                    result, self.time_signature = (
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

        rprint(f"Track lyric encode: {self.encoding}")
        self.length = md.tick2second(
            total_time,
            ticks_per_beat=self.ppqn,
            tempo=self.tempo,
        )
        rprint("Track total secs/time: " + f"{self.length}/{total_time}")
        bpm = round(
            md.tempo2bpm(self.tempo, time_signature=self.time_signature)
        )
        rprint("bpm(tempo): " + f"{bpm}({self.tempo})")
        if not blind_lyric:
            print(f'LYRIC: "{lyric}"')


class MidiMessageAnalyzer:
    """MidiMessageAnalyzer"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_PPQN,
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
            time = md.tick2second(
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
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        time_signature=DEFAULT_TIME_SIGNATURE,
    ):
        super().__init__(msg, ppqn, tempo=tempo, idx=idx, length=length)
        self.time_signature = time_signature

    def analysis(self, blind_time=False):
        bpm = round(
            md.tempo2bpm(self.msg.tempo, time_signature=self.time_signature)
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
        ppqn=DEFAULT_PPQN,
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
        ppqn=DEFAULT_PPQN,
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
        ppqn=DEFAULT_PPQN,
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
