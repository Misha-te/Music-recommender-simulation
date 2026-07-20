import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# --- Scoring recipe (see README "How The System Works") -------------------
# Each feature contributes a 0-1 sub-score; the weights below say how much it
# counts. They sum to 1.00, so a song's final score is a clean 0%-100% number.
# Kept as data (not magic numbers scattered in code) so the recipe is easy to
# tweak for the README "Experiments" section.
FEATURE_WEIGHTS = [
    # (key, weight, kind, label shown in reasons)
    # EXPERIMENT (sensitivity test): energy doubled 0.20 -> 0.40 and genre
    # halved 0.30 -> 0.15. The weights no longer sum to 1.00, but score_song
    # normalizes by the weight actually used, so the final score stays a valid
    # 0-100%. Original values are noted in comments for easy revert.
    ("genre",        0.15, "categorical", "Genre"),        # was 0.30
    ("energy",       0.40, "numeric",     "Energy"),        # was 0.20
    ("valence",      0.15, "numeric",     "Valence"),
    ("danceability", 0.15, "numeric",     "Danceability"),
    ("mood",         0.15, "categorical", "Mood"),
    ("acousticness", 0.05, "numeric",     "Acousticness"),
]

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

NUMERIC_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dicts, numeric fields as floats."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("id"):  # skip blank trailing lines
                continue
            song = dict(row)
            song["id"] = int(row["id"])
            for field_name in NUMERIC_FIELDS:
                if song.get(field_name) not in (None, ""):
                    song[field_name] = float(song[field_name])
            songs.append(song)
    return songs

def _numeric_reason(label: str, value: float, target: float, closeness: float) -> str:
    """Turn a numeric feature's closeness into a human-readable reason."""
    if closeness >= 0.90:
        return f"{label} is very close to your preferred level"
    if closeness >= 0.75:
        return f"{label} is close to your preferred level"
    direction = "higher" if value > target else "lower"
    return f"{label} is {direction} than your preferred level"


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user_prefs, returning (percent_score, reasons)."""
    weighted_sum = 0.0
    used_weight = 0.0
    reasons: List[str] = []

    for key, weight, kind, label in FEATURE_WEIGHTS:
        # Only score features the user actually expressed a preference for.
        pref = user_prefs.get(key)
        if pref is None or pref == "":
            continue
        used_weight += weight

        if kind == "categorical":
            matched = str(song.get(key, "")).lower() == str(pref).lower()
            sub = 1.0 if matched else 0.0
            if matched:
                reasons.append(f"{label} matches your preference for {pref}")
            else:
                reasons.append(f"{label} ({song.get(key)}) differs from your preferred {pref}")
        else:  # numeric: both values are on the same 0-1 scale
            target = float(pref)
            value = float(song.get(key, 0.0))
            sub = max(0.0, min(1.0, 1.0 - abs(value - target)))
            reasons.append(_numeric_reason(label, value, target, sub))

        weighted_sum += weight * sub

    if used_weight == 0.0:
        return 0.0, ["No matching preferences were provided to score this song."]

    # Normalize by the weight actually used so the result is a true 0-100%
    # even when the user only specified some of the features.
    score = max(0.0, min(100.0, (weighted_sum / used_weight) * 100.0))
    return score, reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, List[str]]]:
    """Score every song, rank high->low, and return the top-k (song, score, reasons)."""
    # k must be a real integer -- bool is an int subclass, so reject it too.
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError(f"k must be an integer, got {type(k).__name__}")
    if k < 0:
        raise ValueError(f"k must be non-negative, got {k}")

    # Build a new list of (song, score, reasons); never mutate the catalog.
    scored: List[Tuple[Dict, float, List[str]]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))

    # sorted() returns a NEW list; slicing past the end is safe (returns all).
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranked[:k]

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
