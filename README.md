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

## Example Output

```
Rock Collection - Led Zeppelin
Jazz Masters - Miles Davis
Compilation Album - (not set)
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