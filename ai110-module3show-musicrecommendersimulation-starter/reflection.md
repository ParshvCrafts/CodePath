# Reflection: Music Recommender Simulation

## Profile Comparisons

### Happy Pop Fan vs. Chill Lofi Listener

The Happy Pop Fan's top 5 are all high-energy, upbeat tracks (Sunrise City at 0.82, Gym Hero at 0.93, Salsa del Sol at 0.88). The Chill Lofi Listener's top 5 are all low-energy, mellow tracks (Library Rain at 0.35, Midnight Coding at 0.42, Focus Flow at 0.40). This makes sense because the energy similarity score rewards songs that are close to the user's target, so a target of 0.8 pulls toward the top of the energy range while 0.35 pulls toward the bottom. The genre and mood matches reinforce this separation: pop/happy lives in a completely different space than lofi/chill. There is zero overlap between the two top-5 lists, which shows that the system can effectively distinguish between very different taste profiles.

### Intense Rock Lover vs. EDM Party Mode

Both profiles have high energy targets (0.9 and 0.95), but their genre preferences pull them in different directions. Storm Runner (rock/intense) is #1 for the rock lover but does not appear at all in the EDM top 5. Bass Cathedral (edm/intense) is #1 for the EDM profile but only #3 for the rock lover. Interestingly, Gym Hero (pop/intense, energy 0.93) appears in both top-5 lists because its mood match (+1.0 for intense) and high energy similarity score it well for either profile. This shows that when two profiles share a mood and energy range, the genre weight is what differentiates them. If we lowered the genre weight, these two profiles would converge.

### Happy Pop Fan vs. EDM Party Mode

Both want happy, high-energy music, but differ on genre (pop vs edm) and exact energy target (0.8 vs 0.95). The pop fan gets Sunrise City (#1) and Gym Hero (#2), while the EDM fan gets Bass Cathedral (#1) and Salsa del Sol (#2). Neon Bounce (electronic/happy) appears in both lists (#4 for pop, #3 for EDM) because its genre is close to "edm" in spirit, even though the system treats "electronic" and "edm" as completely different strings. This is a limitation: the system has no concept of genre similarity, so it treats "electronic" and "edm" as unrelated, even though musically they are close neighbors.

### Mellow Acoustic (Edge Case) vs. Chill Lofi Listener

These profiles share a preference for acoustic, low-energy music, but the acoustic profile asks for "sad" mood while the lofi profile asks for "chill." The acoustic profile's top result is Rainy Window (acoustic/sad, 0.25 energy) with 4.59 points. The lofi profile's top result is Library Rain (lofi/chill, 0.35 energy) with 5.78 points. The lofi profile scores much higher because it has more genre matches in the catalog (3 lofi songs) while acoustic has only 1. This means the acoustic user quickly runs out of matching songs and the remaining recommendations are just "whatever has the highest baseline score," which happens to be Salsa del Sol and Rooftop Lights. This is a clear case of catalog coverage bias: the system is only as good as the data it has.

### Why Does "Gym Hero" Keep Showing Up?

Gym Hero (pop/intense, energy 0.93) appears in the top 5 for the Happy Pop Fan, the Intense Rock Lover, and nearly for the EDM Party Mode. It is a "universally high-scoring" song because it has a strong genre (pop is common), high energy (close to many targets), high danceability (0.88), decent valence (0.77), and very low acousticness (0.05, which benefits any non-acoustic user). In plain language: Gym Hero is the "crowd-pleaser" of the catalog. If you imagine a real system with millions of songs, this is exactly how popularity bias works. Some songs just have attributes that score well for many different profiles, so they get recommended to everyone, creating a rich-get-richer cycle.

## Experiment Observations

### Weight Shift (2x energy, 0.5x genre)

When I doubled the energy weight from 1.5 to 3.0 and halved genre from 2.0 to 1.0, the rankings shifted noticeably. Neon Bounce jumped from #4 to #2 for the pop fan because its energy (0.85) is very close to the 0.8 target, contributing a massive 2.85 points from energy alone. Rooftop Lights also jumped up because its 0.76 energy scores well. Meanwhile, Gym Hero dropped from #2 to #5 because its 0.93 energy is further from the 0.8 target, and the genre bonus was cut in half, so the energy penalty was no longer offset. This experiment showed me that energy-focused scoring produces more "vibe-accurate" results but less "genre-loyal" results. A real system probably needs a balance.

### Feature Removal (mood disabled)

With mood set to 0.0, the pop fan's list became more genre-dominated. Sunrise City and Gym Hero held their positions because they are both pop, but the gap between them and non-pop songs widened. Salsa del Sol dropped from #3 to #3 but with a lower score (3.00 vs 4.00) because it lost the mood match bonus. This showed that mood was acting as a "cross-genre bridge," letting non-pop happy songs compete with pop songs. Without it, the system becomes a genre-first system, which creates a tighter filter bubble.

## What I Learned

The most eye-opening part of this project was realizing how much the choice of weights shapes the user's experience. A 0.5-point change in genre weight can be the difference between a diverse recommendations list and a genre echo chamber. Real recommender teams probably spend a lot of time tuning these weights, and the consequences of getting them wrong are real: users get bored, artists get invisible, and the platform loses engagement.

I also learned that transparency matters. Being able to see exactly why each song scored the way it did made debugging easy and made the results feel trustworthy. When a recommendation felt wrong (like Rainy Window for the high-energy acoustic user), I could look at the score breakdown and immediately understand the cause. Most real recommenders are black boxes, which makes it much harder for users to understand or contest the results.
