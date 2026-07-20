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


def main() -> None:
    songs = load_songs(str(CSV_PATH))

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("Top Recommendations")
    print("===================")
    print()
    for position, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"{position}. {song['title']}")
        print(f"   Score: {score:.2f}%")
        print("   Reasons:")
        for reason in reasons:
            print(f"   - {reason}")
        print()


if __name__ == "__main__":
    main()
