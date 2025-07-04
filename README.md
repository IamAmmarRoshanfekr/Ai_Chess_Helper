# ♟️ Pygame Chess Helper

An advanced chess board built using **Pygame**, **python-chess**, and **Stockfish**, designed to help players improve by showing legal moves, best suggestions, and supporting adjustable AI strength via Elo slider.

---

## 🚀 Features

- 🎯 Best move suggestion (AI Helper) using Stockfish
- 🟢 Legal moves shown as green dots
- 🔴 Capture moves shown as red dots above target pieces
- 🔁 Real-time Elo slider to adjust Stockfish strength (1350–2850)
- 🧠 Toggle AI Helper on/off
- 📥 Load PGN to set up custom board positions
- 🔄 Reset board button
- ♛ Pawn promotion menu (queen, rook, bishop, knight)
- 📍 File/rank labels and PGN input bar

---

## 📂 Folder Structure

chess-helper/
├── chess_helper.py
├── README.md
├── stockfish # Stockfish engine executable
├── images/
│ ├── wp.png # white pawn
│ ├── bq.png # black queen
│ └── ... # other chess piece images
├── sounds/
│ ├── move.wav
│ ├── capture.wav
│ └── check.wav

---

## 🛠️ Installation

### 1. Install Python packages:

```bash
pip install pygame python-chess


### 2. Download Stockfish
- Get it from: https://stockfishchess.org/download/
- Place the executable in the same folder or update the STOCKFISH_PATH variable in chess_helper.py

