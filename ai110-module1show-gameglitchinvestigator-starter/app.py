import random
import streamlit as st

# FIX: Refactored all game logic functions from app.py into logic_utils.py
# using Claude Agent mode so the logic is testable independently with pytest.
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game — now fully debugged!")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIX: Changed initial attempts from 1 to 0 — starting at 1 caused an off-by-one
# that made the first guess always hit the string-conversion bug path.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

attempts_left = attempt_limit - st.session_state.attempts
# FIX: Used {low} and {high} instead of hardcoded "1 and 100" — now matches difficulty.
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempts_left}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

# FIX: Wrapped input + button in st.form to fix double-submit bug.
# Claude explained that Streamlit reruns twice (once for text change, once for button)
# when they're separate widgets — st.form groups them into a single submission.
with st.form("guess_form"):
    raw_guess = st.text_input("Enter your guess:")
    col1, col2, col3 = st.columns(3)
    with col1:
        submit = st.form_submit_button("Submit Guess 🚀")
    with col2:
        pass
    with col3:
        show_hint = st.checkbox("Show hint", value=True)

new_game = st.button("New Game 🔁")

# FIX: New Game now resets ALL session state — original only reset attempts and secret,
# leaving status as "won"/"lost" and history intact, which blocked new games.
# Also uses randint(low, high) instead of hardcoded randint(1, 100) to match difficulty.
if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.score = 0
    st.success("New game started!")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won! Press New Game to play again.")
    else:
        st.error("Game over! Press New Game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        st.error(err)
    else:
        # FIX: Moved attempts increment AFTER validation — original incremented before
        # parse_guess, so typing garbage wasted a turn. Now only valid guesses count.
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: Removed the attempts%2 string-conversion of secret — original turned
        # the secret into a string on even attempts, causing int-vs-str TypeError
        # and wrong hints via ASCII comparison. Now always compare ints directly.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
