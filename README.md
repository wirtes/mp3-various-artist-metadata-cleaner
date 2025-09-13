# Audio Metadata Scanner

A Python script that recursively scans directories for audio files and reports directories where the "Album Artist" metadata is not set to "Various Artists".

## Features

- Recursively scans directory structures for audio files
- Supports multiple audio formats: MP3, FLAC, M4A, MP4, OGG, WAV, WMA, AAC
- Checks Album Artist metadata across different tag formats (ID3, Vorbis, MP4)
- Can update Album Artist metadata with missing values or force update all files
- Can set RELEASETYPE metadata for better music organization
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

# With RELEASETYPE metadata (also forces Album Artist)
python audio_scanner.py --force --release-type "compilation" /path/to/music/directory
python audio_scanner.py -f "Soundtrack" --release-type "soundtrack" /path/to/music/directory
```

In force mode, the script will:
- Update ALL audio files to set Album Artist to specified value (default: "Various Artists")
- Overwrites existing Album Artist values regardless of current content
- Optionally set RELEASETYPE metadata with `--release-type` flag
- Output the names of directories that were updated
- Accepts custom Album Artist value as parameter

### Release Type Only Mode
```bash
# Only set RELEASETYPE, don't change Album Artist
python audio_scanner.py --release-type "album;compilation" /path/to/music/directory
python audio_scanner.py -r "soundtrack" /path/to/music/directory
```

In release type only mode, the script will:
- Set RELEASETYPE metadata on ALL audio files
- Does NOT modify Album Artist values
- Useful for categorizing existing collections without changing artist information

Plex supported release-type values:
- `album;live` for live albums
- `album;compliation` for compilation albums

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

### Force Mode with RELEASETYPE
```
Force updating ALL files to set Album Artist to 'Various Artists' and RELEASETYPE to 'compilation'...
Force Updated: Mixed Collection
Force Updated: Best Of Albums
Force Updated: Greatest Hits
```

### Release Type Only Mode
```
Setting RELEASETYPE to 'compilation' on all files...
Release Type Updated: Mixed Collection
Release Type Updated: Best Of Albums
Release Type Updated: Greatest Hits
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
