from copy import deepcopy
from importlib.metadata import version
import platform

import numpy as np
import mido
from rich import print as rprint
import librosa
from numba import njit

import midii


def test_sample():
    print(midii.sample.dataset)
    print(midii.sample.simple)


def test_midii_simple_print_tracks():
    ma = midii.MidiFile(midii.sample.simple[0])
    ma.print_tracks()


def test_mido_dataset_print_tracks():
    ma = mido.MidiFile(midii.sample.dataset[1])
    ma.print_tracks()


def test_midii_print_tracks():
    ma = midii.MidiFile(
        midii.sample.dataset[1], convert_1_to_0=True, lyric_encoding="utf-8"
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
    unit_tick = midii.beat2tick(midii.NOTE["n/32"].beat, ticks_per_beat=480)
    q, e = midii.quantize(ticks, unit=unit_tick)
    print(q, e)


def test_version():
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
    # subset = slice(0, 70)
    subset_last = slice(-33, None)
    unit = midii.beat2tick(
        midii.NOTE["n/32"].beat, ticks_per_beat=ma.ticks_per_beat
    )
    times_q32, error_q32 = midii.quantize(ma.times, unit=unit)
    # times_q64, error_q64 = midii.quantize(
    #     ma.times, unit="64", ticks_per_beat=ma.ticks_per_beat
    # )
    # times_q128, error_q128 = midii.quantize(
    #     ma.times, unit="128", ticks_per_beat=ma.ticks_per_beat
    # )
    # print(ma.times[subset])
    print(ma.times[subset_last])
    ma.quantize()
    # print(ma.times[subset])
    # print(times_q32[subset])
    print(ma.times[subset_last], type(ma.times[subset_last]))
    print(times_q32[subset_last], type(times_q32[subset_last]))
    # print(times_q64[subset], error_q64)
    # print(times_q128[subset], error_q128)
    # print(times_q64[subset_last])
    # print(times_q128[subset_last])


def test_divmod(t, u):
    if False:
        # $ hyperfine --warmup 10 -r 200 "python test.py"
        # Benchmark 1: python test.py
        # Time (mean ± σ): 228.3 ms ± 8.0 ms [User: 103.5 ms, System: 90.9 ms]
        # Range (min … max): 215.8 ms … 262.7 ms 200 runs
        q, r = divmod(t, u)
    else:
        # hyperfine --warmup 10 -r 200 "python test.py"
        # Benchmark 1: python test.py
        # Time (mean ± σ): 229.2 ms ± 8.5 ms [User: 104.3 ms, System: 89.7 ms]
        # Range (min … max): 215.4 ms … 275.7 ms    200 runs
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
    print(librosa.time_to_frames(0.03125, hop_length=256))
    print(midii.second2frame([0.03125], hop_length=256))
    print(midii.second2frame(0.03125, hop_length=256))


DEFAULT_SAMPLING_RATE = 22050
DEFAULT_HOP_LENGTH = 256


def test_continuous_quantization():
    sampling_rate = 22050
    hop_length = 256
    tick_per_beat = 480
    # time_to_pos = 16
    frames = np.load("test/ba_05004_+4_a_s01_f_02.npy")
    print("frames", frames[:10], frames.sum())
    seconds = midii.frame2second(
        frames, sr=sampling_rate, hop_length=hop_length
    )
    print("seconds", seconds[-10:], seconds.sum())
    unit_beats = midii.NOTE["n/64"].beat
    unit_ticks = midii.beat2tick(unit_beats, ticks_per_beat=tick_per_beat)
    unit_seconds = mido.tick2second(
        unit_ticks, ticks_per_beat=tick_per_beat, tempo=midii.DEFAULT_TEMPO
    )
    unit_frames = midii.second2frame(
        unit_seconds, sr=sampling_rate, hop_length=hop_length
    )
    print("unit_beats", unit_beats)
    print("unit_ticks", unit_ticks)
    print("unit_seconds", unit_seconds)
    print("unit_frames", unit_frames)
    quantized_seconds, err = midii.quantize(seconds, unit=unit_seconds)
    print(quantized_seconds[-10:], sum(quantized_seconds))
    q_frames = midii.second2frame(
        quantized_seconds, sr=sampling_rate, hop_length=hop_length
    )
    print(q_frames[:10], q_frames.sum())
    q_frames_rosa = librosa.time_to_frames(
        quantized_seconds, sr=sampling_rate, hop_length=hop_length
    )
    print(q_frames_rosa[:10], q_frames_rosa.sum())


def test_seconds_to_frames_loss_comparison():
    sr = DEFAULT_SAMPLING_RATE
    hop_length = DEFAULT_HOP_LENGTH
    frames_per_sec = sr / hop_length

    np.random.seed(42)
    num_durations = 20
    base_frames = np.random.randint(5, 150, size=num_durations)
    fractional_parts = np.random.uniform(0.1, 0.9, size=num_durations)
    ideal_float_frames = base_frames + fractional_parts
    times_in_seconds = ideal_float_frames / frames_per_sec

    print(f"Sampling Rate (sr): {sr} Hz")
    print(f"Hop Length (hop_length): {hop_length} samples")
    print(f"Frames per Second: {frames_per_sec:.4f}")
    # print("\n생성된 Base 정수 프레임:")
    # print(base_frames)
    # print("\n추가된 임의 소수 부분:")
    # print(np.round(fractional_parts, 4))
    print("\nideal frames : Base + Fraction")
    print(np.round(ideal_float_frames, 4))
    print("\nseconds:")
    print(np.round(times_in_seconds, 6))
    print(f"({num_durations})")
    print("-" * 60)

    target_total_frames_float = np.sum(ideal_float_frames)
    target_total_frames_floor = np.floor(target_total_frames_float).astype(int)
    target_total_frames_round = np.round(target_total_frames_float).astype(int)
    total_fractional_parts = np.sum(fractional_parts)

    print(f"'sum of ideal frames: {target_total_frames_float:.4f}")
    print(f"  -> int conversion (floor): {target_total_frames_floor}")
    print(f"  -> int conversion (round): {target_total_frames_round}")
    print(f"(sum of fractional parts: {total_fractional_parts:.4f})")
    print("-" * 60)

    frames_librosa = librosa.time_to_frames(
        times_in_seconds, sr=sr, hop_length=hop_length
    )
    total_frames_librosa = np.sum(frames_librosa)
    diff_librosa_vs_target_floor = (
        total_frames_librosa - target_total_frames_floor
    )
    diff_librosa_vs_target_round = (
        total_frames_librosa - target_total_frames_round
    )

    print("--- librosa.time_to_frames  ---")
    print(frames_librosa)
    print(f"\ntotal frames: {total_frames_librosa}")
    print(f"(vs ideal floor): {diff_librosa_vs_target_floor} frames")
    print(f"(vs ideal round): {diff_librosa_vs_target_round} frames")
    print(f"(estimated loss: {total_fractional_parts:.2f} frames)")

    print("-" * 60)

    # frames_optimized = second2frame_optimized(
    frames_optimized = midii.second2frame(
        times_in_seconds, sr=sr, hop_length=hop_length
    )
    total_frames_optimized = np.sum(frames_optimized)
    diff_optimized_vs_target_floor = (
        total_frames_optimized - target_total_frames_floor
    )
    diff_optimized_vs_target_round = (
        total_frames_optimized - target_total_frames_round
    )

    print("--- midii.second2frame ---")
    print("converted frames:")
    print(frames_optimized)
    print(f"\ntotal frames: {total_frames_optimized}")
    print(f"(vs ideal floor): {diff_optimized_vs_target_floor} frames")
    print(f"(vs ideal round): {diff_optimized_vs_target_round} frames")


if __name__ == "__main__":
    # test_sample()
    # test_midii_simple_print_tracks()
    # test_mido_dataset_print_tracks()
    # test_midii_print_tracks()
    # test_midii_quantization()

    # test_midii_quantize()
    # test_to_json()
    # test_lyrics()
    # test_times()
    # test_EF_w_wo()
    # test_midi_type()

    # test_version()
    # test_midii_print_times()
    # test_standalone_quantize()
    # test_divmod(100, 18)
    # test_remainder()
    # test_remainder_numba()
    # test_midii_quantization_function()
    # test_times_to_frames()
    # test_continuous_quantization()
    test_seconds_to_frames_loss_comparison()
