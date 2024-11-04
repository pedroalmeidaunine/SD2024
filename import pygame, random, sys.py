import pygame
import random
import sys
import json
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
            elif event.type == MOUSEBUTTONDOWN:  # Redémarrer avec un clic
                return

def playerHasHitBaddie(playerRect, baddies):
    for b in baddies:
        if playerRect.colliderect(b['rect']):
            return True
    return False

def drawText(text, font, surface, x, y, color=TEXTCOLOR):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_button(surface, text, x, y, width, height, color):
    pygame.draw.rect(surface, color, (x, y, width, height))
    drawText(text, smallFont, surface, x + 10, y + 10)

# Initialise pygame
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Dodger Game')
pygame.mouse.set_visible(True)

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

        # Indiquer la difficulté sélectionnée
        easy_color = (255, 0, 0) if selectedLevel == 'easy' else (0, 0, 0)
        medium_color = (255, 0, 0) if selectedLevel == 'medium' else (0, 0, 0)
        hard_color = (255, 0, 0) if selectedLevel == 'hard' else (0, 0, 0)

        drawText('1. Easy', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2) + 40, easy_color)
        drawText('2. Medium', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2) + 80, medium_color)
        drawText('3. Hard', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2) + 120, hard_color)

        # Bouton start
        start_button_color = (0, 255, 0) if playerName and selectedLevel else (150, 150, 150)
        draw_button(windowSurface, 'Start', (WINDOWWIDTH / 2 - 50), (WINDOWHEIGHT / 2) + 160, 100, 40, start_button_color)

        # Affichage du tableau des scores
        drawText('High Scores:', smallFont, windowSurface, (WINDOWWIDTH / 4 * 3), 50)  # Position ajustée
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        for index, (name, score) in enumerate(sorted_scores):
            drawText(f'{index + 1}. {name}: {score}', smallFont, windowSurface, (WINDOWWIDTH / 4 * 3), 100 + index * 30)  # Position ajustée

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_RETURN and playerName and selectedLevel:
                    return playerName, selectedLevel  # Démarrer le jeu
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
                mouse_x, mouse_y = event.pos
                # Vérifie si le bouton Start est cliqué
                if (WINDOWWIDTH / 2 - 50 < mouse_x < WINDOWWIDTH / 2 + 50) and (WINDOWHEIGHT / 2 + 160 < mouse_y < WINDOWHEIGHT / 2 + 200):
                    if playerName and selectedLevel:  # Vérifie que le nom et le niveau sont valides
                        return playerName, selectedLevel  # Démarrer le jeu

# Boucle principale du jeu
def game_loop(playerName, selectedLevel):
    global ADDNEWBADDIERATE, BADDIEMAXSPEED
    if selectedLevel == 'easy':
        ADDNEWBADDIERATE = 8
        BADDIEMAXSPEED = 5
    elif selectedLevel == 'medium':
        ADDNEWBADDIERATE = 6
        BADDIEMAXSPEED = 7
    else:
        ADDNEWBADDIERATE = 4
        BADDIEMAXSPEED = 9

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
            elif event.type == MOUSEMOTION:
                playerRect.center = event.pos  # Déplacer le joueur avec la souris

        # Mouvement du joueur
        if moveLeft and playerRect.left > 0:
            playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
        if moveRight and playerRect.right < WINDOWWIDTH:
            playerRect.move_ip(PLAYERMOVERATE, 0)
        if moveUp and playerRect.top > 0:
            playerRect.move_ip(0, -1 * PLAYERMOVERATE)
        if moveDown and playerRect.bottom < WINDOWHEIGHT:
            playerRect.move_ip(0, PLAYERMOVERATE)

        # Ajouter de nouveaux ennemis
        baddieAddCounter += 1
        if baddieAddCounter >= ADDNEWBADDIERATE:
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            baddieSpeed = random.randint(BADDIEMINSPEED, BADDIEMAXSPEED)
            baddieRect = pygame.Rect(WINDOWWIDTH, random.randint(0, WINDOWHEIGHT - baddieSize), baddieSize, baddieSize)
            baddies.append({'rect': baddieRect, 'surface': pygame.transform.scale(baddieImage, (baddieSize, baddieSize)), 'speed': baddieSpeed})
            baddieAddCounter = 0

        # Mouvements des ennemis
        for b in baddies:
            b['rect'].move_ip(-b['speed'], 0)

        # Vérifier si le joueur a touché un ennemi
        if playerHasHitBaddie(playerRect, baddies):
            break  # Quitter la boucle du jeu si le joueur touche un ennemi

        # Écran d'affichage
        windowSurface.blit(waterImage, (backgroundX, 0))  # Défilement de l'eau
        windowSurface.blit(waterImage, (backgroundX + waterImage.get_width(), 0))  # Deuxième image pour le défilement
        backgroundX -= backgroundSpeed
        if backgroundX <= -waterImage.get_width():
            backgroundX = 0  # Réinitialiser le défilement

        # Dessiner le joueur
        windowSurface.blit(playerImage, playerRect)

        # Dessiner les ennemis
        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])

        # Afficher le score
        drawText(f'Score: {score}', smallFont, windowSurface, 10, 10)

        pygame.display.update()
        mainClock.tick(FPS)

    # Afficher les résultats après la fin du jeu
    show_game_over_screen(playerName, score)

# Affiche l'écran de fin de jeu
def show_game_over_screen(playerName, score):
    global scores

    # Ajout du score au tableau des scores
    if playerName in scores:
        scores[playerName] += score
    else:
        scores[playerName] = score
    save_scores(scores)

    while True:
        windowSurface.fill((255, 255, 255))
        drawText('Game Over', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
        drawText(f'Your Score: {score}', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2))
        drawText('Press Enter to play again or Escape to quit', smallFont, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 2) + 50)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                if event.key == K_RETURN:
                    return  # Retourner au début de la boucle du jeu

# Boucle principale du programme
while True:
    playerName, selectedLevel = show_main_menu()  # Afficher le menu principal
    game_loop(playerName, selectedLevel)  # Démarrer le jeu


