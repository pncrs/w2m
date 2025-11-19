"""
Drum detection module for detecting drum hits and classifying drum types.
"""
import librosa
import numpy as np
from scipy.stats import mode


class DrumDetector:
    """Detects drum onsets and classifies drum types from audio."""

    # General MIDI Drum Map (Channel 10)
    DRUM_MAP = {
        'kick': 36,      # Bass Drum 1
        'snare': 38,     # Acoustic Snare
        'closed_hh': 42, # Closed Hi-Hat
        'open_hh': 46,   # Open Hi-Hat
        'low_tom': 45,   # Low Tom
        'mid_tom': 47,   # Mid Tom
        'high_tom': 50,  # High Tom
        'crash': 49,     # Crash Cymbal 1
        'ride': 51,      # Ride Cymbal 1
    }

    def __init__(self, sample_rate=22050, hop_length=512):
        """
        Initialize the drum detector.

        Args:
            sample_rate (int): Sample rate of the audio
            hop_length (int): Number of samples between successive frames
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length

    def detect_onsets(self, audio_data):
        """
        Detect drum hit onsets in the audio.

        Args:
            audio_data (np.ndarray): Audio time series

        Returns:
            np.ndarray: Array of onset times in seconds
        """
        # Detect onsets using spectral flux
        onset_frames = librosa.onset.onset_detect(
            y=audio_data,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            backtrack=False,
            units='frames'
        )

        # Convert frames to time
        onset_times = librosa.frames_to_time(
            onset_frames,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )

        return onset_times

    def extract_drum_features(self, audio_data, onset_time, window_size=0.05):
        """
        Extract spectral features around a drum onset.

        Args:
            audio_data (np.ndarray): Audio time series
            onset_time (float): Onset time in seconds
            window_size (float): Analysis window size in seconds

        Returns:
            dict: Dictionary of features
        """
        # Get samples around onset
        onset_sample = int(onset_time * self.sample_rate)
        window_samples = int(window_size * self.sample_rate)

        start = max(0, onset_sample)
        end = min(len(audio_data), onset_sample + window_samples)

        segment = audio_data[start:end]

        if len(segment) < self.hop_length:
            return None

        # Extract features
        features = {}

        # Spectral centroid (brightness - high for cymbals/hats, low for kicks)
        centroid = librosa.feature.spectral_centroid(
            y=segment,
            sr=self.sample_rate,
            hop_length=len(segment)
        )
        features['spectral_centroid'] = np.mean(centroid)

        # Spectral rolloff (frequency content)
        rolloff = librosa.feature.spectral_rolloff(
            y=segment,
            sr=self.sample_rate,
            hop_length=len(segment)
        )
        features['spectral_rolloff'] = np.mean(rolloff)

        # Zero crossing rate (noisiness - high for snares/hats)
        zcr = librosa.feature.zero_crossing_rate(segment)
        features['zero_crossing_rate'] = np.mean(zcr)

        # RMS energy (loudness)
        rms = librosa.feature.rms(y=segment)
        features['rms_energy'] = np.mean(rms)

        # Low frequency energy ratio (kicks have high low-freq energy)
        # Compute STFT
        stft = np.abs(librosa.stft(segment, hop_length=len(segment)))
        freqs = librosa.fft_frequencies(sr=self.sample_rate)

        # Energy below 200 Hz vs total energy
        low_freq_mask = freqs < 200
        low_energy = np.sum(stft[low_freq_mask, :])
        total_energy = np.sum(stft)

        features['low_freq_ratio'] = low_energy / (total_energy + 1e-10)

        return features

    def classify_drum_type(self, features, debug=False):
        """
        Classify drum type based on spectral features using rule-based approach.

        Args:
            features (dict): Dictionary of extracted features
            debug (bool): Print classification reasoning

        Returns:
            str: Drum type ('kick', 'snare', 'closed_hh', 'open_hh', 'tom', 'crash', 'ride')
        """
        if features is None:
            return 'unknown'

        centroid = features['spectral_centroid']
        zcr = features['zero_crossing_rate']
        low_freq_ratio = features['low_freq_ratio']
        rms = features['rms_energy']

        # Normalize spectral centroid to 0-1 range (typical range: 0-11025 Hz)
        centroid_norm = centroid / (self.sample_rate / 2)

        if debug:
            print(f"  Centroid: {centroid:.1f} Hz (norm: {centroid_norm:.3f})")
            print(f"  ZCR: {zcr:.4f}")
            print(f"  Low freq ratio: {low_freq_ratio:.3f}")
            print(f"  RMS: {rms:.4f}")

        # Rule-based classification
        # Kick: Very low centroid, high low-freq energy
        if low_freq_ratio > 0.5 and centroid_norm < 0.15:
            return 'kick'

        # Hi-hat (closed or open): High centroid, high ZCR (noisy)
        elif centroid_norm > 0.3 and zcr > 0.1:
            # Open hi-hat has slightly lower centroid and more energy
            if centroid_norm < 0.5 and rms > 0.05:
                return 'open_hh'
            else:
                return 'closed_hh'

        # Crash cymbal: Very high centroid, high ZCR, high energy
        elif centroid_norm > 0.4 and zcr > 0.15 and rms > 0.08:
            return 'crash'

        # Ride cymbal: High centroid, moderate ZCR
        elif centroid_norm > 0.35 and zcr > 0.08:
            return 'ride'

        # Snare: Mid centroid, high ZCR (noisy), low-mid low-freq energy
        elif centroid_norm > 0.15 and centroid_norm < 0.35 and zcr > 0.08:
            return 'snare'

        # Tom: Mid-low centroid, low ZCR, moderate low-freq energy
        elif centroid_norm > 0.1 and centroid_norm < 0.3 and low_freq_ratio > 0.2:
            # Could differentiate between low/mid/high tom based on centroid
            if centroid_norm < 0.15:
                return 'low_tom'
            elif centroid_norm < 0.22:
                return 'mid_tom'
            else:
                return 'high_tom'

        # Default to snare if unsure
        else:
            return 'snare'

    def detect_drums(self, audio_data, min_onset_gap=0.03, debug=False):
        """
        Detect and classify drum hits in audio.

        Args:
            audio_data (np.ndarray): Audio time series
            min_onset_gap (float): Minimum time between onsets in seconds
            debug (bool): Print debug information

        Returns:
            list: List of dictionaries with drum hit information:
                - time: Onset time in seconds
                - drum_type: Classified drum type
                - midi_note: MIDI note number
                - velocity: Velocity (based on energy)
        """
        # Detect onsets
        onset_times = self.detect_onsets(audio_data)

        if debug:
            print(f"\n=== Drum Detection Debug Info ===")
            print(f"Total onsets detected: {len(onset_times)}")

        # Filter out onsets that are too close together
        filtered_onsets = []
        if len(onset_times) > 0:
            filtered_onsets.append(onset_times[0])
            for onset in onset_times[1:]:
                if onset - filtered_onsets[-1] >= min_onset_gap:
                    filtered_onsets.append(onset)

        if debug:
            print(f"Onsets after filtering (min gap {min_onset_gap}s): {len(filtered_onsets)}")
            print()

        # Classify each onset
        drum_hits = []
        drum_type_counts = {}

        for i, onset_time in enumerate(filtered_onsets):
            # Extract features
            features = self.extract_drum_features(audio_data, onset_time)

            if features is None:
                continue

            # Classify drum type
            if debug and i < 10:  # Only show first 10 for brevity
                print(f"Onset {i+1} at {onset_time:.3f}s:")

            drum_type = self.classify_drum_type(features, debug=(debug and i < 10))

            if debug and i < 10:
                print(f"  → Classified as: {drum_type}")
                print()

            # Get MIDI note
            midi_note = self.DRUM_MAP.get(drum_type, 38)  # Default to snare

            # Calculate velocity based on RMS energy (0-127)
            velocity = min(127, max(20, int(features['rms_energy'] * 1000)))

            drum_hits.append({
                'time': onset_time,
                'drum_type': drum_type,
                'midi_note': midi_note,
                'velocity': velocity
            })

            # Track drum type counts
            drum_type_counts[drum_type] = drum_type_counts.get(drum_type, 0) + 1

        if debug:
            print(f"\n=== Drum Classification Summary ===")
            print(f"Total drum hits detected: {len(drum_hits)}")
            print(f"\nBreakdown by drum type:")
            for drum_type, count in sorted(drum_type_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {drum_type:12s}: {count:3d} hits ({100*count/len(drum_hits):.1f}%)")

        return drum_hits
