#!/usr/bin/env python3
"""Analyze a MIDI melody with sliding-window Shannon entropy."""

import argparse
from collections import Counter

import matplotlib.pyplot as plt
import mido
import numpy as np


def shannon_entropy(values):
    """Shannon entropy in bits; returns 0 for an empty collection."""
    if not values:
        return 0.0

    counts = np.array(list(Counter(values).values()), dtype=float)
    probabilities = counts / counts.sum()
    return float(-np.sum(probabilities * np.log2(probabilities)))


def read_note_onsets(path):
    """Return (beat, MIDI pitch) for each note-on event with nonzero velocity."""
    midi = mido.MidiFile(path)
    events = []

    # Merge tracks so their delta times are interpreted on one timeline.
    absolute_tick = 0
    for message in mido.merge_tracks(midi.tracks):
        absolute_tick += message.time
        if (
            message.type == "note_on"
            and message.velocity > 0
            and not message.is_meta
        ):
            beat = absolute_tick / midi.ticks_per_beat
            events.append((beat, message.note))

    events.sort()
    if not events:
        raise ValueError("No note-on events found in the MIDI file.")

    return events


def analyze(events, window_beats=4.0, hop_beats=0.25):
    """Compute normalized pitch-class and interval entropy at each window."""
    beats = np.array([beat for beat, _ in events])
    pitches = np.array([pitch for _, pitch in events])

    start = float(beats.min())
    end = float(beats.max())
    centers, pitch_entropy, interval_entropy = [], [], []

    center = start + window_beats / 2
    while center <= end + hop_beats:
        left = center - window_beats / 2
        right = center + window_beats / 2

        # Use note onsets inside the window.
        mask = (beats >= left) & (beats < right)
        window_pitches = pitches[mask]

        centers.append(center)

        # Pitch class has 12 possible values, so normalize by log2(12).
        pcs = [int(pitch % 12) for pitch in window_pitches]
        pitch_entropy.append(shannon_entropy(pcs) / np.log2(12))

        # Interval entropy uses the differences between consecutive pitches.
        intervals = np.diff(window_pitches).tolist()
        # MIDI melodic intervals range from -127 to +127: 255 possibilities.
        interval_entropy.append(
            shannon_entropy(intervals) / np.log2(255)
            if intervals else 0.0
        )

        center += hop_beats

    pitch_entropy = np.array(pitch_entropy)
    interval_entropy = np.array(interval_entropy)

    # Equal weighting; adjust these weights to suit your analysis.
    tension = 0.5 * pitch_entropy + 0.5 * interval_entropy

    return np.array(centers), pitch_entropy, interval_entropy, tension


def main():
    parser = argparse.ArgumentParser(
        description="Plot a MIDI melody's entropy-based tension curve."
    )
    parser.add_argument("midi_file", help="Path to a .mid or .midi file")
    parser.add_argument("--window", type=float, default=4.0,
                        help="Analysis window in beats (default: 4)")
    parser.add_argument("--hop", type=float, default=0.25,
                        help="Step between windows in beats (default: 0.25)")
    parser.add_argument("--output", default="tension_graph.png",
                        help="Output image filename")
    args = parser.parse_args()

    events = read_note_onsets(args.midi_file)
    centers, pitch_h, interval_h, tension = analyze(
        events, args.window, args.hop
    )

    plt.figure(figsize=(11, 5))
    plt.plot(centers, tension, label="Combined entropy tension", linewidth=2)
    plt.plot(centers, pitch_h, "--", alpha=0.7, label="Pitch-class entropy")
    plt.plot(centers, interval_h, "--", alpha=0.7, label="Interval entropy")
    plt.ylim(0, 1)
    plt.xlabel("Time (beats)")
    plt.ylabel("Normalized entropy (0–1)")
    plt.title("MIDI Melody: Entropy-Based Tension Graph")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output, dpi=160)
    print(f"Saved graph to {args.output}")
    plt.show()


if __name__ == "__main__":
    main()
