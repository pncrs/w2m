#!/usr/bin/env python3
"""
Audio to MIDI Converter

Converts audio files (WAV, MP3, etc.) to MIDI files by detecting musical notes.
"""
import argparse
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from audio_loader import AudioLoader
from pitch_detector import PitchDetector
from midi_generator import MidiGenerator


def convert_audio_to_midi(
    input_file,
    output_file=None,
    sample_rate=22050,
    hop_length=512,
    min_note_duration=0.1,
    voiced_threshold=0.5,
    tempo=120,
    velocity=64,
    instrument=0,
    verbose=False,
    debug=False
):
    """
    Convert an audio file to MIDI.

    Args:
        input_file (str): Path to input audio file
        output_file (str): Path to output MIDI file (optional)
        sample_rate (int): Sample rate for audio processing
        hop_length (int): Hop length for pitch detection
        min_note_duration (float): Minimum note duration in seconds
        voiced_threshold (float): Minimum voicing probability (0-1)
        tempo (int): MIDI tempo in BPM
        velocity (int): Note velocity (0-127)
        instrument (int): MIDI instrument number (0-127)
        verbose (bool): Print detailed information
        debug (bool): Print debugging information

    Returns:
        str: Path to the created MIDI file
    """
    input_path = Path(input_file)

    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.with_suffix('.mid')
    else:
        output_file = Path(output_file)

    if verbose:
        print(f"Input file: {input_path}")
        print(f"Output file: {output_file}")
        print(f"Sample rate: {sample_rate} Hz")
        print(f"Minimum note duration: {min_note_duration} seconds")
        print(f"Voiced threshold: {voiced_threshold}")
        print(f"Tempo: {tempo} BPM")
        print()

    # Step 1: Load audio
    if verbose:
        print("Loading audio file...")
    loader = AudioLoader(sample_rate=sample_rate)
    try:
        audio_data, sr = loader.load(input_file)
        duration = loader.get_duration(audio_data, sr)
        if verbose:
            print(f"Audio loaded successfully (duration: {duration:.2f} seconds)")
            print()
    except Exception as e:
        print(f"Error loading audio: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Detect pitches and extract notes
    if verbose:
        print("Detecting notes...")
    detector = PitchDetector(
        sample_rate=sr,
        hop_length=hop_length
    )
    try:
        notes = detector.extract_notes(
            audio_data,
            min_note_duration=min_note_duration,
            voiced_threshold=voiced_threshold,
            debug=debug
        )
        if verbose and not debug:  # debug mode already prints detailed info
            print(f"Detected {len(notes)} notes")
            if notes:
                print(f"First note starts at {notes[0]['start_time']:.2f} seconds")
                print(f"Last note ends at {notes[-1]['end_time']:.2f} seconds")
            print()
    except Exception as e:
        print(f"Error detecting notes: {e}", file=sys.stderr)
        sys.exit(1)

    if not notes:
        if not debug:  # If not in debug mode, give simpler error message
            print("\nNo notes detected in the audio file!", file=sys.stderr)
            print("\nCommon issues and solutions:", file=sys.stderr)
            print(f"  1. Notes too short: Your --min-duration is {min_note_duration}s. Try a lower value like 0.05 or 0.1", file=sys.stderr)
            print(f"  2. Low confidence: Your --voiced-threshold is {voiced_threshold}. Try 0.3 for more sensitivity", file=sys.stderr)
            print(f"  3. For bass/low instruments: Add --hop-length 2048 for better low frequency detection", file=sys.stderr)
            print(f"\nRun with --debug flag to see detailed analysis", file=sys.stderr)
        sys.exit(1)

    # Step 3: Generate MIDI file
    if verbose:
        print("Generating MIDI file...")
    generator = MidiGenerator(tempo=tempo, velocity=velocity)
    try:
        output_path = generator.create_midi(notes, output_file, instrument=instrument)
        if verbose:
            instrument_name = generator.get_instrument_name(instrument)
            print(f"MIDI file created successfully: {output_path}")
            print(f"Instrument: {instrument_name}")
    except Exception as e:
        print(f"Error generating MIDI: {e}", file=sys.stderr)
        sys.exit(1)

    return str(output_path)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Convert audio files (WAV, MP3) to MIDI by detecting musical notes.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.wav
  %(prog)s input.mp3 -o output.mid
  %(prog)s input.wav --tempo 140 --instrument 24
  %(prog)s input.wav --min-duration 0.05 --voiced-threshold 0.3 -v

Instrument numbers (General MIDI):
  0  = Acoustic Grand Piano (default)
  24 = Acoustic Guitar (nylon)
  25 = Acoustic Guitar (steel)
  32 = Acoustic Bass
  40 = Violin
  73 = Flute
        """
    )

    parser.add_argument(
        'input_file',
        help='Input audio file (WAV, MP3, FLAC, OGG, M4A)'
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Output MIDI file (default: input filename with .mid extension)'
    )

    parser.add_argument(
        '-sr', '--sample-rate',
        type=int,
        default=22050,
        help='Sample rate for audio processing (default: 22050 Hz)'
    )

    parser.add_argument(
        '-hl', '--hop-length',
        type=int,
        default=512,
        help='Hop length for pitch detection (default: 512)'
    )

    parser.add_argument(
        '-md', '--min-duration',
        type=float,
        default=0.1,
        help='Minimum note duration in seconds (default: 0.1)'
    )

    parser.add_argument(
        '-vt', '--voiced-threshold',
        type=float,
        default=0.5,
        help='Voicing probability threshold 0-1 (default: 0.5)'
    )

    parser.add_argument(
        '-t', '--tempo',
        type=int,
        default=120,
        help='MIDI tempo in BPM (default: 120)'
    )

    parser.add_argument(
        '--velocity',
        type=int,
        default=64,
        help='Note velocity 0-127 (default: 64)'
    )

    parser.add_argument(
        '-i', '--instrument',
        type=int,
        default=0,
        help='MIDI instrument number 0-127 (default: 0 = Piano)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print detailed information during conversion'
    )

    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Print debugging information (pitch detection analysis)'
    )

    args = parser.parse_args()

    # Validate arguments
    if not Path(args.input_file).exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    if not 0 <= args.voiced_threshold <= 1:
        print("Error: Voiced threshold must be between 0 and 1", file=sys.stderr)
        sys.exit(1)

    if not 0 <= args.velocity <= 127:
        print("Error: Velocity must be between 0 and 127", file=sys.stderr)
        sys.exit(1)

    if not 0 <= args.instrument <= 127:
        print("Error: Instrument must be between 0 and 127", file=sys.stderr)
        sys.exit(1)

    # Convert audio to MIDI
    try:
        output_path = convert_audio_to_midi(
            input_file=args.input_file,
            output_file=args.output_file,
            sample_rate=args.sample_rate,
            hop_length=args.hop_length,
            min_note_duration=args.min_duration,
            voiced_threshold=args.voiced_threshold,
            tempo=args.tempo,
            velocity=args.velocity,
            instrument=args.instrument,
            verbose=args.verbose,
            debug=args.debug
        )
        if not args.verbose:
            print(f"MIDI file created: {output_path}")
    except KeyboardInterrupt:
        print("\nConversion interrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
