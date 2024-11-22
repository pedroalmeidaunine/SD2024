import pygame
import random
import sys
import json
from pygame.locals import * # type: ignore
from moviepy.editor import VideoFileClip
import time

# Initialize Pygame and window settings
pygame.init()
pygame.mixer.init()
info_object = pygame.display.Info()
window_width = info_object.current_w
window_height = info_object.current_h

# Initialize Oxygen level
oxygen_max = 20  # Maximum oxygen level
increase_in_oxygen = 5
oxygen_decrease_rate = 3  # Adjust this rate to make oxygen last longer or shorter

text_color = (255,255,255)
fps = 60
baddie_min_size = 20
baddie_max_size = 40
baddie_min_speed = 1
baddie_max_speed = 8
add_new_baddie_rate = 6

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

# Draw text and buttons
def draw_text(text, font, surface, x, y, color=text_color):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_button(surface, text, x, y, width, height, color):
    pygame.draw.rect(surface, color, (x, y, width, height))
    draw_text(text, smallFont, surface, x + 10, y + 10,(0,0,0))

# Load resources
main_clock = pygame.time.Clock()
window_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Dodger Game')
pygame.mouse.set_visible(True)

font = pygame.font.SysFont(None, 48)
smallFont = pygame.font.SysFont(None, 36)


baddie_image = pygame.image.load('shark.png')  # https://creazilla.com/media/clipart/26116/shark
fish_image = pygame.image.load("fish.png") #https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.freepik.com%2Ffree-photos-vectors%2Ffish-clipart&psig=AOvVaw0CIFismgnzHrTir36AEXqa&ust=1732210925248000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCOjIidm664kDFQAAAAAdAAAAABAJ
oxygen_image = pygame.image.load("oxygen.png")  # https://favpng.com/png_view/dense-fog-the-discovery-of-oxygen-oxygen-therapy-clip-art-png/9DamM6uQ
trash_image = pygame.image.load("trash.png")  # https://www.freepik.com/premium-vector/hand-drawn-garbage-cartoon-vector-illustration-clipart-white-background_151613278.htm
bullet_image= pygame.image.load("bullet.png") #https://creazilla.com/media/clipart/7931732/flying-bullet
waterImage = pygame.image.load('water.png').convert()
waterRect = waterImage.get_rect()

# Explosion images
explosion_images = [pygame.image.load(f"exp{i}.png").convert_alpha() for i in range(1, 6)]
explosion_images = [pygame.transform.scale(img, (100, 100)) for img in explosion_images]

def play_intro_video(video_path):
    clip = VideoFileClip(video_path)
    clip = clip.resize((window_width, window_height))  # type: ignore # Resize to fit the window

    clip.preview()  # Plays video with sound
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
    

class Diver:
    def __init__(self, image_path):
        """
        Initialize the Diver object.
        :param image_path: Path to the player's image.
        """
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (90,50))
        self.rect = self.image.get_rect()
        self.rect.topleft = (50, window_height // 2)  # Start position
        self.move_rate = 1  # Default movement rate
    
    def move(self, move_left, move_right, move_up, move_down):
        """
        Move the player based on input flags.

        :param move_left: Boolean indicating left movement.
        :param move_right: Boolean indicating right movement.
        :param move_up: Boolean indicating upward movement.
        :param move_down: Boolean indicating downward movement.
        """
        if move_left and self.rect.left > 0:
            self.rect.move_ip(-self.move_rate, 0)
        if move_right and self.rect.right < window_width:
            self.rect.move_ip(self.move_rate, 0)
        if move_up and self.rect.top > 0:
            self.rect.move_ip(0, -self.move_rate)
        if move_down and self.rect.bottom < window_height:
            self.rect.move_ip(0, self.move_rate)
    
    def has_hit_baddie(self, baddies):
        """
        Check if the player has collided with any baddie.

        :param baddies: List of baddie objects.
        :return: True if a collision occurred, False otherwise.
        """
        for baddie in baddies:
            if self.rect.colliderect(baddie.rect):
                return True
        return False


class Fish:
    def __init__(self, image, is_friendly):
        """
        Initialize a Fish object.

        :param image: Pygame image for the fish.
        :param is_friendly: Boolean indicating if the fish is friendly.
        """
        self.image = image
        self.is_friendly = is_friendly
        self.size = random.randint(baddie_min_size, baddie_max_size)
        self.speed = random.randint(baddie_min_speed, baddie_max_speed)
        self.rect = pygame.Rect(
            window_width,  # Start off-screen to the right
            random.randint(0, window_height - self.size),  # Random y-position
            self.size,
            self.size,
        )
        self.surface = pygame.transform.scale(image, (self.size, self.size))
    
    def move(self):
        """
        Move the fish to the left based on its speed.
        """
        self.rect.x -= self.speed

    def is_off_screen(self):
        """
        Check if the fish has moved off-screen to the left.
        """
        return self.rect.right < 0

    def check_collision(self, projectiles):
        """
        Check for collisions with projectiles.

        :param projectiles: List of projectiles (each containing a rect).
        :return: The projectile it collides with, or None.
        """
        for projectile in projectiles:
            if self.rect.colliderect(projectile.rect):
                return projectile
        return None

    def handle_collision(self, projectile, explosions, score):
        pygame.mixer.music.load("blast.wav")

        # Play the MP3 file
        pygame.mixer.music.play()
        """
        Handle what happens when this fish collides with a projectile.

        :param projectile: The projectile that hit the fish.
        :param explosions: List to append explosions.
        :param score: Current game score (passed by reference).
        :return: Updated score.
        """
        # Friendly fish reduces score; hostile fish increases it
        if self.is_friendly:
            score-=20
        else:
            score+=10
        # Create an explosion at the collision point
        explosions.append(Explosion(self.rect.centerx, self.rect.centery))
        return score


class Projectile:
    def __init__(self, x, y):
        """
        Initialize a Projectile object.

        :param x: Starting x-coordinate of the projectile.
        :param y: Starting y-coordinate of the projectile.
        """
        self.rect = pygame.Rect(x, y, 15, 20)
        self.surface = pygame.transform.scale(bullet_image, (30,20))
        self.speed = 8

    def move(self):
        """
        Move the projectile to the right.
        """
        self.rect.x += self.speed

    def is_off_screen(self, window_width):
        """
        Check if the projectile has moved off-screen.

        :param window_width: Width of the game window.
        :return: True if off-screen, False otherwise.
        """
        return self.rect.left > window_width



class OxygenItem:
    def __init__(self, image,isTrash=False):
        """
        Initialize an OxygenItem object.
        
        :param image: The image to be used for the oxygen item.
        """
        self.rect = pygame.Rect(
            random.randint(80, window_width - 20),
            window_height - 40,
            50,50
        )
        self.speed = 3
        self.isTrash = isTrash
        self.surface = pygame.transform.scale(image, (50,50))
        self.spawn_time = time.time()  # Time when the item was created

    def move(self):
        """
        Move the projectile to the right.
        """
        self.rect.y -= self.speed

    def is_off_screen(self):
        """
        Check if the projectile has moved off-screen.

        :param 
        :return: True if off-screen, False otherwise.
        """
        return self.rect.top < 10
    
    def has_expired(self, current_time, expiration_rate):
        """
        Check if the oxygen item has expired based on the spawn time and expiration rate.
        
        :param current_time: The current time.
        :param expiration_rate: How long the item lasts before disappearing.
        :return: True if expired, False otherwise.
        """
        return current_time - self.spawn_time > expiration_rate

    def check_collision(self, player_rect):
        """
        Check if the oxygen item collides with the player.

        :param player_rect: The player's rectangle to check for collision.
        :return: True if collision detected, False otherwise.
        """
        return self.rect.colliderect(player_rect)
    
    def handle_collision(self, player):
        """
        Handle the collision with the player. This depends on the item type.
        
        :param player: The player object.
        :return: The score or oxygen change based on item type.
        """
        if self.isTrash:
            return 1  # Increase score by 10 for trash items
        else:
            return 'oxygen'  # Return a flag indicating it's an oxygen item



# Function to show the loss menu after the player dies
def show_loss_menu(playerName, score):
    # Load the background image
    background_image = pygame.image.load('background.png').convert()
    background_image = pygame.transform.scale(background_image, (window_width, window_height))  # Resize to fit the window

    while True:
        window_surface.blit(background_image, (0, 0))  # Draw the background image
        draw_text('Game Over', font, window_surface, (window_width / 4), (window_height / 6),(0,0,0))
        draw_text(f'Your Score: {score}', smallFont, window_surface, (window_width / 4), (window_height / 3.5),(0,0,0))

        # Draw buttons with custom colors
        backToMenu_button_color = (0, 0, 255)  # Blue
        playAgain_button_color = (0, 255, 0)  # Green
        quit_button_color = (255, 0, 0)  # Red

        # Draw the buttons
        draw_button(window_surface, 'Back to Menu', (window_width / 3), (window_height / 2), 180, 40, backToMenu_button_color)
        draw_button(window_surface, 'Play Again', (window_width / 3), (window_height / 2) + 60, 180, 40, playAgain_button_color)
        draw_button(window_surface, 'Quit', (window_width / 3), (window_height / 2) + 120, 180, 40, quit_button_color)

        # Display high scores on the right side
        draw_text('High Scores:', font, window_surface, (window_width *4 /5), (window_height / 6),(0,0,0))
        
        # Sort the scores and display the top 5 (or all if less)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for idx, (name, sc) in enumerate(sorted_scores):
            draw_text(f'{idx + 1}. {name}: {sc}', smallFont, window_surface, (window_width * 4 / 5), (window_height / 6) + 40 + (30 * idx),(0,0,0))


        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Check if "Back to Menu" is clicked
                if (window_width / 3 < mouse_x < window_width / 3 + 180) and (window_height / 2 < mouse_y < window_height / 2 + 40):
                    return 'menu'

                # Check if "Play Again" is clicked
                if (window_width / 3 < mouse_x < window_width / 3 + 180) and (window_height / 2 + 60 < mouse_y < window_height / 2 + 100):
                    return 'play_again'

                # Check if "Quit" is clicked
                if (window_width / 3 < mouse_x < window_width / 3 + 180) and (window_height / 2 + 120 < mouse_y < window_height / 2 + 160):
                    terminate()


# Main menu function
def show_main_menu():
    playerName = ""
    selectedLevel = None
    # Load the background image
    background_image = pygame.image.load('bg2.jpg').convert()  #https://images.pexels.com/photos/932638/pexels-photo-932638.jpeg?cs=srgb&dl=pexels-blaque-x-264516-932638.jpg&fm=jpg
    background_image = pygame.transform.scale(background_image, (window_width, window_height))  # Resize to fit the window

    while True:
        window_surface.blit(background_image, (0, 0))  # Draw the background image
        draw_text('Dodger Game', font, window_surface, (window_width / 3), (window_height / 6))
        draw_text('Enter your name: ' + playerName, smallFont, window_surface, (window_width / 3), (window_height / 3))
        draw_text('Select Difficulty:', smallFont, window_surface, (window_width / 3), (window_height / 2))

        # Set colors based on selected difficulty level
        easy_color = (255, 0, 0) if selectedLevel == 'easy' else (255,255,255)
        medium_color = (255, 0, 0) if selectedLevel == 'medium' else (255,255,255)
        hard_color = (255, 0, 0) if selectedLevel == 'hard' else (255,255,255)

        # Display difficulty options
        draw_text('1. Easy', smallFont, window_surface, (window_width / 3), (window_height / 2) + 40, easy_color)
        draw_text('2. Medium', smallFont, window_surface, (window_width / 3), (window_height / 2) + 80, medium_color)
        draw_text('3. Hard', smallFont, window_surface, (window_width / 3), (window_height / 2) + 120, hard_color)

        # Display Start button with appropriate color
        start_button_color = (0, 255, 0) if playerName and selectedLevel else (150, 150, 150)
        start_button_x = window_width / 2 - 50
        start_button_y = (window_height / 2) + 160
        draw_button(window_surface, 'Start', start_button_x, start_button_y, 100, 40, start_button_color)

        # Display QUIT button at bottom right
        quit_button_x = window_width - 120
        quit_button_y = window_height - 60
        draw_button(window_surface, 'QUIT', quit_button_x, quit_button_y, 100, 40, (255, 0, 0))

        # Display high scores on the right side
        draw_text('High Scores:', font, window_surface, (window_width * 2 / 3), (window_height / 6))
        
        # Sort the scores and display the top 5 (or all if less)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for idx, (name, sc) in enumerate(sorted_scores):
            draw_text(f'{idx + 1}. {name}: {sc}', smallFont, window_surface, (window_width * 2 / 3), (window_height / 6) + 40 + (30 * idx))

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
                if event.button == 1:  # Left mouse button
                    mouse_x, mouse_y = event.pos
                    
                    # Check if Start button clicked
                    if (start_button_x < mouse_x < start_button_x + 100) and (start_button_y < mouse_y < start_button_y + 40) and playerName and selectedLevel:
                        return playerName, selectedLevel
                    
                    # Check if QUIT button clicked
                    elif (quit_button_x < mouse_x < quit_button_x + 100) and (quit_button_y < mouse_y < quit_button_y + 40):
                        terminate()
                    
                    # Check if difficulty buttons clicked
                    if (window_width / 3 < mouse_x < window_width / 3 + 100):
                        if (window_height / 2 + 40 < mouse_y < window_height / 2 + 80):
                            selectedLevel = 'easy'
                        elif (window_height / 2 + 80 < mouse_y < window_height / 2 + 120):
                            selectedLevel = 'medium'
                        elif (window_height / 2 + 120 < mouse_y < window_height / 2 + 160):
                            selectedLevel = 'hard'


# Game loop
def game_loop(playerName, selectedLevel):
    global add_new_baddie_rate, baddie_max_speed,oxygen_decrease_rate
    baddie_speed = 5
    baddie_rate = 25

    if selectedLevel == 'easy':
        add_new_baddie_rate = baddie_rate
        baddie_max_speed = baddie_speed
    elif selectedLevel == 'medium':
        add_new_baddie_rate = add_new_baddie_rate +2
        baddie_max_speed = baddie_max_speed + 3
        oxygen_decrease_rate -=0.5
    else:
        add_new_baddie_rate = add_new_baddie_rate +3
        baddie_max_speed = baddie_max_speed +7
        oxygen_decrease_rate -=1

    baddies = []
    fishes = []
    projectiles = []
    explosions = []  # Store explosions
    oxygen_items = []  # List to hold oxygen bubbles/items
    trash_items = []
    score = 0
    moveLeft = moveRight = moveUp = moveDown = False
    baddieAddCounter = 0
    oxygen_spawn_counter = 0  # To control oxygen item spawns
    oxygen_level = oxygen_max  # Start fully charged
    last_update_time = pygame.time.get_ticks()
    player = Diver("diver.png")  # https://creazilla.com/media/clipart/1795612/scuba-diver
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key in [K_LEFT, K_a]: moveLeft = True
                elif event.key in [K_RIGHT, K_d]: moveRight = True
                elif event.key in [K_UP, K_w]: moveUp = True
                elif event.key in [K_DOWN, K_s]: moveDown = True
                elif event.key == K_SPACE:
                    projectile = Projectile(player.rect.right,player.rect.centery -5)
                    projectiles.append(projectile)
            elif event.type == KEYUP:
                if event.key in [K_LEFT, K_a]: moveLeft = False
                elif event.key in [K_RIGHT, K_d]: moveRight = False
                elif event.key in [K_UP, K_w]: moveUp = False
                elif event.key in [K_DOWN, K_s]: moveDown = False
            elif event.type == MOUSEMOTION:
                player.rect.center = event.pos

        player.move(moveLeft, moveRight, moveUp, moveDown)

        baddieAddCounter += 1
        if baddieAddCounter >= add_new_baddie_rate:
            if(random.randint(1,10) == 3 and oxygen_spawn_counter<2):
                item = OxygenItem(oxygen_image)
                oxygen_spawn_counter +=1
                oxygen_items.append(item)

            if(random.randint(1,5) == 4 and len(trash_items)<2):
                trash = OxygenItem(trash_image,True)
                trash_items.append(trash)

            if(random.randint(1,7) == 6 and len(fishes)<3):
                fish = Fish(fish_image,True)
                fishes.append(fish)
            baddieAddCounter = 0
            newBaddie = Fish(baddie_image,False)
            baddies.append(newBaddie)

        for b in baddies[:]:
            b.move()
            
            if b.is_off_screen():
                baddies.remove(b)
                continue
            projectile = b.check_collision(projectiles)
            if projectile:
                score = b.handle_collision(projectile, explosions, score)
                baddies.remove(b)
                projectiles.remove(projectile)

        for fish in fishes[:]:
            fish.move()
            
            # Remove fish that go off-screen
            if fish.is_off_screen():
                fishes.remove(fish)
                continue

            projectile = fish.check_collision(projectiles)
            if projectile:
                score = fish.handle_collision(projectile, explosions, score)
                fishes.remove(fish)
                projectiles.remove(projectile)

        for projectile in projectiles[:]:
            projectile.move()

            # Remove projectiles that move off-screen
            if projectile.is_off_screen(window_width):
                projectiles.remove(projectile)

        current_time = time.time()
        for item in oxygen_items[:]:
            item.move()
            if item.is_off_screen():
                oxygen_items.remove(item)
                continue

            if item.check_collision(player.rect):
                pygame.mixer.music.load("pickup.wav")
                pygame.mixer.music.play()
                oxygen_level += increase_in_oxygen  # Increase item level
                oxygen_items.remove(item)  # Remove the collected oxygen item
                oxygen_spawn_counter -= 1
                
            if item.has_expired(current_time, oxygen_decrease_rate):
                oxygen_items.remove(item)
                oxygen_spawn_counter -= 1

        for trash in trash_items[:]:
            if trash.has_expired(current_time,oxygen_decrease_rate):
                trash_items.remove(trash)

        for trash in trash_items[:]:
            if trash.check_collision(player.rect):
                if trash.handle_collision(player) == 1:
                    score +=10
                    trash_items.remove(trash)

        # Update and draw explosions
        for explosion in explosions[:]:
            if explosion.update():
                explosions.remove(explosion)

        #Player Hits Baddie  
        if player.has_hit_baddie(baddies) or oxygen_level == 0:
            pygame.mixer.music.load("gameover.wav")
            # Play the MP3 file
            pygame.mixer.music.play()
            # Update the player's high score
            if playerName in scores:
                scores[playerName] = max(scores[playerName], score)
            else:
                scores[playerName] = score
            
            # Save the updated scores
            save_scores(scores)

            # Show the loss menu and handle the player's choice
            menu_choice = show_loss_menu(playerName, score)
            if menu_choice == 'menu':
                show_main_menu()  # Return to the main menu
                return "menu"     # Exit the game loop
            elif menu_choice == 'play_again':
                game_loop(playerName, selectedLevel)  # Restart the game loop
                return "play_again"  # Optional for clarity


        if pygame.time.get_ticks() - last_update_time >= 1000:  # 1000 ms = 1 second
            oxygen_level -= 1
            last_update_time = pygame.time.get_ticks()
                            

        window_surface.fill((255, 255, 255))
        window_surface.blit(waterImage, (0, 0))

        for b in baddies:
            window_surface.blit(b.surface, b.rect)

        for fish in fishes:
            window_surface.blit(fish.surface, fish.rect)

        for projectile in projectiles:
            window_surface.blit(projectile.surface, projectile.rect)

        for explosion in explosions:
            window_surface.blit(explosion.image, explosion.rect)

        for oxygen in oxygen_items:
            window_surface.blit(oxygen.surface,oxygen.rect)

        for trash in trash_items:
            window_surface.blit(trash.surface,trash.rect)

        window_surface.blit(player.image, player.rect)
        draw_text(f'Score: {score}', smallFont, window_surface, 10, 10,color=(255,255,0))
        draw_text(f'Oxygen Level: {oxygen_level}', smallFont, window_surface, window_width-250, 10,color=(200,0,20))

        pygame.display.update()
        main_clock.tick(fps)

# Main application loop
while True:
    playerName, selectedLevel = show_main_menu()
    game_loop(playerName, selectedLevel)
    