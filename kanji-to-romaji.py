import os
import pickle
import re
import sys  # Import sys to access command-line arguments
from typing import List, Dict

import musicbrainzngs
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC


def find_latin_alias(
        alias_list: List[Dict[str, str]],
) -> str:
    latin_pattern = r'\u0041-\u005A\u0061-\u007A\u00C0-\u00FF'
    # Include space in the pattern
    pattern = f'^[{latin_pattern} ]+$'

    regex = re.compile(pattern)

    for entry in alias_list:
        alias = entry.get('alias', '')
        if regex.match(alias):
            return alias
    return None


# Function to initialize MusicBrainz API with email address
def initialize_musicbrainz(email_address):
    musicbrainzngs.set_useragent("Kanji-Romaji Finder", "1.0", email_address)


# Dictionary to store kanji-to-romaji translations
CACHE_FILE = 'transcription_cache.pkl'

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'rb') as f:
        transcription_cache = pickle.load(f)
else:
    transcription_cache = {}


# Function to check if a string contains only kanji
def contains_only_kanji(text):
    return all(char.isspace() or '\u4e00' <= char <= '\u9fff' for char in text)


# Function to get romaji transcription using MusicBrainz
def get_romaji_transcription(kanji_name):
    if kanji_name in transcription_cache:
        return transcription_cache[kanji_name]

    result = musicbrainzngs.search_artists(artist=kanji_name, limit=1, strict=True)
    if result['artist-list']:
        result = result['artist-list'][0]
        if result and result.get('alias-list', None):
            romaji_name = f"{find_latin_alias(result['alias-list'])} ({result['name']})"
            transcription_cache[kanji_name] = romaji_name
            return romaji_name
        else:
            romaji_name = result['sort-name'].split(', ')
            if len(romaji_name) == 2:
                romaji_name = f"{romaji_name[1]} {romaji_name[0]} ({result['name']})"
                transcription_cache[kanji_name] = romaji_name
                return romaji_name
    return None


# Function to update the tags of a file
def update_tags(file_path):
    audio = None
    if file_path.endswith('.mp3'):
        audio = EasyID3(file_path)
    elif file_path.endswith('.flac'):
        audio = FLAC(file_path)

    if audio is None:
        return

    romaji_name = None

    for tag in ['ARTIST', 'ALBUMARTIST']:
        if tag in audio:
            original_name = audio[tag][0]
            if contains_only_kanji(original_name):
                romaji_name = get_romaji_transcription(original_name)
                if romaji_name:
                    audio[tag] = romaji_name
                    print(f"Updated {tag} for {file_path}: {romaji_name}")
                else:
                    print(f"Could not find transcription for {original_name}")

    if romaji_name:
        audio.save()


def find_and_update_files(directory):
    for entry in os.scandir(directory):
        if entry.is_dir(follow_symlinks=False) and not entry.name == "data" and not entry.name.startswith('.@__thumb'):
            print(entry.path)
            find_and_update_files(entry.path)
        elif entry.is_file() and entry.name.endswith(('.mp3', '.flac')):
            update_tags(entry.path)


# Main function to accept command-line arguments
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <path> <email_address>")
        print("<email_address> use the email address you used to register to MusicBrainz")
        print("<path> the path to the music you want to process")
        sys.exit(1)

    path = sys.argv[1]
    email_address = sys.argv[2]

    initialize_musicbrainz(email_address)
    
    try:
        find_and_update_files(path)
    finally:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(transcription_cache, f)
