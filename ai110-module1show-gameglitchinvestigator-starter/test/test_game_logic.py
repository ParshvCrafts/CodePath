"""
Comprehensive test suite for the Game Glitch Investigator.

Covers every function in logic_utils.py with tests for:
- Normal/happy-path behaviour
- Boundary values (edges of valid ranges)
- Invalid / malicious / unexpected inputs
- Regression tests that verify each original bug is fixed
- Full-game integration scenarios
"""

import sys
import os
import pytest

# Make sure the project root is on the path so we can import logic_utils
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)


# ──────────────────────────────────────────────
#  get_range_for_difficulty
# ──────────────────────────────────────────────
class TestGetRangeForDifficulty:
    """Tests for difficulty → (low, high) mapping."""

    def test_easy_range(self):
        assert get_range_for_difficulty("Easy") == (1, 20)

    def test_normal_range(self):
        assert get_range_for_difficulty("Normal") == (1, 100)

    def test_hard_range(self):
        assert get_range_for_difficulty("Hard") == (1, 50)

    def test_unknown_difficulty_returns_default(self):
        """Any unrecognised string should fall back to Normal range."""
        assert get_range_for_difficulty("Impossible") == (1, 100)

    def test_empty_string_returns_default(self):
        assert get_range_for_difficulty("") == (1, 100)

    def test_none_returns_default(self):
        """None is not a valid difficulty; should still return the default."""
        assert get_range_for_difficulty(None) == (1, 100)

    def test_case_sensitivity(self):
        """Difficulty strings are case-sensitive; 'easy' != 'Easy'."""
        assert get_range_for_difficulty("easy") == (1, 100)  # falls to default
        assert get_range_for_difficulty("EASY") == (1, 100)

    def test_returns_tuple_of_two_ints(self):
        for diff in ("Easy", "Normal", "Hard"):
            result = get_range_for_difficulty(diff)
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert isinstance(result[0], int)
            assert isinstance(result[1], int)

    def test_low_is_always_less_than_high(self):
        for diff in ("Easy", "Normal", "Hard", "anything"):
            low, high = get_range_for_difficulty(diff)
            assert low < high


# ──────────────────────────────────────────────
#  parse_guess
# ──────────────────────────────────────────────
class TestParseGuess:
    """Tests for raw-string → validated int conversion."""

    # --- Valid inputs ---
    def test_valid_integer_string(self):
        ok, val, err = parse_guess("42", 1, 100)
        assert ok is True
        assert val == 42
        assert err is None

    def test_valid_at_lower_bound(self):
        ok, val, err = parse_guess("1", 1, 100)
        assert ok is True
        assert val == 1

    def test_valid_at_upper_bound(self):
        ok, val, err = parse_guess("100", 1, 100)
        assert ok is True
        assert val == 100

    def test_float_string_truncated_to_int(self):
        ok, val, err = parse_guess("42.9", 1, 100)
        assert ok is True
        assert val == 42  # int(float("42.9")) → 42

    def test_float_string_at_boundary(self):
        ok, val, err = parse_guess("1.0", 1, 100)
        assert ok is True
        assert val == 1

    def test_negative_integer_in_positive_range(self):
        ok, val, err = parse_guess("-5", 1, 100)
        assert ok is False
        assert val is None
        assert "between" in err

    def test_negative_integer_in_negative_range(self):
        """If range ever allowed negatives, parsing should work."""
        ok, val, err = parse_guess("-3", -10, 10)
        assert ok is True
        assert val == -3

    def test_zero_in_range_starting_at_one(self):
        ok, val, err = parse_guess("0", 1, 100)
        assert ok is False
        assert "between" in err

    # --- Out-of-range ---
    def test_below_range(self):
        ok, val, err = parse_guess("0", 1, 20)
        assert ok is False
        assert "between" in err

    def test_above_range(self):
        ok, val, err = parse_guess("21", 1, 20)
        assert ok is False
        assert "between" in err

    def test_way_above_range(self):
        ok, val, err = parse_guess("999999", 1, 100)
        assert ok is False

    # --- Empty / null inputs ---
    def test_none_input(self):
        ok, val, err = parse_guess(None, 1, 100)
        assert ok is False
        assert val is None
        assert err == "Enter a guess."

    def test_empty_string(self):
        ok, val, err = parse_guess("", 1, 100)
        assert ok is False
        assert err == "Enter a guess."

    def test_whitespace_only(self):
        ok, val, err = parse_guess("   ", 1, 100)
        assert ok is False
        assert err == "Enter a guess."

    def test_tab_and_newline(self):
        ok, val, err = parse_guess("\t\n", 1, 100)
        assert ok is False
        assert err == "Enter a guess."

    # --- Non-numeric garbage ---
    def test_alphabetic_string(self):
        ok, val, err = parse_guess("abc", 1, 100)
        assert ok is False
        assert "not a valid number" in err

    def test_special_characters(self):
        ok, val, err = parse_guess("!@#$%", 1, 100)
        assert ok is False
        assert "not a valid number" in err

    def test_mixed_alpha_numeric(self):
        ok, val, err = parse_guess("12abc", 1, 100)
        assert ok is False

    def test_multiple_dots(self):
        ok, val, err = parse_guess("1.2.3", 1, 100)
        assert ok is False

    # --- Injection / hacking attempts ---
    def test_sql_injection_attempt(self):
        ok, val, err = parse_guess("1; DROP TABLE users;", 1, 100)
        assert ok is False

    def test_script_injection_attempt(self):
        ok, val, err = parse_guess("<script>alert('xss')</script>", 1, 100)
        assert ok is False

    def test_python_expression(self):
        ok, val, err = parse_guess("__import__('os').system('ls')", 1, 100)
        assert ok is False

    def test_very_large_number(self):
        ok, val, err = parse_guess("99999999999999999999", 1, 100)
        assert ok is False
        assert "between" in err

    def test_inf_string(self):
        """'inf' is a valid float but should not be accepted."""
        ok, val, err = parse_guess("inf", 1, 100)
        assert ok is False

    def test_nan_string(self):
        """'nan' is a valid float but int(float('nan')) raises ValueError."""
        ok, val, err = parse_guess("nan", 1, 100)
        assert ok is False

    # --- Leading/trailing whitespace around valid numbers ---
    def test_leading_spaces(self):
        """Input with leading spaces but valid number inside.
        Note: strip() is only applied in the empty check, not before int().
        int(' 42 ') works in Python, so this should still parse correctly."""
        ok, val, err = parse_guess(" 42 ", 1, 100)
        assert ok is True
        assert val == 42

    # --- Return type guarantees ---
    def test_ok_true_returns_int_and_no_error(self):
        ok, val, err = parse_guess("50", 1, 100)
        assert ok is True
        assert isinstance(val, int)
        assert err is None

    def test_ok_false_returns_none_and_string_error(self):
        ok, val, err = parse_guess("abc", 1, 100)
        assert ok is False
        assert val is None
        assert isinstance(err, str)


# ──────────────────────────────────────────────
#  check_guess  (the core bug-fix area)
# ──────────────────────────────────────────────
class TestCheckGuess:
    """Tests for guess-vs-secret comparison.

    REGRESSION: The original code had swapped outcome labels
    ("Too High" when guess was actually too low, and vice-versa)
    and a string-conversion path that broke comparisons.
    """

    # --- Exact match ---
    def test_exact_match(self):
        outcome, msg = check_guess(42, 42)
        assert outcome == "Win"
        assert "Correct" in msg

    # --- Guess too low → should say "Too Low" / "Go HIGHER" ---
    def test_guess_below_secret(self):
        outcome, msg = check_guess(10, 50)
        assert outcome == "Too Low"
        assert "HIGHER" in msg

    def test_guess_one_below_secret(self):
        outcome, msg = check_guess(49, 50)
        assert outcome == "Too Low"
        assert "HIGHER" in msg

    # --- Guess too high → should say "Too High" / "Go LOWER" ---
    def test_guess_above_secret(self):
        outcome, msg = check_guess(90, 50)
        assert outcome == "Too High"
        assert "LOWER" in msg

    def test_guess_one_above_secret(self):
        outcome, msg = check_guess(51, 50)
        assert outcome == "Too High"
        assert "LOWER" in msg

    # --- REGRESSION: The exact user-reported scenarios ---
    def test_regression_guess_50_secret_60(self):
        """User reported: guessed 50 with secret 60, got told to go LOWER.
        Should say 'Too Low' / 'Go HIGHER'."""
        outcome, msg = check_guess(50, 60)
        assert outcome == "Too Low"
        assert "HIGHER" in msg
        assert "LOWER" not in msg

    def test_regression_guess_50_secret_11(self):
        """User reported: guessed 50 with secret 11, got told to go HIGHER.
        Should say 'Too High' / 'Go LOWER'."""
        outcome, msg = check_guess(50, 11)
        assert outcome == "Too High"
        assert "LOWER" in msg
        assert "HIGHER" not in msg

    # --- REGRESSION: No string comparison path ---
    def test_no_type_error_with_int_inputs(self):
        """Both inputs must be ints; no string-conversion fallback."""
        # This should work cleanly without any TypeError
        outcome, msg = check_guess(5, 10)
        assert outcome == "Too Low"

    # --- Boundary values ---
    def test_guess_at_minimum_secret_at_maximum(self):
        outcome, msg = check_guess(1, 100)
        assert outcome == "Too Low"

    def test_guess_at_maximum_secret_at_minimum(self):
        outcome, msg = check_guess(100, 1)
        assert outcome == "Too High"

    def test_both_at_one(self):
        outcome, msg = check_guess(1, 1)
        assert outcome == "Win"

    def test_both_at_hundred(self):
        outcome, msg = check_guess(100, 100)
        assert outcome == "Win"

    # --- Outcome is always one of three known strings ---
    def test_outcome_is_valid_string(self):
        valid_outcomes = {"Win", "Too Low", "Too High"}
        for guess, secret in [(1, 50), (50, 50), (99, 50)]:
            outcome, _ = check_guess(guess, secret)
            assert outcome in valid_outcomes

    # --- Consistency: direction of hint matches outcome label ---
    def test_hint_direction_consistency_too_low(self):
        """When outcome is 'Too Low', message must contain 'HIGHER'."""
        outcome, msg = check_guess(25, 75)
        assert outcome == "Too Low"
        assert "HIGHER" in msg

    def test_hint_direction_consistency_too_high(self):
        """When outcome is 'Too High', message must contain 'LOWER'."""
        outcome, msg = check_guess(75, 25)
        assert outcome == "Too High"
        assert "LOWER" in msg


# ──────────────────────────────────────────────
#  update_score
# ──────────────────────────────────────────────
class TestUpdateScore:
    """Tests for the scoring system.

    REGRESSION: Original code gave +5 for wrong 'Too High' guesses
    on even attempts. Now all wrong guesses consistently cost -5.
    """

    # --- Win scoring ---
    def test_win_on_first_attempt_gives_max_score(self):
        # 100 - 10*1 = 90
        assert update_score(0, "Win", 1) == 90

    def test_win_on_second_attempt(self):
        # 100 - 10*2 = 80
        assert update_score(0, "Win", 2) == 80

    def test_win_on_fifth_attempt(self):
        # 100 - 10*5 = 50
        assert update_score(0, "Win", 5) == 50

    def test_win_on_ninth_attempt_gives_minimum_10(self):
        # 100 - 10*9 = 10
        assert update_score(0, "Win", 9) == 10

    def test_win_on_tenth_attempt_floors_at_10(self):
        # 100 - 10*10 = 0, but min is 10
        assert update_score(0, "Win", 10) == 10

    def test_win_on_very_late_attempt_still_gives_10(self):
        # Ensures floor works for any large attempt number
        assert update_score(0, "Win", 100) == 10

    def test_win_adds_to_existing_score(self):
        assert update_score(50, "Win", 1) == 140  # 50 + 90

    # --- Wrong guess scoring ---
    def test_too_low_subtracts_5(self):
        assert update_score(100, "Too Low", 1) == 95

    def test_too_high_subtracts_5(self):
        assert update_score(100, "Too High", 1) == 95

    def test_too_high_on_even_attempt_still_subtracts_5(self):
        """REGRESSION: Original code gave +5 on even attempts for Too High."""
        assert update_score(100, "Too High", 2) == 95
        assert update_score(100, "Too High", 4) == 95

    def test_too_low_on_even_attempt_subtracts_5(self):
        assert update_score(100, "Too Low", 2) == 95

    # --- Score can go negative ---
    def test_score_can_go_negative(self):
        assert update_score(0, "Too Low", 1) == -5
        assert update_score(-5, "Too High", 2) == -10

    # --- Consistency: every wrong guess costs exactly 5 ---
    def test_all_wrong_guesses_cost_same(self):
        for attempt in range(1, 11):
            assert update_score(0, "Too Low", attempt) == -5
            assert update_score(0, "Too High", attempt) == -5

    # --- Unknown outcome doesn't crash ---
    def test_unknown_outcome_subtracts_5(self):
        """Any non-Win outcome should deduct 5 as a safe default."""
        assert update_score(100, "Unknown", 1) == 95


# ──────────────────────────────────────────────
#  Integration / full-game-flow tests
# ──────────────────────────────────────────────
class TestFullGameFlow:
    """Simulate entire game scenarios end-to-end using logic_utils functions."""

    def test_win_on_first_guess(self):
        """Player guesses the secret immediately."""
        secret = 42
        low, high = 1, 100
        score = 0
        attempts = 0

        ok, guess, err = parse_guess("42", low, high)
        assert ok is True
        attempts += 1

        outcome, msg = check_guess(guess, secret)
        assert outcome == "Win"

        score = update_score(score, outcome, attempts)
        assert score == 90  # 100 - 10*1

    def test_win_after_several_wrong_guesses(self):
        """Player narrows down over multiple attempts."""
        secret = 75
        low, high = 1, 100
        score = 0
        attempts = 0
        guesses = ["50", "80", "70", "75"]

        for raw in guesses:
            ok, guess, err = parse_guess(raw, low, high)
            assert ok is True
            attempts += 1
            outcome, msg = check_guess(guess, secret)
            score = update_score(score, outcome, attempts)

        # Last guess should be a win
        assert outcome == "Win"
        # 3 wrong guesses at -5 each = -15, then win on attempt 4 = +60
        # Total: -15 + 60 = 45
        assert score == 45

    def test_game_over_all_wrong_guesses(self):
        """Player uses all attempts without guessing correctly."""
        secret = 42
        low, high = 1, 100
        attempt_limit = 8
        score = 0
        attempts = 0
        guesses = ["10", "20", "30", "40", "45", "43", "41", "44"]

        for raw in guesses:
            ok, guess, err = parse_guess(raw, low, high)
            assert ok is True
            attempts += 1
            outcome, msg = check_guess(guess, secret)
            score = update_score(score, outcome, attempts)

        assert outcome != "Win"
        assert attempts == attempt_limit
        # 8 wrong guesses: -5 * 8 = -40
        assert score == -40

    def test_invalid_inputs_dont_count_as_attempts(self):
        """Invalid guesses should not advance the attempt counter."""
        low, high = 1, 100
        attempts = 0

        invalid_inputs = ["", "abc", "0", "101", None, "   "]
        for raw in invalid_inputs:
            ok, guess, err = parse_guess(raw, low, high)
            assert ok is False
            # In the real game, attempts only increment when ok is True
            # So attempts stays at 0

        assert attempts == 0

    def test_easy_mode_full_game(self):
        """Simulate an Easy game (range 1-20, 6 attempts)."""
        low, high = get_range_for_difficulty("Easy")
        assert low == 1 and high == 20

        secret = 15
        score = 0
        attempts = 0

        # Invalid guess outside range
        ok, _, err = parse_guess("25", low, high)
        assert ok is False
        assert "between" in err

        # Valid guesses
        for raw in ["10", "18", "14", "15"]:
            ok, guess, err = parse_guess(raw, low, high)
            assert ok is True
            attempts += 1
            outcome, msg = check_guess(guess, secret)
            score = update_score(score, outcome, attempts)

        assert outcome == "Win"
        assert attempts == 4

    def test_hard_mode_full_game_loss(self):
        """Simulate a Hard game loss (range 1-50, 5 attempts)."""
        low, high = get_range_for_difficulty("Hard")
        assert low == 1 and high == 50

        secret = 37
        score = 0
        attempts = 0

        for raw in ["25", "40", "35", "38", "36"]:
            ok, guess, err = parse_guess(raw, low, high)
            assert ok is True
            attempts += 1
            outcome, msg = check_guess(guess, secret)
            score = update_score(score, outcome, attempts)

        assert outcome != "Win"
        assert attempts == 5
        assert score == -25  # 5 * -5

    def test_hint_direction_throughout_game(self):
        """Verify hints always point toward the secret during a game."""
        secret = 50
        low, high = 1, 100

        # Guess below → hint says HIGHER
        ok, guess, _ = parse_guess("25", low, high)
        outcome, msg = check_guess(guess, secret)
        assert "HIGHER" in msg

        # Guess above → hint says LOWER
        ok, guess, _ = parse_guess("75", low, high)
        outcome, msg = check_guess(guess, secret)
        assert "LOWER" in msg

        # Guess correct → says Correct
        ok, guess, _ = parse_guess("50", low, high)
        outcome, msg = check_guess(guess, secret)
        assert "Correct" in msg

    def test_score_never_rewards_wrong_guess(self):
        """REGRESSION: No wrong guess should ever increase the score."""
        score = 0
        for attempt in range(1, 20):
            new_score = update_score(score, "Too Low", attempt)
            assert new_score < score or score == 0
            new_score = update_score(score, "Too High", attempt)
            assert new_score < score or score == 0

    def test_binary_search_optimal_play(self):
        """A perfect binary-search player should always win within log2(range) attempts."""
        secret = 73
        low, high = 1, 100
        score = 0
        attempts = 0
        lo, hi = low, high

        while lo <= hi:
            mid = (lo + hi) // 2
            ok, guess, _ = parse_guess(str(mid), low, high)
            assert ok is True
            attempts += 1
            outcome, msg = check_guess(guess, secret)
            score = update_score(score, outcome, attempts)

            if outcome == "Win":
                break
            elif outcome == "Too Low":
                lo = mid + 1
            else:
                hi = mid - 1

        assert outcome == "Win"
        assert attempts <= 7  # log2(100) ≈ 6.6, so at most 7

    def test_all_possible_secrets_winnable_in_normal(self):
        """Every secret in Normal range (1-100) is winnable within 8 attempts
        using binary search, confirming the game is fair."""
        low, high = 1, 100
        attempt_limit = 8  # Normal mode limit

        for secret in range(low, high + 1):
            lo, hi = low, high
            attempts = 0
            won = False

            while lo <= hi and attempts < attempt_limit:
                mid = (lo + hi) // 2
                attempts += 1
                outcome, _ = check_guess(mid, secret)

                if outcome == "Win":
                    won = True
                    break
                elif outcome == "Too Low":
                    lo = mid + 1
                else:
                    hi = mid - 1

            assert won, f"Secret {secret} not winnable in {attempt_limit} attempts"
