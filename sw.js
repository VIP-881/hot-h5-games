const CACHE = 'gamehub-v1';
const URLS = [
  '.',
  'index.html',
  'manifest.json',
  '2048.html', 'achievements.html', 'aimtrainer.html', 'angling.html',
  'api-clicker.html', 'api-snake.html', 'api-speedrunner.html', 'api-towerdefense.html',
  'archery.html', 'asteroids.html', 'axe.html', 'badminton.html',
  'balance.html', 'balloon.html', 'baserow-racer.html', 'battlepong.html',
  'battleship.html', 'bball.html', 'blackjack.html', 'bowling.html',
  'breakout.html', 'bubble.html', 'bubble2.html', 'bubbleshooter.html',
  'build-battle.html', 'bulls.html', 'calc24.html', 'cards.html',
  'catch.html', 'catchfruit.html', 'chick.html', 'chopper.html',
  'claw.html', 'code-typer.html', 'color.html', 'colorswitch.html',
  'commit-racer.html', 'connect4.html', 'darts.html', 'data-miner.html',
  'debug-detective.html', 'defuse.html', 'dice.html', 'dicepoker.html',
  'dino.html', 'doodlejump.html', 'draw.html', 'duel.html',
  'eat.html', 'evolve.html', 'firebase-arena.html', 'fish.html',
  'flagquiz.html', 'flappy.html', 'freethrow.html', 'frog.html',
  'frogger.html', 'fruit.html', 'gear.html', 'goldminer.html',
  'golf.html', 'gradient.html', 'guess.html', 'hangman.html',
  'hanoi.html', 'helix.html', 'hole.html', 'hoop.html',
  'horserace.html', 'http-archer.html', 'ice.html', 'invader.html',
  'jenga.html', 'jigsaw.html', 'jump.html', 'kaleido.html',
  'knife.html', 'lander.html', 'lemonade.html', 'lights.html',
  'link.html', 'magfish.html', 'marble.html', 'mastermind.html',
  'match3.html', 'math.html', 'mathchallenge.html', 'maze.html',
  'memory.html', 'merge-conflict.html', 'meteor.html', 'mines.html',
  'mole.html', 'monopoly.html', 'netlify-portal.html', 'nonogram.html',
  'numpair.html', 'numsnake.html', 'othello.html', 'pacman.html',
  'parachute.html', 'park.html', 'penalty.html', 'pet.html',
  'piano.html', 'pinball.html', 'pipeline-puzzle.html', 'pipepuzzle.html',
  'pixel.html', 'pong.html', 'puttinggolf.html', 'puzzle.html',
  'quiz.html', 'racer.html', 'range.html', 'react.html',
  'regex-challenge.html', 'rhythm.html', 'ringtoss.html', 'roll.html',
  'rope.html', 'rpg.html', 'rps.html', 'run.html',
  'sandbox.html', 'shmup.html', 'shooter.html', 'simon.html',
  'skeet.html', 'ski.html', 'sling.html', 'sling2.html',
  'slot.html', 'slots2.html', 'snake.html', 'snakewar.html',
  'sokoban.html', 'spider.html', 'spinwheel.html', 'spot.html',
  'sql-defender.html', 'stack.html', 'star-hunter.html', 'status-memory.html',
  'stopwatch.html', 'stroop.html', 'sudoku.html', 'suika.html',
  'surf.html', 'switch.html', 'tangram.html', 'tennis.html',
  'territory.html', 'tetris.html', 'tictactoe.html', 'timber.html',
  'top.html', 'towerdef.html', 'tubes.html', 'typingtest.html',
  'volley.html', 'water.html', 'wheel.html', 'word.html',
  'wordsearch.html'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => {
      return cache.addAll(URLS);
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});