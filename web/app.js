const $ = (id) => document.getElementById(id);
let current = null;
let authMode = 'login';
let busy = false;

async function api(path, payload) {
  const options = payload === undefined ? {} : {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  };
  const response = await fetch(`/api/${path}`, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'The request could not be completed.');
  return data;
}

function notify(message) {
  $('notice').textContent = message;
  $('notice').hidden = false;
}

function clearNotice() {
  $('notice').hidden = true;
}

function showView(name) {
  for (const view of ['auth', 'lobby', 'play', 'over']) {
    $(`${view}-view`).hidden = view !== name;
  }
  $('logout').hidden = name === 'auth';
}

function renderBoard(container, rows, unit) {
  container.replaceChildren();
  if (!rows?.length) {
    const empty = document.createElement('li');
    empty.className = 'board-empty';
    empty.textContent = 'No records yet. Yours could be first.';
    container.append(empty);
    return;
  }
  rows.forEach((entry, index) => {
    const row = document.createElement('li');
    const rank = document.createElement('span');
    rank.className = 'rank';
    rank.textContent = String(index + 1).padStart(2, '0');
    const name = document.createElement('span');
    name.className = 'leader-name';
    name.textContent = entry.user;
    const value = document.createElement('span');
    value.className = 'leader-value';
    value.textContent = `${entry.value} ${unit}`;
    row.append(rank, name, value);
    container.append(row);
  });
}

function render(state) {
  current = state;
  clearNotice();
  if (!state.authenticated) {
    showView('auth');
    return;
  }
  $('logout').hidden = false;
  $('lobby-user').textContent = state.user;
  $('lobby-best').textContent = `${state.best_score} pts`;
  $('lobby-level').textContent = `level ${state.max_level}`;
  $('resume-button').hidden = !state.has_saved_game;
  $('saved-copy').textContent = state.has_saved_game
    ? `Saved at level ${state.saved_level ?? state.level}, with ${state.saved_score ?? state.score} points. Resume it, or begin a fresh run.`
    : 'Start a run and see how far your instincts take you.';
  renderBoard($('score-board'), state.leaderboard?.scores, 'pts');
  renderBoard($('level-board'), state.leaderboard?.levels, 'lvl');

  if (state.phase === 'setup') {
    showView('lobby');
    return;
  }
  if (state.phase === 'game_over') {
    $('over-copy').textContent = state.feedback;
    $('over-score').textContent = `${state.score} pts`;
    $('over-level').textContent = state.level;
    $('over-best').textContent = `${state.best_score} pts`;
    $('save-message').textContent = state.save_message;
    showView('over');
    return;
  }

  showView('play');
  $('level-label').textContent = String(state.level).padStart(2, '0');
  $('big-level').textContent = String(state.level).padStart(2, '0');
  $('range-maximum').textContent = state.maximum;
  $('guess-input').max = state.maximum;
  $('live-score').replaceChildren(document.createTextNode(String(state.score)), makeSpan('pts'));
  $('stat-level').textContent = state.level;
  $('stat-best').textContent = `${state.best_score} pts`;
  $('stat-peak').textContent = state.max_level;
  $('feedback').textContent = state.feedback;
  $('feedback').className = `feedback ${state.last_result?.kind || ''}`;
  const remaining = Math.max(0, state.attempt_limit - state.attempts + 1);
  $('attempt-label').textContent = `${remaining} / ${state.attempt_limit}`;
  $('attempt-dots').setAttribute('aria-label', `${remaining} attempts remaining`);
  $('attempt-dots').replaceChildren(...Array.from({length: state.attempt_limit}, (_, index) => {
    const dot = document.createElement('i');
    if (index >= remaining) dot.className = 'used';
    return dot;
  }));
  $('guess-input').disabled = busy;
  $('guess-form').querySelector('button').disabled = busy;
  if (state.last_result?.kind === 'correct') {
    $('guess-panel').classList.remove('pulse');
    requestAnimationFrame(() => $('guess-panel').classList.add('pulse'));
  }
}

function makeSpan(text) {
  const span = document.createElement('span');
  span.textContent = text;
  return span;
}

async function act(path, payload) {
  if (busy) return;
  busy = true;
  $('guess-input').disabled = true;
  $('guess-form').querySelector('button').disabled = true;
  try {
    render(await api(path, payload));
    if (current.phase === 'playing' && path === 'guess') {
      $('guess-input').value = '';
      $('guess-input').focus({preventScroll: true});
    }
  } catch (error) {
    notify(error.message);
  } finally {
    busy = false;
    if (current?.phase === 'playing') {
      $('guess-input').disabled = false;
      $('guess-form').querySelector('button').disabled = false;
    }
  }
}

function setAuthMode(mode) {
  authMode = mode;
  const registering = mode === 'register';
  $('login-tab').setAttribute('aria-selected', String(!registering));
  $('register-tab').setAttribute('aria-selected', String(registering));
  $('name-fields').hidden = !registering;
  $('name-fields').querySelectorAll('input').forEach(input => { input.required = registering; });
  $('password-help').hidden = !registering;
  $('auth-title').textContent = registering ? 'Make it yours.' : 'Welcome back.';
  $('auth-subtitle').textContent = registering ? 'Create an account to save your progress.' : 'Sign in to continue your game.';
  $('auth-submit-label').textContent = registering ? 'Create account' : 'Sign in';
  $('auth-form').elements.password.autocomplete = registering ? 'new-password' : 'current-password';
}

$('login-tab').addEventListener('click', () => setAuthMode('login'));
$('register-tab').addEventListener('click', () => setAuthMode('register'));
$('auth-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (busy) return;
  const form = new FormData(event.currentTarget);
  const payload = Object.fromEntries(form.entries());
  busy = true;
  try {
    render(await api(authMode === 'register' ? 'register' : 'login', payload));
  } catch (error) {
    notify(error.message);
  } finally {
    busy = false;
  }
});

$('new-button').addEventListener('click', () => act('new', {}));
$('resume-button').addEventListener('click', () => act('resume', {}));
$('guess-form').addEventListener('submit', event => {
  event.preventDefault();
  act('guess', {guess: $('guess-input').value});
});
$('retry-button').addEventListener('click', () => act('new', {}));
$('over-menu').addEventListener('click', () => {
  if (current) render({...current, phase: 'setup', has_saved_game: false});
});
$('back-to-lobby').addEventListener('click', () => {
  if (current) render({...current, phase: 'setup', has_saved_game: true, saved_level: current.level, saved_score: current.score});
});
$('refresh-board').addEventListener('click', async () => {
  try {
    const board = await api('leaderboard');
    renderBoard($('score-board'), board.scores, 'pts');
    renderBoard($('level-board'), board.levels, 'lvl');
  } catch (error) { notify(error.message); }
});
$('logout').addEventListener('click', async () => {
  try {
    render(await api('logout', {}));
    $('auth-form').reset();
    setAuthMode('login');
  } catch (error) { notify(error.message); }
});

$('instructions-open').addEventListener('click', () => $('instructions-dialog').showModal());
document.querySelectorAll('.dialog-close').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
$('instructions-dialog').addEventListener('click', event => {
  const dialog = event.currentTarget;
  const bounds = dialog.getBoundingClientRect();
  if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) dialog.close();
});

async function initialize() {
  try {
    render(await api('state'));
  } catch (error) {
    notify(`${error.message} Keep the Python launcher running and reload this page.`);
  }
}

initialize();