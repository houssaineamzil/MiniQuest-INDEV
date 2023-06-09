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
from explosion import SpellExplosion, ArrowExplosion, Explosion


class Map:
    def __init__(self, map_file, screen_width, screen_height):
        self.map_file = map_file
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enemies = []
        self.projectiles = []
        self.portals = []
        self.particles = []
        self.explosions = []
        self.collision_tiles = []
        self.change_map(map_file)

    def spawn_enemies(self):
        self.enemy_objects = self.map_data.get_layer_by_name("enemies")
        for obj in self.enemy_objects:
            try:
                enemy_class = globals()[obj.name]
                enemy = enemy_class(obj.x + obj.width // 2, obj.y + obj.height // 2)
                self.add_enemy(enemy)
            except KeyError:
                print(f"Warning: Unknown enemy type {obj.name}")

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def add_particle(self, particle):
        self.particles.append(particle)

    def add_projectile(self, projectile):
        self.projectiles.append(projectile)

    def add_explosion(self, explosion):
        self.explosions.append(explosion)

    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def remove_projectile(self, projectile):
        if projectile in self.projectiles:
            self.projectiles.remove(projectile)

    def remove_particle(self, particle):
        if particle in self.particles:
            self.particles.remove(particle)

    def remove_explosion(self, explosion):
        if explosion in self.particles:
            self.explosions.remove(explosion)

    def update(self, game_screen, player):
        self.update_portals(player)
        self.update_enemies(game_screen, player)
        self.update_projectiles(game_screen, player)
        self.update_particles(game_screen)
        self.update_explosions(game_screen)

    def update_portals(self, player):
        for portal in self.portals:
            if player.collision_rect.colliderect(portal.rect):
                self.change_map("source/tile/" + portal.map_file + ".tmx")
                player.teleport(portal.destination[0], portal.destination[1])
                break

    def update_enemies(self, game_screen, player):
        for enemy in self.enemies:
            enemy.ai_move(
                self.collision_tiles,
                self.screen_width,
                self.screen_height,
                player.rect.centerx,
                player.rect.centery,
            )

            if enemy.shoot(player.rect.centerx, player.rect.centery):
                self.add_projectile(enemy.projectile)

            enemy.draw(game_screen)

            for projectile in self.projectiles:
                if enemy.rect.colliderect(projectile.rect) and isinstance(
                    projectile.owner, Player
                ):
                    enemy.take_damage()
                    explosion = projectile.explosion(
                        projectile.rect.centerx, projectile.rect.centery
                    )
                    self.add_explosion(explosion)

                    self.remove_projectile(projectile)
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                        break

    def update_projectiles(self, game_screen, player):
        for projectile in self.projectiles:
            if (
                player.rect.colliderect(projectile.rect)
                and projectile.owner is not player
            ):
                for enemy in self.enemies:
                    enemy.canshoot = False
                self.projectiles.remove(projectile)
                player.hit_by_projectile()

            if projectile.update(
                self.collision_tiles, self.screen_width, self.screen_height
            ):
                explosion = projectile.explosion(
                    projectile.rect.centerx, projectile.rect.centery
                )
                self.add_explosion(explosion)
                self.remove_projectile(projectile)
            else:
                self.add_particle(projectile.particle)
                game_screen.blit(projectile.image, projectile.rect)

    def update_particles(self, game_screen):
        for particle in list(self.particles):
            if particle.update():
                self.remove_particle(particle)
            else:
                game_screen.blit(particle.image, particle.rect)

    def update_explosions(self, game_screen):
        for explosion in list(self.explosions):
            if explosion.update():
                self.remove_explosion(explosion)
            else:
                for particle in explosion.particles:
                    game_screen.blit(particle.image, particle.rect)

    def change_map(self, map_file):
        self.map_file = map_file
        self.map_data = pytmx.load_pygame(map_file)
        self.collisionSetup()
        self.enemies.clear()
        self.projectiles.clear()
        self.particles.clear()
        self.explosions.clear()
        self.spawn_enemies()

    def collisionSetup(self):
        self.collision_tiles = []
        self.portals = []
        for layer in self.map_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "portal":
                    for obj in layer:
                        if obj.name is not None:
                            portal_rect = pygame.Rect(
                                obj.x, obj.y, obj.width, obj.height
                            )
                            portal_info = obj.name.split(",")
                            map_file = portal_info[0]
                            destination = tuple(int(i) for i in portal_info[1:])
                            self.portals.append(
                                Portal(portal_rect, map_file, destination)
                            )
            if layer.name == "collision":
                for obj in layer:
                    collision_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    self.collision_tiles.append(collision_rect)

    def drawGroundLayer(self, game_screen):
        ground_layer = self.map_data.get_layer_by_name("ground")

        for x, y, gid in ground_layer:
            tile = self.map_data.get_tile_image_by_gid(gid)
            if tile:
                game_screen.blit(
                    tile, (x * self.map_data.tilewidth, y * self.map_data.tileheight)
                )

    def drawFloorLayer(self, game_screen):
        ground_layer = self.map_data.get_layer_by_name("floor")

        for x, y, gid in ground_layer:
            tile = self.map_data.get_tile_image_by_gid(gid)
            if tile:
                game_screen.blit(
                    tile, (x * self.map_data.tilewidth, y * self.map_data.tileheight)
                )

    def drawAboveGroundLayer(self, game_screen):
        above_ground_layer = self.map_data.get_layer_by_name("above_ground")

        for x, y, gid in above_ground_layer:
            tile = self.map_data.get_tile_image_by_gid(gid)
            if tile:
                game_screen.blit(
                    tile, (x * self.map_data.tilewidth, y * self.map_data.tileheight)
                )

    def walk_particles(self, entity):
        if random.random() < 0.3:
            x = entity.rect.x + entity.image.get_width() // 2
            y = entity.rect.y + entity.image.get_height()

            velocity_x = random.uniform(-0.3, 0.3)
            velocity_y = random.uniform(-0.3, -0.3)
            color = (
                random.randint(100, 165),
                random.randint(50, 115),
                random.randint(10, 45),
            )

            particle = Particle(
                x, y, velocity_x, velocity_y, color, random.randint(2, 4)
            )
            self.add_particle(particle)


class Portal:
    def __init__(self, rect, map_file, destination):
        self.rect = rect
        self.map_file = map_file
        self.destination = destination
