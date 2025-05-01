[![PyPI version](https://img.shields.io/pypi/v/midii)](https://pypi.org/project/midii/) [![GitHub license](https://img.shields.io/github/license/ccss17/midii)](https://github.com/ccss17/midii/blob/master/LICENSE) 

# MIDI Insights

This package inherits `MidiFile` of [`mido`](https://github.com/mido/mido), adding note duration quantization functionality `MidiFile.quantize` and improving the `MidiFile.print_tracks` method.

```python
import midii

mid = midii.MidiFile(
    midii.sample.dataset[0], # or 'song.mid'
    lyric_encoding="utf-8" # or some lyric encoding for your MIDI file
)
mid.quantize(unit="32")
mid.print_tracks()
```

# Introduction

Singing Voice Synthesis (SVS) models require the duration of each note as input during training and synthesis. Many public singing voice datasets provide note durations in MIDI format. However, since these durations are often extracted from performances or audio recordings, they may not perfectly align with musical note values, potentially degrading SVS model performance. This motivates the need for note duration regularization. Simple quantization algorithms, which align the start and end times of each note to the nearest grid lines, can lead to accumulating errors during the correction process. This accumulation increases synchronization errors between the quantized score and the singing voice data. This package implements a forward error propagation quantization algorithm that prevents desynchronization by suppressing error accumulation while aligning note durations to the rhythmic grid. 

<!-- Simple quantization techniques are sometimes used to regularize the timing information in MIDI data. Let the actual start and end times of a note be referred to as the note's <b>start and end timing</b>. This method forces the note's timing to the nearest rhythm grid line, generating structured timing information. However, errors introduced during this process accumulate over time, increasing the timing synchronization error with the original data.  -->

<!-- This paper proposes a new quantization method to address this issue. The algorithm features a \textbf{Forward Error Propagation (EF) mechanism}, which processes the error generated in one quantization step by incorporating it into the next step. This mechanism mitigates the accumulation of errors during the quantization process. -->

Delta-time (of MIDI event like note on, note off) quantization aligns the timing of musical events to a grid defined by standard musical rhythm units. Quantization begins by selecting the quantization unit, i.e., the <b>minimum beat unit</b>. For example, let's take the 32nd note (0.125 beats) as the minimum unit.

For `TPQN=480`, converting the irregular tick sequence `[2400, 944, 34, 2, 62]` to beats yields `[5.0, 1.97, 0.07, 0.004, 0.13]`. Quantization aims to make these beats consist only of multiples of 0.125 beats (32nd notes). A simple quantization method approximates each note duration to the nearest rhythm grid line, resulting in the quantized sequence `[4, 2, 0.125, 0, 0.125]`. This effectively regularizes the unregularized notes into a whole note, half note, 32nd note, rest, and 32nd note, respectively.

However, in this method, the numerical error generated during each approximation is simply discarded. This error accumulates for each note, causing the overall timing of the quantized sequence to progressively deviate from the original timing. Therefore, it is necessary to handle the error generated at each step, which motivates the error propagation quantization mechanism(below pseudocode) implemented in this package. This pseudocode assumes a constant set `quanta=[4, 2, 1, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625]`, which includes the beat values of standard musical notes from whole notes to 256th notes.

![](figure/pseudocode.png)

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

`midii.quantize(ticks, unit, sync_error_mitigation=True)`: quantization function with mitigating quantization error by forwarding and managing error of previous quantization step to current quantization step with <b>generalized tick unit</b>. 

- While the unit was assumed to be ticks for clarity, the unit parameter accepted by this function can represent the note's duration in units of beats (`float`), ticks (`int`), seconds (`float`), or frames (`int`). Consequently, while converting the note's duration to any unit space and subsequently performing normalization is permissible, attention must be paid to the loss incurred during float-to-integer conversion. Meanwhile, `midii.second2frame` is provided to mitigate the loss incurred during seconds-to-frames conversion

## `class midii.MidiFile`

`class midii.MidiFile(filename=None, file=None, type=1, ticks_per_beat=480, charset='latin1', debug=False, clip=False, tracks=None, convert_1_to_0=False, lyric_encoding='latin-1')`

- The parameters of this class are no different from those of the `mido.MidiFile` class it inherits, except for `convert_1_to_0=False` and `lyric_encoding='latin-1'`. 

  If you want to convert midi file type `1` to `0`, pass `convert_1_to_0=True`. 

  `lyric_encoding` specify encoding of lyric data.

- `quantize(unit, targets=["note_on", "note_off", "lyrics"], sync_error_mitigation=True)`: Quantize note duration. You can define least unit of quantization from `"1"`(whole note), `"2"`, `"4"`, `"8"`, `"16"`, `"32"`, `"64"`, `"128"`, `"256"`(two hundred fifty-sixth note)

  By `targets` parameter(`list`), you can specify MIDI event types to quantize ticks(delta-time).

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

The goal of quantization is to align musical events to the rhythm grid. Above figure compares a segment of a MIDI file with the result after applying the proposed quantization algorithm using a 32nd note unit. As shown in the top panel, the original notes exhibit deviations from the grid. The bottom panel shows that after quantization, all notes are aligned to the 32nd note rhythm grid.


## EF effect(time drift mitigating)

[generated by](test/figure_EF_effect.ipynb.ipynb)

![](figure/figure_EF_w_wo_comparison.png)

To evaluate the effectiveness of mitigating the timing discrepancy of simple quantization, we compared the timing resulting from the proposed method (w/ EF) with that from the simple quantization method without error propagation (w/o EF). 

<!-- The <b>start timing</b> of any note is the sum of the delta-times of all preceding notes. Above figure displays the start timing of each note during the quantization process.  -->

<!-- For every note $i$, let the original start timing be $o_i$, the start timing after applying the proposed quantization be $q_i$, and the start timing after applying simple quantization be $q'_i$. The timing discrepancy caused by the proposed quantization is calculated as $q_i-o_i$ (orange line), and the discrepancy from simple quantization is $q'_i-o_i$ (blue line). The line $y=0$ (black dotted line) represents perfect synchronization with the original timing. The blue line shows accumulating errors, whereas the orange line remains close to $y=0$. -->

## timing deviation for each quantization units

[generated by](test/figure_timing_deviation.ipynb.ipynb.ipynb)

![](figure/figure_timing_deviation.png)

This illustrates the trade-off determined by the choice of the quantization <b>unit</b>. A <b>larger quantization unit</b> enforces a stronger rhythmic structure, aligning notes to fewer, wider grid points. This results in a <b>higher degree of rhythmic regularization</b>. However, this also causes <b>greater deviation</b> from the original event timings, altering the original performance timing more significantly.

Conversely, a <b>smaller quantization unit</b> aligns notes to a denser grid, resulting in <b>smaller deviation</b> from the original timing. This preserves more of the original timing information and alters the performance timing less, but at the cost of <b>weaker rhythmic regularization</b>. That is, although the notes are aligned to the grid, they remain closer to the potentially noisy or irregular input timing. Therefore, the choice of quantization unit must be carefully considered based on the specific goals of the preprocessing step.

<!-- The timing deviations for different quantization units can also be quantitatively evaluated using MAE, and the results are shown in Table~\ref{tab:quantitative_comparison}. -->

# License

MIT
