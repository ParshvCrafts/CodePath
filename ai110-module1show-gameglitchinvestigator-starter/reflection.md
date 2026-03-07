# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

The first bug I noticed was that the hint seems to be inverted. For example, when the number was 60 and I guessed 50, it told me to go LOWER, when it should have been higher, and when the number was 11, and I guessed 50, it told me to go HIGHER, when it should have been lower. Also, to submit my guess, I have to presse the Submit button twice. Lastly, pressing New Game does not reset the game properly as the previous history still remains and it does not let me play with a message "You already won. Start a new game to play again."

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

I used Claude Code as my main AI tool for this project. I described the bugs I was seeing while playing the game, and it read through the code with me to find what was actually causing them.

**Correct suggestion:** The AI told me that the double-submit problem was happening because Streamlit reruns the page separately for the text input change and the button click, so the button press gets lost on the first click. It suggested wrapping the input and submit button inside an `st.form()` so they get processed together in one go. I verified this by running the app after the fix. One click was all it took to submit my guess, and the hint showed up immediately without needing to press Submit twice.

**Incorrect/misleading suggestion:** At first, the AI pointed to the swapped outcome labels in `check_guess()` as the sole reason for the inverted hints. The labels were indeed backwards ("Too High" when the guess was actually too low), but just swapping those labels wouldn't have fully fixed what I was seeing. When I played the game, my very first guess still got the wrong hint. Digging deeper, we found the real reason was that the code was secretly converting the secret number to a string on every even attempt (`secret = str(st.session_state.secret)`), which made Python do ASCII character comparison instead of number comparison and that gave completely wrong directions. So the initial suggestion was partially right but missed the bigger issue. I verified this by checking the Developer Debug Info panel, when I guessed 50 and the secret was 60, the string comparison path was treating "50" and "60" as text, and since "5" comes before "6" alphabetically it returned the wrong hint. After removing that string conversion entirely, the hints finally worked correctly every single time.


## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

I used both manual testing and a pytest suite to make sure things were actually fixed and not just looks fine on one try. After each fix I ran the Streamlit app, played a few rounds, and checked the Developer Debug Info panel to make sure the secret stayed as an integer, the attempts counted correctly, and the history cleared on New Game.

For automated testing, I wrote 76 pytest cases in `test/test_game_logic.py` that cover all four logic functions. The tests I am most proud of are the regression tests. For example, `test_regression_guess_50_secret_60` literally recreates the exact scenario where I guessed 50 and the secret was 60. It checks that the outcome is "Too Low" and the message says "Go HIGHER" and does NOT say "Go LOWER." Before the fix, this test would have failed because the old code returned the inverted hint. Another one, `test_too_high_on_even_attempt_still_subtracts_5`, catches the scoring bug where wrong guesses on even attempts used to give you +5 points instead of taking away 5. I also wrote a test called `test_all_possible_secrets_winnable_in_normal` that loops through every possible secret from 1 to 100 and proves a binary-search player can always win within 8 attempts, which confirms the game is actually fair and beatable.

The AI helped me think about edge cases I wouldn't have considered on my own, like what happens if someone types `inf`, `nan`, or SQL injection strings into the guess box. It suggested those tests and I ran them. All 76 passed, which gave me real confidence that the fixes hold up and the game logic is solid.

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

The secret number kept changing because of how Streamlit works under the hood. Every time I clicked a button or type something, Streamlit literally reruns your entire Python script from top to bottom. So if I just write `secret = random.randint(1, 100)` as a normal variable, it gets a brand new random number on every single click. That is why it felt impossible to win.

In Streamlit, that "drawer" is `st.session_state`. It is a dictionary that survives across reruns. So instead of `secret = random.randint(1, 100)`, I wrote `if "secret" not in st.session_state: st.session_state.secret = random.randint(1, 100)`. That way it only picks a number the first time, and every rerun after that just reads it from the drawer instead of rolling a new one.

The original code actually already had the `session_state` check for the secret, so the number itself was stable. The real issue was that other things around it were broken. The attempt counter started at 1 instead of 0, the secret got converted to a string on even attempts, and the text input triggered extra reruns that made it seem like things were resetting. Fixing the `st.form` wrapper and the state initialization is what made the game feel stable and predictable.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

The biggest habit I am taking away from this is writing regression tests for the exact bugs I found. Not just general tests that check if things work, but tests that recreate the specific broken scenario, like "guess 50, secret is 60, make sure it says HIGHER and not LOWER." That way if something ever breaks again in the same way, I will catch it immediately instead of finding out by playing the game and scratching my head. I also want to keep separating logic into its own file so it is actually testable without needing to spin up the whole UI.

Next time I work with AI on a coding task, I would push back sooner when the first suggestion does not fully explain what I am seeing. In this project the AI initially said the labels are just swapped which was only half the story. I should have said okay but why does it still break on the first guess specifically? right away instead of accepting the partial answer. Being more specific with my follow-up questions would have gotten us to the real root cause faster.

The original game was written by an AI and it looked clean and reasonable at first glance, but it had some really sneaky bugs hidden in there, like converting numbers to strings on alternating turns. It taught me that AI can write code that looks right but has subtle logic errors in it, so I really need to test and play with it myself before I trust it.
