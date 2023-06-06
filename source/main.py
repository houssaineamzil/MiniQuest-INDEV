import random
import pygame
import pytmx
import math

from player import Player
from particle import Particle
from projectile import Projectile
from explosion import Explosion
from archer import Archer
from dragon import Dragon
from enemy import Enemy
from projectile import Arrow
from projectile import Spell
from explosion import SpellExplosion, ArrowExplosion

pygame.init()
pygame.mixer.init()

screenWidth = 800
screenHeight = 800
tileSize = 20
last_shot = 0
gameScreen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("MiniQuest")
map = pytmx.load_pygame("source/tile/village.tmx", pixelalpha=True)
clockObject = pygame.time.Clock()
collision_tiles = []
enemies = []
portal_tiles = []


player = Player(400, 700, tileSize)


def create_particle(particle):
    particles.append(particle)


def walk_particles(self):
    if random.random() < 0.3:
        x = self.rect.x + self.image.get_width() // 2
        y = self.rect.y + self.image.get_height()

        velocity_x = random.uniform(-0.2, 0.2)  # random velocity values
        velocity_y = random.uniform(-0.2, 0.2)
        color = (
            random.randint(100, 165),
            random.randint(50, 115),  # random brown colour
            random.randint(10, 45),
        )

        new_particle = Particle(
            x, y, velocity_x, velocity_y, color, random.randint(2, 6)
        )
        particles.append(new_particle)


def drawGroundLayer2():
    ground_layer = map.get_layer_by_name("ground2")

    for x, y, gid in ground_layer:
        tile = map.get_tile_image_by_gid(gid)
        if tile:
            gameScreen.blit(tile, (x * map.tilewidth, y * map.tileheight))


def drawGroundLayer():
    ground_layer = map.get_layer_by_name("ground")

    for x, y, gid in ground_layer:
        tile = map.get_tile_image_by_gid(gid)
        if tile:
            gameScreen.blit(tile, (x * map.tilewidth, y * map.tileheight))


def drawAboveGroundLayer():
    above_ground_layer = map.get_layer_by_name("above_ground")

    for x, y, gid in above_ground_layer:
        tile = map.get_tile_image_by_gid(gid)
        if tile:
            gameScreen.blit(tile, (x * map.tilewidth, y * map.tileheight))


def collisionSetup():
    collision = map.get_layer_by_name("collision")
    portal_layer = map.get_layer_by_name("portal")
    for x, y, gid in collision:
        if gid:  # Check if the tile exists
            collision_tiles.append(
                pygame.Rect(
                    x * map.tilewidth,
                    y * map.tileheight,
                    map.tilewidth,
                    map.tileheight,
                )
            )

    for x, y, gid in portal_layer:
        if gid:  # Check if the tile exists
            portal_tiles.append(
                pygame.Rect(
                    x * map.tilewidth,
                    y * map.tileheight,
                    map.tilewidth,
                    map.tileheight,
                )
            )


collisionSetup()
# Create the enemy
for _ in range(1):
    dragon = Dragon(250, 300, "source/img/dragon.png", 60, 1)
    enemies.append(dragon)
for _ in range(0):
    archer = Archer(250, 400, "source/img/archer.png", 35, 1)
    enemies.append(archer)

# Load the music file
pygame.mixer.music.load("source/sound/music.wav")
fireball_sound = pygame.mixer.Sound("source/sound/fireball.mp3")
explosion_sound = pygame.mixer.Sound("source/sound/explosion.mp3")

# Play the music indefinitely
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.4)
# Inside your game loop
projectiles = []
particles = []
explosions = []
canshoot = True
run = True
while run:
    clockObject.tick(60)

    collision_tiles = []  # Reset the list of collision tiles
    portal_tiles = []
    collisionSetup()  # Update the list of collision tiles

    drawGroundLayer2()
    drawGroundLayer()  # Draw ground layer

    for portal in portal_tiles:
        if player.rect.colliderect(portal):
            # Load new map
            map = pytmx.load_pygame("source/tile/path.tmx", pixelalpha=True)

            # Define the position where you want to teleport the player
            player.rect.x = 560
            player.rect.y = 760
            player.collision_rect.x = 560
            player.collision_rect.y = (
                760 + player.rect.height - player.collision_rect.height
            )

            # Update the list of collision and portal tiles
            collisionSetup()
            for _ in range(1):
                archer = Archer(250, 400, "source/img/archer.png", 35, 1)
                enemies.append(archer)
            break

    for enemy in enemies:  # Loop over each enemy in the list
        if isinstance(enemy, Archer):
            enemy.ai_move(
                collision_tiles,
                screenWidth,
                screenHeight,
                player.rect.centerx,
                player.rect.centery,
            )
        else:
            enemy.ai_move(collision_tiles, screenWidth, screenHeight)
        enemy.draw(gameScreen)
        enemy.shoot(
            player.rect.centerx, player.rect.centery, projectiles, create_particle
        )

        for projectile in projectiles:
            if enemy.rect.colliderect(projectile.rect) and not isinstance(
                projectile.owner, Enemy
            ):
                enemy.take_damage()
                if isinstance(projectile, Arrow):
                    explosions.append(
                        ArrowExplosion(projectile.rect.centerx, projectile.rect.centery)
                    )
                elif isinstance(projectile, Spell):
                    explosions.append(
                        SpellExplosion(projectile.rect.centerx, projectile.rect.centery)
                    )
                explosion_sound.play()
                if (
                    projectile in projectiles
                ):  # Check if projectile still exists in the list
                    projectiles.remove(projectile)
                if enemy.hp <= 0:
                    enemies.remove(enemy)  # Remove enemy from the list
                    break

    for projectile in projectiles:
        if player.rect.colliderect(projectile.rect) and projectile.owner is not player:
            # Disable player movement
            player.speed = 0
            # Remove the projectile
            projectiles.remove(projectile)
            # Stop shooting
            canshoot = False
            player.hit_by_projectile()
            player.image = pygame.transform.rotate(
                player.image, -90
            )  # rotate 90 degrees clockwise

            if (
                projectile in projectiles
            ):  # Check if projectile still exists in the list
                projectiles.remove(projectile)

        if projectile.update(collision_tiles, screenWidth, screenHeight):
            if isinstance(projectile, Arrow):
                explosions.append(
                    ArrowExplosion(projectile.rect.centerx, projectile.rect.centery)
                )
            elif isinstance(projectile, Spell):
                explosions.append(
                    SpellExplosion(projectile.rect.centerx, projectile.rect.centery)
                )
            explosion_sound.play()
            if (
                projectile in projectiles
            ):  # Check if projectile still exists in the list
                projectiles.remove(projectile)
        else:
            gameScreen.blit(projectile.image, projectile.rect)

    for particle in list(particles):  # Iterate over a copy of the list
        if particle.update():
            if particle in particles:  # Check if particle still exists in the list
                particles.remove(particle)
        else:
            gameScreen.blit(particle.image, particle.rect)

    for explosion in list(explosions):  # Iterate over a copy of the list
        if explosion.update():
            if explosion in explosions:  # Check if explosion still exists in the list
                explosions.remove(explosion)
        else:
            for particle in explosion.particles:
                gameScreen.blit(particle.image, particle.rect)

    player.movement(
        collision_tiles, walk_particles, screenWidth, screenHeight
    )  # Draw player
    # Draw player
    gameScreen.blit(player.image, player.rect)
    # pygame.draw.rect(gameScreen, (255, 0, 0), player.collision_rect, 2)
    # pygame.draw.rect(gameScreen, (0, 255, 0), player.rect, 2)

    drawAboveGroundLayer()  # Draw above ground layer

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 & canshoot:  # Left mouse button
                current_time = pygame.time.get_ticks()
                if (
                    current_time - last_shot >= 1000
                ):  # Checks if it's been 1 second (1000 ms) since the last shot
                    # Play the fireball sound effect
                    fireball_sound.play()

                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    new_projectile = Arrow(
                        player.rect.centerx,
                        player.rect.centery,
                        mouse_x,
                        mouse_y,
                        20,
                        20,
                        player,
                        create_particle,  # Pass the callback function
                    )
                    projectiles.append(new_projectile)
                    last_shot = current_time  # Update the last_shot time

    pygame.display.update()

pygame.quit()
