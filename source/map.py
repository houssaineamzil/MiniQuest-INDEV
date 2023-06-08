import random
import pygame
import pytmx
import math
from player import Player
from particle import Particle
from archer import Archer
from dragon import Dragon
from enemy import Enemy
from projectile import Arrow, Spell
from explosion import SpellExplosion, ArrowExplosion


class Map:
    def __init__(self, map_file, screen_width, screen_height):
        self.map_file = map_file
        self.map_data = pytmx.load_pygame(map_file)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enemies = []
        self.projectiles = []
        self.portals = []
        self.particles = []
        self.explosions = []
        self.collision_tiles = []

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def add_particle(self, particle):
        self.particles.append(particle)

    def add_projectile(self, projectile):
        self.projectiles.append(projectile)

    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def remove_projectile(self, projectile):
        if projectile in self.projectiles:
            self.projectiles.remove(projectile)

    def update(
        self,
        gameScreen,
        player,
    ):
        for portal in self.portals:
            if player.collision_rect.colliderect(portal.rect):
                self.change_map("source/tile/" + portal.map_file + ".tmx")

                # Update the player's position
                player.rect.midbottom = (portal.destination[0], portal.destination[1])
                player.collision_rect.midbottom = (
                    portal.destination[0],
                    portal.destination[1],
                )
                # self.add_enemy(Dragon(250, 300, "source/img/dragon.png", 50, 5))
                if portal.map_file == "path":
                    self.add_enemy(
                        Archer(100, 100, "source/img/archer.png", 30, 2)
                    )  # Create enemy
                break

        for enemy in self.enemies:  # Loop over each enemy in the list
            if isinstance(enemy, Archer):
                enemy.ai_move(
                    self.collision_tiles,
                    self.screen_width,
                    self.screen_height,
                    player.rect.centerx,
                    player.rect.centery,
                )
            else:
                enemy.ai_move(
                    self.collision_tiles, self.screen_width, self.screen_height
                )
            enemy.draw(gameScreen)
            enemy.shoot(
                player.rect.centerx,
                player.rect.centery,
                self.projectiles,
                self.add_particle,
            )

            for projectile in self.projectiles:
                if enemy.rect.colliderect(projectile.rect) and not isinstance(
                    projectile.owner, Enemy
                ):
                    enemy.take_damage()
                    if isinstance(projectile, Arrow):
                        self.explosions.append(
                            ArrowExplosion(
                                projectile.rect.centerx, projectile.rect.centery
                            )
                        )
                    elif isinstance(projectile, Spell):
                        self.explosions.append(
                            SpellExplosion(
                                projectile.rect.centerx, projectile.rect.centery
                            )
                        )

                    if (
                        projectile in self.projectiles
                    ):  # Check if projectile still exists in the list
                        self.projectiles.remove(projectile)
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)  # Remove enemy from the list
                        break

        for projectile in self.projectiles:
            if (
                player.rect.colliderect(projectile.rect)
                and projectile.owner is not player
            ):
                for enemy in self.enemies:
                    enemy.canshoot = False
                # Disable player movement
                player.speed = 0
                player.canshoot = False

                # Remove the projectile
                self.projectiles.remove(projectile)
                # Stop shooting
                canshoot = False
                player.hit_by_projectile()
                player.image = pygame.transform.rotate(
                    player.image, -90
                )  # rotate 90 degrees clockwise

                if (
                    projectile in self.projectiles
                ):  # Check if projectile still exists in the list
                    self.projectiles.remove(projectile)

            if projectile.update(
                self.collision_tiles, self.screen_width, self.screen_height
            ):
                if isinstance(projectile, Arrow):
                    self.explosions.append(
                        ArrowExplosion(projectile.rect.centerx, projectile.rect.centery)
                    )
                elif isinstance(projectile, Spell):
                    self.explosions.append(
                        SpellExplosion(projectile.rect.centerx, projectile.rect.centery)
                    )
                if (
                    projectile in self.projectiles
                ):  # Check if projectile still exists in the list
                    self.projectiles.remove(projectile)
            else:
                gameScreen.blit(projectile.image, projectile.rect)

        for particle in list(self.particles):  # Iterate over a copy of the list
            if particle.update():
                if (
                    particle in self.particles
                ):  # Check if particle still exists in the list
                    self.particles.remove(particle)
            else:
                gameScreen.blit(particle.image, particle.rect)

        for explosion in list(self.explosions):  # Iterate over a copy of the list
            if explosion.update():
                if (
                    explosion in self.explosions
                ):  # Check if explosion still exists in the list
                    self.explosions.remove(explosion)
            else:
                for particle in explosion.particles:
                    gameScreen.blit(particle.image, particle.rect)

    def change_map(self, map_file):
        self.map_file = map_file
        self.map_data = pytmx.load_pygame(map_file)  # Load the new map data
        self.collisionSetup()  # Update the list of collision tiles
        self.enemies.clear()  # Remove any existing enemies
        self.projectiles.clear()  # Remove any existing projectiles
        self.particles.clear()  # Remove any existing particles
        self.explosions.clear()  # Remove any existing explosions

    def collisionSetup(self):
        self.collision_tiles = []
        self.portals = []
        for layer in self.map_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "portal":
                    for obj in layer:
                        if obj.name is not None:  # check if name is not None
                            portal_rect = pygame.Rect(
                                obj.x, obj.y, obj.width, obj.height
                            )
                            portal_info = obj.name.split(
                                ","
                            )  # Split the portal name into parts
                            map_file = portal_info[0]
                            destination = tuple(
                                int(i) for i in portal_info[1:]
                            )  # convert to integers and pack in a tuple
                            self.portals.append(
                                Portal(portal_rect, map_file, destination)
                            )
            if layer.name == "collision":
                for obj in layer:
                    collision_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    self.collision_tiles.append(collision_rect)

    def drawGroundLayer(self, gameScreen):
        ground_layer = self.map_data.get_layer_by_name("ground")

        for x, y, gid in ground_layer:
            tile = self.map_data.get_tile_image_by_gid(gid)
            if tile:
                gameScreen.blit(
                    tile, (x * self.map_data.tilewidth, y * self.map_data.tileheight)
                )

    def drawFloorLayer(self, gameScreen):
        ground_layer = self.map_data.get_layer_by_name("floor")

        for x, y, gid in ground_layer:
            tile = self.map_data.get_tile_image_by_gid(gid)
            if tile:
                gameScreen.blit(
                    tile, (x * self.map_data.tilewidth, y * self.map_data.tileheight)
                )

    def drawAboveGroundLayer(self, gameScreen):
        above_ground_layer = self.map_data.get_layer_by_name("above_ground")

        for x, y, gid in above_ground_layer:
            tile = self.map_data.get_tile_image_by_gid(gid)
            if tile:
                gameScreen.blit(
                    tile, (x * self.map_data.tilewidth, y * self.map_data.tileheight)
                )

    def walk_particles(self, entity):
        if random.random() < 0.3:
            x = entity.rect.x + entity.image.get_width() // 2
            y = entity.rect.y + entity.image.get_height()

            velocity_x = random.uniform(-0.3, 0.3)  # random velocity values
            velocity_y = random.uniform(-0.3, -0.3)
            color = (
                random.randint(100, 165),
                random.randint(50, 115),  # random brown colour
                random.randint(10, 45),
            )

            new_particle = Particle(
                x, y, velocity_x, velocity_y, color, random.randint(2, 4)
            )
            self.particles.append(new_particle)


class Portal:
    def __init__(self, rect, map_file, destination):
        self.rect = rect
        self.map_file = map_file
        self.destination = destination
