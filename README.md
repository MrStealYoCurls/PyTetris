# Tetris Game in Python

Welcome to this simple rendition of the classic Tetris game, built using Python and the pygame library.

## Rules

Tetris is a tile-matching puzzle game. The objective is to manipulate the falling tetrominoes, which move downwards one space at a time, in order to create a horizontal line without gaps. When such a line is created, it disappears, and any tetrominoes above move down. The game ends if the playing field is filled. The goal is to achieve the highest score possible.

### Game Controls

- **Left and Right Arrow Keys**: Shifts the tetrominoes left or right.
- **Up Arrow Key**: Rotates the tetrominoes.
- **Down Arrow Key**: Drops the tetrominoes into place.

## Code Walkthrough

For those interested in learning how the game is coded, here's a brief explanation of the main components:

### 1. Main Game Loop (`Main` class)

This is where the game's main functionalities are looped through, handling user input, updating game state, and rendering the game.

- `pygame.event.get()`: Collects all the events that happen during the game, like pressing keys or clicking the mouse.
- `self.game.run()`: Runs the game logic.
- `self.score.run()`: Updates the score.
- `self.preview.run(self.next_shapes)`: Shows a preview of the next shape.

### 2. Game Logic (`Game` class)

This class manages the logic for moving the tetrominoes, checking for collisions, and clearing lines.

### 3. Scoring (`Score` class)

Manages the player's score, based on the number of lines cleared.

### 4. Preview (`Preview` class)

Shows the next shape(s) that will fall.


## How to Play

1. Clone or download this repository.
   
   Open a terminal and navigate to the location where you want to save the file.
   
   Then run:
   ```bash
   git clone https://github.com/MrStealYoCurls/PyTetris.git
   ```
3. Install the Pygame library using:
   ### Windows
    ```bash
    pip install pygame-ce
    ```
    ### Mac
    ```bash
    pip3 install pygame-ce
    ```
4. Navigate to the directory and run the game script.
   ### Windows
    ```bash
    python PyTetris.py
    ```
    ### Mac
    ```bash
    python3 PyTetris.py
    ```
5. Enjoy and try to beat your high score!
