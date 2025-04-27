import midii
import mido
from numba import njit


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
    ma.print_tracks(print_note_info=False, track_list=["piano-r"])


def test_mido_dataset_print_tracks():
    ma = mido.MidiFile(midii.sample.dataset[1])
    ma.print_tracks()


def test_midii_print_tracks():
    ma = midii.MidiFile(
        midii.sample.dataset[1], convert_1_to_0=True, lyric_encoding="cp949"
    )
    # ma.quantize(unit="32")
    ma.print_tracks(
        track_limit=None,
        track_list=None,
        print_note_info=False,
    )


def test_midii_quantization():
    ma = midii.MidiFile(
        midii.sample.dataset[0],
        lyric_encoding="cp949",
        # midii.sample.dataset[0], convert_1_to_0=True, lyric_encoding="cp949"
    )
    ma.quantize(unit="32", error_forwarding=False)
    ma.print_tracks(
        track_limit=None,
        track_list=None,
        print_note_info=False,
    )


def test_midii_quantization_function():
    ticks = [2400, 944, 34, 2, 62]
    q, e = midii.quantize(ticks, unit="32", ticks_per_beat=480)
    print(q, e)


def test_version():
    from importlib.metadata import version
    import platform

    pkgs = [
        "mido",
        "rich",
        "ipykernel",
        "matplotlib",
        "pytest",
        "numpy",
        "numba",
    ]
    for pkg in pkgs:
        print(f"{pkg} version:", version(pkg))
    print("Python version:", platform.python_version())

    # mido version: 1.3.3
    # rich version: 14.0.0
    # ipykernel version: 6.29.5
    # matplotlib version: 3.10.1
    # pytest version: 8.3.5
    # numpy version: 2.2.5
    # numba version: 0.61.2
    # Python version: 3.13.1

    # print("mido version:", version("mido"))
    # print("numpy version:", version("numpy"))
    # print("rich version:", version("rich"))
    # print("numba version:", version("numba"))


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


def test_divmod(t, u):
    if False:
        # $ hyperfine --warmup 10 -r 200 "python test.py"
        # Benchmark 1: python test.py
        #   Time (mean ± σ):     228.3 ms ±   8.0 ms    [User: 103.5 ms, System: 90.9 ms]
        #   Range (min … max):   215.8 ms … 262.7 ms    200 runs
        q, r = divmod(t, u)
    else:
        # hyperfine --warmup 10 -r 200 "python test.py"
        # Benchmark 1: python test.py
        #   Time (mean ± σ):     229.2 ms ±   8.5 ms    [User: 104.3 ms, System: 89.7 ms]
        #   Range (min … max):   215.4 ms … 275.7 ms    200 runs
        q = t // u
        r = t - q * u  # r = t % u
    return q, r


def test_remainder():
    # for i in range(100_000):
    # r = i % 7
    for i in range(100_000):
        q = i // 7
        r = i - q * 7
    return r


@njit(cache=True, fastmath=True)
def test_remainder_numba():
    for i in range(100_000):
        r = i % 7
    # for i in range(100_000):
    #     q = i // 7
    #     r = i - q * 7
    return r


def test_times_to_frames():
    import librosa

    print(librosa.time_to_frames(0.03125, hop_length=256))
    print(midii.duration_secs_to_frames([0.03125], hop_length=256))
    print(midii.duration_secs_to_frames(0.03125, hop_length=256))


if __name__ == "__main__":
    # test_sample()
    # test_midii_simple_print_tracks()
    # test_midii_real_print_tracks()
    # test_mido_dataset_print_tracks()
    # test_midii_print_tracks()
    # test_midii_quantization()
    # test_version()
    # test_midii_print_times()
    # test_standalone_quantize()
    # test_divmod(100, 18)
    # test_remainder()
    # test_remainder_numba()
    # test_midii_quantization_function()
    test_times_to_frames()
