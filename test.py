import midii
import mido


def test_sample():
    print(midii.sample.real)
    print(midii.sample.dataset)
    print(midii.sample.simple)


def test_midii_simple_print_tracks():
    ma = midii.MidiFile(midii.sample.simple[0])
    ma.quantization(unit="256")
    ma.print_tracks()


def test_midii_real_print_tracks():
    ma = midii.MidiFile(midii.sample.real[1])
    ma.quantization(unit="256")
    ma.print_tracks(blind_note_info=True, track_list=["piano-r"])


def test_mido_dataset_print_tracks():
    ma = mido.MidiFile(midii.sample.dataset[1])
    ma.print_tracks()


def test_midii_print_tracks():
    ma = midii.MidiFile(
        midii.sample.dataset[1], convert_1_to_0=True, lyric_encoding="cp949"
    )
    # ma.quantization(unit="32")
    ma.print_tracks(
        track_bound=None,
        track_list=None,
        blind_note_info=True,
        blind_lyric=True,
    )


def test_midii_quantization():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    ma.quantization(unit="32", error_forwarding=False)
    ma.print_tracks(
        track_bound=None,
        track_list=None,
        blind_note_info=True,
        blind_lyric=True,
    )


def test_version():
    from importlib.metadata import version

    print("mido version:", version("mido"))
    print("numpy version:", version("numpy"))
    print("rich version:", version("rich"))


def test_midii_print_times():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    # ma.print_tracks()
    print(ma.times)
    ma.quantize(unit="64")
    print(ma.times)


def test_standalone_quantize():
    ma = midii.MidiFile(
        midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    subset = slice(0, 70)
    subset_last = slice(-33, None)
    times_q32, error_q32 = midii.quantize(
        ma.times, unit="32", ticks_per_beat=ma.ticks_per_beat
    )
    times_q64, error_q64 = midii.quantize(
        ma.times, unit="64", ticks_per_beat=ma.ticks_per_beat
    )
    times_q128, error_q128 = midii.quantize(
        ma.times, unit="128", ticks_per_beat=ma.ticks_per_beat
    )
    # print(ma.times[subset])
    print(ma.times[subset_last])
    ma.quantize()
    # print(ma.times[subset])
    # print(times_q32[subset])
    print(ma.times[subset_last])
    print(times_q32[subset_last])
    # print(times_q64[subset], error_q64)
    # print(times_q128[subset], error_q128)
    # print(times_q64[subset_last])
    # print(times_q128[subset_last])


if __name__ == "__main__":
    # test_sample()
    # test_midii_simple_print_tracks()
    # test_midii_real_print_tracks()
    # test_mido_dataset_print_tracks()
    # test_midii_print_tracks()
    # test_midii_quantization()
    # test_version()
    # test_midii_print_times()
    test_standalone_quantize()
