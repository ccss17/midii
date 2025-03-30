import mida
import mida.sample


def test_sample():
    print(mida.sample.real)
    print(mida.sample.dataset)


def test_MidiAnalyzer():
    ma = mida.MidiAnalyzer(mida.sample.dataset[3], convert_1_to_0=True)
    ma.split_space_note(remove_silence_threshold=0.3)
    ma.quantization(unit="32")
    ma.analysis(
        track_bound=None,
        track_list=None,
        blind_note_info=True,
        blind_lyric=False,
    )


if __name__ == "__main__":
    # test_sample()
    test_MidiAnalyzer()
