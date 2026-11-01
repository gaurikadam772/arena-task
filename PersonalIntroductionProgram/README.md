# Personal Introduction Program

**Week 1 — Python Basics | The Developers Arena**

## Project overview
A beginner-friendly command-line program that asks the user for their name, age, and favorite hobby, then prints a friendly personalized welcome message.

## Features
- Collects three pieces of information with `input()`.
- Stores responses in variables.
- Uses an f-string to format personalized output.
- Validates age input using `try/except` and a loop.
- Handles blank name and hobby inputs.

## Requirements
- Python 3.8 or newer
- No third-party packages are required.

## Setup and run
1. Install Python 3 from https://www.python.org/downloads/ if it is not already installed.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Run:

   ```bash
   python personal_intro.py
   ```

   On some systems, use `python3 personal_intro.py`.

## Project structure
```text
personal-introduction/
├── README.md
├── personal_intro.py
├── requirements.txt
└── screenshot.png
```

## How it works
1. `main()` prints a title.
2. `input()` collects the name, age, and hobby.
3. A `while` loop and `try/except` validate the age.
4. An f-string combines the values into a personalized message.
5. The `if __name__ == "__main__":` guard runs the program when this file is executed directly.

## Testing evidence
Try the following cases:
- Valid input: `Alex`, `21`, `Coding` — should show a personalized welcome.
- Non-numeric age: `twenty` — should ask for age again.
- Negative age: `-2` — should ask for age again.
- Blank name — should request the name again.
- Blank hobby — should use a default phrase.

## What I learned
I practiced Python variables, strings, user input, output with `print()`, f-strings, loops, conditionals, and exception handling. I also learned to validate user input and organize code inside a `main()` function.

## Screenshot
See `screenshot.png` for an example of the program's console output.
