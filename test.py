import midii


def test_sample():
    print(midii.sample.real)
    print(midii.sample.dataset)


def test_MidiAnalyzer():
    ma = midii.MidiFile(midii.sample.dataset[1], convert_1_to_0=True)
    ma.quantization(unit="32")
    ma.analysis(
        track_bound=None,
        track_list=None,
        blind_note_info=True,
        blind_lyric=True,
    )


if __name__ == "__main__":
    # test_sample()
    test_MidiAnalyzer()
