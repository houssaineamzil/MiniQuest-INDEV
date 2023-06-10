import random
import pygame
import pytmx
import math

from spritesheet import Spritesheet
from animation import Animation


class Player:
    def __init__(self, x, y):
        self.size_x = 32
        self.size_y = 50
        self.spritesheet = Spritesheet("source/img/player.png")

        self.animation_north = Animation(self.spritesheet, 3, 0, 0, 32, 50)
        self.animation_east = Animation(self.spritesheet, 3, 0, 50, 32, 50)
        self.animation_south = Animation(self.spritesheet, 3, 0, 100, 32, 50)
        self.animation_west = Animation(self.spritesheet, 3, 0, 150, 32, 50)

        self.standing_animation_north = Animation(self.spritesheet, 1, 0, 0, 32, 50)
        self.standing_animation_east = Animation(self.spritesheet, 1, 0, 50, 32, 50)
        self.standing_animation_south = Animation(self.spritesheet, 1, 0, 100, 32, 50)
        self.standing_animation_west = Animation(self.spritesheet, 1, 0, 150, 32, 50)

        self.current_animation = self.animation_south
        self.armours = []
        self.rect = pygame.FRect(x, y, self.size_x, self.size_y)
        self.speed = 3
        self.dead = False
        self.collision_rect = pygame.FRect(
            self.rect.x, self.rect.y, self.rect.width - 3, self.rect.height * 0.35
        )
        self.collision_rect.midbottom = self.rect.midbottom

    def is_collision(self, rect, tiles):
        return rect.collidelist(tiles) != -1

    def hit_by_projectile(self):
        self.dead = True
        dead_image = pygame.image.load("source/img/player_dead.png")
        dead_image = pygame.transform.scale(dead_image, (self.size_x, self.size_y))
        self.image = dead_image

    def teleport(self, x, y):
        self.rect.midbottom = (x, y)
        self.collision_rect.midbottom = (x, y)

    def update(self):
        self.current_animation.update()
        for armour in self.armours:
            armour.update(self.current_animation.direction, self.moved)
        self.weapon.update(self.current_animation.direction, self.moved)

    def draw(self, screen):
        self.current_animation.draw(screen, self.rect.x, self.rect.y)
        for armour in self.armours:
            armour.draw(screen, self.rect.x, self.rect.y, self.moved)
        self.weapon.draw(screen, self.rect.x, self.rect.y, self.moved)

    def equip_armour(self, armour):
        self.armours.append(armour)

    def equip_weapon(self, weapon):
        self.weapon = weapon

    def movement(self, tiles, screen_width, screen_height):
        if not self.dead:
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
