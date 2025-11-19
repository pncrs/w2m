"""
MIDI file generation module.
"""
import mido
from pathlib import Path


class MidiGenerator:
    """Generates MIDI files from detected notes."""

    def __init__(self, tempo=120, velocity=64):
        """
        Initialize the MIDI generator.

        Args:
            tempo (int): Tempo in beats per minute (BPM)
            velocity (int): Note velocity (0-127, default: 64)
        """
        self.tempo = tempo
        self.velocity = velocity

    def create_midi(self, notes, output_path, instrument=0):
        """
        Create a MIDI file from a list of notes.

        Args:
            notes (list): List of note dictionaries with:
                - midi_note: MIDI note number (0-127)
                - start_time: Start time in seconds
                - duration: Duration in seconds
            output_path (str): Path to save the MIDI file
            instrument (int): MIDI instrument/program number (0-127, default: 0 = Piano)

        Returns:
            str: Path to the created MIDI file
        """
        # Create a new MIDI file
        midi_file = mido.MidiFile()
        track = mido.MidiTrack()
        midi_file.tracks.append(track)

        # Set tempo
        microseconds_per_beat = mido.bpm2tempo(self.tempo)
        track.append(mido.MetaMessage('set_tempo', tempo=microseconds_per_beat))

        # Set instrument (program change)
        track.append(mido.Message('program_change', program=instrument, time=0))

        # Convert notes to MIDI messages
        # We need to sort notes by start time and create note_on/note_off events
        events = []

        for note in notes:
            # Ensure MIDI note is in valid range
            midi_note = int(note['midi_note'])
            if not 0 <= midi_note <= 127:
                continue  # Skip invalid notes

            start_time = note['start_time']
            duration = note['duration']
            end_time = start_time + duration

            # Add note on event
            events.append({
                'time': start_time,
                'type': 'note_on',
                'note': midi_note,
                'velocity': self.velocity
            })

            # Add note off event
            events.append({
                'time': end_time,
                'type': 'note_off',
                'note': midi_note,
                'velocity': 0
            })

        # Sort events by time
        events.sort(key=lambda x: x['time'])

        # Convert events to MIDI messages with delta times
        current_time = 0.0
        for event in events:
            # Calculate delta time in ticks
            # MIDI time is in ticks, we need to convert from seconds
            delta_time = event['time'] - current_time
            delta_ticks = int(mido.second2tick(delta_time, midi_file.ticks_per_beat, microseconds_per_beat))

            if event['type'] == 'note_on':
                track.append(mido.Message(
                    'note_on',
                    note=event['note'],
                    velocity=event['velocity'],
                    time=delta_ticks
                ))
            else:  # note_off
                track.append(mido.Message(
                    'note_off',
                    note=event['note'],
                    velocity=event['velocity'],
                    time=delta_ticks
                ))

            current_time = event['time']

        # Save the MIDI file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        midi_file.save(str(output_path))

        return str(output_path)

    def get_instrument_name(self, program_number):
        """
        Get the name of a MIDI instrument by program number.

        Args:
            program_number (int): MIDI program number (0-127)

        Returns:
            str: Instrument name
        """
        # General MIDI instrument names (simplified)
        instruments = {
            0: 'Acoustic Grand Piano',
            1: 'Bright Acoustic Piano',
            24: 'Acoustic Guitar (nylon)',
            25: 'Acoustic Guitar (steel)',
            32: 'Acoustic Bass',
            40: 'Violin',
            42: 'Cello',
            73: 'Flute',
            80: 'Lead (square)',
        }
        return instruments.get(program_number, f'Instrument {program_number}')
