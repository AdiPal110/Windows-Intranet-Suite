#!/usr/bin/env python3
"""
Multi-Game Browser Server with Desktop UI
A Flask-based web server hosting 5 games with adaptive desktop/mobile controls
Includes desktop UI with start/stop buttons and console logging
"""

import sys
import threading
import socket
import json
import time
from flask import Flask, render_template_string, request
import tkinter as tk
from tkinter import scrolledtext, messagebox
import webbrowser
from werkzeug.serving import make_server

app = Flask(__name__)

# Device detection helper
def is_mobile_device(user_agent):
    """Detect if the request is from a mobile device"""
    mobile_keywords = ['android', 'iphone', 'ipad', 'mobile', 'blackberry', 'windows phone']
    return any(keyword in user_agent.lower() for keyword in mobile_keywords)

def get_local_ip():
    """Get the local IP address for LAN access"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

# Main game selection page
@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = is_mobile_device(user_agent)
    
    return render_template_string(INDEX_TEMPLATE, is_mobile=is_mobile)

# Individual game routes
@app.route('/game/<game_name>')
def game(game_name):
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = is_mobile_device(user_agent)
    
    games = {
        '2048': render_template_string(GAME_2048_TEMPLATE, is_mobile=is_mobile),
        'jumping': render_template_string(JUMPING_GAME_TEMPLATE, is_mobile=is_mobile),
        'spaceship': render_template_string(SPACESHIP_GAME_TEMPLATE, is_mobile=is_mobile),
        'snake': render_template_string(SNAKE_GAME_TEMPLATE, is_mobile=is_mobile),
        'fighting': render_template_string(FIGHTING_GAME_TEMPLATE, is_mobile=is_mobile),
        'climber': render_template_string(CLIMBER_GAME_TEMPLATE, is_mobile=is_mobile)
    }
    
    return games.get(game_name, "Game not found")

# HTML Templates embedded in Python
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LAN Game Collection</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .container {
            text-align: center;
            max-width: 800px;
            padding: 20px;
        }
        
        h1 {
            font-size: 3em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .games-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        
        .game-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            transition: transform 0.3s ease;
            cursor: pointer;
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .game-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }
        
        .game-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .game-title {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        
        .game-description {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .device-info {
            margin-top: 30px;
            font-size: 0.9em;
            opacity: 0.7;
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 2em; }
            .games-grid { grid-template-columns: 1fr; }
            .game-card { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 LAN Game Collection</h1>
        <p>Choose your game and start playing!</p>
        
        <div class="games-grid">
            <div class="game-card" onclick="location.href='/game/2048'">
                <div class="game-icon">🔢</div>
                <div class="game-title">2048</div>
                <div class="game-description">Slide tiles to reach 2048</div>
            </div>
            
            <div class="game-card" onclick="location.href='/game/jumping'">
                <div class="game-icon">🦘</div>
                <div class="game-title">Jumping Game</div>
                <div class="game-description">Jump over obstacles and collect coins in this endless runner</div>
            </div>
            
            <div class="game-card" onclick="location.href='/game/spaceship'">
                <div class="game-icon">🚀</div>
                <div class="game-title">Spaceship Shooter</div>
                <div class="game-description">Iirodum-style space combat</div>
            </div>
            
            <div class="game-card" onclick="location.href='/game/snake'">
                <div class="game-icon">🐍</div>
                <div class="game-title">Snake</div>
                <div class="game-description">Classic snake game</div>
            </div>
            
            <div class="game-card" onclick="location.href='/game/fighting'">
                <div class="game-icon">👊</div>
                <div class="game-title">Fighting Game</div>
                <div class="game-description">Combat against AI</div>
            </div>
            
            <div class="game-card" onclick="location.href='/game/climber'">
                <div class="game-icon">🔼</div>
                <div class="game-title">Bounce</div>
                <div class="game-description">Avoid Falling</div>
            </div>
        </div>
        
        <div class="device-info">
            Device: {{ 'Mobile' if is_mobile else 'Desktop' }} | 
            Controls: {{ 'Touch' if is_mobile else 'Keyboard/Mouse' }}
        </div>
    </div>
</body>
</html>
"""

GAME_2048_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>2048</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
      background: #faf8ef;
      font-family: Arial, sans-serif;
      overflow: hidden;
      touch-action: none;
    }
    .container {
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 1rem;
      text-align: center;
    }
    h1 {
      margin: 0;
      font-size: clamp(1rem, 5vw, 3rem);
    }
    .score {
      font-size: 1.2rem;
      background: #bbada0;
      color: #fff;
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      margin: 0.5rem;
    }
    .grid-container {
      width: clamp(250px, 90vmin, 400px);
      aspect-ratio: 1 / 1;
      background: #bbada0;
      padding: 0.5vmin;
      border-radius: 5px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 0.5vmin;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .grid-row {
      display: flex;
      flex: 1;
      gap: 0.5vmin;
    }
    .grid-cell {
      flex: 1;
      background: rgba(238, 228, 218, 0.35);
      border-radius: 5px;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: clamp(0.8rem, 5vmin, 2rem);
      font-weight: bold;
      color: #776e65;
      transition: background 0.2s ease, transform 0.2s ease;
      overflow: hidden;
      word-break: break-word;
    }
    .grid-cell.merged {
      animation: pop 200ms ease-in-out;
      z-index: 2;
    }
    @keyframes pop {
      0%   { transform: scale(1); }
      50%  { transform: scale(1.2); }
      100% { transform: scale(1); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>2048</h1>
    <div class="score">Score: <span id="score">0</span></div>
    <div class="grid-container" id="grid"></div>
  </div>
  <script>
    const gridSize = 4;
    let grid = [];
    let score = 0;

    const colors = {
      2: '#eee4da', 4: '#ede0c8', 8: '#f2b179',
      16: '#f59563', 32: '#f67c5f', 64: '#f65e3b',
      128: '#edcf72', 256: '#edcc61', 512: '#edc850',
      1024: '#edc53f', 2048: '#edc22e'
    };

    const container = document.getElementById('grid');
    const scoreEl = document.getElementById('score');

    function createGrid() {
      container.innerHTML = '';
      grid = [];
      for (let i = 0; i < gridSize; i++) {
        const row = [];
        const rowDiv = document.createElement('div');
        rowDiv.className = 'grid-row';
        for (let j = 0; j < gridSize; j++) {
          const cell = document.createElement('div');
          cell.className = 'grid-cell';
          rowDiv.appendChild(cell);
          row.push(0);
        }
        container.appendChild(rowDiv);
        grid.push(row);
      }
    }

    function updateGrid() {
      const rows = container.children;
      for (let i = 0; i < gridSize; i++) {
        const cells = rows[i].children;
        for (let j = 0; j < gridSize; j++) {
          const cell = cells[j];
          const value = grid[i][j];
          cell.textContent = value > 0 ? value : '';
          cell.style.background = value > 0 ? colors[value] || '#3c3a32' : 'rgba(238, 228, 218, 0.35)';
        }
      }
    }

    function addRandomTile() {
      const empty = [];
      for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
          if (grid[i][j] === 0) empty.push([i, j]);
        }
      }
      if (empty.length > 0) {
        const [i, j] = empty[Math.floor(Math.random() * empty.length)];
        grid[i][j] = Math.random() < 0.9 ? 2 : 4;
      }
    }

    function compress(row) {
      return row.filter(val => val !== 0);
    }

    function merge(row, rowEl) {
      for (let i = 0; i < row.length - 1; i++) {
        if (row[i] === row[i + 1]) {
          row[i] *= 2;
          score += row[i];
          row[i + 1] = 0;
          const cell = rowEl.children[i];
          cell.classList.add('merged');
          cell.addEventListener('animationend', () => {
            cell.classList.remove('merged');
          });
        }
      }
      return compress(row);
    }

    function moveLeft() {
      const rows = container.children;
      let moved = false;
      for (let i = 0; i < gridSize; i++) {
        const row = compress(grid[i]);
        const mergedRow = merge([...row], rows[i]);
        const newRow = [...compress(mergedRow)];
        while (newRow.length < gridSize) newRow.push(0);
        if (grid[i].toString() !== newRow.toString()) moved = true;
        grid[i] = newRow;
      }
      if (moved) {
        addRandomTile();
        updateGrid();
        updateScore();
      }
    }

    function moveRight() {
      const rows = container.children;
      let moved = false;
      for (let i = 0; i < gridSize; i++) {
        let row = [...grid[i]].reverse();
        row = compress(row);
        const mergedRow = merge([...row], rows[i]);
        let newRow = compress(mergedRow);
        while (newRow.length < gridSize) newRow.push(0);
        newRow.reverse();
        if (grid[i].toString() !== newRow.toString()) moved = true;
        grid[i] = newRow;
      }
      if (moved) {
        addRandomTile();
        updateGrid();
        updateScore();
      }
    }

    function moveUp() {
      let moved = false;
      for (let j = 0; j < gridSize; j++) {
        let col = [];
        for (let i = 0; i < gridSize; i++) col.push(grid[i][j]);
        col = compress(col);
        for (let i = 0; i < col.length - 1; i++) {
          if (col[i] === col[i + 1]) {
            col[i] *= 2;
            score += col[i];
            col[i + 1] = 0;
          }
        }
        col = compress(col);
        while (col.length < gridSize) col.push(0);
        for (let i = 0; i < gridSize; i++) {
          if (grid[i][j] !== col[i]) moved = true;
          grid[i][j] = col[i];
        }
      }
      if (moved) {
        addRandomTile();
        updateGrid();
        updateScore();
      }
    }

    function moveDown() {
      let moved = false;
      for (let j = 0; j < gridSize; j++) {
        let col = [];
        for (let i = gridSize - 1; i >= 0; i--) col.push(grid[i][j]);
        col = compress(col);
        for (let i = 0; i < col.length - 1; i++) {
          if (col[i] === col[i + 1]) {
            col[i] *= 2;
            score += col[i];
            col[i + 1] = 0;
          }
        }
        col = compress(col);
        while (col.length < gridSize) col.push(0);
        for (let i = 0; i < gridSize; i++) {
          if (grid[gridSize - 1 - i][j] !== col[i]) moved = true;
          grid[gridSize - 1 - i][j] = col[i];
        }
      }
      if (moved) {
        addRandomTile();
        updateGrid();
        updateScore();
      }
    }

    function updateScore() {
      scoreEl.textContent = score;
    }

    document.addEventListener('keydown', e => {
      switch (e.key) {
        case 'ArrowLeft': moveLeft(); break;
        case 'ArrowRight': moveRight(); break;
        case 'ArrowUp': moveUp(); break;
        case 'ArrowDown': moveDown(); break;
      }
    });

    let touchStartX = 0, touchStartY = 0;
    document.addEventListener("touchstart", e => {
      const t = e.touches[0];
      touchStartX = t.clientX;
      touchStartY = t.clientY;
    });

    document.addEventListener("touchend", e => {
      const t = e.changedTouches[0];
      const dx = t.clientX - touchStartX;
      const dy = t.clientY - touchStartY;
      if (Math.abs(dx) > Math.abs(dy)) {
        if (dx > 20) moveRight();
        else if (dx < -20) moveLeft();
      } else {
        if (dy > 20) moveDown();
        else if (dy < -20) moveUp();
      }
    });

    // Init
    createGrid();
    addRandomTile();
    addRandomTile();
    updateGrid();
    updateScore();
  </script>
</body>
</html>
"""

JUMPING_GAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Mobile Game with Bottom Controls</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <style>
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
      overflow: hidden;
      font-family: sans-serif;
      background: #f0f0f0;
    }

    #gameCanvas {
      display: block;
      background: skyblue;
      width: 100vw;
    }

    #gameArea {
      display: flex;
      flex-direction: column;
      height: 100vh;
    }

    #controlBar {
      height: 20vh; /* approx 3 fingers tall */
      min-height: 140px;
      background: black;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 20px;
      box-sizing: border-box;
      touch-action: none;
    }

    .dpad {
      display: flex;
      gap: 15px;
    }

    .btn {
      width: 60px;
      height: 60px;
      background: white;
      color: black;
      font-size: 28px;
      border-radius: 12px;
      border: none;
      touch-action: manipulation;
    }

    #scoreboard {
      position: absolute;
      top: 5px;
      left: 5px;
      color: black;
      font-size: 16px;
      z-index: 100;
      background: rgba(255,255,255,0.7);
      padding: 5px 10px;
      border-radius: 5px;
    }

    @media (min-width: 768px) {
      #controlBar {
        display: none; /* hide on desktop */
      }
    }
  </style>
</head>
<body>
  <div id="gameArea">
    <div id="scoreboard">Score: <span id="score">0</span> | Coins: <span id="coins">0</span></div>
    <canvas id="gameCanvas"></canvas>
    <div id="controlBar">
      <div class="dpad">
        <button class="btn" id="leftBtn">&lt;</button>
        <button class="btn" id="rightBtn">&gt;</button>
      </div>
      <button class="btn" id="jumpBtn">↑</button>
    </div>
  </div>

  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    function resizeCanvas() {
      const controlBarHeight = document.getElementById('controlBar').offsetHeight;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight - controlBarHeight;
    }

    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();

    // Game objects
    const player = {
      x: 50, y: 0, width: 40, height: 60,
      speed: 5, isJumping: false, velY: 0, gravity: 0.5, jumpPower: 12
    };

    const keys = { left: false, right: false };
    const obstacles = [], coins = [];
    let score = 0, coinsCollected = 0, gameOver = false, gameSpeed = 3;

    function jump() {
      if (!player.isJumping) {
        player.velY = -player.jumpPower;
        player.isJumping = true;
      }
    }

    function update() {
      if (gameOver) {
        alert(`Game Over! Score: ${score}`);
        location.reload();
        return;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Movement
      if (keys.left && player.x > 0) player.x -= player.speed;
      if (keys.right && player.x < canvas.width - player.width) player.x += player.speed;

      // Jump Physics
      player.velY += player.gravity;
      player.y += player.velY;

      if (player.y + player.height >= canvas.height) {
        player.y = canvas.height - player.height;
        player.velY = 0;
        player.isJumping = false;
      }

      // Obstacles
      for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= gameSpeed;
        ctx.fillStyle = "#8B4513";
        ctx.fillRect(obs.x, obs.y, obs.width, obs.height);

        if (player.x < obs.x + obs.width &&
            player.x + player.width > obs.x &&
            player.y < obs.y + obs.height &&
            player.y + player.height > obs.y) {
          gameOver = true;
        }

        if (obs.x + obs.width < 0) {
          obstacles.splice(i, 1);
          score++;
          document.getElementById("score").textContent = score;
        }
      }

      // Coins
      for (let i = coins.length - 1; i >= 0; i--) {
        let c = coins[i];
        c.x -= gameSpeed;
        ctx.fillStyle = "#FFD700";
        ctx.beginPath();
        ctx.arc(c.x + 10, c.y + 10, 10, 0, Math.PI * 2);
        ctx.fill();

        if (player.x < c.x + c.width &&
            player.x + player.width > c.x &&
            player.y < c.y + c.height &&
            player.y + player.height > c.y) {
          coins.splice(i, 1);
          coinsCollected++;
          document.getElementById("coins").textContent = coinsCollected;
        }

        if (c.x + c.width < 0) coins.splice(i, 1);
      }

      // Generate obstacles and coins
      if (Math.random() < 0.02) {
        obstacles.push({ x: canvas.width, y: canvas.height - 40, width: 30, height: 40 });
      }
      if (Math.random() < 0.01) {
        coins.push({ x: canvas.width, y: canvas.height - 100, width: 20, height: 20 });
      }

      // Draw player
      ctx.fillStyle = "#4CAF50";
      ctx.fillRect(player.x, player.y, player.width, player.height);
      ctx.fillStyle = "white";
      ctx.fillRect(player.x + 8, player.y + 10, 8, 8);
      ctx.fillRect(player.x + 24, player.y + 10, 8, 8);

      gameSpeed += 0.001;
      requestAnimationFrame(update);
    }

    update();

    // Button controls
    document.getElementById("leftBtn").addEventListener("touchstart", () => keys.left = true);
    document.getElementById("leftBtn").addEventListener("touchend", () => keys.left = false);

    document.getElementById("rightBtn").addEventListener("touchstart", () => keys.right = true);
    document.getElementById("rightBtn").addEventListener("touchend", () => keys.right = false);

    document.getElementById("jumpBtn").addEventListener("touchstart", jump);

    // Keyboard (desktop)
    window.addEventListener("keydown", e => {
      if (e.key === "ArrowLeft") keys.left = true;
      if (e.key === "ArrowRight") keys.right = true;
      if (e.key === "ArrowUp" || e.key === " " || e.key === "w") jump();
    });
    window.addEventListener("keyup", e => {
      if (e.key === "ArrowLeft") keys.left = false;
      if (e.key === "ArrowRight") keys.right = false;
    });
  </script>
</body>
</html>
"""

SPACESHIP_GAME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Mobile Spaceship Shooter</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      touch-action: none;
    }

    body, html {
      overflow: hidden;
      background: black;
      color: white;
      font-family: 'Arial', sans-serif;
      height: 100%;
      width: 100%;
      position: fixed;
    }

    #gameContainer {
      position: relative;
      width: 100%;
      height: 100%;
    }

    #gameCanvas {
      display: block;
      background: radial-gradient(ellipse at center, #001122 0%, #000000 100%);
      width: 100%;
      height: 100%;
    }

    #health {
      position: absolute;
      top: 10px;
      left: 10px;
      font-size: min(4vw, 18px);
      background: rgba(0, 0, 0, 0.5);
      padding: 5px 10px;
      border-radius: 5px;
      z-index: 10;
    }

    .mobile-controls {
      position: absolute;
      bottom: 3vh;
      left: 0;
      width: 100%;
      display: flex;
      justify-content: space-between;
      padding: 0 5vw;
      z-index: 100;
    }

    .control-joystick {
      width: min(20vw, 120px);
      height: min(20vw, 120px);
      background: rgba(255,255,255,0.1);
      border: min(0.5vw, 3px) solid rgba(255,255,255,0.3);
      border-radius: 50%;
      position: relative;
      touch-action: none;
    }

    .joystick-knob {
      width: min(7vw, 40px);
      height: min(7vw, 40px);
      background: rgba(255,255,255,0.8);
      border-radius: 50%;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      pointer-events: none;
    }

    .fire-btn {
      width: min(16vw, 100px);
      height: min(16vw, 100px);
      background: rgba(255,0,0,0.3);
      border: min(0.5vw, 3px) solid rgba(255,0,0,0.6);
      border-radius: 50%;
      color: white;
      font-size: min(5vw, 28px);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      touch-action: none;
      transition: transform 0.1s;
    }

    .fire-btn:active {
      transform: scale(0.9);
      background: rgba(255,0,0,0.5);
    }

    #score {
      position: absolute;
      top: 10px;
      right: 10px;
      font-size: min(4vw, 18px);
      background: rgba(0, 0, 0, 0.5);
      padding: 5px 10px;
      border-radius: 5px;
      z-index: 10;
    }

    #gameOver {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      z-index: 200;
      display: none;
    }

    #gameOver h1 {
      font-size: min(10vw, 48px);
      margin-bottom: 20px;
      color: #ff5252;
    }

    #restartBtn {
      padding: 12px 30px;
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
      font-size: min(5vw, 20px);
      cursor: pointer;
      margin-top: 20px;
    }

    .instructions {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      background: rgba(0, 0, 0, 0.7);
      padding: 20px;
      border-radius: 10px;
      max-width: 80%;
      z-index: 150;
    }

    .instructions h2 {
      margin-bottom: 15px;
      font-size: min(6vw, 24px);
      color: #4CAF50;
    }

    .instructions p {
      margin: 10px 0;
      font-size: min(4vw, 16px);
    }

    #startBtn {
      margin-top: 20px;
      padding: 10px 25px;
      background: #2196F3;
      color: white;
      border: none;
      border-radius: 5px;
      font-size: min(4.5vw, 18px);
      cursor: pointer;
    }

    @media (max-height: 500px) {
      .mobile-controls {
        bottom: 1vh;
      }
      
      .control-joystick {
        width: min(18vw, 100px);
        height: min(18vw, 100px);
      }
      
      .fire-btn {
        width: min(14vw, 80px);
        height: min(14vw, 80px);
      }
    }
  </style>
</head>
<body>
  <div id="gameContainer">
    <canvas id="gameCanvas"></canvas>
    <div id="health">Health: 100</div>
    <div id="score">Score: 0</div>
    
    <div class="instructions">
      <h2>Spaceship Shooter</h2>
      <p>← → Move your spaceship</p>
      <p>🔥 Fire at enemies</p>
      <p>Avoid enemy ships and bullets!</p>
      <button id="startBtn">Start Game</button>
    </div>
    
    <div id="gameOver">
      <h1>Game Over</h1>
      <div id="finalScore">Score: 0</div>
      <button id="restartBtn">Play Again</button>
    </div>

    <!-- Mobile controls -->
    <div class="mobile-controls">
      <div class="control-joystick" id="joystick">
        <div class="joystick-knob" id="joystickKnob"></div>
      </div>
      <div class="fire-btn" id="fireBtn">🔥</div>
    </div>
  </div>

  <script>
    // Game elements
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const healthDisplay = document.getElementById("health");
    const scoreDisplay = document.getElementById("score");
    const finalScoreDisplay = document.getElementById("finalScore");
    const gameOverScreen = document.getElementById("gameOver");
    const restartBtn = document.getElementById("restartBtn");
    const startBtn = document.getElementById("startBtn");
    const instructions = document.querySelector(".instructions");
    
    // Game state
    let gameActive = false;
    let health = 100;
    let score = 0;
    let keys = {};
    
    // Player object
    const player = {
      x: canvas.width / 2,
      y: canvas.height - 60,
      width: 40,
      height: 40,
      speed: 5,
      color: "lime",
      moving: false
    };

    // Game objects
    const bullets = [];
    const enemies = [];
    const particles = [];
    
    // Resize canvas to fit window
    function resizeCanvas() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      player.x = Math.min(player.x, canvas.width - player.width);
      player.y = canvas.height - 60;
    }
    
    // Initialize game
    function initGame() {
      health = 100;
      score = 0;
      bullets.length = 0;
      enemies.length = 0;
      particles.length = 0;
      healthDisplay.textContent = `Health: ${health}`;
      scoreDisplay.textContent = `Score: ${score}`;
      player.x = canvas.width / 2 - player.width / 2;
      gameActive = true;
      gameOverScreen.style.display = "none";
      instructions.style.display = "none";
    }
    
    // Player shooting
    function shootBullet() {
      if (!gameActive) return;
      
      bullets.push({
        x: player.x + player.width / 2 - 2,
        y: player.y,
        width: 4,
        height: 10,
        speed: 8,
        color: "yellow"
      });
    }
    
    // Spawn enemies
    function spawnEnemy() {
      if (!gameActive) return;
      
      const size = Math.random() * 20 + 30;
      enemies.push({
        x: Math.random() * (canvas.width - size),
        y: -size,
        width: size,
        height: size,
        speed: Math.random() * 1.5 + 1,
        color: `hsl(${Math.random() * 60}, 100%, 50%)`,
        health: Math.floor(size / 15)
      });
    }
    
    // Create explosion particles
    function createExplosion(x, y, color) {
      for (let i = 0; i < 15; i++) {
        particles.push({
          x: x,
          y: y,
          size: Math.random() * 5 + 2,
          speedX: (Math.random() - 0.5) * 4,
          speedY: (Math.random() - 0.5) * 4,
          color: color,
          life: 30
        });
      }
    }
    
    // Collision detection
    function checkCollision(a, b) {
      return (
        a.x < b.x + b.width &&
        a.x + a.width > b.x &&
        a.y < b.y + b.height &&
        a.y + a.height > b.y
      );
    }
    
    // Update game state
    function updateGame() {
      if (!gameActive) return;
      
      // Move player
      if (keys["ArrowLeft"] || keys["a"]) player.x -= player.speed;
      if (keys["ArrowRight"] || keys["d"]) player.x += player.speed;
      
      // Keep player in bounds
      if (player.x < 0) player.x = 0;
      if (player.x + player.width > canvas.width) {
        player.x = canvas.width - player.width;
      }
    
      // Update bullets
      for (let i = bullets.length - 1; i >= 0; i--) {
        bullets[i].y -= bullets[i].speed;
        
        // Remove bullets that go off screen
        if (bullets[i].y < 0) {
          bullets.splice(i, 1);
          continue;
        }
      }
    
      // Update enemies
      for (let i = enemies.length - 1; i >= 0; i--) {
        enemies[i].y += enemies[i].speed;
    
        // Check for player collision
        if (checkCollision(player, enemies[i])) {
          health -= 10;
          healthDisplay.textContent = `Health: ${health}`;
          createExplosion(
            enemies[i].x + enemies[i].width / 2,
            enemies[i].y + enemies[i].height / 2,
            enemies[i].color
          );
          enemies.splice(i, 1);
          
          if (health <= 0) {
            health = 0;
            gameOver();
          }
          continue;
        }
    
        // Check bullet collision
        for (let j = bullets.length - 1; j >= 0; j--) {
          if (checkCollision(bullets[j], enemies[i])) {
            enemies[i].health -= 1;
            bullets.splice(j, 1);
            
            if (enemies[i].health <= 0) {
              createExplosion(
                enemies[i].x + enemies[i].width / 2,
                enemies[i].y + enemies[i].height / 2,
                enemies[i].color
              );
              enemies.splice(i, 1);
              score += 10;
              scoreDisplay.textContent = `Score: ${score}`;
            }
            break;
          }
        }
      }
      
      // Update particles
      for (let i = particles.length - 1; i >= 0; i--) {
        particles[i].x += particles[i].speedX;
        particles[i].y += particles[i].speedY;
        particles[i].life--;
        
        if (particles[i].life <= 0) {
          particles.splice(i, 1);
        }
      }
    }
    
    // Draw game objects
    function drawGame() {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw stars in background
      drawStars();
      
      // Draw player
      drawPlayer();
      
      // Draw bullets
      drawBullets();
      
      // Draw enemies
      drawEnemies();
      
      // Draw particles
      drawParticles();
    }
    
    // Draw background stars
    function drawStars() {
      ctx.fillStyle = "white";
      for (let i = 0; i < 100; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const size = Math.random() * 2;
        ctx.fillRect(x, y, size, size);
      }
    }
    
    // Draw player spaceship
    function drawPlayer() {
      ctx.fillStyle = player.color;
      ctx.fillRect(player.x, player.y, player.width, player.height);
      
      // Draw cockpit
      ctx.fillStyle = "#00FFFF";
      ctx.fillRect(player.x + 10, player.y + 10, player.width - 20, 10);
    }
    
    // Draw bullets
    function drawBullets() {
      bullets.forEach(b => {
        ctx.fillStyle = b.color;
        ctx.fillRect(b.x, b.y, b.width, b.height);
        
        // Add glow effect
        ctx.fillStyle = "rgba(255, 255, 0, 0.3)";
        ctx.fillRect(b.x - 2, b.y - 2, b.width + 4, b.height + 4);
      });
    }
    
    // Draw enemies
    function drawEnemies() {
      enemies.forEach(e => {
        ctx.fillStyle = e.color;
        ctx.fillRect(e.x, e.y, e.width, e.height);
        
        // Draw enemy details
        ctx.fillStyle = "black";
        ctx.fillRect(e.x + 5, e.y + 5, e.width - 10, 5);
        ctx.fillRect(e.x + 5, e.y + e.height - 10, e.width - 10, 5);
      });
    }
    
    // Draw particles
    function drawParticles() {
      particles.forEach(p => {
        ctx.globalAlpha = p.life / 30;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
      });
    }
    
    // Game over function
    function gameOver() {
      gameActive = false;
      finalScoreDisplay.textContent = `Final Score: ${score}`;
      gameOverScreen.style.display = "flex";
    }
    
    // Game loop
    function gameLoop() {
      updateGame();
      drawGame();
      requestAnimationFrame(gameLoop);
    }
    
    // Event listeners
    function setupEventListeners() {
      // Window resize
      window.addEventListener("resize", resizeCanvas);
      
      // Keyboard controls
      document.addEventListener("keydown", e => {
        if (["ArrowLeft", "ArrowRight", "a", "d"].includes(e.key)) {
          keys[e.key] = true;
        }
        if (e.key === " " || e.key === "w") {
          shootBullet();
        }
      });
      
      document.addEventListener("keyup", e => {
        if (["ArrowLeft", "ArrowRight", "a", "d"].includes(e.key)) {
          keys[e.key] = false;
        }
      });
      
      // Fire button
      const fireBtn = document.getElementById("fireBtn");
      fireBtn.addEventListener("touchstart", function(e) {
        e.preventDefault();
        shootBullet();
      });
      fireBtn.addEventListener("mousedown", shootBullet);
      
      // Joystick controls
      const joystick = document.getElementById("joystick");
      const knob = document.getElementById("joystickKnob");
      let joystickCenter = { x: 0, y: 0 };
      let joystickActive = false;
      
      // Touch events
      joystick.addEventListener("touchstart", function(e) {
        e.preventDefault();
        const rect = joystick.getBoundingClientRect();
        joystickCenter = {
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2
        };
        joystickActive = true;
        updateJoystick(e.touches[0].clientX, e.touches[0].clientY);
      });
      
      joystick.addEventListener("touchmove", function(e) {
        e.preventDefault();
        if (joystickActive) {
          updateJoystick(e.touches[0].clientX, e.touches[0].clientY);
        }
      });
      
      joystick.addEventListener("touchend", function(e) {
        e.preventDefault();
        resetJoystick();
      });
      
      // Mouse events for desktop testing
      joystick.addEventListener("mousedown", function(e) {
        const rect = joystick.getBoundingClientRect();
        joystickCenter = {
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2
        };
        joystickActive = true;
        updateJoystick(e.clientX, e.clientY);
      });
      
      document.addEventListener("mousemove", function(e) {
        if (joystickActive) {
          updateJoystick(e.clientX, e.clientY);
        }
      });
      
      document.addEventListener("mouseup", function(e) {
        if (joystickActive) {
          resetJoystick();
        }
      });
      
      // Update joystick position
      function updateJoystick(x, y) {
        const dx = x - joystickCenter.x;
        const maxDistance = joystick.offsetWidth / 3;
        const distance = Math.min(maxDistance, Math.sqrt(dx * dx));
        
        const angle = Math.atan2(0, dx);
        const knobX = Math.cos(angle) * distance;
        
        knob.style.transform = `translate(${knobX}px, 0)`;
        
        // Set movement keys
        keys["ArrowLeft"] = dx < -10;
        keys["ArrowRight"] = dx > 10;
      }
      
      // Reset joystick
      function resetJoystick() {
        joystickActive = false;
        knob.style.transform = "translate(0, 0)";
        keys["ArrowLeft"] = false;
        keys["ArrowRight"] = false;
      }
      
      // Game buttons
      startBtn.addEventListener("click", function() {
        initGame();
      });
      
      restartBtn.addEventListener("click", function() {
        initGame();
      });
    }
    
    // Initialize the game
    window.onload = function() {
      resizeCanvas();
      setupEventListeners();
      gameLoop();
      setInterval(spawnEnemy, 1000);
    };
  </script>
</body>
</html>
"""

SNAKE_GAME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <title>Snake Game</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            margin: 0;
            overflow: hidden;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            touch-action: none;
            user-select: none;
            height: 100vh;
            display: flex;
            flex-direction: column;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 15px;
            flex: 1;
            display: flex;
            flex-direction: column;
            width: 100%;
        }
        
        header {
            text-align: center;
            padding: 10px 0;
            margin-bottom: 10px;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 5px;
            background: linear-gradient(to right, #ff7e5f, #feb47b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-label {
            font-size: 1rem;
            color: #a0a0c0;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #4cc9f0;
        }
        
        #game-container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        }
        
        canvas {
            background: #111;
            width: 100%;
            max-width: 100%;
            max-height: 100%;
            border: 2px solid #333;
            border-radius: 10px;
        }
        
        .overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: rgba(0, 0, 0, 0.85);
            z-index: 10;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        
        .hidden {
            display: none;
        }
        
        .overlay h2 {
            font-size: 2.2rem;
            margin-bottom: 20px;
            color: #ff7e5f;
        }
        
        .overlay p {
            font-size: 1.2rem;
            margin-bottom: 25px;
            max-width: 80%;
            line-height: 1.6;
        }
        
        .btn {
            background: linear-gradient(to right, #ff7e5f, #feb47b);
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 1.1rem;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(255, 126, 95, 0.3);
            margin: 10px 5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(255, 126, 95, 0.5);
        }
        
        .btn:active {
            transform: translateY(1px);
        }
        
        .controls {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
            width: 100%;
        }
        
        .instructions {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            font-size: 0.9rem;
            color: #a0a0c0;
        }
        
        .mobile-controls {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 10px;
            margin-top: 20px;
            max-width: 300px;
            width: 100%;
            margin: 20px auto;
        }
        
        .control-btn {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            height: 60px;
            font-size: 24px;
            border-radius: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }
        
        .control-btn:active {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0.95);
        }
        
        .up-btn { grid-column: 2; grid-row: 1; }
        .left-btn { grid-column: 1; grid-row: 2; }
        .right-btn { grid-column: 3; grid-row: 2; }
        .down-btn { grid-column: 2; grid-row: 2; }
        
        .pause-btn {
            grid-column: 2;
            grid-row: 1;
            background: rgba(76, 201, 240, 0.3);
        }
        
        .difficulty {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 15px;
        }
        
        .difficulty-btn {
            background: rgba(255, 255, 255, 0.1);
            color: #a0a0c0;
            border: none;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .difficulty-btn.active {
            background: rgba(76, 201, 240, 0.3);
            color: #4cc9f0;
        }
        
        @media (max-width: 500px) {
            h1 {
                font-size: 2rem;
            }
            
            .stat-value {
                font-size: 1.5rem;
            }
            
            .overlay h2 {
                font-size: 1.8rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Snake Game</h1>
        </header>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">SCORE</div>
                <div id="score" class="stat-value">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">HIGH SCORE</div>
                <div id="high-score" class="stat-value">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">SPEED</div>
                <div id="speed" class="stat-value">5</div>
            </div>
        </div>
        
        <div id="game-container">
            <canvas id="gameCanvas"></canvas>
            
            <div id="start-screen" class="overlay">
                <h2>Ready to Play?</h2>
                <p>Use arrow keys or swipe to control the snake. Eat food to grow and earn points. Avoid hitting walls or yourself!</p>
                <div class="difficulty">
                    <button id="easy-btn" class="difficulty-btn active">Easy</button>
                    <button id="medium-btn" class="difficulty-btn">Medium</button>
                    <button id="hard-btn" class="difficulty-btn">Hard</button>
                </div>
                <button id="start-btn" class="btn">Start Game</button>
            </div>
            
            <div id="pause-screen" class="overlay hidden">
                <h2>Game Paused</h2>
                <p>Press SPACE or the pause button to continue</p>
                <button id="resume-btn" class="btn">Resume</button>
                <button id="restart-btn" class="btn">Restart</button>
            </div>
            
            <div id="game-over-screen" class="overlay hidden">
                <h2>Game Over!</h2>
                <p>Your score: <span id="final-score">0</span></p>
                <p>High score: <span id="final-high-score">0</span></p>
                <button id="play-again-btn" class="btn">Play Again</button>
                <button id="menu-btn" class="btn">Main Menu</button>
            </div>
        </div>
        
        <div class="mobile-controls">
            <button class="control-btn up-btn">↑</button>
            <button class="control-btn left-btn">←</button>
            <button class="control-btn pause-btn">❚❚</button>
            <button class="control-btn right-btn">→</button>
            <button class="control-btn down-btn">↓</button>
        </div>
        
        <div class="instructions">
            <p>Use arrow keys or buttons to control the snake | Press SPACE or Pause button to pause</p>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const gameContainer = document.getElementById('game-container');
        
        // Game state elements
        const startScreen = document.getElementById('start-screen');
        const pauseScreen = document.getElementById('pause-screen');
        const gameOverScreen = document.getElementById('game-over-screen');
        const scoreElement = document.getElementById('score');
        const highScoreElement = document.getElementById('high-score');
        const speedElement = document.getElementById('speed');
        const finalScoreElement = document.getElementById('final-score');
        const finalHighScoreElement = document.getElementById('final-high-score');
        
        // Buttons
        const startBtn = document.getElementById('start-btn');
        const resumeBtn = document.getElementById('resume-btn');
        const restartBtn = document.getElementById('restart-btn');
        const playAgainBtn = document.getElementById('play-again-btn');
        const menuBtn = document.getElementById('menu-btn');
        
        // Difficulty buttons
        const easyBtn = document.getElementById('easy-btn');
        const mediumBtn = document.getElementById('medium-btn');
        const hardBtn = document.getElementById('hard-btn');
        
        // Mobile controls
        const upBtn = document.querySelector('.up-btn');
        const leftBtn = document.querySelector('.left-btn');
        const rightBtn = document.querySelector('.right-btn');
        const downBtn = document.querySelector('.down-btn');
        const pauseControlBtn = document.querySelector('.pause-btn');
        
        // Game settings
        const gridSize = 20;
        let tileCount;
        let baseSpeed = 5;
        let speed = baseSpeed;
        let gameSpeed = baseSpeed;
        let difficulty = 'easy';
        
        // Game state
        let snake = [];
        let direction = {x: 1, y: 0};
        let nextDirection = {x: 1, y: 0};
        let food = {x: 0, y: 0};
        let score = 0;
        let highScore = localStorage.getItem('snakeHighScore') || 0;
        let gameState = 'start'; // 'start', 'playing', 'paused', 'gameover'
        let animationId;
        let lastRenderTime = 0;
        let touchStartX, touchStartY;
        
        // Initialize game
        function init() {
            resizeCanvas();
            setupEventListeners();
            updateHighScoreDisplay();
            
            // Set initial difficulty
            setDifficulty('easy');
        }
        
        function resizeCanvas() {
            const size = Math.min(gameContainer.clientWidth, gameContainer.clientHeight * 1.2);
            canvas.width = size;
            canvas.height = size;
            tileCount = Math.floor(canvas.width / gridSize);
            
            // Reinitialize game elements if needed
            if (gameState !== 'start') {
                resetGame();
            }
        }
        
        function setupEventListeners() {
            window.addEventListener('resize', resizeCanvas);
            
            // Keyboard controls
            window.addEventListener('keydown', handleKeyDown);
            
            // Touch controls for swiping
            canvas.addEventListener('touchstart', handleTouchStart);
            canvas.addEventListener('touchend', handleTouchEnd);
            
            // Button events
            startBtn.addEventListener('click', startGame);
            resumeBtn.addEventListener('click', resumeGame);
            restartBtn.addEventListener('click', restartGame);
            playAgainBtn.addEventListener('click', restartGame);
            menuBtn.addEventListener('click', showMainMenu);
            
            // Difficulty buttons
            easyBtn.addEventListener('click', () => setDifficulty('easy'));
            mediumBtn.addEventListener('click', () => setDifficulty('medium'));
            hardBtn.addEventListener('click', () => setDifficulty('hard'));
            
            // Mobile control buttons
            upBtn.addEventListener('click', () => changeDirection(0, -1));
            leftBtn.addEventListener('click', () => changeDirection(-1, 0));
            rightBtn.addEventListener('click', () => changeDirection(1, 0));
            downBtn.addEventListener('click', () => changeDirection(0, 1));
            pauseControlBtn.addEventListener('click', togglePause);
        }
        
        function setDifficulty(level) {
            difficulty = level;
            
            // Update UI
            easyBtn.classList.remove('active');
            mediumBtn.classList.remove('active');
            hardBtn.classList.remove('active');
            
            if (level === 'easy') {
                baseSpeed = 5;
                easyBtn.classList.add('active');
            } else if (level === 'medium') {
                baseSpeed = 8;
                mediumBtn.classList.add('active');
            } else if (level === 'hard') {
                baseSpeed = 12;
                hardBtn.classList.add('active');
            }
            
            // Update speed if game is in progress
            if (gameState === 'playing') {
                updateGameSpeed();
            }
        }
        
        function startGame() {
            resetGame();
            gameState = 'playing';
            startScreen.classList.add('hidden');
            gameLoop(0);
        }
        
        function resumeGame() {
            gameState = 'playing';
            pauseScreen.classList.add('hidden');
            gameLoop(0);
        }
        
        function togglePause() {
            if (gameState === 'playing') {
                gameState = 'paused';
                pauseScreen.classList.remove('hidden');
            } else if (gameState === 'paused') {
                resumeGame();
            }
        }
        
        function restartGame() {
            resetGame();
            gameState = 'playing';
            gameOverScreen.classList.add('hidden');
            pauseScreen.classList.add('hidden');
            gameLoop(0);
        }
        
        function showMainMenu() {
            gameState = 'start';
            gameOverScreen.classList.add('hidden');
            pauseScreen.classList.add('hidden');
            startScreen.classList.remove('hidden');
        }
        
        function resetGame() {
            // Reset snake
            snake = [
                {x: Math.floor(tileCount / 2), y: Math.floor(tileCount / 2)}
            ];
            direction = {x: 1, y: 0};
            nextDirection = {x: 1, y: 0};
            
            // Reset food
            generateFood();
            
            // Reset score and speed
            score = 0;
            updateGameSpeed();
            scoreElement.textContent = score;
            
            // Reset game state
            gameOver = false;
        }
        
        function updateGameSpeed() {
            gameSpeed = baseSpeed + Math.floor(score / 40);
            speedElement.textContent = gameSpeed;
        }
        
        function generateFood() {
            // Generate new food at random position
            food = {
                x: Math.floor(Math.random() * tileCount),
                y: Math.floor(Math.random() * tileCount)
            };
            
            // Make sure food doesn't appear on snake
            let foodOnSnake = true;
            while (foodOnSnake) {
                foodOnSnake = false;
                snake.forEach(segment => {
                    if (segment.x === food.x && segment.y === food.y) {
                        foodOnSnake = true;
                        food = {
                            x: Math.floor(Math.random() * tileCount),
                            y: Math.floor(Math.random() * tileCount)
                        };
                    }
                });
            }
        }
        
        function handleKeyDown(e) {
            if (gameState === 'start' && e.key !== ' ') {
                startGame();
                return;
            }
            
            switch(e.key) {
                case 'ArrowLeft':
                    if (direction.x !== 1) nextDirection = {x: -1, y: 0};
                    break;
                case 'ArrowRight':
                    if (direction.x !== -1) nextDirection = {x: 1, y: 0};
                    break;
                case 'ArrowUp':
                    if (direction.y !== 1) nextDirection = {x: 0, y: -1};
                    break;
                case 'ArrowDown':
                    if (direction.y !== -1) nextDirection = {x: 0, y: 1};
                    break;
                case ' ':
                case 'p':
                    togglePause();
                    break;
            }
        }
        
        function changeDirection(x, y) {
            if (gameState !== 'playing') return;
            
            if ((x === -1 && direction.x !== 1) || 
                (x === 1 && direction.x !== -1) || 
                (y === -1 && direction.y !== 1) || 
                (y === 1 && direction.y !== -1)) {
                nextDirection = {x, y};
            }
        }
        
        function handleTouchStart(e) {
            if (gameState === 'start') {
                startGame();
                return;
            }
            
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            e.preventDefault();
        }
        
        function handleTouchEnd(e) {
            if (!touchStartX || !touchStartY || gameState !== 'playing') return;
            
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            
            const dx = touchEndX - touchStartX;
            const dy = touchEndY - touchStartY;
            
            // Determine swipe direction
            if (Math.abs(dx) > Math.abs(dy)) {
                if (dx > 20) {
                    if (direction.x !== -1) nextDirection = {x: 1, y: 0}; // Right
                } else if (dx < -20) {
                    if (direction.x !== 1) nextDirection = {x: -1, y: 0}; // Left
                }
            } else {
                if (dy > 20) {
                    if (direction.y !== -1) nextDirection = {x: 0, y: 1}; // Down
                } else if (dy < -20) {
                    if (direction.y !== 1) nextDirection = {x: 0, y: -1}; // Up
                }
            }
            
            touchStartX = null;
            touchStartY = null;
        }
        
        function updateHighScoreDisplay() {
            highScoreElement.textContent = highScore;
            finalHighScoreElement.textContent = highScore;
        }
        
        function update() {
            // Update direction
            direction = {...nextDirection};
            
            // Move snake
            const head = {x: snake[0].x + direction.x, y: snake[0].y + direction.y};
            
            // Check wall collision
            if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
                endGame();
                return;
            }
            
            // Check self collision
            for (let i = 0; i < snake.length; i++) {
                if (snake[i].x === head.x && snake[i].y === head.y) {
                    endGame();
                    return;
                }
            }
            
            snake.unshift(head);
            
            // Check food collision
            if (head.x === food.x && head.y === food.y) {
                score += 10;
                scoreElement.textContent = score;
                updateGameSpeed();
                generateFood();
            } else {
                snake.pop();
            }
        }
        
        function draw() {
            // Clear canvas
            ctx.fillStyle = '#111';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw grid
            ctx.strokeStyle = 'rgba(50, 50, 70, 0.3)';
            ctx.lineWidth = 0.5;
            for (let i = 0; i < tileCount; i++) {
                ctx.beginPath();
                ctx.moveTo(i * gridSize, 0);
                ctx.lineTo(i * gridSize, canvas.height);
                ctx.stroke();
                
                ctx.beginPath();
                ctx.moveTo(0, i * gridSize);
                ctx.lineTo(canvas.width, i * gridSize);
                ctx.stroke();
            }
            
            // Draw snake
            snake.forEach((segment, index) => {
                // Gradient from head (dark green) to tail (light green)
                const gradient = index / snake.length;
                const r = Math.floor(50 + 100 * gradient);
                const g = Math.floor(180 + 50 * gradient);
                const b = Math.floor(80);
                
                ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
                
                // Draw rounded segments
                ctx.beginPath();
                ctx.roundRect(
                    segment.x * gridSize + 1, 
                    segment.y * gridSize + 1, 
                    gridSize - 2, 
                    gridSize - 2,
                    5
                );
                ctx.fill();
                
                // Draw eyes on head
                if (index === 0) {
                    ctx.fillStyle = 'white';
                    
                    // Determine eye positions based on direction
                    const eyeOffsetX = direction.x !== 0 ? 4 : 0;
                    const eyeOffsetY = direction.y !== 0 ? 4 : 0;
                    
                    // Left eye
                    ctx.beginPath();
                    ctx.arc(
                        segment.x * gridSize + (gridSize / 2) - (direction.x * 3) - eyeOffsetX, 
                        segment.y * gridSize + (gridSize / 2) - (direction.y * 3) - eyeOffsetY, 
                        2, 
                        0, 
                        Math.PI * 2
                    );
                    ctx.fill();
                    
                    // Right eye
                    ctx.beginPath();
                    ctx.arc(
                        segment.x * gridSize + (gridSize / 2) + (direction.x * 3) - eyeOffsetX, 
                        segment.y * gridSize + (gridSize / 2) + (direction.y * 3) - eyeOffsetY, 
                        2, 
                        0, 
                        Math.PI * 2
                    );
                    ctx.fill();
                }
            });
            
            // Draw food (apple)
            ctx.fillStyle = '#ff5252';
            ctx.beginPath();
            ctx.arc(
                food.x * gridSize + gridSize / 2, 
                food.y * gridSize + gridSize / 2, 
                gridSize / 2 - 2, 
                0, 
                Math.PI * 2
            );
            ctx.fill();
            
            // Draw stem
            ctx.fillStyle = '#3d8d40';
            ctx.beginPath();
            ctx.moveTo(food.x * gridSize + gridSize / 2, food.y * gridSize + 3);
            ctx.lineTo(food.x * gridSize + gridSize / 2 - 3, food.y * gridSize - 1);
            ctx.lineTo(food.x * gridSize + gridSize / 2 + 3, food.y * gridSize - 1);
            ctx.closePath();
            ctx.fill();
            
            // Draw border
            ctx.strokeStyle = '#4cc9f0';
            ctx.lineWidth = 2;
            ctx.strokeRect(1, 1, canvas.width - 2, canvas.height - 2);
        }
        
        function endGame() {
            gameState = 'gameover';
            
            // Update high score if needed
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('snakeHighScore', highScore);
                updateHighScoreDisplay();
            }
            
            // Update final score display
            finalScoreElement.textContent = score;
            
            // Show game over screen
            gameOverScreen.classList.remove('hidden');
        }
        
        function gameLoop(currentTime) {
            if (gameState !== 'playing') return;
            
            // Calculate time since last render
            const secondsSinceLastRender = (currentTime - lastRenderTime) / 1000;
            
            // Only update at specified speed (frames per second)
            if (secondsSinceLastRender < 1 / gameSpeed) {
                animationId = requestAnimationFrame(gameLoop);
                return;
            }
            
            lastRenderTime = currentTime;
            
            update();
            draw();
            
            animationId = requestAnimationFrame(gameLoop);
        }
        
        // Initialize canvas rounded rectangle function
        if (CanvasRenderingContext2D.prototype.roundRect === undefined) {
            CanvasRenderingContext2D.prototype.roundRect = function(x, y, width, height, radius) {
                if (width < 2 * radius) radius = width / 2;
                if (height < 2 * radius) radius = height / 2;
                
                this.beginPath();
                this.moveTo(x + radius, y);
                this.arcTo(x + width, y, x + width, y + height, radius);
                this.arcTo(x + width, y + height, x, y + height, radius);
                this.arcTo(x, y + height, x, y, radius);
                this.arcTo(x, y, x + width, y, radius);
                this.closePath();
                return this;
            };
        }
        
        // Initialize the game
        init();
    </script>
</body>
</html>
"""

FIGHTING_GAME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fighting Game</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(to bottom, #87CEEB, #DEB887);
            overflow: hidden;
            font-family: Arial, sans-serif;
        }
        
        #gameCanvas {
            display: block;
            margin: 0 auto;
            border: 3px solid #8B4513;
            background: linear-gradient(to bottom, #87CEEB 0%, #87CEEB 70%, #DEB887 70%, #CD853F 100%);
        }
        
        .back-btn {
            position: absolute;
            top: 10px;
            left: 10px;
            background: #8B4513;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            z-index: 100;
        }
        
        .hud {
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 20px;
            z-index: 100;
        }
        
        .health-bar {
            width: 200px;
            height: 20px;
            background: #333;
            border: 2px solid #000;
            border-radius: 10px;
            overflow: hidden;
        }
        
        .health-fill {
            height: 100%;
            transition: width 0.3s ease;
            border-radius: 8px;
        }
        
        .player-health { background: #00FF00; }
        .ai-health { background: #FF0000; }
        
        .player-info, .ai-info {
            text-align: center;
            color: white;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }
        
        .mobile-controls {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: {{ 'flex' if is_mobile else 'none' }};
            gap: 15px;
            z-index: 100;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .control-btn {
            background: rgba(139, 69, 19, 0.8);
            color: white;
            border: none;
            padding: 12px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            min-width: 60px;
            touch-action: manipulation;
        }
        
        .control-btn:active {
            background: rgba(139, 69, 19, 1);
            transform: scale(0.95);
        }
        
        .move-controls {
            display: flex;
            gap: 5px;
        }
        
        .action-controls {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .instructions {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            text-align: center;
            display: {{ 'none' if is_mobile else 'block' }};
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }
        
        .game-result {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            display: none;
            z-index: 200;
            border: 3px solid #8B4513;
        }
        
        .restart-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            margin-top: 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        
        .combo-display {
            position: absolute;
            top: 100px;
            right: 20px;
            color: #FFD700;
            font-weight: bold;
            font-size: 18px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            z-index: 100;
        }
    </style>
</head>
<body>
    <a href="/" class="back-btn">← Back</a>
    
    <div class="hud">
        <div class="player-info">
            <div>Player</div>
            <div class="health-bar">
                <div class="health-fill player-health" id="playerHealth" style="width: 100%;"></div>
            </div>
        </div>
        <div class="ai-info">
            <div>AI Opponent</div>
            <div class="health-bar">
                <div class="health-fill ai-health" id="aiHealth" style="width: 100%;"></div>
            </div>
        </div>
    </div>
    
    <div class="combo-display" id="comboDisplay"></div>
    
    <canvas id="gameCanvas" width="800" height="500"></canvas>
    
    {% if is_mobile %}
    <div class="mobile-controls">
        <div class="control-group">
            <div class="move-controls">
                <button class="control-btn" id="leftBtn">←</button>
                <button class="control-btn" id="rightBtn">→</button>
            </div>
            <button class="control-btn" id="jumpBtn">Jump</button>
        </div>
        <div class="control-group">
            <div class="action-controls">
                <button class="control-btn" id="punchBtn">Punch</button>
                <button class="control-btn" id="kickBtn">Kick</button>
                <button class="control-btn" id="blockBtn">Block</button>
            </div>
        </div>
    </div>
    {% else %}
    <div class="instructions">
        AD/Arrow Keys: Move | W/Space: Jump | J: Punch | K: Kick | S: Block
    </div>
    {% endif %}
    
    <div class="game-result" id="gameResult">
        <h2 id="resultTitle">Round Over!</h2>
        <p id="resultMessage">Good fight!</p>
        <button class="restart-btn" onclick="game.restart()">Next Round</button>
    </div>
    
    <script>
        class FightingGame {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.isMobile = {{ 'true' if is_mobile else 'false' }};
                
                // Game settings
                this.gravity = 0.8;
                this.ground = this.canvas.height - 50;
                
                // Player
                this.player = {
                    x: 150,
                    y: this.ground - 80,
                    width: 40,
                    height: 80,
                    velX: 0,
                    velY: 0,
                    speed: 5,
                    jumpPower: 16,
                    onGround: true,
                    health: 100,
                    maxHealth: 100,
                    facing: 1,
                    color: '#0066CC',
                    
                    // Combat properties
                    attacking: false,
                    blocking: false,
                    attackCooldown: 0,
                    blockCooldown: 0,
                    stunned: 0,
                    
                    // Animation
                    animFrame: 0,
                    animTimer: 0
                };
                
                // AI Opponent
                this.ai = {
                    x: 600,
                    y: this.ground - 80,
                    width: 40,
                    height: 80,
                    velX: 0,
                    velY: 0,
                    speed: 3,
                    jumpPower: 14,
                    onGround: true,
                    health: 100,
                    maxHealth: 100,
                    facing: -1,
                    color: '#CC0066',
                    
                    // Combat properties
                    attacking: false,
                    blocking: false,
                    attackCooldown: 0,
                    blockCooldown: 0,
                    stunned: 0,
                    
                    // AI behavior
                    behavior: 'aggressive', // aggressive, defensive, balanced
                    actionTimer: 0,
                    lastAction: 'none',
                    
                    // Animation
                    animFrame: 0,
                    animTimer: 0
                };
                
                // Game state
                this.gameRunning = true;
                this.round = 1;
                this.combo = 0;
                this.comboTimer = 0;
                
                // Input handling
                this.keys = {};
                this.setupControls();
                
                // Particle effects
                this.particles = [];
                
                // Start game loop
                this.gameLoop();
            }
            
            setupControls() {
                if (this.isMobile) {
                    this.setupTouchControls();
                } else {
                    this.setupKeyboardControls();
                }
            }
            
            setupTouchControls() {
                document.getElementById('leftBtn').addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    this.keys.left = true;
                });
                document.getElementById('leftBtn').addEventListener('touchend', (e) => {
                    e.preventDefault();
                    this.keys.left = false;
                });
                
                document.getElementById('rightBtn').addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    this.keys.right = true;
                });
                document.getElementById('rightBtn').addEventListener('touchend', (e) => {
                    e.preventDefault();
                    this.keys.right = false;
                });
                
                document.getElementById('jumpBtn').addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    this.jump();
                });
                
                document.getElementById('punchBtn').addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    this.punch();
                });
                
                document.getElementById('kickBtn').addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    this.kick();
                });
                
                document.getElementById('blockBtn').addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    this.keys.block = true;
                });
                document.getElementById('blockBtn').addEventListener('touchend', (e) => {
                    e.preventDefault();
                    this.keys.block = false;
                });
            }
            
            setupKeyboardControls() {
                document.addEventListener('keydown', (e) => {
                    switch(e.key.toLowerCase()) {
                        case 'a':
                        case 'arrowleft':
                            this.keys.left = true;
                            break;
                        case 'd':
                        case 'arrowright':
                            this.keys.right = true;
                            break;
                        case 'w':
                        case ' ':
                            e.preventDefault();
                            this.jump();
                            break;
                        case 'j':
                            this.punch();
                            break;
                        case 'k':
                            this.kick();
                            break;
                        case 's':
                        case 'arrowdown':
                            this.keys.block = true;
                            break;
                    }
                });
                
                document.addEventListener('keyup', (e) => {
                    switch(e.key.toLowerCase()) {
                        case 'a':
                        case 'arrowleft':
                            this.keys.left = false;
                            break;
                        case 'd':
                        case 'arrowright':
                            this.keys.right = false;
                            break;
                        case 's':
                        case 'arrowdown':
                            this.keys.block = false;
                            break;
                    }
                });
            }
            
            jump() {
                if (this.player.onGround && this.gameRunning && this.player.stunned <= 0) {
                    this.player.velY = -this.player.jumpPower;
                    this.player.onGround = false;
                }
            }
            
            punch() {
                if (this.gameRunning && this.player.attackCooldown <= 0 && this.player.stunned <= 0) {
                    this.player.attacking = 'punch';
                    this.player.attackCooldown = 30;
                    this.checkHit('punch', 15);
                }
            }
            
            kick() {
                if (this.gameRunning && this.player.attackCooldown <= 0 && this.player.stunned <= 0) {
                    this.player.attacking = 'kick';
                    this.player.attackCooldown = 45;
                    this.checkHit('kick', 25);
                }
            }
            
            checkHit(attackType, damage) {
                const player = this.player;
                const ai = this.ai;
                
                // Calculate attack range
                const attackRange = attackType === 'kick' ? 60 : 50;
                const distance = Math.abs(player.x - ai.x);
                
                if (distance < attackRange) {
                    let actualDamage = damage;
                    
                    // Check if AI is blocking
                    if (ai.blocking) {
                        actualDamage = Math.floor(damage * 0.3);
                        this.createParticles(ai.x, ai.y + 40, '#FFFF00', 'block');
                    } else {
                        this.createParticles(ai.x, ai.y + 40, '#FF0000', 'hit');
                        ai.stunned = 20;
                        
                        // Combo system
                        this.combo++;
                        this.comboTimer = 60;
                        actualDamage += Math.floor(this.combo * 2);
                    }
                    
                    ai.health -= actualDamage;
                    ai.health = Math.max(0, ai.health);
                    
                    // Knockback
                    ai.velX = player.facing * 3;
                    
                    this.updateHealthBars();
                    
                    if (ai.health <= 0) {
                        this.endRound(true);
                    }
                }
            }
            
            updateAI() {
                const ai = this.ai;
                const player = this.player;
                
                if (ai.stunned > 0) {
                    ai.stunned--;
                    return;
                }
                
                ai.actionTimer--;
                
                const distance = Math.abs(ai.x - player.x);
                const isPlayerAttacking = player.attacking;
                
                // Update facing direction
                ai.facing = ai.x > player.x ? -1 : 1;
                
                // AI Decision making
                if (ai.actionTimer <= 0) {
                    const randomFactor = Math.random();
                    
                    if (isPlayerAttacking && distance < 70 && randomFactor > 0.3) {
                        // Try to block incoming attacks
                        ai.blocking = true;
                        ai.blockCooldown = 20;
                        ai.actionTimer = 30;
                    } else if (distance > 100) {
                        // Move closer
                        ai.keys = {move: ai.facing > 0 ? 'right' : 'left'};
                        ai.actionTimer = 20;
                    } else if (distance < 60 && ai.attackCooldown <= 0) {
                        // Attack
                        if (randomFactor > 0.6) {
                            this.aiKick();
                        } else {
                            this.aiPunch();
                        }
                        ai.actionTimer = 40;
                    } else if (distance > 150 && randomFactor > 0.7) {
                        // Jump occasionally
                        this.aiJump();
                        ai.actionTimer = 60;
                    } else {
                        // Move randomly
                        ai.keys = {move: randomFactor > 0.5 ? 'right' : 'left'};
                        ai.actionTimer = 30;
                    }
                }
                
                // Execute AI movement
                if (ai.keys && ai.keys.move === 'left' && ai.x > 20) {
                    ai.velX = -ai.speed;
                } else if (ai.keys && ai.keys.move === 'right' && ai.x < this.canvas.width - ai.width - 20) {
                    ai.velX = ai.speed;
                } else {
                    ai.velX *= 0.8;
                }
                
                // Update AI attack cooldowns
                if (ai.attackCooldown > 0) ai.attackCooldown--;
                if (ai.blockCooldown > 0) {
                    ai.blockCooldown--;
                    if (ai.blockCooldown <= 0) {
                        ai.blocking = false;
                    }
                }
            }
            
            aiJump() {
                if (this.ai.onGround) {
                    this.ai.velY = -this.ai.jumpPower;
                    this.ai.onGround = false;
                }
            }
            
            aiPunch() {
                this.ai.attacking = 'punch';
                this.ai.attackCooldown = 35;
                this.checkAIHit('punch', 12);
            }
            
            aiKick() {
                this.ai.attacking = 'kick';
                this.ai.attackCooldown = 50;
                this.checkAIHit('kick', 20);
            }
            
            checkAIHit(attackType, damage) {
                const player = this.player;
                const ai = this.ai;
                
                const attackRange = attackType === 'kick' ? 60 : 50;
                const distance = Math.abs(player.x - ai.x);
                
                if (distance < attackRange) {
                    let actualDamage = damage;
                    
                    if (player.blocking) {
                        actualDamage = Math.floor(damage * 0.3);
                        this.createParticles(player.x, player.y + 40, '#FFFF00', 'block');
                    } else {
                        this.createParticles(player.x, player.y + 40, '#FF0000', 'hit');
                        player.stunned = 15;
                        
                        // Reset player combo on getting hit
                        this.combo = 0;
                        this.comboTimer = 0;
                    }
                    
                    player.health -= actualDamage;
                    player.health = Math.max(0, player.health);
                    
                    // Knockback
                    player.velX = ai.facing * 3;
                    
                    this.updateHealthBars();
                    
                    if (player.health <= 0) {
                        this.endRound(false);
                    }
                }
            }
            
            createParticles(x, y, color, type) {
                const particleCount = type === 'hit' ? 8 : 5;
                
                for (let i = 0; i < particleCount; i++) {
                    this.particles.push({
                        x: x + Math.random() * 20 - 10,
                        y: y + Math.random() * 20 - 10,
                        vx: (Math.random() - 0.5) * 6,
                        vy: (Math.random() - 0.5) * 6,
                        color: color,
                        life: 30,
                        size: Math.random() * 4 + 2
                    });
                }
            }
            
            update() {
                if (!this.gameRunning) return;
                
                // Update combo timer
                if (this.comboTimer > 0) {
                    this.comboTimer--;
                    if (this.comboTimer <= 0) {
                        this.combo = 0;
                    }
                }
                
                this.updateComboDisplay();
                
                // Update player
                this.updateCharacter(this.player);
                
                // Update AI
                this.updateAI();
                this.updateCharacter(this.ai);
                
                // Update particles
                for (let i = this.particles.length - 1; i >= 0; i--) {
                    const particle = this.particles[i];
                    particle.x += particle.vx;
                    particle.y += particle.vy;
                    particle.vx *= 0.95;
                    particle.vy *= 0.95;
                    particle.life--;
                    
                    if (particle.life <= 0) {
                        this.particles.splice(i, 1);
                    }
                }
            }
            
            updateCharacter(char) {
                // Handle movement input (only for player)
                if (char === this.player) {
                    if (this.keys.left && char.x > 20 && char.stunned <= 0) {
                        char.velX = -char.speed;
                        char.facing = -1;
                    } else if (this.keys.right && char.x < this.canvas.width - char.width - 20 && char.stunned <= 0) {
                        char.velX = char.speed;
                        char.facing = 1;
                    } else {
                        char.velX *= 0.8;
                    }
                    
                    // Handle blocking
                    if (this.keys.block && char.stunned <= 0) {
                        char.blocking = true;
                        char.velX *= 0.3; // Slow down while blocking
                    } else {
                        char.blocking = false;
                    }
                }
                
                // Apply physics
                char.velY += this.gravity;
                char.x += char.velX;
                char.y += char.velY;
                
                // Ground collision
                if (char.y + char.height >= this.ground) {
                    char.y = this.ground - char.height;
                    char.velY = 0;
                    char.onGround = true;
                }
                
                // Keep in bounds
                char.x = Math.max(20, Math.min(this.canvas.width - char.width - 20, char.x));
                
                // Update cooldowns
                if (char.attackCooldown > 0) char.attackCooldown--;
                if (char.stunned > 0) char.stunned--;
                
                // Reset attacking state
                if (char.attacking && char.attackCooldown <= 0) {
                    char.attacking = false;
                }
                
                // Update animation
                char.animTimer++;
                if (char.animTimer > 10) {
                    char.animFrame = (char.animFrame + 1) % 4;
                    char.animTimer = 0;
                }
            }
            
            updateHealthBars() {
                const playerHealthPercent = (this.player.health / this.player.maxHealth) * 100;
                const aiHealthPercent = (this.ai.health / this.ai.maxHealth) * 100;
                
                document.getElementById('playerHealth').style.width = playerHealthPercent + '%';
                document.getElementById('aiHealth').style.width = aiHealthPercent + '%';
            }
            
            updateComboDisplay() {
                const display = document.getElementById('comboDisplay');
                if (this.combo > 1) {
                    display.textContent = `Combo: ${this.combo}x`;
                    display.style.display = 'block';
                } else {
                    display.style.display = 'none';
                }
            }
            
            draw() {
                // Clear canvas with background
                this.ctx.fillStyle = '#87CEEB';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height * 0.7);
                
                this.ctx.fillStyle = '#DEB887';
                this.ctx.fillRect(0, this.canvas.height * 0.7, this.canvas.width, this.canvas.height * 0.3);
                
                // Draw ground
                this.ctx.fillStyle = '#CD853F';
                this.ctx.fillRect(0, this.ground, this.canvas.width, this.canvas.height - this.ground);
                
                // Draw characters
                this.drawCharacter(this.player);
                this.drawCharacter(this.ai);
                
                // Draw particles
                for (let particle of this.particles) {
                    this.ctx.fillStyle = particle.color;
                    this.ctx.globalAlpha = particle.life / 30;
                    this.ctx.fillRect(particle.x, particle.y, particle.size, particle.size);
                    this.ctx.globalAlpha = 1;
                }
            }
            
            drawCharacter(char) {
                // Main body
                this.ctx.fillStyle = char.color;
                if (char.stunned > 0) {
                    this.ctx.fillStyle = '#999999'; // Gray when stunned
                }
                this.ctx.fillRect(char.x, char.y, char.width, char.height);
                
                // Head
                this.ctx.fillStyle = '#FFDBAC';
                this.ctx.fillRect(char.x + 10, char.y - 15, 20, 20);
                
                // Eyes
                this.ctx.fillStyle = '#000000';
                this.ctx.fillRect(char.x + 13, char.y - 10, 3, 3);
                this.ctx.fillRect(char.x + 24, char.y - 10, 3, 3);
                
                // Arms
                this.ctx.fillStyle = char.color;
                if (char.attacking === 'punch') {
                    // Extended arm for punch
                    this.ctx.fillRect(
                        char.x + (char.facing > 0 ? char.width : -15),
                        char.y + 20,
                        15, 8
                    );
                } else if (char.attacking === 'kick') {
                    // Extended leg for kick
                    this.ctx.fillRect(
                        char.x + (char.facing > 0 ? char.width : -20),
                        char.y + 50,
                        20, 10
                    );
                }
                
                // Blocking indicator
                if (char.blocking) {
                    this.ctx.strokeStyle = '#FFFF00';
                    this.ctx.lineWidth = 3;
                    this.ctx.strokeRect(char.x - 5, char.y - 5, char.width + 10, char.height + 10);
                }
                
                // Legs
                this.ctx.fillStyle = char.color;
                this.ctx.fillRect(char.x + 5, char.y + char.height, 12, 15);
                this.ctx.fillRect(char.x + 23, char.y + char.height, 12, 15);
            }
            
            gameLoop() {
                this.update();
                this.draw();
                
                if (this.gameRunning) {
                    requestAnimationFrame(() => this.gameLoop());
                }
            }
            
            endRound(playerWon) {
                this.gameRunning = false;
                
                const resultTitle = document.getElementById('resultTitle');
                const resultMessage = document.getElementById('resultMessage');
                
                if (playerWon) {
                    resultTitle.textContent = 'Victory!';
                    resultMessage.textContent = `You defeated the AI opponent! Round ${this.round} complete.`;
                } else {
                    resultTitle.textContent = 'Defeat!';
                    resultMessage.textContent = 'The AI opponent has defeated you. Try again!';
                }
                
                document.getElementById('gameResult').style.display = 'block';
            }
            
            restart() {
                // Reset characters
                this.player.health = this.player.maxHealth;
                this.player.x = 150;
                this.player.y = this.ground - 80;
                this.player.velX = 0;
                this.player.velY = 0;
                this.player.attacking = false;
                this.player.blocking = false;
                this.player.stunned = 0;
                this.player.attackCooldown = 0;
                
                this.ai.health = this.ai.maxHealth;
                this.ai.x = 600;
                this.ai.y = this.ground - 80;
                this.ai.velX = 0;
                this.ai.velY = 0;
                this.ai.attacking = false;
                this.ai.blocking = false;
                this.ai.stunned = 0;
                this.ai.attackCooldown = 0;
                this.ai.actionTimer = 0;
                
                // Reset game state
                this.combo = 0;
                this.comboTimer = 0;
                this.round++;
                this.gameRunning = true;
                this.particles = [];
                
                this.updateHealthBars();
                document.getElementById('gameResult').style.display = 'none';
                
                this.gameLoop();
            }
        }
        
        // Initialize game
        const game = new FightingGame();
    </script>
</body>
</html>
"""

CLIMBER_GAME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Doodle Jump - Tilt Edition</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      touch-action: manipulation;
      user-select: none;
    }
    
    body {
      font-family: 'Arial Rounded MT Bold', 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #6ab7ff, #1a237e);
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: white;
      text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .game-container {
      position: relative;
      width: 100%;
      max-width: 400px;
      max-height: 700px;
      aspect-ratio: 400/700;
      background: rgba(0, 0, 0, 0.2);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
      border: 4px solid #ffcc00;
    }
    
    canvas {
      display: block;
      background: linear-gradient(to bottom, #87CEEB, #E0F7FA);
      width: 100%;
      height: 100%;
    }
    
    .ui-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      padding: 20px;
      display: flex;
      justify-content: space-between;
      z-index: 10;
    }
    
    .score-display {
      background: rgba(0, 0, 0, 0.4);
      padding: 8px 20px;
      border-radius: 20px;
      font-size: 1.4rem;
      font-weight: bold;
      min-width: 100px;
      text-align: center;
      border: 2px solid #ffcc00;
    }
    
    .game-message {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(0, 0, 0, 0.85);
      padding: 30px 40px;
      border-radius: 20px;
      text-align: center;
      z-index: 20;
      border: 3px solid #ffcc00;
      box-shadow: 0 0 30px rgba(255, 204, 0, 0.5);
      max-width: 90%;
    }
    
    .game-message h2 {
      font-size: 2.5rem;
      color: #ffcc00;
      margin-bottom: 20px;
      text-shadow: 0 0 10px rgba(255, 204, 0, 0.7);
    }
    
    .game-message p {
      font-size: 1.3rem;
      margin-bottom: 25px;
      line-height: 1.6;
    }
    
    .btn {
      background: linear-gradient(to bottom, #ffcc00, #ff9800);
      color: #1a237e;
      border: none;
      padding: 12px 30px;
      font-size: 1.3rem;
      border-radius: 30px;
      cursor: pointer;
      font-weight: bold;
      text-transform: uppercase;
      letter-spacing: 1px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
      transition: all 0.3s;
    }
    
    .btn:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    
    .btn:active {
      transform: translateY(1px);
    }
    
    .instructions {
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      width: 90%;
      text-align: center;
      background: rgba(0, 0, 0, 0.4);
      padding: 15px;
      border-radius: 15px;01:34 PM 24-07-2025
      font-size: 1.1rem;
      z-index: 10;
    }
    
    .tilt-indicator {
      position: absolute;
      bottom: 100px;
      left: 50%;
      transform: translateX(-50%);
      width: 80%;
      height: 40px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 20px;
      border: 2px solid rgba(255, 255, 255, 0.4);
      overflow: hidden;
    }
    
    .tilt-ball {
      position: absolute;
      top: 5px;
      left: 50%;
      width: 30px;
      height: 30px;
      background: #ffcc00;
      border-radius: 50%;
      transform: translateX(-50%);
      transition: transform 0.1s ease-out;
      box-shadow: 0 0 10px rgba(255, 204, 0, 0.7);
    }
    
    .hidden {
      display: none;
    }
    
    .game-title {
      font-size: 3.5rem;
      margin-bottom: 30px;
      text-align: center;
      color: #ffcc00;
      text-shadow: 0 0 15px rgba(255, 204, 0, 0.7);
      letter-spacing: 2px;
    }
    
    .controls-info {
      margin-top: 20px;
      padding: 15px;
      background: rgba(0, 0, 0, 0.4);
      border-radius: 15px;
      max-width: 400px;
      text-align: center;
    }
    
    @media (max-width: 500px) {
      .game-title {
        font-size: 2.5rem;
        margin-bottom: 20px;
      }
      
      .game-message {
        padding: 20px;
      }
      
      .game-message h2 {
        font-size: 2rem;
      }
      
      .btn {
        padding: 10px 25px;
        font-size: 1.1rem;
      }
      
      .score-display {
        font-size: 1.2rem;
        padding: 6px 15px;
      }
      
      .instructions {
        font-size: 0.9rem;
      }
    }
  </style>
</head>
<body>
  <h1 class="game-title">DOODLE JUMP</h1>
  
  <div class="game-container">
    <canvas id="game"></canvas>
    
    <div class="ui-overlay">
      <div class="score-display">Score: <span id="score">0</span></div>
    </div>
    
    <div id="startScreen" class="game-message">
      <h2>DOODLE JUMP</h2>
      <p>Tilt your device to move!<br>Jump on platforms to climb higher.</p>
      <button id="startBtn" class="btn">START GAME</button>
    </div>
    
    <div id="gameOverScreen" class="game-message hidden">
      <h2>GAME OVER</h2>
      <p>Your score: <span id="finalScore">0</span></p>
      <button id="restartBtn" class="btn">PLAY AGAIN</button>
    </div>
    
    <div>
      <div></div>
    </div>
    
    <div class="instructions">
      Avoid falling!
    </div>
  </div>
  
  <div class="controls-info">
    <p>Keyboard controls: ← → Arrow Keys | Touch controls: Tap left/right side of screen</p>
  </div>

  <script>
    // Game variables
    const canvas = document.getElementById('game');
    const context = canvas.getContext('2d');
    const scoreElement = document.getElementById('score');
    const finalScoreElement = document.getElementById('finalScore');
    const startScreen = document.getElementById('startScreen');
    const gameOverScreen = document.getElementById('gameOverScreen');
    const startBtn = document.getElementById('startBtn');
    const restartBtn = document.getElementById('restartBtn');
    const tiltBall = document.getElementById('tiltBall');
    
    // Set canvas size
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
    
    // Game state
    let gameState = 'start'; // 'start', 'playing', 'gameover'
    let score = 0;
    let highScore = 0;
    let lastTime = 0;
    let gameSpeed = 1;
    
    // Constants
    const platformWidth = 65;
    const platformHeight = 18;
    const platformStart = canvas.height - 50;
    
    const gravity = 0.33;
    const drag = 0.3;
    const bounceVelocity = -12.5;
    
    let minPlatformSpace = 15;
    let maxPlatformSpace = 20;
    
    // Platforms
    let platforms = [];
    
    function random(min, max) {
      return Math.random() * (max - min) + min;
    }
    
    // Player character
    const doodle = {
      width: 40,
      height: 50,
      x: canvas.width / 2 - 20,
      y: platformStart - 60,
      dx: 0,
      dy: 0,
      rotation: 0
    };
    
    let playerDir = 0;
    let keydown = false;
    let prevDoodleY = doodle.y;
    
    // Platform colors
    const platformColors = [
      '#4CAF50', // Green
      '#FF9800', // Orange
      '#9C27B0', // Purple
      '#2196F3', // Blue
      '#E91E63'  // Pink
    ];
    
    // Create platforms
    function createPlatforms() {
      platforms = [{
        x: canvas.width / 2 - platformWidth / 2,
        y: platformStart
      }];
      
      minPlatformSpace = 15;
      maxPlatformSpace = 20;
      
      let y = platformStart;
      while (y > 0) {
        y -= platformHeight + random(minPlatformSpace, maxPlatformSpace);
        let x;
        do {
          x = random(25, canvas.width - 25 - platformWidth);
        } while (
          y > canvas.height / 2 &&
          x > canvas.width / 2 - platformWidth * 1.5 &&
          x < canvas.width / 2 + platformWidth / 2
        );
        platforms.push({ 
          x, 
          y,
          color: platformColors[Math.floor(random(0, platformColors.length))]
        });
      }
    }
    
    // Draw player character
    function drawPlayer() {
      // Draw body
      context.fillStyle = '#FFCC00';
      context.beginPath();
      context.arc(
        doodle.x + doodle.width/2, 
        doodle.y + doodle.height/2, 
        doodle.width/2, 
        0, 
        Math.PI * 2
      );
      context.fill();
      
      // Draw eyes
      context.fillStyle = '#333';
      context.beginPath();
      context.arc(
        doodle.x + doodle.width/2 - 8, 
        doodle.y + doodle.height/2 - 5, 
        5, 
        0, 
        Math.PI * 2
      );
      context.arc(
        doodle.x + doodle.width/2 + 8, 
        doodle.y + doodle.height/2 - 5, 
        5, 
        0, 
        Math.PI * 2
      );
      context.fill();
      
      // Draw smile
      context.beginPath();
      context.arc(
        doodle.x + doodle.width/2, 
        doodle.y + doodle.height/2 + 5, 
        10, 
        0, 
        Math.PI
      );
      context.strokeStyle = '#333';
      context.lineWidth = 2;
      context.stroke();
      
      // Draw hat
      context.fillStyle = '#FF5722';
      context.beginPath();
      context.moveTo(doodle.x + doodle.width/2 - 25, doodle.y + doodle.height/2 - 15);
      context.lineTo(doodle.x + doodle.width/2 + 25, doodle.y + doodle.height/2 - 15);
      context.lineTo(doodle.x + doodle.width/2 + 20, doodle.y + doodle.height/2 - 25);
      context.lineTo(doodle.x + doodle.width/2 - 20, doodle.y + doodle.height/2 - 25);
      context.closePath();
      context.fill();
    }
    
    // Game Loop
    function loop(timestamp) {
      if (gameState !== 'playing') {
        requestAnimationFrame(loop);
        return;
      }
      
      const deltaTime = Math.min(20, timestamp - lastTime) / 16;
      lastTime = timestamp;
      
      requestAnimationFrame(loop);
      context.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw background elements
      drawBackground();
      
      // Apply gravity
      doodle.dy += gravity * deltaTime;
      
      // Camera movement when player jumps
      if (doodle.y < canvas.height / 2 && doodle.dy < 0) {
        platforms.forEach(p => p.y += -doodle.dy);
        score += Math.floor(-doodle.dy * 0.1);
        scoreElement.textContent = score;
        
        // Create new platforms as needed
        while (platforms[platforms.length - 1].y > 0) {
          platforms.push({
            x: random(25, canvas.width - 25 - platformWidth),
            y: platforms[platforms.length - 1].y - (platformHeight + random(minPlatformSpace, maxPlatformSpace)),
            color: platformColors[Math.floor(random(0, platformColors.length))]
          });
          minPlatformSpace += 0.5;
          maxPlatformSpace = Math.min(maxPlatformSpace + 0.5, canvas.height / 2);
        }
      } else {
        doodle.y += doodle.dy * deltaTime;
      }
      
      // Horizontal drag
      if (!keydown) {
        if (playerDir < 0) {
          doodle.dx += drag * deltaTime;
          if (doodle.dx > 0) {
            doodle.dx = 0;
            playerDir = 0;
          }
        } else if (playerDir > 0) {
          doodle.dx -= drag * deltaTime;
          if (doodle.dx < 0) {
            doodle.dx = 0;
            playerDir = 0;
          }
        }
      }
      
      doodle.x += doodle.dx * deltaTime;
      
      // Wrap around
      if (doodle.x + doodle.width < 0) {
        doodle.x = canvas.width;
      } else if (doodle.x > canvas.width) {
        doodle.x = -doodle.width;
      }
      
      // Draw platforms
      platforms.forEach(platform => {
        // Draw platform
        context.fillStyle = platform.color;
        context.fillRect(platform.x, platform.y, platformWidth, platformHeight);
        
        // Draw platform top
        context.fillStyle = '#FFF';
        context.fillRect(platform.x, platform.y, platformWidth, 5);
        
        // Collision detection
        if (
          doodle.dy > 0 &&
          prevDoodleY + doodle.height <= platform.y &&
          doodle.x < platform.x + platformWidth &&
          doodle.x + doodle.width > platform.x &&
          doodle.y < platform.y + platformHeight &&
          doodle.y + doodle.height > platform.y
        ) {
          doodle.y = platform.y - doodle.height;
          doodle.dy = bounceVelocity;
          
          // Score bonus
          if (platform.y < canvas.height / 2) {
            score += 10;
            scoreElement.textContent = score;
          }
        }
      });
      
      // Draw player
      drawPlayer();
      
      prevDoodleY = doodle.y;
      
      // Remove platforms that are off screen
      platforms = platforms.filter(p => p.y < canvas.height);
      
      // Game over condition
      if (doodle.y > canvas.height) {
        gameOver();
      }
    }
    
    // Draw background elements
    function drawBackground() {
      // Draw clouds
      context.fillStyle = 'rgba(255, 255, 255, 0.8)';
      context.beginPath();
      context.arc(50, 80, 25, 0, Math.PI * 2);
      context.arc(80, 70, 35, 0, Math.PI * 2);
      context.arc(120, 80, 30, 0, Math.PI * 2);
      context.fill();
      
      context.beginPath();
      context.arc(canvas.width - 70, 150, 20, 0, Math.PI * 2);
      context.arc(canvas.width - 100, 140, 30, 0, Math.PI * 2);
      context.arc(canvas.width - 130, 150, 25, 0, Math.PI * 2);
      context.fill();
      
      // Draw sun
      context.fillStyle = '#FFEB3B';
      context.beginPath();
      context.arc(canvas.width - 50, 50, 40, 0, Math.PI * 2);
      context.fill();
    }
    
    // Movement functions
    function moveLeft() {
      keydown = true;
      playerDir = -1;
      doodle.dx = -5;
    }
    
    function moveRight() {
      keydown = true;
      playerDir = 1;
      doodle.dx = 5;
    }
    
    function stopMove() {
      keydown = false;
    }
    
    // Tilt control
    function handleTilt(e) {
      if (gameState !== 'playing') return;
      
      const gamma = e.gamma; // left/right tilt in degrees
      
      // Update tilt indicator
      const maxTilt = 30;
      const tiltPosition = Math.max(-maxTilt, Math.min(maxTilt, gamma));
      const ballPosition = (tiltPosition / maxTilt) * (canvas.clientWidth * 0.35);
      tiltBall.style.transform = `translateX(${ballPosition}px)`;
      
      // Move player based on tilt
      if (gamma < -5) {
        moveLeft();
      } else if (gamma > 5) {
        moveRight();
      } else {
        stopMove();
      }
    }
    
    // Start game
    function startGame() {
      gameState = 'playing';
      score = 0;
      scoreElement.textContent = score;
      startScreen.classList.add('hidden');
      gameOverScreen.classList.add('hidden');
      
      // Reset player position
      doodle.x = canvas.width / 2 - 20;
      doodle.y = platformStart - 60;
      doodle.dx = 0;
      doodle.dy = 0;
      
      // Create new platforms
      createPlatforms();
      
      // Start game loop
      lastTime = performance.now();
      requestAnimationFrame(loop);
    }
    
    // Game over
    function gameOver() {
      gameState = 'gameover';
      finalScoreElement.textContent = score;
      gameOverScreen.classList.remove('hidden');
      
      // Update high score
      if (score > highScore) {
        highScore = score;
      }
    }
    
    // Event listeners
    // Keyboard controls
    document.addEventListener('keydown', e => {
      if (e.key === "ArrowLeft") {
        moveLeft();
      } else if (e.key === "ArrowRight") {
        moveRight();
      }
    });
    
    document.addEventListener('keyup', () => {
      stopMove();
    });
    
    // Touch controls (mobile)
    canvas.addEventListener('touchstart', (e) => {
      const touchX = e.touches[0].clientX;
      if (touchX < canvas.width / 2) {
        moveLeft();
      } else {
        moveRight();
      }
    });
    
    canvas.addEventListener('touchend', () => {
      stopMove();
    });
    
    // Tilt controls
    window.addEventListener('deviceorientation', handleTilt);
    
    // Game buttons
    startBtn.addEventListener('click', startGame);
    restartBtn.addEventListener('click', startGame);
    
    // Initialize the game
    createPlatforms();
    drawBackground();
    
    // Request permission for DeviceOrientation on iOS
    if (typeof DeviceOrientationEvent.requestPermission === 'function') {
      document.addEventListener('click', function initialClick() {
        DeviceOrientationEvent.requestPermission()
          .then(permissionState => {
            if (permissionState === 'granted') {
              console.log("Device orientation permission granted");
            }
          })
          .catch(console.error);
        document.removeEventListener('click', initialClick);
      });
    }
  </script>
</body>
</html>
"""
class ServerThread(threading.Thread):
    """Thread class with a stop() method to properly shutdown the Flask server"""
    def __init__(self, app):
        super().__init__()
        self.server = make_server('0.0.0.0', 7815, app)
        self.ctx = app.app_context()
        self.ctx.push()
        
    def run(self):
        """Run the Flask server"""
        print("Game server Started")
        self.server.serve_forever()
        
    def shutdown(self):
        """Shutdown the Flask server"""
        print("Flask server shutting down...")
        self.server.shutdown()

class ServerControlUI:
    def __init__(self):
        self.server_thread = None
        self.server_running = False
        self.local_ip = get_local_ip()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Game Server Controller")  # Emoji in title
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.iconbitmap(r'B:\Game\LAN-Game-Hub\game.ico')  # Clear the () for no icon default icon
        
        # Create frames
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        
        # Add emoji icon in header
        icon_label = tk.Label(header_frame, text="🎮", font=("Arial", 24), 
                             bg="#2c3e50", fg="white")
        icon_label.pack(side=tk.LEFT, padx=(20, 10))
        
        # Header text
        tk.Label(
            header_frame, 
            text="Multi-Game Server Controller", 
            font=("Arial", 18, "bold"), 
            fg="white", 
            bg="#2c3e50"
        ).pack(side=tk.LEFT, padx=(0, 20), pady=20)
        
        # Status indicator
        self.status_var = tk.StringVar(value="Status: Stopped")
        tk.Label(
            header_frame, 
            textvariable=self.status_var,
            font=("Arial", 12), 
            fg="#ecf0f1", 
            bg="#2c3e50"
        ).pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Create buttons
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(fill=tk.X)
        
        self.start_btn = tk.Button(
            control_frame, text="Start Server", 
            command=self.start_server, width=15, height=2,
            bg="#27ae60", fg="white", font=("Arial", 10, "bold")
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            control_frame, text="Stop Server", 
            command=self.stop_server, width=15, height=2,
            bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_btn = tk.Button(
            control_frame, text="Open in Browser", 
            command=self.open_browser, width=15, height=2,
            bg="#3498db", fg="white", font=("Arial", 10, "bold")
        )
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        # IP info
        self.ip_frame = tk.Frame(control_frame)
        self.ip_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(self.ip_frame, text=f"Local IP: {self.local_ip}", font=("Arial", 9)).pack()
        tk.Label(self.ip_frame, text="Port: 7815", font=("Arial", 9)).pack()
        
        # Create log display
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_area = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, state='disabled', bg="#1a1a1a", fg="#e0e0e0"
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.tag_config("INFO", foreground="#ffffff")
        self.log_area.tag_config("SUCCESS", foreground="#2ecc71")
        self.log_area.tag_config("ERROR", foreground="#e74c3c")
        
        # Redirect stdout and stderr to log area
        sys.stdout = self.TextRedirector(self.log_area, "INFO")
        sys.stderr = self.TextRedirector(self.log_area, "ERROR")
        
        # Display initial message
        print("Game Server Controller Ready")
        print("Click 'Start Server' to begin")
        
        # Start the server automatically
        self.root.after(100, self.start_server)
        
    class TextRedirector:
        def __init__(self, text_widget, tag):
            self.text_widget = text_widget
            self.tag = tag
            
        def write(self, message):
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, message, (self.tag,))
            self.text_widget.configure(state='disabled')
            self.text_widget.see(tk.END)
            
        def flush(self):
            pass
    
    def start_server(self):
        if self.server_running:
            return
            
        self.server_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.open_btn.config(state=tk.NORMAL)
        self.status_var.set("Status: Running")
        self.root.config(bg="#ecf0f1")
        
        print("\nStarting game server...")
        
        # Start Flask server in a separate thread using our custom ServerThread
        self.server_thread = ServerThread(app)
        self.server_thread.start()
        
    def stop_server(self):
        if not self.server_running:
            return
            
        self.server_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Status: Stopped")
        
        print("\nStopping game server...")
        if self.server_thread:
            self.server_thread.shutdown()
            self.server_thread.join(2.0)  # Wait for thread to finish
            self.server_thread = None
            print("Server has been stopped")
    
    def open_browser(self):
        if self.server_running:
            webbrowser.open("http://localhost:7815")
        else:
            messagebox.showwarning("Server Not Running", "Please start the server first")
    
    def on_closing(self):
        if self.server_running:
            self.stop_server()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    # Start the UI which will automatically start the server
    ui = ServerControlUI()
    ui.run()
