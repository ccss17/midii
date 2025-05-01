[![PyPI version](https://img.shields.io/pypi/v/midii)](https://pypi.org/project/midii/) [![GitHub license](https://img.shields.io/github/license/ccss17/midii)](https://github.com/ccss17/midii/blob/main/LICENSE) 

# MIDI Insights

This package inherits `MidiFile` of [`mido`](https://github.com/mido/mido), adding note duration quantization functionality `MidiFile.quantize` and improving the `MidiFile.print_tracks` method.

```python
import midii

mid = midii.MidiFile(
    midii.sample.dataset[0], # or 'song.mid'
    lyric_encoding="utf-8"
)
mid.quantize(unit="32")
mid.print_tracks()
```

# Introduction

Singing Voice Synthesis (SVS) models require the duration of each note as input during training and synthesis. Many public singing voice datasets provide note durations in MIDI format. However, since these durations are often extracted from performances or audio recordings, they may not perfectly align with musical note values, potentially degrading SVS model performance. This motivates the need for note duration regularization. Simple quantization algorithms, which align the start and end times of each note to the nearest grid lines, can lead to accumulating errors during the correction process. This accumulation increases synchronization errors between the quantized score and the singing voice data. This package implements a forward error propagation quantization algorithm that prevents desynchronization by suppressing error accumulation while aligning note durations to the rhythmic grid. 

Delta-time (of MIDI event like note on, note off) quantization aligns the timing of musical events to a grid defined by standard musical rhythm units. Quantization begins by selecting the quantization unit, i.e., the <b>minimum beat unit</b>. For example, let's take the 32nd note (0.125 beats) as the minimum unit.

For `TPQN=480`, converting the irregular tick sequence `[2400, 944, 34, 2, 62]` to beats yields `[5.0, 1.97, 0.07, 0.004, 0.13]`. Quantization aims to make these beats consist only of multiples of 0.125 beats (32nd notes). A simple quantization method approximates each note duration to the nearest rhythm grid line, resulting in the quantized sequence `[4, 2, 0.125, 0, 0.125]`. This effectively regularizes the unregularized notes into a whole note, half note, 32nd note, rest, and 32nd note, respectively.

However, in this method, the numerical error generated during each approximation is simply discarded. This error accumulates for each note, causing the overall timing of the quantized sequence to progressively deviate from the original timing. Therefore, it is necessary to handle the error generated at each step, which motivates the error propagation quantization mechanism implemented in this package.


<!-- In experiments, the proposed method reduced the Mean Absolute Error (MAE) from 334.94 ticks to 3.78 ticks compared to simple quantization, achieving an error reduction rate of approximately 98.87\%. The proposed method is useful for improving the quality and stability of SVS models by correcting note duration errors when training with public MIDI data. -->

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

- The parameters of this class are no different from those of the `mido.MidiFile` class it inherits, except for `convert_1_to_0=False` and `lyric_encoding='latin-1'`. 

  If you want to convert midi file type `1` to `0`, pass `convert_1_to_0=True`. 

  `lyric_encoding` specify encoding of lyric data.

- `quantize(unit)`: Quantize note duration. You can define least unit of quantization from `"1"`(whole note), `"2"`, `"4"`, `"8"`, `"16"`, `"32"`, `"64"`, `"128"`, `"256"`(two hundred fifty-sixth note)

<!-- - `quantize(unit="32")`: Quantize note duration. You can define least unit of quantization from `"1"`(whole note), `"2"`(half note), `"4"`(quarter note), `"8"`(eighth note), `"16"`(sixteenth note), `"32"`(thirty-second note), `"64"`(sixty-fourth note), `"128"`(hundred twenty-eighth note), `"256"`(two hundred fifty-sixth note) -->

<!-- The smaller the minimum unit, the less sync error with the original, and the weaker the quantization effect. As the minimum unit becomes larger, the sync error with the original increases and the quantization effect increases. -->

- `print_tracks(track_limit=None, print_note=True, print_time=True, print_lyric=False, track_list=None, print_note_info=False)`: An overriding function that improves the existing `mido.print_tracks`.

    By default it will print all lines of track. By setting like `track_limit=20`, You can define upper bound of lines to be printed.

    By default it will prints all tracks. You can specify the tracks you want to output in the list `track_list`. For example, `track_list=[]`, or `track_list=["piano", "intro"]`.

## `midii.second2frame`

`midii.second2frame(seconds, sr=22050, hop_length=512)`: convert times to frames with handling rounding error

- simple loss comparison(vs `librosa.time_to_frames`) test from `test_seconds_to_frames_loss_comparison()` of `test/test.py`:

  ```
  ideal frames(Frames defined as real values unlike original mel spectrogram frames, 
  which are integers, allowing for the intentional introduction of loss during the 
  frame-to-seconds-to-frame conversion):
  [107.594   97.5893  19.1057 111.1184  76.5198  25.4199 107.1373 126.879
    79.2862  92.1725 121.5947 104.406  108.8866 135.4734  57.788    6.6442
    92.4604  42.1106 134.8538  25.5506]

  converted seconds:
  [1.249164 1.13301  0.221816 1.290083 0.888393 0.295124 1.243862 1.473062
  0.920511 1.07012  1.411712 1.212151 1.264171 1.572843 0.670917 0.07714
  1.073463 0.488903 1.565649 0.296642]

  sum of ideal frames: 1672.5904
    -> int conversion (floor): 1672
    -> int conversion (round): 1673
  sum of fractional parts: 9.5904

  --- librosa.time_to_frames  ---
  converted frames:
  [107  97  19 111  76  25 107 126  79  92 121 104 108 135  57   6  92  42
  134  25]
  total frames: 1663
  (vs ideal floor): -9 frames
  (vs ideal round): -10 frames
  
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

[generated by](test/figure_piano_roll.ipynb)

![](figure/figure_piano_roll.png)

## EF effect(time drift mitigating)

[generated by](test/figure_EF_effect.ipynb.ipynb)

![](figure/figure_EF_w_wo_comparison.png)

## timing deviation for each quantization units

[generated by](test/figure_timing_deviation.ipynb.ipynb.ipynb)

![](figure/figure_timing_deviation.png)

# License

MIT
