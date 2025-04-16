from copy import deepcopy

import numpy as np
import mido
from rich import print as rprint
import midii


def test_sample():
    print(midii.sample.real)
    print(midii.sample.dataset)
    print(midii.sample.simple)


def test_midii_simple_print_tracks():
    ma = midii.MidiFile(midii.sample.simple[0])
    ma.quantize(unit="256")
    ma.print_tracks()


def test_midii_real_print_tracks():
    ma = midii.MidiFile(midii.sample.real[1])
    ma.quantize(unit="256")
    ma.print_tracks(print_note_info=True, track_list=["piano-r"])


def test_mido_dataset_print_tracks():
    ma = mido.MidiFile(midii.sample.dataset[1])
    ma.print_tracks()


def test_midii_print_tracks():
    ma = midii.MidiFile(
        midii.sample.dataset[1], convert_1_to_0=True, lyric_encoding="cp949"
    )
    ma.quantize(unit="32")
    ma.print_tracks()


def test_midii_quantize():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    print(np.mean(np.array(ma.times) % 15))
    ma.quantize(unit="32")
    print(np.mean(np.array(ma.times) % 15))


def test_version():
    from importlib.metadata import version
    import platform

    print("Python Version (concise):", platform.python_version())
    print("mido version:", version("mido"))
    print("rich version:", version("rich"))


def test_midii_print_times():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    ma.print_tracks()


def test_to_json():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    rprint(ma.to_json())
    ma.quantize()
    rprint(ma.to_json())


def test_lyrics():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    print(ma.lyrics)


def test_times():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    print(ma.times)
    ma.quantize()
    print(ma.times)


def test_EF_w_wo():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    ma2 = deepcopy(ma)
    print(np.cumsum(np.array(ma.times, dtype=np.int64))[-10:])
    ma.quantize()
    print(np.cumsum(np.array(ma.times, dtype=np.int64))[-10:])
    ma2.quantize(error_forwarding=False)
    print(np.cumsum(np.array(ma2.times, dtype=np.int64))[-10:])


def test_midi_type():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    print(ma.type)


if __name__ == "__main__":
    # test_sample()
    # test_midii_simple_print_tracks()
    # test_midii_real_print_tracks()
    # test_mido_dataset_print_tracks()
    # test_midii_print_tracks()
    test_midii_quantize()
    # test_midii_print_times()
    # test_version()
    # test_to_json()
    # test_lyrics()
    # test_times()
    # test_EF_w_wo()
    # test_midi_type()
