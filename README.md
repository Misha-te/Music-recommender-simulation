# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

My recommender is **content-based**: it compares a song's audio features to what the
user has liked before, and recommends songs that "feel" similar.

### What features does each `Song` use

I only use the three numeric audio features that are already scaled from 0 to 1, so I
can compare them directly without any extra math:

- **energy** – how energetic/intense the song is
- **valence** – how positive or happy the song sounds
- **danceability** – how easy it is to dance to

I left out `genre` and `mood` (they're text, so they'd need extra encoding) and
`tempo_bpm` (it's on a much bigger scale, so it would need to be rescaled first). Using
the three clean 0–1 features keeps the first version simple.

### What information does the `UserProfile` store

Each profile stores:

- **Basic user info** (like a name or id)
- **The user's average taste**, built from the songs they've listened to: their average
  energy, average valence, and average danceability. This gives one "ideal song" that
  represents their taste.
- **Songs they play repeatedly**, which count more when building those averages (a song
  you replay says more about your taste than one you heard once).

### How does the `Recommender` compute a score for each song

1. For a given song, I compare its energy, valence, and danceability to the user's
   average values.
2. The closer the song is to the user's averages, the higher its score. I turn that
   closeness into a **percentage that estimates the probability the user will like it**
   (for example, 70%).

### How do I choose which songs to recommend

- **Mostly by probability:** if a song scores high (say above ~70%), I recommend it.
- **Sometimes I explore:** every so often I recommend a song with a *low* probability
  (around 10%) on purpose. This helps the user discover something new, and it gives the
  system more information about whether their taste is wider than we thought.
- **Similar-user idea (stretch goal):** if two users have very similar taste and one of
  them liked a song the other hasn't heard, I can recommend that song to the second user,
  since people with similar taste tend to like similar songs. *(This one goes beyond
  pure content-based recommending — it's a "collaborative filtering" idea I'd add later.)*

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



