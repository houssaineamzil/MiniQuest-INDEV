import random
import pygame
import pytmx
import math

from spritesheet import Spritesheet
from animation import Animation
from inventory import Inventory


class Player:
    def __init__(self, x, y):
        self.size_x = 32
        self.size_y = 50
        self.spritesheet = Spritesheet("source/img/player.png")

        self.animation_north = Animation(self.spritesheet, 8, 65, 513, 64, 64)
        self.animation_east = Animation(self.spritesheet, 8, 65, 705, 64, 64)
        self.animation_south = Animation(self.spritesheet, 8, 65, 641, 64, 64)
        self.animation_west = Animation(self.spritesheet, 8, 65, 577, 64, 64)

        self.standing_animation_north = Animation(self.spritesheet, 1, 0, 513, 64, 64)
        self.standing_animation_east = Animation(self.spritesheet, 1, 0, 705, 64, 64)
        self.standing_animation_south = Animation(self.spritesheet, 1, 0, 641, 64, 64)
        self.standing_animation_west = Animation(self.spritesheet, 1, 0, 577, 64, 64)

        self.current_animation = self.animation_south
        self.inventory = Inventory()

        self.worn_equipment = {
            "Artefact": None,
            "Head": None,
            "Torso": None,
            "Legs": None,
            "Feet": None,
            "Weapon": None,
        }

        self.inventory_open = False
        self.current_chest = None
        self.chest_open = False
        self.rect = pygame.FRect(x, y, self.size_x, self.size_y)
        self.speed = 3
        self.canmove = True
        self.invisible = False
        self.targetable = True
        self.teleporting = False
        self.dead = False
        self.canshoot = True
        self.collision_rect = pygame.FRect(
            self.rect.x, self.rect.y, self.rect.width * 0.9, self.rect.height * 0.4
        )
        self.collision_rect.midbottom = self.rect.midbottom

    def is_collision(self, rect, tiles):
        return rect.collidelist(tiles) != -1

    def hit_by_projectile(self):
        self.dead = True
        self.targetable = False

    def teleport(self, x, y):
        self.rect.midbottom = (x, y)
        self.collision_rect.midbottom = (x, y)

    def update(self):
        self.current_animation.update()
        for item in self.worn_equipment.values():
            if item is not None:
                item.update(self.current_animation.direction, self.moved)

    def toggle_inventory(self):
        self.inventory_open = not self.inventory_open

    def open_chest(self, chest):
        self.inventory_open = True
        self.current_chest = chest

    def close_chest(self):
        self.inventory_open = False
        self.current_chest = None

    def draw(self, screen):
        if not self.invisible:
            self.current_animation.draw(
                screen, self.rect.x, self.rect.y, self.size_x, self.size_y
            )
            for item in self.worn_equipment.values():
                if item is not None:
                    item.draw(
                        screen,
                        self.rect.x,
                        self.rect.y,
                        self.size_x,
                        self.size_y,
                        self.moved,
                    )

    def equip_item(self, equipment):
        slot = equipment.equipment_slot
        if self.worn_equipment[slot]:
            self.inventory.add_item(self.worn_equipment[slot])
        self.worn_equipment[slot] = equipment
        self.sync_animation(self.worn_equipment[slot])

    def sync_animation(self, equipment):
        for direction, (animation, _) in equipment.directions.items():
            player_animation = self.get_player_animation(direction)
            animation.current_frame = player_animation.current_frame
            animation.last_update = player_animation.last_update

    def unequip_item(self, slot):
        self.worn_equipment[slot] = None

    def get_player_animation(self, direction):
        if direction == "north":
            return self.animation_north
        elif direction == "east":
            return self.animation_east
        elif direction == "south":
            return self.animation_south
        elif direction == "west":
            return self.animation_west
        else:
            return None

    def movement(self, tiles, screen_width, screen_height):
        if not self.dead and self.canmove:
            self.moved = False
            key = pygame.key.get_pressed()
            dx, dy = 0, 0
            if key[pygame.K_w]:
                dy -= 1
                self.current_animation = self.animation_north
                self.current_animation.direction = "north"
            if key[pygame.K_s]:
                dy += 1
                self.current_animation = self.animation_south
                self.current_animation.direction = "south"
            if key[pygame.K_a]:
                dx -= 1
                self.current_animation = self.animation_west
                self.current_animation.direction = "west"
            if key[pygame.K_d]:
                dx += 1
                self.current_animation = self.animation_east
                self.current_animation.direction = "east"
            if dx == 0 and dy == 0:
                if self.current_animation.direction == "north":
                    self.current_animation = self.standing_animation_north
                    self.current_animation.direction = "north"
                elif self.current_animation.direction == "east":
                    self.current_animation = self.standing_animation_east
                    self.current_animation.direction = "east"
                elif self.current_animation.direction == "south":
                    self.current_animation = self.standing_animation_south
                    self.current_animation.direction = "south"
                elif self.current_animation.direction == "west":
                    self.current_animation = self.standing_animation_west
                    self.current_animation.direction = "west"

            if dx != 0 or dy != 0:
                dist = math.hypot(dx, dy)
                dx, dy = dx / dist, dy / dist
                dx *= self.speed
                dy *= self.speed

                if dx != 0:
                    temp_rect = self.collision_rect.copy()
                    temp_rect.x += dx
                    if (
                        temp_rect.right <= screen_width
                        and temp_rect.left >= 0
                        and not self.is_collision(temp_rect, tiles)
                    ):
                        self.rect.x += dx
                        self.collision_rect.x += dx
                        self.moved = True

                if dy != 0:
                    temp_rect = self.collision_rect.copy()
                    temp_rect.y += dy
                    if (
                        temp_rect.bottom <= screen_height
                        and temp_rect.top >= 0
                        and not self.is_collision(temp_rect, tiles)
                    ):
                        self.rect.y += dy
                        self.collision_rect.y += dy
                        self.moved = True
                if not self.moved:
                    if self.current_animation.direction == "north":
                        self.current_animation = self.standing_animation_north
                        self.current_animation.direction = "north"
                    elif self.current_animation.direction == "east":
                        self.current_animation = self.standing_animation_east
                        self.current_animation.direction = "east"
                    elif self.current_animation.direction == "south":
                        self.current_animation = self.standing_animation_south
                        self.current_animation.direction = "south"
                    elif self.current_animation.direction == "west":
                        self.current_animation = self.standing_animation_west
                        self.current_animation.direction = "west"
            return self.moved
