"""
Pitch detection module for detecting musical notes from audio.
"""
import librosa
import numpy as np


class PitchDetector:
    """Detects pitches and converts them to MIDI notes."""

    def __init__(self, sample_rate=22050, hop_length=512, fmin=None, fmax=None):
        """
        Initialize the pitch detector.

        Args:
            sample_rate (int): Sample rate of the audio
            hop_length (int): Number of samples between successive frames
            fmin (float): Minimum frequency to detect (Hz). Default: C2 (~65 Hz)
            fmax (float): Maximum frequency to detect (Hz). Default: C7 (~2093 Hz)
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.fmin = fmin or librosa.note_to_hz('C2')
        self.fmax = fmax or librosa.note_to_hz('C7')

    def detect_pitches(self, audio_data):
        """
        Detect pitches in the audio using the pYIN algorithm.

        Args:
            audio_data (np.ndarray): Audio time series

        Returns:
            tuple: (pitches, voiced_flags, voiced_probabilities) where:
                - pitches: Array of detected frequencies in Hz
                - voiced_flags: Boolean array indicating voiced frames
                - voiced_probabilities: Array of voicing probabilities
        """
        # Use pYIN for pitch detection (better for music)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio_data,
            fmin=self.fmin,
            fmax=self.fmax,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            fill_na=None  # Keep NaN for unvoiced frames
        )

        return f0, voiced_flag, voiced_probs

    def detect_onset_frames(self, audio_data):
        """
        Detect note onset frames in the audio.

        Args:
            audio_data (np.ndarray): Audio time series

        Returns:
            np.ndarray: Array of frame indices where onsets occur
        """
        onset_frames = librosa.onset.onset_detect(
            y=audio_data,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            backtrack=True
        )
        return onset_frames

    def hz_to_midi(self, frequencies):
        """
        Convert frequencies in Hz to MIDI note numbers.

        Args:
            frequencies (np.ndarray): Array of frequencies in Hz

        Returns:
            np.ndarray: Array of MIDI note numbers (integers)
        """
        # MIDI note number = 69 + 12 * log2(f / 440)
        # Handle NaN values
        midi_notes = np.full_like(frequencies, np.nan)
        valid_mask = ~np.isnan(frequencies)

        if np.any(valid_mask):
            midi_notes[valid_mask] = librosa.hz_to_midi(frequencies[valid_mask])
            # Round to nearest integer MIDI note
            midi_notes[valid_mask] = np.round(midi_notes[valid_mask])

        return midi_notes

    def frames_to_time(self, frames):
        """
        Convert frame indices to time in seconds.

        Args:
            frames (np.ndarray): Array of frame indices

        Returns:
            np.ndarray: Array of times in seconds
        """
        return librosa.frames_to_time(
            frames,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )

    def extract_notes(self, audio_data, min_note_duration=0.1, voiced_threshold=0.5):
        """
        Extract notes from audio data with onset detection and pitch tracking.

        Args:
            audio_data (np.ndarray): Audio time series
            min_note_duration (float): Minimum duration for a note in seconds
            voiced_threshold (float): Minimum voicing probability (0-1)

        Returns:
            list: List of dictionaries with note information:
                - midi_note: MIDI note number
                - start_time: Note start time in seconds
                - end_time: Note end time in seconds
                - duration: Note duration in seconds
        """
        # Detect pitches
        f0, voiced_flag, voiced_probs = self.detect_pitches(audio_data)

        # Convert to MIDI notes
        midi_notes = self.hz_to_midi(f0)

        # Create a mask for valid notes (voiced and not NaN)
        valid_mask = (
            ~np.isnan(midi_notes) &
            (voiced_probs >= voiced_threshold)
        )

        # Extract note segments
        notes = []
        current_note = None
        current_start = None

        for i in range(len(midi_notes)):
            time = self.frames_to_time(np.array([i]))[0]

            if valid_mask[i]:
                note = int(midi_notes[i])

                if current_note is None:
                    # Start new note
                    current_note = note
                    current_start = time
                elif note != current_note:
                    # Note changed, save previous note
                    duration = time - current_start
                    if duration >= min_note_duration:
                        notes.append({
                            'midi_note': current_note,
                            'start_time': current_start,
                            'end_time': time,
                            'duration': duration
                        })
                    # Start new note
                    current_note = note
                    current_start = time
            else:
                # No valid note, save previous if exists
                if current_note is not None:
                    duration = time - current_start
                    if duration >= min_note_duration:
                        notes.append({
                            'midi_note': current_note,
                            'start_time': current_start,
                            'end_time': time,
                            'duration': duration
                        })
                    current_note = None
                    current_start = None

        # Handle the last note
        if current_note is not None:
            time = self.frames_to_time(np.array([len(midi_notes) - 1]))[0]
            duration = time - current_start
            if duration >= min_note_duration:
                notes.append({
                    'midi_note': current_note,
                    'start_time': current_start,
                    'end_time': time,
                    'duration': duration
                })

        return notes
