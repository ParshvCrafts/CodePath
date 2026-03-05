def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


# FIX: Added low/high params for range validation — AI (Claude) suggested adding
# boundary checks here instead of in app.py to keep validation in one place.
def parse_guess(raw: str, low: int, high: int):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except (ValueError, TypeError):
        return False, None, "That is not a valid number."

    # FIX: Range validation added — rejects out-of-bounds guesses before they reach game logic.
    if value < low or value > high:
        return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


# FIX: Swapped outcome labels — original had "Too High" when guess < secret (backwards).
# Also removed the TypeError/string-comparison fallback that caused wrong hints.
# Claude helped trace the root cause: the old code converted secret to str on even attempts,
# which triggered ASCII string comparison giving inverted results.
def check_guess(guess: int, secret: int):
    """
    Compare guess to secret and return (outcome, message).

    Both guess and secret must be integers.
    outcome: "Win", "Too Low", or "Too High"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess < secret:
        return "Too Low", "📈 Go HIGHER!"
    return "Too High", "📉 Go LOWER!"


# FIX: Removed inconsistent scoring — original gave +5 for wrong "Too High" guesses
# on even attempts, which rewarded wrong answers. Now every wrong guess costs -5.
# Also fixed the win bonus off-by-one (was attempt_number + 1, now just attempt_number).
def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = max(10, 100 - 10 * attempt_number)
        return current_score + points
    return current_score - 5
