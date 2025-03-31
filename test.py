import midii
import mido


def test_sample():
    print(midii.sample.real)
    print(midii.sample.dataset)


def test_mido_print_tracks():
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
        midii.sample.dataset[1], convert_1_to_0=True, lyric_encoding="cp949"
    )
    ma.quantization(unit="32")
    ma.print_tracks(
        track_bound=None,
        track_list=None,
        blind_note_info=True,
        blind_lyric=True,
    )


if __name__ == "__main__":
    # test_sample()
    # test_mido_print_tracks()
    test_midii_print_tracks()
    # test_midii_quantization()
