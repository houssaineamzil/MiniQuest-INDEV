import random
import os
import pygame
import pytmx
import math
import pickle
from player import Player
from particle import Particle
from archer import Archer
from dragon import Dragon
from projectile import Arrow, FireBall
from explosion import FireBallExplosion, ArrowExplosion, Explosion
from chest import Chest


class Map:
    def __init__(self, map_file, screen_width, screen_height):
        self.map_file = map_file
        self.map_data = pytmx.load_pygame(map_file)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enemies = []
        self.projectiles = []
        self.portals = []
        self.below_particles = []
        self.particles = []
        self.explosions = []
        self.collision_tiles = []
        self.chests = []
        self.spawn_chests()
        self.spawn_enemies()

    def spawn_enemies(self):
        self.enemy_objects = self.map_data.get_layer_by_name("enemies")
        for obj in self.enemy_objects:
            try:
                enemy_class = globals()[obj.name]
                enemy = enemy_class(
                    obj.x + obj.width / 2, obj.y + obj.height / 2, obj.hp
                )
                self.add_enemy(enemy)
            except KeyError:
                print(f"Warning: Unknown enemy type {obj.name}")

    def spawn_chests(self):
        chest_objects = self.map_data.get_layer_by_name("chests")
        for obj in chest_objects:
            chest = Chest(obj.x, obj.y, obj.width, obj.height, obj.items)
            self.chests.append(chest)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def add_particle(self, particle):
        self.particles.append(particle)

    def add_below_particle(self, particle):
        self.below_particles.append(particle)

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

    def remove_below_particle(self, particle):
        if particle in self.below_particles:
            self.below_particles.remove(particle)

    def remove_explosion(self, explosion):
        if explosion in self.particles:
            self.explosions.remove(explosion)

    def update(self, game_screen, player):
        self.update_portals(player)
        self.update_enemies(game_screen, player)
        self.update_projectiles(game_screen, player)
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

            if enemy.shoot(player, self.collision_tiles):
                self.add_projectile(enemy.projectile)

            enemy.draw(game_screen)

            for projectile in self.projectiles:
                if enemy.rect.colliderect(projectile.collision_rect) and isinstance(
                    projectile.owner, Player
                ):
                    enemy.take_damage()
                    explosion = projectile.explosion(
                        projectile.collision_rect.centerx,
                        projectile.collision_rect.centery,
                    )
                    self.add_explosion(explosion)

                    self.remove_projectile(projectile)
                    if enemy.hp <= 0:
                        self.remove_enemy(enemy)
                        break

    def update_projectiles(self, game_screen, player):
        for projectile in self.projectiles:
            if (
                player.teleporting == False
                and player.rect.colliderect(projectile.collision_rect)
                and projectile.owner is not player
            ):
                self.remove_projectile(projectile)
                player.hit_by_projectile()

            if projectile.update(
                self.collision_tiles, self.screen_width, self.screen_height
            ):
                explosion = projectile.explosion(
                    projectile.collision_rect.centerx, projectile.collision_rect.centery
                )
                self.add_explosion(explosion)
                self.remove_projectile(projectile)
            else:
                self.add_particle(projectile.particle)
                game_screen.blit(projectile.image, projectile.rect)
            # self.draw_rects(game_screen, projectile)  # DEBUG PROJECTILE COLLISION BOX

    def update_particles(self, game_screen, list):
        for particle in list:
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

    def change_map(self, new_map_file):
        self.save_state(self.map_file + ".pkl")

        self.map_file = new_map_file
        self.map_data = pytmx.load_pygame(new_map_file)
        self.object_setup()
        self.projectiles.clear()
        self.particles.clear()
        self.explosions.clear()
        self.enemies.clear()
        self.chests.clear()

        if (
            not os.path.exists(new_map_file + ".pkl")
            or os.path.getsize(new_map_file + ".pkl") == 0
        ):
            self.spawn_enemies()
            self.spawn_chests()
        else:
            self.load_state(new_map_file + ".pkl")

    def object_setup(self):
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
            if layer.name == "chests":
                for obj in layer:
                    x = obj.x + (obj.width // 4)
                    y = obj.y + (obj.height // 4)
                    width = obj.width // 2
                    height = obj.height // 2
                    collision_rect = pygame.Rect(x, y, width, height)
                    self.collision_tiles.append(collision_rect)

    def draw_layer(self, game_screen, layer):
        layer = self.map_data.get_layer_by_name(layer)

        for x, y, gid in layer:
            tile = self.map_data.get_tile_image_by_gid(gid)
            if tile:
                game_screen.blit(
                    tile, (x * self.map_data.tilewidth, y * self.map_data.tileheight)
                )

    def walk_particles(self, entity):
        if random.random() < 0.3:
            x = entity.rect.x + entity.size_x // 2
            y = entity.rect.y + entity.size_y

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
            self.add_below_particle(particle)

    def draw_rects(self, gameScreen, entity):
        pygame.draw.rect(gameScreen, (255, 0, 0), entity.rect, 2)
        pygame.draw.rect(gameScreen, (0, 255, 0), entity.collision_rect, 2)

    def save_state(self, state_filename):
        state = {
            "chests": [
                (
                    chest.rect.x,
                    chest.rect.y,
                    chest.rect.width,
                    chest.rect.height,
                    [item.class_name for item in chest.items],
                )
                for chest in self.chests
            ],
            "enemies": [
                (type(enemy).__name__, enemy.rect.x, enemy.rect.y, enemy.hp)
                for enemy in self.enemies
            ],
        }
        with open(state_filename, "wb") as f:
            pickle.dump(state, f)
        print(f"State saved in {state_filename}")

    def load_state(self, state_filename):
        if not os.path.exists(state_filename) or os.path.getsize(state_filename) == 0:
            print(f"File {state_filename} not found or empty.")
            return

        with open(state_filename, "rb") as f:
            state = pickle.load(f)

        self.load_enemies_state(state)
        self.load_chests_state(state)

    def load_enemies_state(self, state):
        self.enemies = []
        for enemy_info in state["enemies"]:
            class_name, x, y, hp = enemy_info
            enemy_class = globals()[class_name]
            self.enemies.append(enemy_class(x, y, hp))

    def load_chests_state(self, state):
        self.chests = []
        for chest_info in state["chests"]:
            x, y, width, height, items = chest_info
            items_string = ",".join(items)
            chest = Chest(x, y, width, height, items_string)
            self.chests.append(chest)


class Portal:
    def __init__(self, rect, map_file, destination):
        self.rect = rect
        self.map_file = map_file
        self.destination = destination
