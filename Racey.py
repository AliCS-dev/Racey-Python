import pygame  # Importing the module
import time
import random

pygame.init()  # Initializing to allow us to create commands

# Game window dimensions
game_width = 1000
game_length = 1000

# Creating the display window
gameDisplay = pygame.display.set_mode((game_width, game_length))
pygame.display.set_caption('Racey')  # Title of the game window

# Defining some colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 128, 0)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)

# Load car image and get its size (used for accurate collision)
CarImg = pygame.image.load("Racey.png")
car_width, car_height = CarImg.get_rect().size

clock = pygame.time.Clock()  # A clock used to control frame rate

# Display the number of obstacles dodged
def things_dodged(count):
    font = pygame.font.SysFont(None, 25)
    text = font.render("Dodged: " + str(count), True, black)
    gameDisplay.blit(text, (0, 0))

# Draw a rectangular obstacle
def things(thing_x, thing_y, thing_w, thing_h, color):
    pygame.draw.rect(gameDisplay, color, [thing_x, thing_y, thing_w, thing_h])

# Display the car image at a given location
def car(x, y):
    gameDisplay.blit(CarImg, (x, y))

# Helper function for rendering text
def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

# Display a crash message and restart the game
def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf', 60)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((game_width / 2), (game_length / 2))
    gameDisplay.blit(TextSurf, TextRect)

    pygame.display.update()
    time.sleep(2)
    game_loop()

# Function to handle a crash
def crash():
    message_display('You Crashed!')
    pygame.quit()
    quit()

# Button creation utility
def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))

    smallText = pygame.font.SysFont("comicsansms", 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurf, textRect)

# Game intro screen
def game_intro():
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(white)
        largeText = pygame.font.Font('freesansbold.ttf', 70)
        TextSurf, TextRect = text_objects("FAST AND FURIOUS", largeText)
        TextRect.center = ((game_width / 2), (game_length / 2))
        gameDisplay.blit(TextSurf, TextRect)

        button("GO!", 400, 550, 150, 50, green, bright_green, game_loop)
        button("Quit", 600, 550, 150, 50, red, bright_red, pygame.quit)

        pygame.display.update()
        clock.tick(15)

# The main game loop
def game_loop():
    x = (game_width * 0.32)  # Initial car x position
    y = (game_length * 0.6)  # Initial car y position

    x_change = 0  # Movement tracker

    thing_width = 100
    thing_height = 100
    thing_startx = random.randrange(0, game_width - thing_width)
    thing_starty = -600
    thing_speed = 7

    dodged = 0  # Dodged obstacle count
    gameExit = False

    while not gameExit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -5
                elif event.key == pygame.K_RIGHT:
                    x_change = 5

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0

        x += x_change  # Update car position

        gameDisplay.fill(white)  # Clear screen

        # Draw obstacle
        things(thing_startx, thing_starty, thing_width, thing_height, black)
        thing_starty += thing_speed  # Move obstacle

        # Draw car
        car(x, y)

        # Show dodged score
        things_dodged(dodged)

        # Check boundaries
        if x > game_width - car_width or x < 0:
            crash()

        # Reset obstacle when it goes off screen and increment score
        if thing_starty > game_length:
            thing_starty = 0 - thing_height
            thing_startx = random.randrange(0, game_width - thing_width)
            dodged += 1
            thing_speed += 0.5  # Increase speed as game progresses
            thing_width = min(thing_width + 5, game_width // 2)  # Limit max width

        # Collision detection using accurate rectangle bounds
        car_rect = pygame.Rect(x, y, car_width, car_height)
        obstacle_rect = pygame.Rect(thing_startx, thing_starty, thing_width, thing_height)

        if car_rect.colliderect(obstacle_rect):
            print('Collision detected')
            crash()

        pygame.display.update()
        clock.tick(60)  # 60 FPS

# Start the game
game_intro()
game_loop()
pygame.quit()