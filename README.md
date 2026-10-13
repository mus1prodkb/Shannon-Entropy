# Shannon Entropy: MIDI Melody Tension Graph

A Python script that analyzes a MIDI melody using Shannon entropy and plots an entropy-based tension graph.

The script calculates entropy for pitch classes and melodic intervals in sliding time windows. The resulting graph can help show where the melody becomes more or less varied.

## Requirements

- Python 3
- `mido`
- `numpy`
- `matplotlib`

Install the required packages:

```bash
pip install mido numpy matplotlib

Run the script with a midi file:
python midi\_tension.py melody.mid
## The graph appears on screen and is saved as tension_graph.png in the current folder.

Optional arguments
Set the analysis window length in beats:
python midi\_tension.py melody.mid --window 2

Set the distance between successive windows in beats:
python midi\_tension.py melody.mid --hop 0.125

Choose the output image filename:
python midi\_tension.py melody.mid --output my\_tension\_graph.png

Combine options like this:
python midi\_tension.py melody.mid --window 2 --hop 0.125 --output tension.png

How it works
The script reads note-on events from MIDI tracks and converts their timing to beats. It moves a window across the melody and measures two kinds of variety within each window:

Pitch-class entropy: Variety among the 12 pitch classes. Notes an octave apart count as the same pitch class.
Interval entropy: Variety among the pitch differences between consecutive notes.
Both values are normalized to roughly 0–1. The plotted combined entropy is the average of the two:
combined entropy = 0.5 × pitch-class entropy + 0.5 × interval entropy

Interpreting the graph
The horizontal axis shows time in beats. The vertical axis shows normalized entropy, from 0 to 1.

Higher values indicate greater pitch or interval variety within a window; lower values indicate less variety. The graph also shows the pitch-class and interval entropy lines separately.

Entropy is only a proxy for musical tension. The script does not account for harmony, rhythm, dynamics, register, or listener expectations. A high value does not necessarily mean a passage will sound tense.

Limitations
The script analyzes note onsets across all MIDI tracks.
It does not separate instruments or identify which track contains the melody.
Sparse or empty windows may have low entropy values.
The default analysis window is 4 beats, with measurements every 0.25 beats.

