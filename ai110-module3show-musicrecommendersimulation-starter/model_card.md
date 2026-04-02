# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 is a content-based music recommender that suggests 5 songs from a small catalog based on a user's preferred genre, mood, energy level, and acoustic taste. It is designed for classroom exploration and learning about how recommendation systems work. It is not intended for production use with real listeners or large-scale music libraries.

The system assumes each user has a single, fixed taste profile and that preferences can be captured with just four dimensions (genre, mood, energy, acousticness). Real users have far more complex and shifting tastes.

---

## 3. How the Model Works

The recommender uses a **content-based filtering** approach. For every song in the catalog, it calculates a score by comparing the song's attributes to the user's stated preferences:

- **Genre match**: If the song's genre matches the user's favorite genre, it gets +2.0 points. This is the highest-weighted factor because genre is usually the strongest signal in music taste.
- **Mood match**: If the song's mood matches the user's preferred mood, it gets +1.0 point.
- **Energy similarity**: Instead of rewarding high or low energy, the system rewards songs whose energy level is *close* to the user's target. A perfect match gives +1.5 points; a song at the opposite end of the scale gives nearly 0. This uses the formula: `1.0 - |song_energy - target_energy|`.
- **Valence bonus**: Songs with higher valence (positivity) get a small bonus (+0.5 max).
- **Danceability bonus**: More danceable songs get a small bonus (+0.5 max).
- **Acousticness preference**: If the user likes acoustic music, acoustic songs are rewarded. If not, non-acoustic (electronic/produced) songs are rewarded (+0.8 max).

After scoring every song, the system sorts them from highest to lowest score and returns the top 5. Each recommendation includes a plain-English explanation of why it was chosen.

---

## 4. Data

The catalog contains **20 songs** in `data/songs.csv`. The original starter file had 10 songs, and I added 10 more to increase genre and mood diversity.

**Genres represented** (10 total): pop, lofi, rock, ambient, jazz, synthwave, indie pop, edm, acoustic, latin, metal, folk, electronic, country, classical, hip hop.

**Moods represented** (6 total): happy, chill, intense, moody, relaxed, focused, sad.

**Limitations of the data**:
- 20 songs is far too small to represent the real music landscape. Entire genres like R&B, blues, reggae, and K-pop are missing.
- The mood labels are subjective. One person's "chill" is another person's "sad."
- The dataset was created for a US/Western-centric music context. It does not include music from many global traditions.
- Energy, valence, danceability, and acousticness are all on a 0-1 scale, which oversimplifies how these qualities actually work in real songs.

---

## 5. Strengths

- **Transparency**: Every recommendation comes with a clear explanation of *why* that song scored highly. Users can see exactly how many points came from genre, mood, energy, etc. This is far more transparent than a neural-network-based recommender.
- **Predictable behavior**: For well-defined profiles like "pop/happy/high-energy," the top results are exactly what you would expect (Sunrise City, Gym Hero). The system does not produce surprising or random outputs.
- **Chill Lofi profiles work very well**: The lofi/chill/low-energy profile surfaces Library Rain and Midnight Coding at the top, which is a genuinely good recommendation for that vibe.
- **Simplicity**: The scoring rules are easy to understand, debug, and modify. Anyone can change a weight and immediately see how the rankings shift.

---

## 6. Limitations and Bias

- **Genre dominance**: With a +2.0 weight, genre matching overwhelms other signals. A mediocre pop song will beat a perfect-vibe rock song for a "pop" user. This creates a filter bubble where users only see their declared genre.
- **The edge-case profile exposed a real flaw**: When testing "sad mood + high energy" (0.9), the system still ranked Rainy Window (energy 0.25) first because genre+mood matches dominated. The energy similarity score was terrible (0.35), but the categorical bonuses still won. This means the system cannot handle contradictory preferences well.
- **Small catalog bias**: With only 20 songs, some genres have just one representative. If a user likes "metal," there is exactly one metal song to recommend. The system cannot distinguish between "good metal recommendation" and "only metal option."
- **No diversity mechanism**: The system always picks the top-scoring songs, which can lead to very similar recommendations. For the EDM profile, all top 5 songs are high-energy and upbeat. A real recommender would inject some variety.
- **Western/English bias**: All songs in the catalog have English names and Western genre labels. The system has no way to recommend music from other cultural traditions.

---

## 7. Evaluation

I tested the system with **5 user profiles**:

| Profile | Genre | Mood | Energy | Acoustic | Top Result |
|---------|-------|------|--------|----------|------------|
| Happy Pop Fan | pop | happy | 0.8 | No | Sunrise City (5.94) |
| Chill Lofi Listener | lofi | chill | 0.35 | Yes | Library Rain (5.78) |
| Intense Rock Lover | rock | intense | 0.9 | No | Storm Runner (5.78) |
| Mellow Acoustic (edge case) | acoustic | sad | 0.9 | Yes | Rainy Window (4.59) |
| EDM Party Mode | edm | happy | 0.95 | No | Bass Cathedral (5.09) |

**What surprised me**:
- The "Mellow Acoustic" edge case (sad + energy 0.9) still recommended Rainy Window first (energy 0.25), because genre+mood matches were worth 3.0 points total while the energy penalty was only about 1.0 point. This shows that categorical matches can easily overpower numerical similarity.
- "Salsa del Sol" showed up in 4 out of 5 profiles. It has high valence, high danceability, and moderate-to-high energy, which gives it a strong baseline score even without genre or mood matches. This is a "popularity bias" built into the scoring weights.

**Sensitivity experiments**:
- **Doubling energy weight (3.0) and halving genre (1.0)**: Neon Bounce jumped from #4 to #2 for the pop fan, because its energy (0.85) was slightly closer to the target (0.8) than Gym Hero's (0.93). Genre became less of a lock-in.
- **Removing mood check entirely**: Gym Hero climbed to #2 (from #2 to nearly tied with Sunrise City) for the pop fan, while non-pop/non-happy songs like Salsa del Sol and Neon Bounce dropped. Mood was acting as a diversifier; without it, genre dominance increased.

---

## 8. Future Work

1. **Add diversity-aware re-ranking**: After scoring, shuffle the top results so they are not all from the same genre/mood cluster. For example, ensure at least 2 different genres appear in the top 5.
2. **Support multi-valued preferences**: Let users list multiple genres or moods (e.g., "I like both lofi and jazz"). This would make profiles more realistic.
3. **Introduce collaborative filtering**: Track which songs were recommended to similar profiles and use that signal to surface songs that might not match on attributes alone but are loved by similar users.
4. **Bigger, real-world dataset**: Replace the hand-crafted 20-song catalog with a subset of Spotify's API data (thousands of songs with real audio features).

---

## 9. Personal Reflection

Building this recommender was a great exercise in seeing how simple math can produce surprisingly convincing "AI" behavior. When Sunrise City popped up as #1 for the pop/happy profile, it genuinely felt like a smart recommendation, even though it was just weighted addition.

The biggest learning moment was the edge-case profile. I designed "sad mood + high energy" expecting the system to struggle, and it did. Rainy Window scored highest despite having almost the opposite energy level. That showed me how much categorical features (genre, mood) can dominate numerical features in a weighted scoring system, and why real recommenders need more sophisticated approaches like embedding spaces or neural networks.

What changed my perspective on real music apps: I now realize that when Spotify recommends a song, there is a scoring function like this running behind the scenes, just with hundreds of features instead of six, and trained on billions of interactions instead of hand-tuned weights. The core idea is the same: turn every song into a number, sort, and pick the top results. The "magic" is in the features and the data, not in some fundamentally different kind of intelligence.
