#!/usr/bin/env python3
"""
Audio metadata scanner that checks for Album Artist values.
Recursively scans directories for audio files and reports directories
where Album Artist is not set to "Various Artists".
"""

import os
import sys
from pathlib import Path
from mutagen import File
from mutagen.id3 import ID3NoHeaderError


def get_album_artist(file_path):
    """Extract Album Artist from audio file metadata."""
    try:
        audio_file = File(file_path)
        if audio_file is None:
            return None
        
        # Try different tag formats for Album Artist
        album_artist = None
        
        # ID3 tags (MP3)
        if hasattr(audio_file, 'get'):
            album_artist = audio_file.get('TPE2')  # Album Artist in ID3v2
            if album_artist:
                album_artist = str(album_artist[0]) if isinstance(album_artist, list) else str(album_artist)
        
        # Vorbis comments (FLAC, OGG)
        if not album_artist and hasattr(audio_file, 'get'):
            album_artist = audio_file.get('ALBUMARTIST')
            if album_artist:
                album_artist = album_artist[0] if isinstance(album_artist, list) else album_artist
        
        # MP4 tags (M4A, MP4)
        if not album_artist and hasattr(audio_file, 'get'):
            album_artist = audio_file.get('aART')
            if album_artist:
                album_artist = album_artist[0] if isinstance(album_artist, list) else album_artist
        
        return album_artist
        
    except (ID3NoHeaderError, Exception) as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None


def is_audio_file(file_path):
    """Check if file is an audio file based on extension."""
    audio_extensions = {'.mp3', '.flac', '.m4a', '.mp4', '.ogg', '.wav', '.wma', '.aac'}
    return file_path.suffix.lower() in audio_extensions


def scan_directory(root_path):
    """Scan directory structure for audio files and check metadata."""
    root_path = Path(root_path)
    processed_dirs = set()
    
    for file_path in root_path.rglob('*'):
        if not file_path.is_file() or not is_audio_file(file_path):
            continue
        
        parent_dir = file_path.parent
        
        # Skip if we've already processed this directory
        if parent_dir in processed_dirs:
            continue
        
        album_artist = get_album_artist(file_path)
        
        # Only output if Album Artist is not "Various Artists" or is missing
        if album_artist != "Various Artists":
            dir_name = parent_dir.name
            artist_value = album_artist if album_artist else "(not set)"
            print(f"{dir_name} - {artist_value}")
            processed_dirs.add(parent_dir)


def main():
    """Main function to handle command line arguments and run scanner."""
    if len(sys.argv) != 2:
        print("Usage: python audio_scanner.py <directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a directory.")
        sys.exit(1)
    
    try:
        scan_directory(directory_path)
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error during scan: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()