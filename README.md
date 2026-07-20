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

My recommender is **content-based**: it compares each song to what the user likes and
recommends the songs that "feel" closest. What makes my version different from the
starter idea is that **I score everything in percentages instead of points.** The
assignment suggested a points system (+2 for a genre match, +1 for a mood match, etc.),
but a points total like `3.4` doesn't mean anything on its own and has no ceiling.
Instead, every song gets a single **0%–100% score that reads as "how likely this user is
to like this song."** That matches how I actually pick songs (by probability), and it
makes the number easy to explain.

> A sketch of the full data flow (Input → Loop → Ranking) lives in
> [resource/sketch design.mmd](resource/sketch%20design.mmd).

### What features does each `Song` use

I use six of the song's attributes. Two are **text/categorical** and four are **numeric**
(already scaled 0–1, so I can compare them directly):

- **genre** *(text)* – e.g. pop, lofi, afropop
- **mood** *(text)* – e.g. happy, chill, moody
- **energy** *(0–1)* – how energetic/intense the song is
- **valence** *(0–1)* – how positive or happy it sounds
- **danceability** *(0–1)* – how easy it is to dance to
- **acousticness** *(0–1)* – how acoustic vs. electronic it is

I leave out `tempo_bpm` for now because it's on a much bigger scale (60–160 BPM) and
would need to be rescaled before it could be compared fairly to the 0–1 features.

### What information does the `UserProfile` store

Each profile stores:

- **Basic user info** (a name or id)
- **A favorite genre and mood** – the categorical taste the user tells us about
- **The user's average taste** across the numeric features (average energy, valence,
  danceability, acousticness), built from the songs they've listened to. This gives one
  "ideal song" that represents their taste.
- **Songs they play repeatedly**, which count *twice* when building those averages — a
  song you replay says more about your taste than one you heard once.

### How does the `Recommender` compute a score for each song (the recipe)

For every song, I score each feature **from 0 to 1** on its own, then combine those
sub-scores into one final percentage using a **weight for each feature**. The weights add
up to 100%, so the final score is also a clean 0%–100% number.

**1. Score each feature (the 0–1 part):**

- **Categorical (genre, mood):** `1.0` if the song matches the user's favorite, else
  `0.0`. Either it's a match or it isn't.
- **Numeric (energy, valence, danceability, acousticness):** `1 − |song value − user
  target|`. Because both values are already 0–1, this is just "how close are they" — a
  perfect match is `1.0`, and the further apart they are, the closer to `0`.

**2. Combine with weights (the percentage part):**

```
score = 0.30 · genre_match      (30%)
      + 0.20 · energy_closeness  (20%)
      + 0.15 · valence_closeness (15%)
      + 0.15 · dance_closeness   (15%)
      + 0.15 · mood_match        (15%)
      + 0.05 · acoustic_closeness (5%)
```

Every term is between 0 and 1 and the weights sum to `1.00`, so `score` is always between
0 and 1 → I show it as a percentage (e.g. `0.72` → **72%**).

### How the weights were assigned (and why)

| Feature       | Weight | Why it got that weight                                             |
|---------------|:------:|--------------------------------------------------------------------|
| Genre         | 30%    | The strongest signal — a pop fan should mostly get pop.            |
| Energy        | 20%    | The audio feature that most changes how a song *feels*.           |
| Valence       | 15%    | Positivity matters, but less than raw energy.                     |
| Danceability  | 15%    | Same idea — a meaningful part of "feel," not the top of it.       |
| Mood          | 15%    | Kept at half of genre, matching the assignment's 2:1 genre-to-mood hint. |
| Acousticness  | 5%     | The least important cue, so it only nudges ties.                  |

The four numeric "feel" features add up to 55%, which is what lets a song still score,
say, 65% even when its genre is different — that's how the system can suggest something
outside your usual genre.

### How do I choose which songs to recommend

- **Mostly by probability:** I sort every song by its percentage score and recommend the
  **top K** (default 5). High score = strong match.
- **Sometimes I explore:** every so often I recommend a song with a *low* probability
  (around 10%) on purpose. This helps the user discover something new, and it gives the
  system more information about whether their taste is wider than we thought.
- **Similar-user idea (stretch goal):** if two users have very similar taste and one of
  them liked a song the other hasn't heard, I can recommend that song to the second user,
  since people with similar taste tend to like similar songs. *(This one goes beyond
  pure content-based recommending — it's a "collaborative filtering" idea I'd add later.)*

### Potential bias from how the percentages were assigned

The weights are **my own judgment calls**, so they bake my assumptions into the system:

- **Over-weighting genre (30%).** Genre is the single heaviest feature, so the recommender
  leans hard toward the user's stated favorite genre. That can trap the user in a bubble
  (a pop fan almost never sees rock or jazz) and it's unfair to good songs that just
  happen to be labeled a different genre. It also trusts the CSV's genre labels
  completely, even though genre labels are fuzzy and inconsistent in real data.
- **Under-weighting acousticness (5%).** At only 5%, acousticness almost never changes a
  ranking, so a listener who specifically cares about acoustic vs. electronic sound is
  barely served by the system.
- **The gaps between weights are themselves a bias.** Nothing about the *data* says genre
  should be 6× more important than acousticness — that ratio is a choice I made, and a
  different, equally reasonable choice would produce different recommendations. I test
  this in the **Experiments** section below by changing the genre weight and watching the
  results shift.

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

How the output is produced:

- Each song is scored with **weighted preference matching** — every feature the user
  cares about contributes a 0–1 sub-score, combined using the percentage weights in the
  recipe above.
- Recommendations are **ranked from highest score to lowest**.
- Only the **top `k`** results are returned (default 5).
- Each recommendation includes **reasons** explaining why it scored the way it did.

Example run for the profile `genre=pop, mood=happy, energy=0.8` (`python src/main.py`):

```text
Top Recommendations
===================

1. Shake It Off
   Score: 100.00%
   Reasons:
   - Genre matches your preference for pop
   - Energy is very close to your preferred level
   - Mood matches your preference for happy

2. Sunrise City
   Score: 99.38%
   Reasons:
   - Genre matches your preference for pop
   - Energy is very close to your preferred level
   - Mood matches your preference for happy

3. Gym Hero
   Score: 72.92%
   Reasons:
   - Genre matches your preference for pop
   - Energy is close to your preferred level
   - Mood (intense) differs from your preferred happy

4. Anti-Hero
   Score: 71.38%
   Reasons:
   - Genre matches your preference for pop
   - Energy is close to your preferred level
   - Mood (moody) differs from your preferred happy

5. Talking to the Moon
   Score: 68.31%
   Reasons:
   - Genre matches your preference for pop
   - Energy is lower than your preferred level
   - Mood (moody) differs from your preferred happy
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



