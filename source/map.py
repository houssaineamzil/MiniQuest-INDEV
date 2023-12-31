import random
import os
from resourcePath import resource_path
import pygame
import pytmx
import math
import pickle
from player import Player
from particle import Particle, walkParticle
from enemy import Archer
from enemy import Dragon
from npc import Townsfolk
from projectile import Arrow, FireBall
from particleEffect import FireBallExplosion, ArrowExplosion
from chest import Chest
import tempfile


class Map:
    def __init__(self, map_file, screen_width, temp_dir):
        self.temp_dir = temp_dir
        self.map_file = map_file
        self.map_data = pytmx.load_pygame(resource_path("source/tile/" + map_file))

        self.new_music = None
        self.music_fading = False
        self.music = self.map_data.properties.get("music")
        pygame.mixer.music.load(resource_path("source/sound/" + self.music))
        pygame.mixer.music.play(loops=-1, fade_ms=2000)

        self.screen_width = screen_width
        self.enemies = []
        self.npcs = []
        self.projectiles = []
        self.portals = []
        self.ground_particles = []
        self.particles = []
        self.explosions = []
        self.collision_rects = []
        self.entity_collision_rects = []
        self.chests = []
        self.object_setup()
        self.spawn_chests()
        self.spawn_enemies()
        self.spawn_npcs()
        self.width = self.map_data.width * self.map_data.tilewidth
        self.height = self.map_data.height * self.map_data.tileheight
        self.surface = pygame.Surface((self.width, self.height))

    def update_music(self):
        if self.music_fading and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(resource_path("source/sound/" + self.new_music))
            pygame.mixer.music.play(loops=-1, fade_ms=2000)
            self.music_fading = False

    def spawn_npcs(self):
        npc_objects = self.map_data.get_layer_by_name("npcs")
        for obj in npc_objects:
            try:
                npc_class = globals()[obj.name]
                npc = npc_class(obj.x, obj.y, obj.hp)
                self.entity_collision_rects.append(npc.collision_rect)
                self.add_npc(npc)
            except KeyError:
                print(f"Warning: Unknown npc type {obj.name}")

    def spawn_enemies(self):
        self.enemy_objects = self.map_data.get_layer_by_name("enemies")
        for obj in self.enemy_objects:
            try:
                enemy_class = globals()[obj.name]
                enemy = enemy_class(obj.x, obj.y, obj.hp)
                self.add_enemy(enemy)
                self.entity_collision_rects.append(enemy.collision_rect)
            except KeyError:
                print(f"Warning: Unknown enemy type {obj.name}")

    def spawn_chests(self):
        chest_objects = self.map_data.get_layer_by_name("chests")
        for obj in chest_objects:
            chest = Chest(
                obj.x, obj.y, obj.width, obj.height, obj.items, self.screen_width
            )
            self.add_chest(chest)

    def add_chest(self, chest):
        self.chests.append(chest)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def add_particle(self, particle):
        self.particles.append(particle)

    def add_ground_particle(self, particle):
        self.ground_particles.append(particle)

    def add_projectile(self, projectile):
        self.projectiles.append(projectile)

    def add_explosion(self, explosion):
        self.explosions.append(explosion)

    def add_npc(self, npc):
        self.npcs.append(npc)

    def remove_npc(self, npc):
        if npc in self.npcs:
            self.npcs.remove(npc)

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

    def get_map_surface(self):
        return self.surface

    def update(self, player, camera):
        self.update_particles(self.ground_particles, player)
        self.update_portals(player, camera)
        self.update_projectiles(player)
        self.update_explosions()

    def update_portals(self, player, camera):
        for portal in self.portals:
            if player.collision_rect.colliderect(portal.rect):
                player.teleport(portal.destination[0], portal.destination[1])
                self.change_map(portal.map_file + ".tmx", player, camera)
                break

    def update_npc(self, player, npc):
        if npc.ai_move(
            self.collision_rects,
            self.entity_collision_rects,
            self.width,
            self.height,
        ):
            if random.random() < 0.3:
                walk_particle = walkParticle(npc)
                self.add_ground_particle(walk_particle)

    def update_enemy(self, player, enemy):
        if enemy.ai_move(
            self.collision_rects,
            self.entity_collision_rects,
            self.width,
            self.height,
            player.rect.centerx,
            player.rect.centery,
        ):
            if random.random() < 0.3:
                walk_particle = walkParticle(enemy)
                self.add_ground_particle(walk_particle)

        if enemy.attack(player, self.collision_rects):
            self.add_projectile(enemy.projectile)

        for projectile in self.projectiles:
            if enemy.rect.colliderect(projectile.collision_rect) and isinstance(
                projectile.owner, Player
            ):
                if not enemy.invincible:
                    enemy.take_damage()

                self.remove_projectile(projectile)
                if enemy.hp <= 0:
                    self.entity_collision_rects.remove(enemy.collision_rect)
                    self.remove_enemy(enemy)
                    break

    def update_projectiles(self, player):
        for projectile in self.projectiles:
            if (
                player.teleporting is False
                and player.rect.colliderect(projectile.collision_rect)
                and projectile.owner is not player
            ):
                if not player.invincible:
                    player.hit_by_projectile(projectile.damage)

                self.remove_projectile(projectile)

            if projectile.update(self.collision_rects, self.width, self.height):
                explosion = projectile.explosion(
                    projectile.collision_rect.centerx, projectile.collision_rect.centery
                )
                self.add_explosion(explosion)
                self.remove_projectile(projectile)
            else:
                self.add_particle(projectile.particle)
                self.surface.blit(projectile.image, projectile.rect)
            # self.draw_rects(game_screen, projectile)  # DEBUG PROJECTILE COLLISION BOX

    def update_particles(self, list, player):
        for particle in list:
            if particle.update(player.rect):
                self.remove_particle(particle)
            else:
                self.surface.blit(particle.image, particle.rect)

    def update_explosions(self):
        for explosion in list(self.explosions):
            if explosion.update():
                self.remove_explosion(explosion)
            else:
                for particle in explosion.particles:
                    self.surface.blit(particle.image, particle.rect)

    def change_map(self, new_map_file, player, camera):
        self.save_state(self.map_file + ".pkl")

        self.map_file = new_map_file
        self.map_data = pytmx.load_pygame(resource_path("source/tile/" + new_map_file))
        new_music = self.map_data.properties.get("music")

        if self.music != new_music:
            self.music = new_music
            pygame.mixer.music.fadeout(2000)
            self.new_music = self.music
            self.music_fading = True

        self.width = self.map_data.width * self.map_data.tilewidth
        self.height = self.map_data.height * self.map_data.tileheight
        self.surface = pygame.Surface((self.width, self.height))
        camera.change_map(self.width, self.height)
        camera.teleport_to_player(player.rect.center)

        self.object_setup()
        self.projectiles.clear()
        self.particles.clear()
        self.explosions.clear()
        self.enemies.clear()
        self.chests.clear()
        self.npcs.clear()
        self.entity_collision_rects.clear()
        self.entity_collision_rects.append(player.collision_rect)

        if (
            not os.path.exists(self.temp_dir.name + "/" + new_map_file + ".pkl")
            or os.path.getsize(self.temp_dir.name + "/" + new_map_file + ".pkl") == 0
        ):
            print(f"State file {self.temp_dir.name + new_map_file + '.pkl'} not found.")
            self.spawn_chests()
            self.spawn_enemies()
            self.spawn_npcs()
        else:
            self.load_state(self.temp_dir.name + "/" + new_map_file + ".pkl")
            print(f"State loaded from {self.temp_dir.name + new_map_file + '.pkl'}")

    def object_setup(self):
        self.collision_rects = []
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
                    self.collision_rects.append(collision_rect)
            if layer.name == "chests":
                for obj in layer:
                    x = obj.x + (obj.width // 4)
                    y = obj.y + (obj.height // 4)
                    width = obj.width // 2
                    height = obj.height // 2
                    collision_rect = pygame.Rect(x, y, width, height)
                    self.collision_rects.append(collision_rect)

    def draw_layer(self, layer):
        layer = self.map_data.get_layer_by_name(layer)

        for x, y, gid in layer:
            tile = self.map_data.get_tile_image_by_gid(gid)
            if tile:
                self.surface.blit(
                    tile, (x * self.map_data.tilewidth, y * self.map_data.tileheight)
                )

    def draw_rects(self, gameScreen, entity):
        pygame.draw.rect(gameScreen, (255, 0, 0), entity.rect, 2)
        pygame.draw.rect(gameScreen, (0, 255, 0), entity.collision_rect, 2)

    def draw_rect(self, gameScreen, rect):
        pygame.draw.rect(gameScreen, (0, 255, 0), rect, 2)

    def save_state(self, state_filename):
        state_filename = os.path.join(self.temp_dir.name, state_filename)
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
            "npcs": [
                (type(npc).__name__, npc.rect.x, npc.rect.y, npc.hp)
                for npc in self.npcs
            ],
        }
        with open(state_filename, "wb") as f:
            pickle.dump(state, f)
        print(f"State saved in {state_filename}")

    def load_state(self, state_filename):
        state_filename = os.path.join(self.temp_dir.name, state_filename)
        if not os.path.exists(state_filename) or os.path.getsize(state_filename) == 0:
            print(f"File {state_filename} not found or empty.")
            return

        with open(state_filename, "rb") as f:
            state = pickle.load(f)

        self.load_enemies_state(state)
        self.load_chests_state(state)
        self.load_npcs_state(state)

    def load_enemies_state(self, state):
        self.enemies = []
        for enemy_info in state["enemies"]:
            class_name, x, y, hp = enemy_info
            enemy_class = globals()[class_name]
            enemy = enemy_class(x, y, hp)
            self.entity_collision_rects.append(enemy.collision_rect)
            self.enemies.append(enemy)

    def load_npcs_state(self, state):
        self.npcs = []
        for npc_info in state["npcs"]:
            class_name, x, y, hp = npc_info
            npc_class = globals()[class_name]
            npc = npc_class(x, y, hp)
            self.entity_collision_rects.append(npc.collision_rect)
            self.npcs.append(npc)

    def load_chests_state(self, state):
        self.chests = []
        for chest_info in state["chests"]:
            x, y, width, height, items = chest_info
            items_string = ",".join(items)
            chest = Chest(x, y, width, height, items_string, self.screen_width)
            self.chests.append(chest)


class Portal:
    def __init__(self, rect, map_file, destination):
        self.rect = rect
        self.map_file = map_file
        self.destination = destination
