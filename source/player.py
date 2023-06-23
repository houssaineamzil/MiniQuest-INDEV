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
        self.hp = 6
        self.max_hp = 6
        self.hit_counter = 0
        self.tint = (255, 255, 255)
        self.spritesheet = Spritesheet("source/img/player.png")

        self.walk_animation_north = Animation(self.spritesheet, 8, 65, 513, 64, 64)
        self.walk_animation_east = Animation(self.spritesheet, 8, 65, 705, 64, 64)
        self.walk_animation_south = Animation(self.spritesheet, 8, 65, 641, 64, 64)
        self.walk_animation_west = Animation(self.spritesheet, 8, 65, 577, 64, 64)

        self.stand_animation_north = Animation(self.spritesheet, 1, 0, 513, 64, 64)
        self.stand_animation_east = Animation(self.spritesheet, 1, 0, 705, 64, 64)
        self.stand_animation_south = Animation(self.spritesheet, 1, 0, 641, 64, 64)
        self.stand_animation_west = Animation(self.spritesheet, 1, 0, 577, 64, 64)

        self.current_animation = self.stand_animation_south
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
        self.speed = 2
        self.canmove = True
        self.targetable = True
        self.teleporting = False
        self.dead = False
        self.canattack = True
        self.invincible = False
        adjustment = 3
        self.rect = pygame.FRect(
            x, y - adjustment, self.size_x, self.size_y - adjustment
        )
        self.collision_rect = pygame.FRect(
            self.rect.x, self.rect.y, self.rect.width * 0.9, self.rect.height * 0.4
        )
        self.collision_rect.midbottom = self.rect.midbottom

    def is_collision(self, rect, tiles):
        return rect.collidelist(tiles) != -1

    def hit_by_projectile(self):
        self.take_damage()
        self.check_dead()

    def take_damage(self):
        self.hit_counter = 10
        self.invincible = True
        self.tint = (255, 0, 0)
        self.hp -= 1

    def check_dead(self):
        if self.hp == 0:
            self.dead = True
            self.targetable = False

    def teleport(self, x, y):
        self.rect.midbottom = (x, y)
        self.collision_rect.midbottom = (x, y)

    def update_hit_counter(self):
        if self.hit_counter > 0:
            self.hit_counter -= 1
        else:
            self.tint = (255, 255, 255)
            self.invincible = False

    def update(self):
        self.update_hit_counter()
        for item in self.worn_equipment.values():
            if item is not None:
                item.update(self.current_animation.direction, self.moved)
        self.current_animation.update()

    def toggle_inventory(self):
        self.inventory_open = not self.inventory_open

    def open_chest(self, chest):
        self.inventory_open = True
        self.current_chest = chest

    def close_chest(self):
        self.inventory_open = False
        self.current_chest = None

    def draw(self, screen):
        if not self.teleporting:
            self.current_animation.draw(
                screen, self.rect.x, self.rect.y, self.size_x, self.size_y, self.tint
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
                        self.tint,
                    )

    def equip_item(self, equipment):
        slot = equipment.equipment_slot
        if self.worn_equipment[slot]:
            if self.worn_equipment[slot].has_buff:
                self.worn_equipment[slot].remove_buff(self)
            self.inventory.add_item(self.worn_equipment[slot])
        self.worn_equipment[slot] = equipment
        self.sync_animation(self.worn_equipment[slot])
        if equipment.has_buff:
            equipment.apply_buff(self)

    def unequip_item(self, slot):
        if self.worn_equipment[slot] and self.worn_equipment[slot].has_buff:
            self.worn_equipment[slot].remove_buff(self)
        self.worn_equipment[slot] = None

    def sync_animation(self, equipment):
        for direction, (animation, _) in equipment.directions.items():
            player_animation = self.get_walk_animation(direction)
            animation.current_frame = player_animation.current_frame
            animation.last_update = player_animation.last_update

    def get_walk_animation(self, direction):
        if direction == "north":
            return self.walk_animation_north
        elif direction == "east":
            return self.walk_animation_east
        elif direction == "south":
            return self.walk_animation_south
        elif direction == "west":
            return self.walk_animation_west

    def set_walk_animation(self, direction):
        if direction == "north":
            self.current_animation = self.walk_animation_north
            self.current_animation.direction = "north"
        elif direction == "south":
            self.current_animation = self.walk_animation_south
            self.current_animation.direction = "south"
        elif direction == "west":
            self.current_animation = self.walk_animation_west
            self.current_animation.direction = "west"
        elif direction == "east":
            self.current_animation = self.walk_animation_east
            self.current_animation.direction = "east"

    def set_stand_animation(self):
        if self.current_animation.direction == "north":
            self.current_animation = self.stand_animation_north
            self.current_animation.direction = "north"
        elif self.current_animation.direction == "east":
            self.current_animation = self.stand_animation_east
            self.current_animation.direction = "east"
        elif self.current_animation.direction == "south":
            self.current_animation = self.stand_animation_south
            self.current_animation.direction = "south"
        elif self.current_animation.direction == "west":
            self.current_animation = self.stand_animation_west
            self.current_animation.direction = "west"

    def movement(self, tiles, screen_width, screen_height):
        if not self.dead and self.canmove:
            self.moved = False
            key = pygame.key.get_pressed()
            dx, dy = 0, 0
            if key[pygame.K_w]:
                dy -= 1
                self.set_walk_animation("north")
            if key[pygame.K_s]:
                dy += 1
                self.set_walk_animation("south")
            if key[pygame.K_a]:
                dx -= 1
                self.set_walk_animation("west")
            if key[pygame.K_d]:
                dx += 1
                self.set_walk_animation("east")
            if dx == 0 and dy == 0:
                self.set_stand_animation()

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
                    self.set_stand_animation()
            return self.moved
