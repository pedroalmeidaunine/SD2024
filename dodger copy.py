import pygame, random, sys, json
from pygame.locals import *

# Taille de la fenêtre basée sur la taille de l'écran
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

# Système de meilleur score
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

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return

def playerHasHitBaddie(playerRect, baddies):
    for b in baddies:
        if playerRect.colliderect(b['rect']):
            return True
    return False

def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Initialise pygame
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Dodger with Water Background')
pygame.mouse.set_visible(False)

# Charge les ressources
font = pygame.font.SysFont(None, 48)
smallFont = pygame.font.SysFont(None, 36)

# Load and make the player image transparent
playerImage = pygame.image.load('player.png').convert_alpha()
playerImage = pygame.transform.scale(playerImage, (50, 50))
playerRect = playerImage.get_rect()
baddieImage = pygame.image.load('baddie.png')

# Charge et configure l'image d'eau pour le fond dynamique
waterImage = pygame.image.load('water.png').convert()
waterRect = waterImage.get_rect()

# Variables pour le défilement du fond
backgroundX = 0
backgroundSpeed = 2

# Fonction pour le menu principal
def show_main_menu():
    playerName = ""
    selectedLevel = None
    while True:
        windowSurface.fill((255, 255, 255))
        drawText('Dodger Game', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 6))
        drawText('Enter your name: ' + playerName, smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
        drawText('Select Difficulty:', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2))
        drawText('1. Easy  2. Medium  3. Hard', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2) + 40)
        drawText('Press Enter to start', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2) + 80)

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

# Initialisation du niveau et du joueur
playerName, selectedLevel = show_main_menu()
topScore = scores.get(playerName, 0)

# Configuration du niveau
if selectedLevel == 'easy':
    ADDNEWBADDIERATE = 8
    BADDIEMAXSPEED = 5
elif selectedLevel == 'medium':
    ADDNEWBADDIERATE = 6
    BADDIEMAXSPEED = 7
else:
    ADDNEWBADDIERATE = 4
    BADDIEMAXSPEED = 9

while True:
    # Initialisation du jeu
    baddies = []
    score = 0
    playerRect.topleft = (50, WINDOWHEIGHT / 2)
    moveLeft = moveRight = moveUp = moveDown = False
    baddieAddCounter = 0

    while True:  # Boucle principale
        score += 1

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key in [K_LEFT, K_a]: moveLeft = True
                elif event.key in [K_RIGHT, K_d]: moveRight = True
                elif event.key in [K_UP, K_w]: moveUp = True
                elif event.key in [K_DOWN, K_s]: moveDown = True
            elif event.type == KEYUP:
                if event.key in [K_LEFT, K_a]: moveLeft = False
                elif event.key in [K_RIGHT, K_d]: moveRight = False
                elif event.key in [K_UP, K_w]: moveUp = False
                elif event.key in [K_DOWN, K_s]: moveDown = False

        # Mouvement du joueur
        if moveLeft and playerRect.left > 0:
            playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
        if moveRight and playerRect.right < WINDOWWIDTH:
            playerRect.move_ip(PLAYERMOVERATE, 0)
        if moveUp and playerRect.top > 0:
            playerRect.move_ip(0, -1 * PLAYERMOVERATE)
        if moveDown and playerRect.bottom < WINDOWHEIGHT:
            playerRect.move_ip(0, PLAYERMOVERATE)

        # Ajout et mouvement des baddies
        baddieAddCounter += 1
        if baddieAddCounter >= ADDNEWBADDIERATE:
            baddieAddCounter = 0
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            newBaddie = {'rect': pygame.Rect(WINDOWWIDTH, random.randint(0, WINDOWHEIGHT - baddieSize), baddieSize, baddieSize),
                        'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                        'surface': pygame.transform.scale(baddieImage, (baddieSize, baddieSize)),
                        }
            baddies.append(newBaddie)

        for b in baddies:
            b['rect'].move_ip(-b['speed'], 0)
            if b['rect'].right < 0:
                baddies.remove(b)

        # Mouvement du fond d'eau
        backgroundX -= backgroundSpeed
        if backgroundX <= -waterRect.width:
            backgroundX = 0

        # Dessin du fond, du score, du joueur, et des baddies
        windowSurface.blit(waterImage, (backgroundX, 0))
        windowSurface.blit(waterImage, (backgroundX + waterRect.width, 0))
        drawText(f'Score: {score}', font, windowSurface, 10, 0)
        drawText(f'Top Score: {topScore}', font, windowSurface, 10, 40)
        windowSurface.blit(playerImage, playerRect)
        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])

        pygame.display.update()

        if playerHasHitBaddie(playerRect, baddies):
            if score > topScore:
                topScore = score
                scores[playerName] = topScore
                save_scores(scores)
            break

        mainClock.tick(FPS)

    # Game over
    drawText('GAME OVER', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
    drawText('Press a key to play again.', font, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 50)
    pygame.display.update()
    waitForPlayerToPressKey()
