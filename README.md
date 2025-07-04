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

## 🛠️ Installation

### 1. Install Python packages:

```bash
pip install pygame python-chess
```


### 2. Download Stockfish
- Get it from: https://stockfishchess.org/download/
- Place the executable in the same folder or update the STOCKFISH_PATH variable in chess_helper.py

## ▶️ Running the App

```bash
python chess_helper.py
```

## 🎮 How to Use
- Click on a piece to see legal moves (dots)

- Click a destination square to move

- Promotion? Choose your piece!

- Adjust Elo with the slider at the bottom

- Enter PGN at the top and press Enter

- Use Reset and AI Toggle buttons below the board

### 📜 License
MIT License — free for personal or educational use.

## 👤 Author
Made with ❤️ by Ammar.
Feel free to fork, star, and contribute!
