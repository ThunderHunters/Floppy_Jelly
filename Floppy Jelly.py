# Import necessary modules
import pygame
from pygame.locals import *
import random

# Initialize Pygame and Pygame mixer
pygame.init()
pygame.mixer.init()

# Set up the clock and the frames per second (fps)
clock = pygame.time.Clock()
fps = 60

# Define screen dimensions
SCREEN_WIDTH = 860
SCREEN_HEIGHT = 936

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Floppy Jelly")

# Define font for text rendering
font = pygame.font.SysFont("monospace" , 50)

# Define color
white = (255, 255, 255)

# Define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 250
pipe_frequency = 1500 #miliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
played_death_sound = False 

# Define the path to the images and audio files ((Replace XXX here to your location of downloaded game files))
file_path = "/XXX/"

# Load images
bg = pygame.image.load(file_path + 'Water Tunnel Wide BG.jpg')
ground_img = pygame.image.load(file_path + 'Pink Bottom Lines.png')
sky_img = pygame.image.load(file_path + 'Pink Fence.png')
button_img = pygame.image.load(file_path + 'RESTART Button.png')

# Load music
pygame.mixer.music.load(file_path + 'CD-349321485-TRACK22-1.wav')

# Play music at start of game
pygame.mixer.music.play()  

# Load sound effect
death_sound = pygame.mixer.Sound(file_path + 'Guitar Slide Down 02.wav')

# Function to draw text on the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function to reset the game state
def reset_game():
    pipe_group.empty() 
    flappy.rect.x = 100
    flappy.rect.y = int(SCREEN_HEIGHT / 2)
    score = 0
    pygame.mixer.music.play()  
    return score

# Class definition for the JellyBird sprite
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'{file_path}/JellyBird{num}.png')

            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
            # Gravity effect
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
                

        if game_over == False:
            # Jump mechanism
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
               
            # Handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], 180)
            
# Class definition for the Pipe sprite
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x , y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(file_path + 'Blue Water Cacti.png')
        self.rect = self.image.get_rect()
        # Position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Class definition for the Button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        # Get mouse position
        pos = pygame.mouse.get_pos()

        # Check if mouse is over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # Draw the button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action
    
# Create sprite groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

# Create an instance of the Bird class
flappy = Bird(100, int(SCREEN_HEIGHT/ 2))

bird_group.add(flappy)

# Create an instance of the Button class
button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 30, button_img)

# Main game loop
run = True
while run:
    # Set the frame rate
    clock.tick(fps)

    # Draw the background
    screen.blit(bg, (0,0))

    # Update and draw the bird and pipes
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # Draw the ground graphics
    screen.blit(ground_img, (ground_scroll, 768))
    
    # Draw pink graphics at the top of the screen
    screen.blit(sky_img, (ground_scroll, 0))

    # Check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
    if pass_pipe == True:
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    # Draw the score
    draw_text(str(score), font, white, int(SCREEN_WIDTH/ 2), 40)

    # Look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

        pygame.mixer.music.stop()

    # Check if bird has hit the ground or the top
    if flappy.rect.bottom >= 768 or flappy.rect.top <= 120:
        game_over = True
        flying = False

    # Update the game state if it's not game over and bird is flying
    if game_over == False and flying == True:

        # Generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, -1)
            top_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
            
        # Draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        # Update the pipes
        pipe_group.update()

    # Check for game over and reset
    if game_over == True:
        if not played_death_sound:
            death_sound.play()
            played_death_sound = True

        # Draw and check the restart button
        if button.draw() == True:
            game_over = False
            score = reset_game()
            played_death_sound = False  # Reset the flag when restarting the game
        
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    # Update the display
    pygame.display.update()

# Quit Pygame when the game loop ends
pygame.quit()
