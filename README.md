# Crossword Game

This project implements a simple crossword puzzle generator and game.  It reads a list of words and their clues from a small database, then attempts to lay them out on a square grid so that they intersect in a way similar to traditional crossword puzzles.  Once a puzzle is generated, the game can display the grid, the list of across and down clues and the numbered positions of each answer.

## Features

- **Randomised puzzles** – each run of the generator chooses a random subset of words from the database and attempts to lay them out on a grid.  The resulting puzzles vary from run to run.
- **Customisable database** – the set of words and clues is stored in a JSON file.  You can replace it with your own list of terms and clues.  The generator uses this database to build the crossword.
- **Simple grid display** – the generated puzzle can be printed to the terminal using ASCII characters.  Squares with letters are represented by their letters, empty squares are represented by dots (`.`).  Starting positions of across and down answers are numbered.
- **Clue lists** – the game produces two lists of clues: one for the across answers and one for the down answers.  Each clue is associated with the number on the grid.

## How it works

1. The generator reads words and clues from `database.json`.  Each entry in the database is an object with two keys: `word` and `clue`.
2. It randomly selects a subset of these entries (up to a maximum, configurable via the `max_words` variable).
3. The first selected word is placed horizontally on the centre row of the grid.
4. Each subsequent word is placed by attempting to cross it with one of the words already on the grid.  It chooses positions where the two words share a letter.  If the placement fits within the grid and does not conflict with existing letters, the word is added to the puzzle.  Words that cannot be placed are skipped.
5. Once all words have been processed, the generator numbers the starting squares of each across and down answer and produces the lists of clues.
6. Finally, the game prints the grid and lists of clues to the terminal.

This approach does not guarantee that all words will be placed, and it does not perform advanced optimisation of the puzzle layout.  However, it produces small, playable crossword puzzles suitable for learning and casual play.

## Running the game

First, install the dependencies (only the standard Python library is needed, so there are no external requirements).  Then run the script from the command line:

```bash
python crossword_game.py
```

The script will load the database, generate a crossword and print the resulting grid and clues.  If you wish to add or modify words, edit `database.json` and re‑run the generator.

## Customising the database

The `database.json` file contains an array of objects, each representing a word and its clue.  For example:

```json
[
  { "word": "python", "clue": "A popular programming language." },
  { "word": "flask",  "clue": "A micro web framework for Python." }
]
```

When adding new entries, ensure that the `word` consists only of letters (no spaces or punctuation) and that the clue is a short phrase or sentence.  Longer words and clues make for more interesting puzzles.

## Licence

This project is provided for educational purposes and released under the MIT Licence.
