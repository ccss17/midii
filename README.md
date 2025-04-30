# MIDI Insights

This package inherits `MidiFile` of [`mido`](https://github.com/mido/mido), adding note duration quantization functionality `MidiFile.quantize` and improving the `MidiFile.print_tracks` method.

```python
import midii

mid = midii.MidiFile(
    midii.sample.dataset[0], # or 'song.mid'
    lyric_encoding="cp949"
)
mid.quantize(unit="32")
mid.print_tracks()
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

##  `midii.quantize`

`midii.quantize(ticks, unit, error_forwarding=True)`: quantization function with mitigating quantization error by forwarding and managing error of previous quantization step to current quantization step

## `class midii.MidiFile`

`class midii.MidiFile(filename=None, file=None, type=1, ticks_per_beat=480, charset='latin1', debug=False, clip=False, tracks=None, convert_1_to_0=False, lyric_encoding='latin-1')`

The parameters of this class are no different from those of the `mido.MidiFile` class it inherits, except for `convert_1_to_0=False` and `lyric_encoding='latin-1'`. 

If you want to convert midi file type `1` to `0`, pass `convert_1_to_0=True`. 

`lyric_encoding` specify encoding of lyric data.

- `quantize(unit="32")`: Quantize note duration. You can define least unit of quantization from `"1"`(whole note), `"2"`(half note), `"4"`(quarter note), `"8"`(eighth note), `"16"`(sixteenth note), `"32"`(thirty-second note), `"64"`(sixty-fourth note), `"128"`(hundred twenty-eighth note), `"256"`(two hundred fifty-sixth note)

<!-- The smaller the minimum unit, the less sync error with the original, and the weaker the quantization effect. As the minimum unit becomes larger, the sync error with the original increases and the quantization effect increases. -->

- `print_tracks(track_limit=None, print_note=True, print_time=True, print_lyric=False, track_list=None, print_note_info=False)`: An overriding function that improves the existing `mido.print_tracks`.

    By default it will print all lines of track. By setting like `track_limit=20`, You can define upper bound of lines to be printed.

    By default it will prints all tracks. You can specify the tracks you want to output in the list `track_list`. For example, `track_list=[]`, or `track_list=["piano", "intro"]`.

## `midii.second2frame`

`midii.second2frame(seconds, sr=22050, hop_length=512)`: convert times to frames with handling rounding error

### simple loss comparison test

```
ideal frames : Base + Fraction
[107.594   97.5893  19.1057 111.1184  76.5198  25.4199 107.1373 126.879
  79.2862  92.1725 121.5947 104.406  108.8866 135.4734  57.788    6.6442
  92.4604  42.1106 134.8538  25.5506]

seconds:
[1.249164 1.13301  0.221816 1.290083 0.888393 0.295124 1.243862 1.473062
 0.920511 1.07012  1.411712 1.212151 1.264171 1.572843 0.670917 0.07714
 1.073463 0.488903 1.565649 0.296642]
(20)
------------------------------------------------------------
'sum of ideal frames: 1672.5904
  -> int conversion (floor): 1672
  -> int conversion (round): 1673
(sum of fractional parts: 9.5904)
------------------------------------------------------------
--- librosa.time_to_frames  ---
[107  97  19 111  76  25 107 126  79  92 121 104 108 135  57   6  92  42
 134  25]

total frames: 1663
(vs ideal floor): -9 frames
(vs ideal round): -10 frames
(estimated loss: 9.59 frames)
------------------------------------------------------------
--- midii.second2frame ---
converted frames:
[108  98  19 111  77  25 107 127  79  92 122 104 109 135  58   7  92  42
 135  26]

total frames: 1673
(vs ideal floor): 1 frames
(vs ideal round): 0 frames
```

# Example

## `print_tracks`

- `print_tracks`: `mido.MidiFile.print_tracks` &rarr; `midii.MidiFile.print_tracks` 

    ![](figure/print.png)

    ![](figure/print2.png)

## `quantize`

- `quantize(unit="32")`: 

    The smaller the minimum unit, the less sync error with the original, and the weaker the quantization effect. 
    
    As the minimum unit becomes larger, the sync error with the original increases and the quantization effect increases.

    ![](figure/q1.png)

    ![](figure/q2.png)

# Figure

## quantization effect(piano roll)

![](figure/figure_piano_roll.png)

## EF effect(time drift mitigating)

![](figure/figure_EF_w_wo_comparison.png)

## timing deviation for each quantization units

![](figure/figure_timing_deviation.png)

# License

MIT
