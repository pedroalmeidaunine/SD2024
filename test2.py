import pygame
import random
import sys
import json
from pygame.locals import *
from moviepy.editor import VideoFileClip

# Initialize Pygame and window settings
pygame.init()
infoObject = pygame.display.Info()
WINDOWWIDTH = infoObject.current_w
WINDOWHEIGHT = 600

TEXTCOLOR = (0, 0, 0)
FPS = 60
PLAYERMOVERATE = 5
BADDIEMINSIZE = 10
BADDIEMAXSIZE = 40
BADDIEMINSPEED = 1
BADDIEMAXSPEED = 8
ADDNEWBADDIERATE = 6

# Load and save high scores
def load_scores():
    try:
        with open('scores.txt', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_scores(scores):
    with open('scores.txt', 'w') as f:
        json.dump(scores, f)

scores = load_scores()

def terminate():
    pygame.quit()
    sys.exit()

# Function to wait for player input
def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return
            elif event.type == MOUSEBUTTONDOWN:
                return

def playerHasHitBaddie(playerRect, baddies):
    for b in baddies:
        if playerRect.colliderect(b['rect']):
            return True
    return False

def playerHasHitProjectile(playerRect, projectiles):
    for p in projectiles:
        if playerRect.colliderect(p['rect']):
            return True
    return False

# Draw text and buttons
def drawText(text, font, surface, x, y, color=TEXTCOLOR):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_button(surface, text, x, y, width, height, color):
    pygame.draw.rect(surface, color, (x, y, width, height))
    drawText(text, smallFont, surface, x + 10, y + 10)

# Load resources
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Dodger Game')
pygame.mouse.set_visible(True)

font = pygame.font.SysFont(None, 48)
smallFont = pygame.font.SysFont(None, 36)

playerImage = pygame.image.load('player.png').convert_alpha()
playerImage = pygame.transform.scale(playerImage, (50, 50))
playerRect = playerImage.get_rect()
baddieImage = pygame.image.load('baddie.png')

# Explosion images
explosion_images = [pygame.image.load(f"exp{i}.png").convert_alpha() for i in range(1, 6)]
explosion_images = [pygame.transform.scale(img, (100, 100)) for img in explosion_images]

waterImage = pygame.image.load('water.png').convert()
waterRect = waterImage.get_rect()

backgroundX = 0
backgroundSpeed = 2

# Function to play the intro video
def play_intro_video(video_path):
    clip = VideoFileClip(video_path)
    clip = clip.resize((WINDOWWIDTH, WINDOWHEIGHT))  # Adjust video size to fit the Pygame window
    
    for frame in clip.iter_frames(fps=FPS, dtype="uint8"):
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        windowSurface.blit(frame_surface, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
    
    clip.close()

# Explosion class
class Explosion:
    def __init__(self, x, y):
        self.images = explosion_images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0
        self.explosion_speed = 4

    def update(self):
        self.counter += 1
        if self.counter >= self.explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        return self.index >= len(self.images) - 1  # Return True if animation is done

# Main menu function
def show_main_menu():
    playerName = ""
    selectedLevel = None
    while True:
        windowSurface.fill((255, 255, 255))
        drawText('Dodger Game', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 6))
        drawText('Enter your name: ' + playerName, smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
        drawText('Select Difficulty:', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2))

        easy_color = (255, 0, 0) if selectedLevel == 'easy' else (0, 0, 0)
        medium_color = (255, 0, 0) if selectedLevel == 'medium' else (0, 0, 0)
        hard_color = (255, 0, 0) if selectedLevel == 'hard' else (0, 0, 0)

        drawText('1. Easy', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2) + 40, easy_color)
        drawText('2. Medium', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2) + 80, medium_color)
        drawText('3. Hard', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2) + 120, hard_color)

        start_button_color = (0, 255, 0) if playerName and selectedLevel else (150, 150, 150)
        draw_button(windowSurface, 'Start', (WINDOWWIDTH / 2 - 50), (WINDOWHEIGHT / 2) + 160, 100, 40, start_button_color)

        drawText('High Scores:', smallFont, windowSurface, (WINDOWWIDTH / 4 * 3), 50)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        for index, (name, score) in enumerate(sorted_scores):
            drawText(f'{index + 1}. {name}: {score}', smallFont, windowSurface, (WINDOWWIDTH / 4 * 3), 100 + index * 30)

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_RETURN and playerName and selectedLevel:
                    return playerName, selectedLevel
                elif event.key == K_BACKSPACE:
                    playerName = playerName[:-1]
                elif event.unicode.isalpha():
                    playerName += event.unicode
                elif event.key == K_1:
                    selectedLevel = 'easy'
                elif event.key == K_2:
                    selectedLevel = 'medium'
                elif event.key == K_3:
                    selectedLevel = 'hard'
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and playerName and selectedLevel:
                    mouse_x, mouse_y = event.pos
                    if (WINDOWWIDTH / 2 - 50 < mouse_x < WINDOWWIDTH / 2 + 50) and (WINDOWHEIGHT / 2 + 160 < mouse_y < WINDOWHEIGHT / 2 + 200):
                        return playerName, selectedLevel

# Game over menu function
def show_game_over_menu(score):
    while True:
        windowSurface.fill((255, 255, 255))
        drawText('Game Over', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 6))
        drawText(f'Your Score: {score}', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))

        draw_button(windowSurface, 'Back to Menu', (WINDOWWIDTH / 2 - 100), (WINDOWHEIGHT / 2), 200, 50, (0, 255, 0))
        draw_button(windowSurface, 'Play Again', (WINDOWWIDTH / 2 - 100), (WINDOWHEIGHT / 2 + 60), 200, 50, (0, 255, 0))

        drawText('High Scores:', smallFont, windowSurface, (WINDOWWIDTH / 4 * 3), 50)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        for index, (name, score) in enumerate(sorted_scores):
            drawText(f'{index + 1}. {name}: {score}', smallFont, windowSurface, (WINDOWWIDTH / 4 * 3), 100 + index * 30)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_RETURN:
                    return 'menu'  # Go back to the main menu
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if (WINDOWWIDTH / 2 - 100 < mouse_x < WINDOWWIDTH / 2 + 100) and (WINDOWHEIGHT / 2 < mouse_y < WINDOWHEIGHT / 2 + 50):
                        return 'menu'  # Back to the main menu
                    elif (WINDOWWIDTH / 2 - 100 < mouse_x < WINDOWWIDTH / 2 + 100) and (WINDOWHEIGHT / 2 + 60 < mouse_y < WINDOWHEIGHT / 2 + 110):
                        return 'play_again'  # Play again

# Main game function
def run_game(playerName, selectedLevel):
    score = 0
    baddies = []
    explosions = []
    projectiles = []

    playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 70)

    # Set baddie speed based on difficulty
    if selectedLevel == 'easy':
        baddieSpeed = 4
    elif selectedLevel == 'medium':
        baddieSpeed = 6
    else:
        baddieSpeed = 8

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and playerRect.left > 0:
            playerRect.move_ip(-PLAYERMOVERATE, 0)
        if keys[K_RIGHT] and playerRect.right < WINDOWWIDTH:
            playerRect.move_ip(PLAYERMOVERATE, 0)

        # Add new baddies
        if random.randint(0, ADDNEWBADDIERATE) == 0:
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            baddieRect = baddieImage.get_rect()
            baddieRect.topleft = (random.randint(0, WINDOWWIDTH - baddieSize), 0 - baddieSize)
            baddies.append({'rect': baddieRect, 'size': baddieSize})

        # Move baddies down
        for b in baddies:
            b['rect'].move_ip(0, baddieSpeed)
            if b['rect'].top > WINDOWHEIGHT:
                baddies.remove(b)
                score += 1

        # Check for collisions
        if playerHasHitBaddie(playerRect, baddies):
            explosion = Explosion(playerRect.centerx, playerRect.centery)
            explosions.append(explosion)
            break  # End the game loop on collision

        # Update explosions
        explosions = [exp for exp in explosions if not exp.update()]

        # Drawing
        windowSurface.blit(waterImage, (backgroundX, 0))
        windowSurface.blit(playerImage, playerRect)
        for b in baddies:
            windowSurface.blit(baddieImage, b['rect'])

        # Draw explosions
        for exp in explosions:
            windowSurface.blit(exp.image, exp.rect)

        drawText(f'Score: {score}', smallFont, windowSurface, 10, 10)
        
        pygame.display.update()
        mainClock.tick(FPS)

    # After game over, handle score saving
    if playerName in scores:
        scores[playerName] = max(scores[playerName], score)
    else:
        scores[playerName] = score
    save_scores(scores)

# Main game loop
def main():
    while True:
        playerName, selectedLevel = show_main_menu()
        run_game(playerName, selectedLevel)
        show_game_over_menu(score)

if __name__ == '__main__':
    main()
