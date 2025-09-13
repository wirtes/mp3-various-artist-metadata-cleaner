# Audio Metadata Scanner

A Python script that recursively scans directories for audio files and reports directories where the "Album Artist" metadata is not set to "Various Artists".

## Features

- Recursively scans directory structures for audio files
- Supports multiple audio formats: MP3, FLAC, M4A, MP4, OGG, WAV, WMA, AAC
- Checks Album Artist metadata across different tag formats (ID3, Vorbis, MP4)
- Reports each directory only once
- Handles missing or malformed metadata gracefully

## Requirements

- Python 3.12+
- mutagen library for audio metadata reading

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Scan Mode (Default)
```bash
python audio_scanner.py /path/to/music/directory
```

The script will output lines in the format:
```
DirectoryName - AlbumArtistValue
```

For directories where Album Artist is not set, it will show:
```
DirectoryName - (not set)
```

### Update Mode
```bash
python audio_scanner.py --update /path/to/music/directory
# or
python audio_scanner.py -u /path/to/music/directory
```

In update mode, the script will:
- Find all audio files with missing or empty Album Artist metadata
- Update them to "Various Artists"
- Output the names of directories that were updated

### Force Mode
```bash
python audio_scanner.py --force /path/to/music/directory
# or
python audio_scanner.py -f /path/to/music/directory

# With custom value
python audio_scanner.py --force "Soundtrack" /path/to/music/directory
python audio_scanner.py -f "My Custom Artist" /path/to/music/directory
```

In force mode, the script will:
- Update ALL audio files to set Album Artist to specified value (default: "Various Artists")
- Overwrites existing Album Artist values regardless of current content
- Output the names of directories that were updated
- Accepts custom Album Artist value as parameter

## Example Output

### Scan Mode
```
Rock Collection - Led Zeppelin
Jazz Masters - Miles Davis
Compilation Album - (not set)
```

### Update Mode
```
Updating files with missing Album Artist metadata...
Updated: Compilation Album
Updated: Mixed Tracks
Updated: Unknown Artist Collection
```

### Force Mode
```
Force updating ALL files to set Album Artist to 'Various Artists'...
Force Updated: Rock Collection
Force Updated: Jazz Masters
Force Updated: Compilation Album
```

### Force Mode with Custom Value
```
Force updating ALL files to set Album Artist to 'Soundtrack'...
Force Updated: Movie Themes
Force Updated: Game Music
Force Updated: TV Shows
```

## How It Works

1. Recursively walks through the specified directory
2. Identifies audio files by extension
3. Reads metadata from the first audio file in each directory
4. If Album Artist ≠ "Various Artists", outputs the directory name and Album Artist value
5. Skips remaining files in that directory to avoid duplicates

## Supported Audio Formats

- MP3 (ID3v1/ID3v2 tags)
- FLAC (Vorbis comments)
- M4A/MP4 (iTunes-style tags)
- OGG (Vorbis comments)
- WAV, WMA, AAC