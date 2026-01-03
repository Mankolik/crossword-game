#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crossword_game.py

This module contains a simple crossword puzzle generator and a command‑line
interface for creating and displaying puzzles.  It reads a JSON database of
words and clues, selects a subset at random, and attempts to lay them out on
a square grid so that they intersect like a traditional crossword.  The
resulting grid, along with the across and down clues, is printed to the
terminal.

The generator uses a basic greedy algorithm: it places the longest word
horizontally in the centre of the grid, then tries to cross subsequent words
with the letters already on the grid.  Words that cannot be placed are
skipped.  While this approach does not produce perfect puzzles, it yields
usable crosswords for educational purposes without complex search.

To run the script, simply execute it from the command line:

    python crossword_game.py

It will load the word database, generate a crossword and output the grid
and clues.
"""

import json
import random
import os
from typing import List, Tuple, Dict, Optional


class WordEntry:
    """Represents a single word and its clue."""
    def __init__(self, word: str, clue: str):
        self.word = word.upper()
        self.clue = clue


class PlacedWord:
    """Represents a word placed on the crossword grid."""
    def __init__(self, entry: WordEntry, row: int, col: int, direction: int):
        # direction: 0 = horizontal, 1 = vertical
        self.entry = entry
        self.row = row
        self.col = col
        self.direction = direction



def load_database(filepath: str) -> List[WordEntry]:
    """Load the word database from a JSON file and return a list of WordEntry objects."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entries = []
    for item in data:
        word = item.get('word', '').strip().lower()
        clue = item.get('clue', '').strip()
        # Skip entries with invalid words
        if word and word.isalpha():
            entries.append(WordEntry(word, clue))
    return entries



def select_words(entries: List[WordEntry], max_words: int = 10) -> List[WordEntry]:
    """Randomly select up to max_words entries from the database."""
    # Shuffle the entries and return the first max_words
    random.shuffle(entries)
    return entries[:max_words]



def initialise_grid(size: int) -> List[List[Optional[str]]]:
    """Create an empty crossword grid of the given size."""
    return [[None for _ in range(size)] for _ in range(size)]



def can_place(word: str, row: int, col: int, direction: int, grid: List[List[Optional[str]]]) -> bool:
    """
    Check whether a word can be placed at the given position and direction on the grid.

    Args:
        word: The word to place (uppercase).
        row: The starting row index.
        col: The starting column index.
        direction: 0 for horizontal, 1 for vertical.
        grid: The crossword grid.

    Returns:
        True if placement is possible, otherwise False.
    """
    size = len(grid)
    for i, ch in enumerate(word):
        r = row + (direction == 1) * i
        c = col + (direction == 0) * i
        # Check bounds
        if r < 0 or r >= size or c < 0 or c >= size:
            return False
        # Check conflict with existing letters
        existing = grid[r][c]
        if existing is not None and existing != ch:
            return False
        # Check adjacency (simple version): make sure that adjacent cells
        # perpendicular to the direction of the word do not form illegal words
        if existing is None:
            # Check above and below for horizontal word or left and right for vertical
            if direction == 0:  # horizontal
                # Check above
                if r > 0 and grid[r - 1][c] is not None:
                    return False
                # Check below
                if r < size - 1 and grid[r + 1][c] is not None:
                    return False
            else:  # vertical
                # Check left
                if c > 0 and grid[r][c - 1] is not None:
                    return False
                # Check right
                if c < size - 1 and grid[r][c + 1] is not None:
                    return False
    # Check boundaries at ends of the word (prevent immediate adjacency to another word)
    if direction == 0:  # horizontal
        # cell before the start
        if col > 0 and grid[row][col - 1] is not None:
            return False
        # cell after the end
        end_c = col + len(word)
        if end_c < size and grid[row][end_c] is not None:
            return False
    else:  # vertical
        # cell above the start
        if row > 0 and grid[row - 1][col] is not None:
            return False
        # cell below the end
        end_r = row + len(word)
        if end_r < size and grid[end_r][col] is not None:
            return False
    return True



def place_word(word: str, row: int, col: int, direction: int, grid: List[List[Optional[str]]]):
    """Place a word on the grid at the specified position and direction."""
    for i, ch in enumerate(word):
        r = row + (direction == 1) * i
        c = col + (direction == 0) * i
        grid[r][c] = ch



def try_place_word(entry: WordEntry, placed: List[PlacedWord], grid: List[List[Optional[str]]]) -> Optional[PlacedWord]:
    """
    Try to place a new word on the grid by crossing it with existing words.

    Args:
        entry: The WordEntry to place.
        placed: A list of already placed words on the grid.
        grid: The current grid.

    Returns:
        A PlacedWord instance if the word was placed, otherwise None.
    """
    word = entry.word
    # For each letter in the new word, try to cross with existing words
    for placed_word in placed:
        pw = placed_word.entry.word
        for i, pw_ch in enumerate(pw):
            for j, ch in enumerate(word):
                if pw_ch != ch:
                    continue
                # Determine placement position depending on placed word direction
                if placed_word.direction == 0:  # existing word is horizontal, so new word should be vertical
                    row = placed_word.row - j
                    col = placed_word.col + i
                    direction = 1
                else:  # existing word is vertical, new word will be horizontal
                    row = placed_word.row + i
                    col = placed_word.col - j
                    direction = 0
                # Check placement
                if can_place(word, row, col, direction, grid):
                    place_word(word, row, col, direction, grid)
                    return PlacedWord(entry, row, col, direction)
    return None



def generate_crossword(entries: List[WordEntry], size: int = 13, max_words: int = 10) -> Tuple[List[List[Optional[str]]], List[PlacedWord]]:
    """
    Generate a crossword grid and return the grid along with the list of placed words.

    Args:
        entries: The list of WordEntry objects to choose from.
        size: The size of the square grid.
        max_words: The maximum number of words to place.

    Returns:
        A tuple containing the grid and a list of PlacedWord objects.
    """
    # Randomly select words
    selected = select_words(entries, max_words)
    # Sort words by length descending to place longer words first
    selected.sort(key=lambda e: len(e.word), reverse=True)

    grid = initialise_grid(size)
    placed_words: List[PlacedWord] = []

    # Place the first word horizontally in the middle row
    if selected:
        first = selected.pop(0)
        word_len = len(first.word)
        row = size // 2
        col = max(0, (size - word_len) // 2)
        if can_place(first.word, row, col, 0, grid):
            place_word(first.word, row, col, 0, grid)
            placed_words.append(PlacedWord(first, row, col, 0))
    # Try to place the remaining words
    for entry in selected:
        pw = try_place_word(entry, placed_words, grid)
        if pw:
            placed_words.append(pw)
        # If not placed, skip
    return grid, placed_words



def number_grid(grid: List[List[Optional[str]]], placed_words: List[PlacedWord]) -> Tuple[Dict[int, Tuple[int, int]], Dict[int, str], Dict[int, str]]:
    """
    Assign numbers to starting positions of across and down answers.

    Args:
        grid: The crossword grid.
        placed_words: List of placed words on the grid.

    Returns:
        A tuple containing:
            numbers: mapping from number to (row, col) coordinates.
            across: mapping from number to clue for across words.
            down: mapping from number to clue for down words.
    """
    size = len(grid)
    numbers: Dict[int, Tuple[int, int]] = {}
    across: Dict[int, str] = {}
    down: Dict[int, str] = {}
    num = 1
    # Create a quick lookup from coordinates to PlacedWord
    placed_lookup: Dict[Tuple[int, int], List[PlacedWord]] = {}
    for pw in placed_words:
        word = pw.entry.word
        for i in range(len(word)):
            r = pw.row + (pw.direction == 1) * i
            c = pw.col + (pw.direction == 0) * i
            placed_lookup.setdefault((r, c), []).append(pw)
    # Determine starting positions
    for r in range(size):
        for c in range(size):
            ch = grid[r][c]
            if ch is None:
                continue
            # Check if this is the start of an across word
            start_across = False
            start_down = False
            # Across: if at left edge or cell to left is empty, and cell to right is letter
            if c == 0 or grid[r][c - 1] is None:
                # ensure there is at least one more letter to the right to make a word (length>1)
                if c + 1 < size and grid[r][c + 1] is not None:
                    start_across = True
            # Down: if at top edge or cell above is empty, and cell below is letter
            if r == 0 or grid[r - 1][c] is None:
                if r + 1 < size and grid[r + 1][c] is not None:
                    start_down = True
            if start_across or start_down:
                numbers[num] = (r, c)
                # Determine which placed word corresponds to this start cell and direction
                if start_across:
                    # Find the placed word that is horizontal and has this start
                    for pw in placed_words:
                        if pw.direction == 0 and pw.row == r and pw.col == c:
                            across[num] = pw.entry.clue
                            break
                if start_down:
                    for pw in placed_words:
                        if pw.direction == 1 and pw.row == r and pw.col == c:
                            down[num] = pw.entry.clue
                            break
                num += 1
    return numbers, across, down



def print_crossword(grid: List[List[Optional[str]]], numbers: Dict[int, Tuple[int, int]], across: Dict[int, str], down: Dict[int, str]):
    """Print the crossword grid and the lists of across and down clues."""
    size = len(grid)
    # Create a reverse lookup for numbers
    number_lookup: Dict[Tuple[int, int], int] = {pos: n for n, pos in numbers.items()}
    print("\nCrossword Grid:\n")
    for r in range(size):
        row_str = ''
        for c in range(size):
            ch = grid[r][c]
            if ch is None:
                row_str += ' . '
            else:
                # If this cell has a number, prefix with number inside brackets
                num = number_lookup.get((r, c))
                if num is not None:
                    # Print number padded to 2 digits for alignment
                    row_str += f"[{num:2}]"
                else:
                    row_str += f" {ch} "
        print(row_str)
    print("\nAcross:")
    for num in sorted(across.keys()):
        print(f"{num}. {across[num]}")
    print("\nDown:")
    for num in sorted(down.keys()):
        print(f"{num}. {down[num]}")



def main():
    # Determine the path to the database relative to this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    db_path = os.path.join(script_dir, 'database.json')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")
    entries = load_database(db_path)
    if not entries:
        print("No valid words found in the database.  Please populate database.json.")
        return
    # Generate the crossword
    grid, placed_words = generate_crossword(entries, size=13, max_words=13)
    # Number the grid and get clues
    numbers, across, down = number_grid(grid, placed_words)
    # Print the result
    print_crossword(grid, numbers, across, down)


if __name__ == '__main__':
    main()
