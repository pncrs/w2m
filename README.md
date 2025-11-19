# Audio to MIDI Converter

A Python script that detects notes in audio files and converts them to MIDI format. Supports WAV, MP3, FLAC, OGG, and M4A audio formats.

## Features

- **Multi-format support**: Handles WAV, MP3, FLAC, OGG, and M4A files
- **Intelligent pitch detection**: Uses the pYIN algorithm for accurate note detection
- **Configurable parameters**: Adjust sensitivity, note duration, tempo, and more
- **MIDI instrument selection**: Choose from 128 General MIDI instruments
- **Easy-to-use CLI**: Simple command-line interface with sensible defaults

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: For MP3 support, you may need to install ffmpeg:

- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

### Basic Usage

Convert an audio file to MIDI (output will be `input.mid`):

```bash
python audio_to_midi.py input.wav
```

Specify output filename:

```bash
python audio_to_midi.py input.mp3 -o output.mid
```

### Advanced Usage

Enable verbose output for detailed information:

```bash
python audio_to_midi.py input.wav -v
```

Adjust sensitivity for better note detection:

```bash
# Lower threshold for more sensitive detection
python audio_to_midi.py input.wav --voiced-threshold 0.3 --min-duration 0.05

# Higher threshold for less noise
python audio_to_midi.py input.wav --voiced-threshold 0.7 --min-duration 0.2
```

Set tempo and instrument:

```bash
# Guitar with 140 BPM tempo
python audio_to_midi.py input.wav --tempo 140 --instrument 24
```

### Command-Line Options

```
positional arguments:
  input_file            Input audio file (WAV, MP3, FLAC, OGG, M4A)

optional arguments:
  -h, --help            Show help message and exit
  -o, --output OUTPUT   Output MIDI file (default: input filename with .mid extension)
  -sr, --sample-rate SR Sample rate for audio processing (default: 22050 Hz)
  -hl, --hop-length HL  Hop length for pitch detection (default: 512)
  -md, --min-duration MD
                        Minimum note duration in seconds (default: 0.1)
  -vt, --voiced-threshold VT
                        Voicing probability threshold 0-1 (default: 0.5)
  -t, --tempo TEMPO     MIDI tempo in BPM (default: 120)
  --velocity VELOCITY   Note velocity 0-127 (default: 64)
  -i, --instrument INST MIDI instrument number 0-127 (default: 0 = Piano)
  -v, --verbose         Print detailed information during conversion
```

### MIDI Instruments

Some common General MIDI instrument numbers:

- `0` - Acoustic Grand Piano (default)
- `24` - Acoustic Guitar (nylon)
- `25` - Acoustic Guitar (steel)
- `32` - Acoustic Bass
- `40` - Violin
- `42` - Cello
- `73` - Flute
- `80` - Lead (square synth)

See the [General MIDI specification](https://en.wikipedia.org/wiki/General_MIDI) for a complete list.

## How It Works

1. **Audio Loading**: The audio file is loaded and converted to mono at the specified sample rate
2. **Pitch Detection**: The pYIN algorithm analyzes the audio to detect fundamental frequencies
3. **Note Extraction**: Detected pitches are converted to MIDI note numbers and grouped into discrete notes
4. **MIDI Generation**: Notes are written to a MIDI file with the specified tempo and instrument

## Tips for Best Results

### For Monophonic Instruments

This tool works best with **monophonic** audio (single notes at a time):
- Vocals
- Solo instruments (flute, trumpet, etc.)
- Bass lines
- Melodies

### Parameter Tuning

- **Low-pitched instruments** (bass, cello): Increase `--hop-length` to 1024 or 2048
- **Fast passages**: Decrease `--min-duration` to 0.05
- **Noisy recordings**: Increase `--voiced-threshold` to 0.6 or 0.7
- **Clean recordings**: Decrease `--voiced-threshold` to 0.3 or 0.4

### Limitations

- **Polyphonic audio** (multiple simultaneous notes) will have mixed results
- **Percussion and drums** are not suitable for pitch detection
- **Background noise** can affect accuracy
- **Vibrato and pitch bends** may cause note fragmentation

## Examples

Convert a piano recording:

```bash
python audio_to_midi.py piano_solo.wav --tempo 90 -v
```

Convert a vocal track with sensitive detection:

```bash
python audio_to_midi.py vocals.mp3 --voiced-threshold 0.4 --min-duration 0.08 --instrument 73
```

Convert a bass line:

```bash
python audio_to_midi.py bass.wav --hop-length 2048 --instrument 32 -o bass_midi.mid
```

## Project Structure

```
w2m/
├── audio_to_midi.py       # Main CLI script
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── src/
    ├── audio_loader.py   # Audio file loading
    ├── pitch_detector.py # Pitch and note detection
    └── midi_generator.py # MIDI file generation
```

## Troubleshooting

### No notes detected

Try adjusting the parameters:
- Lower `--voiced-threshold` (e.g., 0.3)
- Lower `--min-duration` (e.g., 0.05)
- Check if the audio is monophonic

### Too many spurious notes

Try adjusting the parameters:
- Increase `--voiced-threshold` (e.g., 0.7)
- Increase `--min-duration` (e.g., 0.2)

### MP3 files not loading

Install ffmpeg (see Installation section)

## Technical Details

- **Pitch Detection**: pYIN (probabilistic YIN) algorithm via librosa
- **Sample Rate**: Default 22050 Hz (configurable)
- **Hop Length**: Default 512 samples (~23ms at 22050 Hz)
- **MIDI Format**: Standard MIDI File format (.mid)

## License

This project is provided as-is for educational and personal use.

## Contributing

Contributions, issues, and feature requests are welcome!

## Acknowledgments

- [librosa](https://librosa.org/) - Audio analysis library
- [mido](https://mido.readthedocs.io/) - MIDI file handling
- pYIN algorithm for pitch detection
