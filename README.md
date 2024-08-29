# music-tags-kanji-to-romaji
Add romaji transcription to kanji names of Japanese artists in music artist tags (FLAC, MP3)

I created a Python script to automatically go through all my music files and transcribe kanji-only artist names into romaji + kanji (e.g. "坂本龍一" -> "Ryuichi Sakamoto (坂本龍一)"). The script uses the MusicBrainz API and caches the results to avoid over-stressing their API. The search for a matching artist is strict enough that it should not give any false transcriptions, if it cannot find an artist it skips it.

## Requirements

- Python 3.12
- mutagen, musicbrainzngs
