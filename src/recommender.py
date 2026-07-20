from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.

    Design (see README "How The System Works"): a profile stores basic user
    info plus the user's *average taste* across the three numeric audio
    features we use for recommending. Songs the user plays repeatedly are
    tracked separately so they can count more when we build that average.
    """
    # --- basic user info ---
    name: str = "Guest"

    # --- average taste, from the songs this user likes/listens to ---
    avg_energy: float = 0.5
    avg_valence: float = 0.5
    avg_danceability: float = 0.5

    # --- songs the user plays repeatedly (ids from songs.csv) ---
    replayed_song_ids: List[int] = field(default_factory=list)

    # --- kept for backward compatibility with the starter tests ---
    favorite_genre: str = ""
    favorite_mood: str = ""
    target_energy: float = 0.0
    likes_acoustic: bool = False

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    # TODO: Implement CSV loading logic
    print(f"Loading songs from {csv_path}...")
    return []

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, reasons)
    return []

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    return []

def build_profile(
    name: str,
    songs: List[Song],
    liked_ids: List[int],
    replayed_ids: Optional[List[int]] = None,
) -> UserProfile:
    """
    Build a UserProfile by averaging the audio features of the songs a user
    likes. Songs the user replays repeatedly are counted twice, so they pull
    the average toward the user's strongest preferences.
    """
    replayed_ids = replayed_ids or []
    songs_by_id = {song.id: song for song in songs}

    # Build a weighted list: a replayed song appears twice.
    listened: List[Song] = []
    for song_id in liked_ids:
        song = songs_by_id.get(song_id)
        if song is None:
            continue
        weight = 2 if song_id in replayed_ids else 1
        listened.extend([song] * weight)

    if not listened:
        return UserProfile(name=name, replayed_song_ids=list(replayed_ids))

    count = len(listened)
    return UserProfile(
        name=name,
        avg_energy=round(sum(s.energy for s in listened) / count, 3),
        avg_valence=round(sum(s.valence for s in listened) / count, 3),
        avg_danceability=round(sum(s.danceability for s in listened) / count, 3),
        replayed_song_ids=list(replayed_ids),
    )

def sample_profiles() -> List[UserProfile]:
    """
    A few example users with different tastes, for testing the recommender.
    The average values below are hand-set to represent each taste; normally
    you would compute them from a user's listening history with build_profile.
    """
    return [
        # Pop fan (Taylor Swift, Bruno Mars): upbeat, danceable, positive.
        UserProfile(
            name="Amina (pop fan)",
            avg_energy=0.76,
            avg_valence=0.77,
            avg_danceability=0.75,
            replayed_song_ids=[12, 13],  # Shake It Off, 24K Magic
        ),
        # Afropop / bongo fan (Diamond Platnumz, Sauti Sol): warm and danceable.
        UserProfile(
            name="Baraka (afropop fan)",
            avg_energy=0.66,
            avg_valence=0.72,
            avg_danceability=0.79,
            replayed_song_ids=[15, 17],  # Jeje, Sura Yako
        ),
        # Study / chill listener (lofi, ambient): calm, low energy.
        UserProfile(
            name="Chris (chill listener)",
            avg_energy=0.36,
            avg_valence=0.60,
            avg_danceability=0.55,
            replayed_song_ids=[9],  # Focus Flow
        ),
    ]
