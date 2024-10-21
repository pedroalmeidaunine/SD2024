import pygame, random, sys
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

# Load and make the player image transparent
playerImage = pygame.image.load('player.png').convert_alpha()  # Ensure the image supports transparency
playerImage = pygame.transform.scale(playerImage, (50, 50))  # Scale the diver to an appropriate size
playerRect = playerImage.get_rect()
baddieImage = pygame.image.load('baddie.png')

# Charge et configure l'image d'eau pour le fond dynamique
waterImage = pygame.image.load('water.png').convert()
waterRect = waterImage.get_rect()

# Variables pour le défilement du fond
backgroundX = 0
backgroundSpeed = 2  # Vitesse de défilement du fond

# Affichage de l'écran de démarrage
windowSurface.fill((255, 255, 255))
drawText('Dodger', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
drawText('Press a key to start.', font, windowSurface, (WINDOWWIDTH / 3) - 30, (WINDOWHEIGHT / 3) + 50)
pygame.display.update()
waitForPlayerToPressKey()

topScore = 0
while True:
    # Initialisation du jeu
    baddies = []
    score = 0
    playerRect.topleft = (50, WINDOWHEIGHT / 2)
    moveLeft = moveRight = moveUp = moveDown = False
    reverseCheat = slowCheat = False
    baddieAddCounter = 0

    while True:  # Boucle principale
        score += 1

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_z:
                    reverseCheat = True
                if event.key == K_x:
                    slowCheat = True
                if event.key == K_LEFT or event.key == K_a:
                    moveRight = False
                    moveLeft = True
                if event.key == K_RIGHT or event.key == K_d:
                    moveLeft = False
                    moveRight = True
                if event.key == K_UP or event.key == K_w:
                    moveDown = False
                    moveUp = True
                if event.key == K_DOWN or event.key == K_s:
                    moveUp = False
                    moveDown = True
            if event.type == KEYUP:
                if event.key == K_z:
                    reverseCheat = False
                    score = 0
                if event.key == K_x:
                    slowCheat = False
                    score = 0
                if event.key == K_ESCAPE:
                    terminate()

                if event.key == K_LEFT or event.key == K_a:
                    moveLeft = False
                if event.key == K_RIGHT or event.key == K_d:
                    moveRight = False
                if event.key == K_UP or event.key == K_w:
                    moveUp = False
                if event.key == K_DOWN or event.key == K_s:
                    moveDown = False

        # Ajout des baddies
        baddieAddCounter += 1
        if baddieAddCounter == ADDNEWBADDIERATE:
            baddieAddCounter = 0
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            newBaddie = {'rect': pygame.Rect(WINDOWWIDTH, random.randint(0, WINDOWHEIGHT - baddieSize), baddieSize, baddieSize),
                        'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                        'surface': pygame.transform.scale(baddieImage, (baddieSize, baddieSize)),
                        }
            baddies.append(newBaddie)

        # Mouvement du joueur
        if moveLeft and playerRect.left > 0:
            playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
        if moveRight and playerRect.right < WINDOWWIDTH:
            playerRect.move_ip(PLAYERMOVERATE, 0)
        if moveUp and playerRect.top > 0:
            playerRect.move_ip(0, -1 * PLAYERMOVERATE)
        if moveDown and playerRect.bottom < WINDOWHEIGHT:
            playerRect.move_ip(0, PLAYERMOVERATE)

        # Déplacement des baddies
        for b in baddies:
            if not reverseCheat and not slowCheat:
                b['rect'].move_ip(-b['speed'], 0)
            elif reverseCheat:
                b['rect'].move_ip(5, 0)
            elif slowCheat:
                b['rect'].move_ip(-1, 0)

        # Supprimer les baddies qui sortent de l'écran
        for b in baddies[:]:
            if b['rect'].right < 0:
                baddies.remove(b)

        # Mouvement du fond d'eau
        backgroundX -= backgroundSpeed
        if backgroundX <= -waterRect.width:
            backgroundX = 0  # Réinitialise le fond une fois qu'il a défilé complètement

        # Dessine le fond d'eau
        windowSurface.blit(waterImage, (backgroundX, 0))
        windowSurface.blit(waterImage, (backgroundX + waterRect.width, 0))  # Deuxième image pour le défilement

        # Dessine le score, le joueur, et les baddies
        drawText(f'Score: {score}', font, windowSurface, 10, 0)
        drawText(f'Top Score: {topScore}', font, windowSurface, 10, 40)
        windowSurface.blit(playerImage, playerRect)

        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])

        pygame.display.update()

        if playerHasHitBaddie(playerRect, baddies):
            if score > topScore:
                topScore = score
            break

        mainClock.tick(FPS)

    # Game over
    drawText('GAME OVER', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
    drawText('Press a key to play again.', font, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 50)
    pygame.display.update()
    waitForPlayerToPressKey()
