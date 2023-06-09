import random
import pygame
import pytmx
import math

from player import Player
from particle import Particle
from archer import Archer
from dragon import Dragon
from projectile import Arrow, Spell, Projectile
from explosion import SpellExplosion, ArrowExplosion
from map import Map

pygame.init()
pygame.mixer.init()

screenWidth = 800
screenHeight = 800
tileSize = 20
last_shot = 0
gameScreen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("MiniQuest")
clockObject = pygame.time.Clock()


player = Player(400, 400, tileSize)  # Load players


map_file = "source/tile/village.tmx"  # Starting map
map = Map(map_file, screenWidth, screenHeight)
map.collisionSetup()


map.add_enemy(Archer(250, 300, "source/img/archer.png", 30, 1))  # Create enemy


pygame.mixer.music.load("source/sound/music.wav")  # Load music
pygame.mixer.music.play(
    -1
)  # Play the music forever - Todo: add different music for every map
pygame.mixer.music.set_volume(0.1)
run = True
while run:
    clockObject.tick(60)
    map.drawFloorLayer(gameScreen)
    map.drawGroundLayer(gameScreen)  # Draw ground layers

    # Map handles update of its entities
    map.update(gameScreen, player)

    player.movement(  # Movement for player
        map.collision_tiles, map.walk_particles, screenWidth, screenHeight
    )

    gameScreen.blit(player.image, player.rect)  # Uodate the player
    map.drawAboveGroundLayer(gameScreen)  # Draw above ground layer

    # player.drawRects(gameScreen)  # debug

    for event in pygame.event.get():  # check for player inputs - Todo: extract methods
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 & player.canshoot:  # Left mouse button
                current_time = pygame.time.get_ticks()
                if (
                    current_time - last_shot
                    >= 1000  # Checks if it's been 1 second (1000 ms) since the last shot
                ):
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    new_projectile = Spell(  # create the new projectile
                        mouse_x,
                        mouse_y,
                        30,
                        20,
                        player,
                    )
                    map.projectiles.append(
                        new_projectile
                    )  # add the projectile to the map
                    last_shot = current_time  # Update the last_shot time

    pygame.display.update()

pygame.quit()
