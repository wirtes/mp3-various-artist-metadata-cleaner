#!/usr/bin/env python3
"""
Audio metadata scanner that checks for Album Artist values.
Recursively scans directories for audio files and reports directories
where Album Artist is not set to "Various Artists".
Can optionally update missing Album Artist values to "Various Artists".
"""

import os
import sys
import argparse
from pathlib import Path
from mutagen import File
from mutagen.id3 import ID3NoHeaderError, TPE2, TXXX
from mutagen.flac import FLAC
from mutagen.mp4 import MP4


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


def set_album_artist(file_path, album_artist_value):
    """Set Album Artist metadata for an audio file."""
    try:
        audio_file = File(file_path)
        if audio_file is None:
            return False
        
        # Handle different file formats
        if file_path.suffix.lower() == '.mp3':
            # ID3 tags for MP3
            if not hasattr(audio_file, 'tags') or audio_file.tags is None:
                audio_file.add_tags()
            audio_file.tags['TPE2'] = TPE2(encoding=3, text=[album_artist_value])
            
        elif file_path.suffix.lower() in ['.flac', '.ogg']:
            # Vorbis comments for FLAC/OGG
            audio_file['ALBUMARTIST'] = album_artist_value
            
        elif file_path.suffix.lower() in ['.m4a', '.mp4']:
            # MP4 tags
            audio_file['aART'] = [album_artist_value]
            
        else:
            # Generic approach for other formats
            if hasattr(audio_file, '__setitem__'):
                audio_file['ALBUMARTIST'] = album_artist_value
        
        audio_file.save()
        return True
        
    except Exception as e:
        print(f"Error updating {file_path}: {e}", file=sys.stderr)
        return False


def set_release_type(file_path, release_type_value):
    """Set RELEASETYPE metadata for an audio file."""
    try:
        audio_file = File(file_path)
        if audio_file is None:
            return False
        
        # Handle different file formats
        if file_path.suffix.lower() == '.mp3':
            # ID3 tags for MP3 - use TXXX for custom fields
            if not hasattr(audio_file, 'tags') or audio_file.tags is None:
                audio_file.add_tags()
            audio_file.tags['TXXX:RELEASETYPE'] = TXXX(encoding=3, desc='RELEASETYPE', text=[release_type_value])
            
        elif file_path.suffix.lower() in ['.flac', '.ogg']:
            # Vorbis comments for FLAC/OGG
            audio_file['RELEASETYPE'] = release_type_value
            
        elif file_path.suffix.lower() in ['.m4a', '.mp4']:
            # MP4 tags - use freeform atom
            audio_file['----:com.apple.iTunes:RELEASETYPE'] = [release_type_value.encode('utf-8')]
            
        else:
            # Generic approach for other formats
            if hasattr(audio_file, '__setitem__'):
                audio_file['RELEASETYPE'] = release_type_value
        
        audio_file.save()
        return True
        
    except Exception as e:
        print(f"Error updating RELEASETYPE in {file_path}: {e}", file=sys.stderr)
        return False


def is_audio_file(file_path):
    """Check if file is an audio file based on extension."""
    audio_extensions = {'.mp3', '.flac', '.m4a', '.mp4', '.ogg', '.wav', '.wma', '.aac'}
    return file_path.suffix.lower() in audio_extensions


def scan_directory(root_path, update_mode=False, force_mode=False, force_value="Various Artists", release_type=None, release_type_only=False):
    """Scan directory structure for audio files and check metadata."""
    root_path = Path(root_path)
    processed_dirs = set()
    updated_dirs = set()
    
    for file_path in root_path.rglob('*'):
        if not file_path.is_file() or not is_audio_file(file_path):
            continue
        
        parent_dir = file_path.parent
        
        # In update or force mode, process files in directories
        if update_mode or force_mode or release_type_only:
            if parent_dir not in processed_dirs:
                dir_files = [f for f in parent_dir.iterdir() if f.is_file() and is_audio_file(f)]
                
                if release_type_only:
                    # Release type only mode: only set RELEASETYPE, don't touch Album Artist
                    updated_any = False
                    for audio_file in dir_files:
                        if set_release_type(audio_file, release_type):
                            updated_any = True
                    
                    if updated_any:
                        print(f"Release Type Updated: {parent_dir.name}")
                        updated_dirs.add(parent_dir)
                        
                elif force_mode:
                    # Force mode: update ALL files regardless of current Album Artist value
                    updated_any = False
                    for audio_file in dir_files:
                        success = set_album_artist(audio_file, force_value)
                        
                        # Also set RELEASETYPE if specified
                        if release_type and set_release_type(audio_file, release_type):
                            success = True
                        
                        if success:
                            updated_any = True
                    
                    if updated_any:
                        print(f"Force Updated: {parent_dir.name}")
                        updated_dirs.add(parent_dir)
                        
                elif update_mode:
                    # Update mode: only update files with missing Album Artist
                    needs_update = False
                    for audio_file in dir_files:
                        album_artist = get_album_artist(audio_file)
                        if album_artist is None or album_artist.strip() == "":
                            needs_update = True
                            break
                    
                    if needs_update:
                        # Update all files in this directory that have missing Album Artist
                        updated_any = False
                        for audio_file in dir_files:
                            album_artist = get_album_artist(audio_file)
                            if album_artist is None or album_artist.strip() == "":
                                if set_album_artist(audio_file, "Various Artists"):
                                    updated_any = True
                        
                        if updated_any:
                            print(f"Updated: {parent_dir.name}")
                            updated_dirs.add(parent_dir)
                
                processed_dirs.add(parent_dir)
        else:
            # Original scan mode - report directories with non-"Various Artists" values
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
    parser = argparse.ArgumentParser(
        description="Scan audio files for Album Artist metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audio_scanner.py /path/to/music                              # Scan and report
  python audio_scanner.py --update /path/to/music                     # Update missing Album Artist to "Various Artists"
  python audio_scanner.py --force /path/to/music                      # Force all Album Artist to "Various Artists"
  python audio_scanner.py --force "Soundtrack" /path/music            # Force all Album Artist to "Soundtrack"
  python audio_scanner.py --force --release-type "album;compilation" /path  # Force Album Artist + set RELEASETYPE
  python audio_scanner.py --release-type "compilation" /path          # Only set RELEASETYPE (no Album Artist change)
        """
    )
    
    parser.add_argument('directory', help='Directory path to scan for audio files')
    
    # Create mutually exclusive group for update modes
    update_group = parser.add_mutually_exclusive_group()
    update_group.add_argument('--update', '-u', action='store_true', 
                             help='Update files with missing Album Artist to "Various Artists"')
    update_group.add_argument('--force', '-f', metavar='VALUE', nargs='?', const='Various Artists',
                             help='Force update ALL files to set Album Artist (default: "Various Artists")')
    
    # RELEASETYPE flag (can work standalone or with --force)
    parser.add_argument('--release-type', '-r', metavar='TYPE',
                       help='Set RELEASETYPE metadata (can be used alone or with --force)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory.")
        sys.exit(1)
    
    try:
        force_value = "Various Artists"
        release_type_only = False
        
        if args.force:
            force_value = args.force
            message = f"Force updating ALL files to set Album Artist to '{force_value}'"
            if args.release_type:
                message += f" and RELEASETYPE to '{args.release_type}'"
            print(f"{message}...")
        elif args.release_type:
            # Release type only mode (no Album Artist changes)
            release_type_only = True
            print(f"Setting RELEASETYPE to '{args.release_type}' on all files...")
        elif args.update:
            print("Updating files with missing Album Artist metadata...")
        
        scan_directory(args.directory, update_mode=args.update, force_mode=bool(args.force), 
                      force_value=force_value, release_type=args.release_type, release_type_only=release_type_only)
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error during scan: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()