# Audio to MIDI Converter

A Python script that detects notes in audio files and converts them to MIDI format. Supports both **melodic instruments** (piano, guitar, vocals) and **drums/percussion**. Handles WAV, MP3, FLAC, OGG, and M4A audio formats.

## Features

- **Dual mode operation**:
  - **Melodic mode**: Pitch detection for singing, instruments, bass lines
  - **Drum mode**: Onset detection and drum type classification
- **Multi-format support**: Handles WAV, MP3, FLAC, OGG, and M4A files
- **Intelligent pitch detection**: Uses the pYIN algorithm for accurate note detection
- **Drum classification**: Automatically identifies kicks, snares, hi-hats, toms, and cymbals
- **Configurable parameters**: Adjust sensitivity, note duration, tempo, and more
- **MIDI instrument selection**: Choose from 128 General MIDI instruments
- **Easy-to-use CLI**: Simple command-line interface with sensible defaults
- **Debug mode**: Detailed analysis of detection process

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

### Drum Mode

Convert drum/percussion audio to MIDI:

```bash
python audio_to_midi.py drums.wav --drums
```

With debug to see drum classification:

```bash
python audio_to_midi.py drums.wav --drums --debug
```

Adjust sensitivity (minimum time between hits):

```bash
python audio_to_midi.py drums.wav --drums --min-onset-gap 0.02
```

**Detected drum types** (automatically classified):
- Kick (Bass Drum) → MIDI note 36
- Snare → MIDI note 38
- Closed Hi-Hat → MIDI note 42
- Open Hi-Hat → MIDI note 46
- Low/Mid/High Tom → MIDI notes 45, 47, 50
- Crash Cymbal → MIDI note 49
- Ride Cymbal → MIDI note 51

**Note**: Drum mode uses onset detection and spectral analysis to classify drum types. Works best with isolated drum tracks or simple drum patterns.

### Advanced Usage (Melodic Mode)

Enable verbose output for detailed information:

```bash
python audio_to_midi.py input.wav -v
```

**Debug mode** - See exactly what's being detected at each stage:

```bash
python audio_to_midi.py input.wav --debug
```

This will show:
- How many frames were analyzed
- Pitch detection statistics
- Frequency and MIDI note ranges detected
- Note duration statistics
- Helpful suggestions for parameter tuning

Adjust sensitivity for better note detection:

```bash
# Lower threshold for more sensitive detection
python audio_to_midi.py input.wav --voiced-threshold 0.3 --min-duration 0.05

# Higher threshold for less noise
python audio_to_midi.py input.wav --voiced-threshold 0.7 --min-duration 0.2
```

**For bass instruments** (bass guitar, cello, tuba, etc.):

```bash
# Bass needs longer hop length and lower min-duration
python audio_to_midi.py bass.wav --hop-length 2048 --min-duration 0.15 --instrument 32
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
  -d, --debug           Print debugging information (pitch detection analysis)
  --drums               Drum mode: detect and classify drum hits instead of pitched notes
  --min-onset-gap GAP   Minimum time between drum hits in seconds (drums mode only, default: 0.03)
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

**Melodic Mode:**
- **Polyphonic audio** (multiple simultaneous notes) will have mixed results
- **Background noise** can affect accuracy
- **Vibrato and pitch bends** may cause note fragmentation

**Drum Mode:**
- Works best with **isolated drum tracks** or simple patterns
- Complex polyphonic drum patterns may be misclassified
- Classification accuracy depends on recording quality and drum sound

## Examples

### Melodic Examples

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
python audio_to_midi.py bass.wav --hop-length 2048 --min-duration 0.15 --instrument 32 -o bass_midi.mid
```

### Drum Examples

Convert drum track with debug info:

```bash
python audio_to_midi.py drums.wav --drums --debug -v
```

Convert drum loop at 126 BPM:

```bash
python audio_to_midi.py drum_loop.wav --drums -t 126 -o drum_loop.mid
```

Adjust for fast hi-hat patterns:

```bash
python audio_to_midi.py drums.wav --drums --min-onset-gap 0.02
```

### General

Debug mode to troubleshoot detection issues:

```bash
python audio_to_midi.py problem.wav --debug
```

## Project Structure

```
w2m/
├── audio_to_midi.py       # Main CLI script
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── src/
    ├── audio_loader.py   # Audio file loading
    ├── pitch_detector.py # Pitch and note detection (melodic mode)
    ├── drum_detector.py  # Drum onset detection and classification (drum mode)
    └── midi_generator.py # MIDI file generation
```

## Troubleshooting

### No notes detected

**First, run with --debug flag to see what's happening:**

```bash
python audio_to_midi.py your-file.wav --debug
```

The debug output will tell you exactly why notes aren't being detected and suggest parameter adjustments.

**Common issues:**

1. **Min-duration too high** - Most musical notes are 0.1-0.5 seconds. If you set `--min-duration 2.0`, you'll only capture notes longer than 2 seconds!
   - Solution: Try `--min-duration 0.05` to `0.15`

2. **Voiced threshold too high** - Default is 0.5, which might miss quieter or less confident pitches
   - Solution: Try `--voiced-threshold 0.3` to `0.4`

3. **Bass instruments need special settings** - Low frequencies need longer analysis windows
   - Solution: Add `--hop-length 2048` for bass, cello, tuba, etc.

4. **Polyphonic audio** - Multiple notes playing at once don't work well
   - Solution: Extract individual instrument tracks first

### Too many spurious notes

Try adjusting the parameters:
- Increase `--voiced-threshold` (e.g., 0.7)
- Increase `--min-duration` (e.g., 0.2)

### MP3 files not loading

Install ffmpeg (see Installation section)

## Technical Details

### Melodic Mode
- **Pitch Detection**: pYIN (probabilistic YIN) algorithm via librosa
- **Note Extraction**: Continuous pitch tracking with voicing probability filtering
- **MIDI Channel**: 0-15 (configurable instrument)

### Drum Mode
- **Onset Detection**: Spectral flux-based onset detection via librosa
- **Feature Extraction**: Spectral centroid, rolloff, zero-crossing rate, RMS energy, low-frequency ratio
- **Classification**: Rule-based classifier using spectral features
- **MIDI Channel**: 9 (Channel 10 - General MIDI Percussion)
- **Detected Drums**: Kick, snare, closed/open hi-hat, toms, crash, ride

### General
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
