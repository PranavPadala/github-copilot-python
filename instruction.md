# Sudoku Project Instructions

## Project goals
- Preserve the existing Flask application structure and public API behavior.
- Keep the Sudoku generator working with a strict unique-solution guarantee.
- Support Easy, Medium, and Hard difficulty modes without changing the route contract.
- Keep the frontend usable, responsive, and accessible while maintaining the existing visual style.

## Coding expectations
- Prefer small, reusable functions and clear module boundaries.
- Keep comments focused on non-obvious logic or rubric requirements.
- Do not add unnecessary dependencies or large framework changes.
- Preserve working behavior while improving maintainability and testability.

## Testing requirements
- Use pytest for all automated validation.
- Add or update tests for Sudoku logic, Flask routes, difficulty handling, and invalid game states.
- Verify uniqueness of generated puzzles and keep regression tests focused on real behavior.
- Run the complete suite before concluding work is complete.

## UI and gameplay constraints
- Keep the board responsive for mobile and desktop.
- Preserve alternating 3x3 square coloring and readable controls.
- Prefilled cells must remain locked/read-only.
- Keep game state consistent and handle errors gracefully.
- New Game, timer, hint, difficulty tuning, and leaderboard should all keep working together.

## Safety and project hygiene
- Do not remove required files or screenshots.
- Do not add virtual environments or generated cache directories to the final project state.
- Keep requirements.txt aligned with the libraries actually needed to run and test the app.
