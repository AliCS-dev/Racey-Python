Racey Game - README
Overview
Racey is a simple car dodging game built using Python and the Pygame library. In this game, you control a car and attempt to dodge falling obstacles while collecting points for every obstacle avoided. The game increases in difficulty as the speed and size of the obstacles grow over time.

Features
Car Movement: Move your car left or right to dodge obstacles using the arrow keys.

Obstacles: Rectangular obstacles fall from the top of the screen that you must avoid. The speed and size of obstacles increase as you dodge more.

Score: The game keeps track of how many obstacles you dodge during gameplay.

Collision Detection: The game features collision detection to end the game if your car collides with an obstacle.

Game Restart: After crashing, you can restart the game from the intro screen or quit.

Requirements
Python 3.x

Pygame library

To install Pygame, you can use the following command:

bash
Copy
Edit
pip install pygame
Setup and Usage
Clone the Repository (or download the code files).

Make sure you have the necessary dependencies installed.

Place your car image (Racey.png) in the same directory as the script, or update the path in the script if your image is located elsewhere.

Run the game by executing the Python script:

bash
Copy
Edit
python racey_game.py
Enjoy playing the game!

Game Controls
Left Arrow: Move the car left.

Right Arrow: Move the car right.

Escape / Quit: Exit the game from the main menu or after crashing.

Game Flow
Intro Screen:

The game starts with a title screen that shows "FAST AND FURIOUS".

You can either press the GO! button to start playing or Quit to exit the game.

Main Game Loop:

The car starts at a fixed position on the screen.

Obstacles will begin to fall from the top. Use the arrow keys to dodge them.

The more obstacles you dodge, the higher your score and the faster the game gets.

If the car collides with an obstacle, the game ends, and you are shown a crash message.

Restart or Quit:

After a crash, a "You Crashed!" message is displayed. You can then choose to restart the game or quit.

Code Explanation
Pygame Initialization:

pygame.init() initializes all Pygame modules to allow you to create a game window, handle input, and draw graphics.

Game Window Setup:

The game window is set to a size of 1000x1000 pixels.

The window’s title is set to "Racey".

Game Mechanics:

The car is represented by an image loaded using pygame.image.load("Racey.png"), and its position is tracked by the x and y variables.

Obstacles fall from the top of the screen and increase in speed and size as the player avoids them.

If the car collides with an obstacle, the crash() function is called, showing the "You Crashed!" message.

Collision Detection:

Collision is detected by checking if the rectangular area of the car (car_rect) intersects with the rectangular area of the obstacle (obstacle_rect).

Score and Difficulty:

The player earns points for dodging obstacles. Every time an obstacle is successfully dodged, the speed of the obstacles increases, and the width of obstacles grows.

Contributing
If you'd like to contribute to this project, feel free to open an issue or submit a pull request. Any improvements, bug fixes, or new features are welcome!
