import random
from typing import Dict, List, Optional, Tuple

Song = Dict[str, object]
PlaylistMap = Dict[str, List[Song]]

DEFAULT_PROFILE = {
    "name": "Default",
    "hype_min_energy": 7,
    "chill_max_energy": 3,
    "favorite_genre": "rock",
    "include_mixed": True,
}


def normalize_title(title: str) -> str:
    """Normalize a song title — strip whitespace and title-case."""
    if not isinstance(title, str):
        return ""
    return title.strip().title()


def normalize_artist(artist: str) -> str:
    """Normalize an artist name — strip whitespace and title-case each word.

    Preserves special tokens like 'ft.' and all-caps names (e.g. AC/DC).
    """
    if not artist or not isinstance(artist, str):
        return ""
    artist = artist.strip()
    if not artist:
        return ""
    # Split on spaces, title-case each part, but keep all-caps tokens as-is
    parts = []
    for part in artist.split():
        if part.isupper() and len(part) > 1:
            # Keep tokens like "AC/DC", "M83", "DJ" unchanged
            parts.append(part)
        elif part.lower() in ("ft.", "ft", "feat.", "feat", "vs.", "vs"):
            # Keep connector words lowercase
            parts.append(part.lower())
        else:
            parts.append(part.capitalize())
    return " ".join(parts)


def normalize_genre(genre: str) -> str:
    """Normalize a genre name to lowercase."""
    if not isinstance(genre, str):
        return ""
    return genre.lower().strip()


def normalize_song(raw: Song) -> Song:
    """Return a normalized song dict with expected keys."""
    title = normalize_title(str(raw.get("title", "")))
    artist = normalize_artist(str(raw.get("artist", "")))
    genre = normalize_genre(str(raw.get("genre", "")))
    energy = raw.get("energy", 0)

    if isinstance(energy, str):
        try:
            energy = int(energy)
        except ValueError:
            energy = 0

    # Clamp energy to valid range 1-10
    if isinstance(energy, (int, float)):
        energy = max(1, min(10, int(energy)))
    else:
        energy = 1

    tags = raw.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    elif isinstance(tags, list):
        tags = [str(t).strip() for t in tags if str(t).strip()]
    else:
        tags = []

    return {
        "title": title,
        "artist": artist,
        "genre": genre,
        "energy": energy,
        "tags": tags,
    }


def classify_song(song: Song, profile: Dict[str, object]) -> str:
    """Return a mood label given a song and user profile.

    Classification uses energy thresholds as the primary signal,
    genre keywords as a secondary signal, and favorite genre as a bonus
    that only applies when energy is already moderate-to-high.
    """
    energy = song.get("energy", 0)
    genre = song.get("genre", "")

    hype_min_energy = profile.get("hype_min_energy", 7)
    chill_max_energy = profile.get("chill_max_energy", 3)
    favorite_genre = profile.get("favorite_genre", "")

    hype_keywords = ["rock", "punk", "party"]
    chill_keywords = ["lofi", "ambient", "sleep"]

    is_hype_keyword = any(k in genre for k in hype_keywords)
    is_chill_keyword = any(k in genre for k in chill_keywords)

    # Energy-based classification takes priority
    if energy >= hype_min_energy:
        return "Hype"
    if energy <= chill_max_energy:
        return "Chill"

    # Genre keyword classification for the middle energy range
    if is_hype_keyword:
        return "Hype"
    if is_chill_keyword:
        return "Chill"

    # Favorite genre gives a hype boost only for mid-to-high energy songs
    if genre == favorite_genre and energy > chill_max_energy:
        return "Hype"

    return "Mixed"


def is_duplicate(existing_songs: List[Song], new_song: Song) -> bool:
    """Check if a song already exists by matching title + artist (case-insensitive)."""
    new_title = str(new_song.get("title", "")).lower().strip()
    new_artist = str(new_song.get("artist", "")).lower().strip()
    for song in existing_songs:
        if (str(song.get("title", "")).lower().strip() == new_title
                and str(song.get("artist", "")).lower().strip() == new_artist):
            return True
    return False


def build_playlists(songs: List[Song], profile: Dict[str, object]) -> PlaylistMap:
    """Group songs into playlists based on mood and profile."""
    playlists: PlaylistMap = {
        "Hype": [],
        "Chill": [],
        "Mixed": [],
    }

    for song in songs:
        normalized = normalize_song(song)
        mood = classify_song(normalized, profile)
        normalized["mood"] = mood
        playlists[mood].append(normalized)

    return playlists


def merge_playlists(a: PlaylistMap, b: PlaylistMap) -> PlaylistMap:
    """Merge two playlist maps into a new map without mutating the originals."""
    merged: PlaylistMap = {}
    for key in set(list(a.keys()) + list(b.keys())):
        # Copy both lists to avoid mutating the originals
        merged[key] = list(a.get(key, [])) + list(b.get(key, []))
    return merged


def compute_playlist_stats(playlists: PlaylistMap) -> Dict[str, object]:
    """Compute statistics across all playlists."""
    all_songs: List[Song] = []
    for songs in playlists.values():
        all_songs.extend(songs)

    hype = playlists.get("Hype", [])
    chill = playlists.get("Chill", [])
    mixed = playlists.get("Mixed", [])

    # Use total of all songs for ratio and average calculations
    total = len(all_songs)
    hype_ratio = len(hype) / total if total > 0 else 0.0

    avg_energy = 0.0
    if all_songs:
        # Sum energy across ALL songs, not just hype
        total_energy = sum(song.get("energy", 0) for song in all_songs)
        avg_energy = total_energy / total

    top_artist, top_count = most_common_artist(all_songs)

    return {
        "total_songs": total,
        "hype_count": len(hype),
        "chill_count": len(chill),
        "mixed_count": len(mixed),
        "hype_ratio": hype_ratio,
        "avg_energy": avg_energy,
        "top_artist": top_artist,
        "top_artist_count": top_count,
    }


def most_common_artist(songs: List[Song]) -> Tuple[str, int]:
    """Return the most common artist and count."""
    counts: Dict[str, int] = {}
    for song in songs:
        artist = str(song.get("artist", "")).strip()
        if not artist:
            continue
        counts[artist] = counts.get(artist, 0) + 1

    if not counts:
        return "", 0

    items = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    return items[0]


def search_songs(
    songs: List[Song],
    query: str,
    field: str = "artist",
) -> List[Song]:
    """Return songs where the query is a substring of the field value."""
    if not query or not query.strip():
        return songs

    q = query.lower().strip()
    filtered: List[Song] = []

    for song in songs:
        value = str(song.get(field, "")).lower()
        # Check if query is contained in the field value (not the reverse)
        if value and q in value:
            filtered.append(song)

    return filtered


def lucky_pick(
    playlists: PlaylistMap,
    mode: str = "any",
) -> Optional[Song]:
    """Pick a random song from the playlists according to mode.

    mode='any' includes all playlists (Hype + Chill + Mixed).
    """
    if mode == "hype":
        songs = playlists.get("Hype", [])
    elif mode == "chill":
        songs = playlists.get("Chill", [])
    else:
        # 'any' mode includes ALL playlists, including Mixed
        songs = (
            playlists.get("Hype", [])
            + playlists.get("Chill", [])
            + playlists.get("Mixed", [])
        )

    return random_choice_or_none(songs)


def random_choice_or_none(songs: List[Song]) -> Optional[Song]:
    """Return a random song or None if the list is empty."""
    if not songs:
        return None
    return random.choice(songs)


def history_summary(history: List[Song]) -> Dict[str, int]:
    """Return a summary of moods seen in the history."""
    counts = {"Hype": 0, "Chill": 0, "Mixed": 0}
    for song in history:
        mood = song.get("mood", "Mixed")
        if mood not in counts:
            counts["Mixed"] += 1
        else:
            counts[mood] += 1
    return counts
