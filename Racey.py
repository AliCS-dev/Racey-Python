import pygame  # importing the module
import time
import random
pygame.init()  # initializing to allow us to create commands

game_width = 1000
game_length = 1000

gameDisplay = pygame.display.set_mode((game_width, game_length))  # Display of our game, meaning the surface which is 1000px wide and 1000px tall
pygame.display.set_caption('Racey')  # Giving the title to our game

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0,128,0)
bright_red = (255,0,0)
bright_green = (0,255,0)

car_width = 50

CarImg = pygame.image.load("Racey.png")  # putting the car image that is in pictures folder
clock = pygame.time.Clock()  # A clock used to track time which is very important for FPS

# The function takes x, y starting points, width, height variables, and color
# .rect to draw a polygon, to specify the color and x, y locations followed by width and height

def things_dodged(count):
    font = pygame.font.SysFont(None,25)
    text = font.render("Dodged: " + str(count),True,black)
    gameDisplay.blit(text,(0,0))


def things(thing_x, thing_y, thing_w, thing_h, color):
    pygame.draw.rect(gameDisplay, color, [thing_x, thing_y, thing_w, thing_h])

def car(x, y):  # Car function just to put the car image on the screen
    gameDisplay.blit(CarImg, (x, y))  # blit just draws the image to the screen based on parameters

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf', 60)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((game_width / 2), (game_length / 2))
    gameDisplay.blit(TextSurf, TextRect)

    pygame.display.update()
    time.sleep(2)
    game_loop()

def crash():
    message_display('You Crashed!')
    pygame.quit()
    quit()

'''
x-> location x top left coordinate
y -> location y top left coordinate
w -> button width
h -> button height
ic -> inactive color
ac -> active color
'''


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
def game_intro():
    intro = True
    while intro:
        for event in pygame.event.get():
           # print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(white)
        largeText = pygame.font.Font('freesansbold.ttf',70)
        TextSurf, TextRect = text_objects("FAST AND FURIOUS",largeText)
        TextRect.center = ((game_width/2),(game_length/2))
        gameDisplay.blit(TextSurf,TextRect)

        button("GO!", 400, 550, 150, 50,green,bright_green,game_loop)
        button("Quit",600, 550, 150, 50,red,bright_red,pygame.quit)

        mouse = pygame.mouse.get_pos()
        if 425 + 100 > mouse[0] > 425 and 550+50 > mouse[1] > 550:
            pygame.draw.rect(gameDisplay,bright_green,(425,550,100,50))
        else:
             pygame.draw.rect(gameDisplay,green,(425,550,100,50))
                
        smallText = pygame.font.Font('freesansbold.ttf',20)
        textSurf,textRect = text_objects("Go!",smallText)
        textRect.center = ((425+(100/2)),(550+(50/2)))
        gameDisplay.blit(textSurf,textRect)
        
        pygame.draw.rect(gameDisplay,red,(550,550,100,50))
        
        pygame.display.update()
        clock.tick(15)


x_change = 0  # Variable to track movement change
car_speed = 0  # Currently unused, can be utilized for dynamic speed changes

def game_loop():
    x = (game_width * 0.32)  # Initial car x position
    y = (game_length * 0.6)  # Initial car y position

    x_change = 0  # Reset movement variable
    
    thing_width = 100
    thing_height = 100
    thing_startx = random.randrange(0, game_width - thing_width)  # We want the starting position of the object to be random
    thing_starty = -600  # So the player has some time to avoid the obstacle
    thing_speed = 7  # Specifying object speed, the block will move 7 pixels
    
    thingCount = 1
    dodged = 0

    gameExit = False

    while not gameExit:  # Run until it crashes
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameExit = True

            if event.type == pygame.KEYDOWN:  # Key press detection
                if event.key == pygame.K_LEFT:
                    x_change = -5  # Move left
                elif event.key == pygame.K_RIGHT:
                    x_change = 5  # Move right

            if event.type == pygame.KEYUP:  # Key release detection
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0  # Stop movement

        x = x + x_change  # Update car position based on movement

        gameDisplay.fill(white)  # Fill the whole surface with white color

        things(thing_startx, thing_starty, thing_width, thing_height, black)  # Draw obstacle
        thing_starty = thing_starty + thing_speed  # Move obstacle downwards

        car(x, y)  # Draw the car

        if x > game_width - car_width or x < 0:  # Check if the car goes out of bounds
            crash()

        if thing_starty > game_length:  # Reset obstacle when it moves off-screen
            thing_starty = 0 - thing_height
            thing_startx = random.randrange(0, game_width - thing_width)

        if thing_starty > game_length:
            thing_starty = 0 - thing_height
            thing_startx = random.randrange(0 , game_width)
            dodged = dodged + 1
            thing_width = int(thing_width* 1.2)
       
       
        # Collision detection
        if (x < thing_startx + thing_width and x+ car_width > thing_startx and y < thing_starty + thing_height and y + car_width):
            print('Collision detected')
            crash()
        
        '''
        Above logic states that if y, the car's top left or bottom left has crossed the object, then there is a y crossover.
        '''

        pygame.display.update()  # Update the screen
        clock.tick(60)  # Run the game at 60 FPS

        # We can either use display.flip() which updates the entire surface
        # Here display.update() can be used to update a specific part of the surface
        # But in this case, it doesn't matter because we are not giving any parameters to the update() function,
        # so it will act the same as flip()
game_intro()
game_loop()  
pygame.quit()  # Quit pygame when the game loop ends
