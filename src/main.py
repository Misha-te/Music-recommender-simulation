"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path

try:  # works as a package (python -m src.main)
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:  # works as a plain script (python src/main.py)
    from recommender import load_songs, recommend_songs

# Resolve the CSV relative to the project root so it works from any directory.
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"

# A few distinct listeners to try the recommender against. Each is a plain
# user-preference dict: the keys line up with the FEATURE_WEIGHTS recipe in
# recommender.py, and any key can be left out.
USER_PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "danceability": 0.85,
        "valence": 0.85,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "danceability": 0.55,
        "acousticness": 0.8,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.9,
        "danceability": 0.6,
        "valence": 0.45,
    },
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print the top-k recommendations for a single named profile."""
    header = f"Top Recommendations — {name}"
    print(header)
    print("=" * len(header))
    prefs_summary = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print(f"Profile: {prefs_summary}")
    print()
    for position, (song, score, reasons) in enumerate(
        recommend_songs(user_prefs, songs, k=k), start=1
    ):
        print(f"{position}. {song['title']}")
        print(f"   Score: {score:.2f}%")
        print("   Reasons:")
        for reason in reasons:
            print(f"   - {reason}")
        print()


def main() -> None:
    songs = load_songs(str(CSV_PATH))

    for name, user_prefs in USER_PROFILES.items():
        print_recommendations(name, user_prefs, songs, k=5)
        print()


if __name__ == "__main__":
    main()
