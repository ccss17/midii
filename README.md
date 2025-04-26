# MIDI Insights

This package inherits `MidiFile` of [`mido`](https://github.com/mido/mido), adding note duration quantization functionality `MidiFile.quantize` and improving the `MidiFile.print_tracks` method.

```python
import midii

mid = midii.MidiFile(
    midii.sample.dataset[0], # or 'song.mid'
    convert_1_to_0=True, lyric_encoding="cp949"
)
mid.quantize(unit="32")
mid.print_tracks(
    track_limit=None,
    track_list=None,
    print_note_info=True,
    print_lyric=False,
)
```

## Installation

```shell
pip install midii
```

# API

##  `midii.sample`

`midii.sample`: It contains some sample midi files.

- `dataset`: List object that contains some midi dataset for deep learning model. The lyric encoding of these midi files is `"cp949"` or `"utf-8"`

- `simple`: List object that contains some simple midi dataset. It is artificially created midi file for test purpose.

- `real`: List object that contains real-world midi examples.

##  `midii.quantize`

`midii.quantize`: 

## `class midii.MidiFile`

`class midii.MidiFile(filename=None, file=None, type=1, ticks_per_beat=480, charset='latin1', debug=False, clip=False, tracks=None, convert_1_to_0=False, lyric_encoding='latin-1')`

The parameters of this class are no different from those of the `mido.MidiFile` class it inherits, except for `convert_1_to_0=False` and `lyric_encoding='latin-1'`. 

If you want to convert midi file type `1` to `0`, pass `convert_1_to_0=True`. 

`lyric_encoding` specify encoding of lyric data.

- `quantize(unit="32")`: Quantize note duration. You can define least unit of quantization from `"1"`(whole note), `"2"`(half note), `"4"`(quarter note), `"8"`(eighth note), `"16"`(sixteenth note), `"32"`(thirty-second note), `"64"`(sixty-fourth note), `"128"`(hundred twenty-eighth note), `"256"`(two hundred fifty-sixth note)

    The smaller the minimum unit, the less sync error with the original, and the weaker the quantization effect. As the minimum unit becomes larger, the sync error with the original increases and the quantization effect increases.

- `print_tracks(track_limit=None, print_note=True, print_time=True, print_lyric=False, track_list=None, print_note_info=False)`: An overriding function that improves the existing `mido.print_tracks`.

    By default it will print all lines of track. By setting like `track_limit=20`, You can define upper bound of lines to be printed.

    By default it will prints all tracks. You can specify the tracks you want to output in the list `track_list`. For example, `track_list=[]`, or `track_list=["piano", "intro"]`.

## Example

### `print_tracks`

- `print_tracks`: `mido.MidiFile.print_tracks` &rarr; `midii.MidiFile.print_tracks` 

    ![](figure/print.png)

    ![](figure/print2.png)

### `quantize`

- `quantize(unit="32")`: 

    The smaller the minimum unit, the less sync error with the original, and the weaker the quantization effect. 
    
    As the minimum unit becomes larger, the sync error with the original increases and the quantization effect increases.

    ![](figure/q1.png)

    ![](figure/q2.png)

## Figure

### time drift mitigating

![](figure/figure_EF_w_wo_comparison.pdf)

## License

MIT
