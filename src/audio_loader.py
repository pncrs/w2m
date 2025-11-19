"""
Audio loader module for loading WAV and MP3 files.
"""
import librosa
import numpy as np
from pathlib import Path


class AudioLoader:
    """Handles loading and preprocessing of audio files."""

    def __init__(self, sample_rate=22050):
        """
        Initialize the audio loader.

        Args:
            sample_rate (int): Target sample rate for audio processing
        """
        self.sample_rate = sample_rate

    def load(self, file_path):
        """
        Load an audio file (WAV or MP3).

        Args:
            file_path (str): Path to the audio file

        Returns:
            tuple: (audio_data, sample_rate) where audio_data is a numpy array

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Check file extension
        valid_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        if file_path.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"Unsupported file format: {file_path.suffix}. "
                f"Supported formats: {', '.join(valid_extensions)}"
            )

        # Load audio using librosa
        try:
            audio_data, sr = librosa.load(
                str(file_path),
                sr=self.sample_rate,
                mono=True  # Convert to mono for pitch detection
            )
            return audio_data, sr
        except Exception as e:
            raise ValueError(f"Error loading audio file: {e}")

    def get_duration(self, audio_data, sample_rate):
        """
        Get the duration of the audio in seconds.

        Args:
            audio_data (np.ndarray): Audio data
            sample_rate (int): Sample rate

        Returns:
            float: Duration in seconds
        """
        return len(audio_data) / sample_rate
