const SIZE = 9;
const LEADERBOARD_KEY = 'sudoku-top10-leaderboard';
const THEME_KEY = 'sudoku-theme';
const PLAYER_KEY = 'sudoku-player-name';

const state = {
  puzzle: [],
  solution: [],
  board: [],
  prefilled: new Set(),
  hinted: new Set(),
  hintsUsed: 0,
  difficulty: 'medium',
  timerId: null,
  startTime: null,
  elapsedSeconds: 0,
  isSolved: false,
};

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function setMessage(text, type = 'info') {
  const msg = document.getElementById('message');
  msg.textContent = text;
  msg.className = `message ${type}`;
}

function getBoardFromInputs() {
  const board = [];
  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let col = 0; col < SIZE; col++) {
      const input = document.querySelector(`.sudoku-cell[data-row="${row}"][data-col="${col}"]`);
      const value = input && input.value.trim();
      board[row][col] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

function clearTimer() {
  if (state.timerId) {
    clearInterval(state.timerId);
    state.timerId = null;
  }
}

function startTimer() {
  clearTimer();
  state.startTime = Date.now();
  state.elapsedSeconds = 0;
  document.getElementById('timer').textContent = '00:00';

  state.timerId = setInterval(() => {
    if (!state.startTime) return;
    state.elapsedSeconds = Math.floor((Date.now() - state.startTime) / 1000);
    document.getElementById('timer').textContent = formatTime(state.elapsedSeconds);
  }, 1000);
}

function stopTimer() {
  clearTimer();
  document.getElementById('timer').textContent = formatTime(state.elapsedSeconds);
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';

  for (let row = 0; row < SIZE; row++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';

    for (let col = 0; col < SIZE; col++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.inputMode = 'numeric';
      input.pattern = '[1-9]*';
      input.className = 'sudoku-cell';
      input.dataset.row = String(row);
      input.dataset.col = String(col);
      input.setAttribute('aria-label', `Row ${row + 1}, column ${col + 1}`);
      input.addEventListener('input', (event) => {
        const target = event.target;
        const value = target.value.replace(/[^1-9]/g, '').slice(0, 1);
        target.value = value;
        if (!value) {
          return;
        }
        const r = Number(target.dataset.row);
        const c = Number(target.dataset.col);
        state.board[r][c] = parseInt(value, 10);
        if (isBoardSolved()) {
          finishGame();
        }
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, solution) {
  state.puzzle = puz.map((row) => [...row]);
  state.solution = solution.map((row) => [...row]);
  state.board = puz.map((row) => [...row]);
  state.prefilled = new Set();
  state.hinted = new Set();
  state.hintsUsed = 0;
  state.isSolved = false;

  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      if (puz[row][col] !== 0) {
        state.prefilled.add(`${row}-${col}`);
      }
    }
  }

  createBoardElement();
  const inputs = document.querySelectorAll('.sudoku-cell');
  inputs.forEach((input) => {
    const row = Number(input.dataset.row);
    const col = Number(input.dataset.col);
    const value = state.board[row][col];
    input.value = value === 0 ? '' : String(value);
    input.disabled = state.prefilled.has(`${row}-${col}`) || state.hinted.has(`${row}-${col}`);
    input.classList.toggle('prefilled', state.prefilled.has(`${row}-${col}`));
    input.classList.toggle('hinted', state.hinted.has(`${row}-${col}`));
  });

  document.getElementById('hints-used').textContent = '0';
  setMessage('');
  startTimer();
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  state.difficulty = difficulty;
  try {
    const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Unable to load a new puzzle');
    }
    renderPuzzle(data.puzzle, data.solution);
  } catch (error) {
    setMessage(error.message, 'error');
  }
}

function isBoardSolved() {
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      if (state.board[row][col] !== state.solution[row][col]) {
        return false;
      }
    }
  }
  return true;
}

function finishGame() {
  if (state.isSolved) {
    return;
  }
  state.isSolved = true;
  stopTimer();
  setMessage(`Congratulations! Puzzle solved in ${formatTime(state.elapsedSeconds)} with ${state.hintsUsed} hint(s).`, 'success');
  openLeaderboardModal();
}

function openLeaderboardModal() {
  const modal = document.getElementById('leaderboard-modal');
  const input = document.getElementById('player-name');
  const existingName = localStorage.getItem(PLAYER_KEY) || 'Player';

  input.value = existingName;
  modal.classList.remove('hidden');
  modal.setAttribute('aria-hidden', 'false');
  input.focus();
  input.select();
}

function closeLeaderboardModal() {
  const modal = document.getElementById('leaderboard-modal');
  modal.classList.add('hidden');
  modal.setAttribute('aria-hidden', 'true');
  document.getElementById('leaderboard-form').reset();
}

function saveLeaderboardEntry(playerNameOverride = null) {
  const submittedName = (playerNameOverride || document.getElementById('player-name').value || localStorage.getItem(PLAYER_KEY) || 'Player').trim();
  const playerName = submittedName || localStorage.getItem(PLAYER_KEY) || 'Player';
  localStorage.setItem(PLAYER_KEY, playerName);

  const leaderboard = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || '[]');
  leaderboard.push({
    playerName,
    completionTime: formatTime(state.elapsedSeconds),
    difficulty: state.difficulty,
    hintsUsed: state.hintsUsed,
    timeSeconds: state.elapsedSeconds,
  });

  leaderboard.sort((left, right) => {
    if (left.timeSeconds !== right.timeSeconds) {
      return left.timeSeconds - right.timeSeconds;
    }
    return left.hintsUsed - right.hintsUsed;
  });

  const trimmed = leaderboard.slice(0, 10);
  localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(trimmed));
  renderLeaderboard();
  closeLeaderboardModal();
  setMessage(`Saved to the leaderboard: ${playerName} finished in ${formatTime(state.elapsedSeconds)}.`, 'success');
}

function renderLeaderboard() {
  const leaderboardList = document.getElementById('leaderboard-list');
  const leaderboard = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || '[]');

  leaderboardList.innerHTML = '';
  if (!leaderboard.length) {
    const item = document.createElement('li');
    item.textContent = 'No records yet';
    leaderboardList.appendChild(item);
    return;
  }

  leaderboard.forEach((record, index) => {
    const item = document.createElement('li');
    const details = document.createElement('span');
    details.textContent = `#${index + 1} ${record.playerName}`;
    const time = document.createElement('span');
    time.textContent = record.completionTime;
    item.appendChild(details);
    item.appendChild(time);
    item.title = `${record.difficulty} • ${record.hintsUsed} hint(s)`;
    leaderboardList.appendChild(item);
  });
}

async function checkSolution() {
  if (!state.solution.length) {
    setMessage('No game in progress.', 'error');
    return;
  }

  const board = getBoardFromInputs();
  try {
    const res = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Check failed');
    }

    const incorrect = new Set(data.incorrect.map(([row, col]) => `${row}-${col}`));
    const inputs = document.querySelectorAll('.sudoku-cell');
    inputs.forEach((input) => {
      if (state.prefilled.has(`${input.dataset.row}-${input.dataset.col}`) || state.hinted.has(`${input.dataset.row}-${input.dataset.col}`)) {
        input.classList.remove('incorrect');
        return;
      }
      input.classList.toggle('incorrect', incorrect.has(`${input.dataset.row}-${input.dataset.col}`));
    });

    if (incorrect.size === 0) {
      finishGame();
      return;
    }
    setMessage('Some cells are incorrect.', 'error');
  } catch (error) {
    setMessage(error.message, 'error');
  }
}

async function requestHint() {
  if (!state.solution.length) {
    setMessage('No game in progress.', 'error');
    return;
  }

  const board = getBoardFromInputs();
  try {
    const res = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'No hint is available');
    }

    if (data.solved === true) {
      state.board = state.solution.map((row) => [...row]);
      finishGame();
      return;
    }

    const row = Number(data.row);
    const col = Number(data.col);
    if (!Number.isInteger(row) || !Number.isInteger(col) || Number.isNaN(row) || Number.isNaN(col)) {
      state.board = state.solution.map((rowData) => [...rowData]);
      finishGame();
      return;
    }

    const key = `${row}-${col}`;
    state.board[row][col] = Number(data.value);
    state.hinted.add(key);
    state.hintsUsed += 1;
    document.getElementById('hints-used').textContent = String(state.hintsUsed);

    const input = document.querySelector(`.sudoku-cell[data-row="${row}"][data-col="${col}"]`);
    if (input) {
      input.value = String(data.value);
      input.disabled = true;
      input.classList.add('hinted');
      input.classList.remove('incorrect');
    }

    if (isBoardSolved()) {
      finishGame();
      return;
    }

    setMessage('Hint applied.', 'info');
  } catch (error) {
    setMessage(error.message, 'error');
  }
}

function applyTheme(theme) {
  document.body.classList.toggle('dark-mode', theme === 'dark');
  localStorage.setItem(THEME_KEY, theme);
  const toggle = document.getElementById('theme-toggle');
  toggle.textContent = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
}

function setInitialTheme() {
  const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
  applyTheme(savedTheme);
}

window.addEventListener('load', () => {
  setInitialTheme();
  renderLeaderboard();

  document.getElementById('new-game').addEventListener('click', () => {
    closeLeaderboardModal();
    newGame();
  });
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('theme-toggle').addEventListener('click', () => {
    const nextTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
    applyTheme(nextTheme);
  });
  document.getElementById('leaderboard-form').addEventListener('submit', (event) => {
    event.preventDefault();
    saveLeaderboardEntry(document.getElementById('player-name').value);
  });
  document.getElementById('leaderboard-cancel').addEventListener('click', () => {
    closeLeaderboardModal();
  });

  newGame();
});