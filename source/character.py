import random
import pygame
import pytmx
import math

from spritesheet import Spritesheet
from animation import Animation


class Character:
    def __init__(self, hp, spritesheet):
        self.hp = hp

        self.hit = False
        self.hit_counter = 0
        self.move_counter = 0
        self.direction = 0
        self.last_shot = 0
        self.canattack = True
        self.invincible = False
        self.tint = (255, 255, 255)

        self.spritesheet = Spritesheet(spritesheet)

        self.animation_north = Animation(self.spritesheet, 8, 65, 513, 64, 64)
        self.animation_east = Animation(self.spritesheet, 8, 65, 705, 64, 64)
        self.animation_south = Animation(self.spritesheet, 8, 65, 641, 64, 64)
        self.animation_west = Animation(self.spritesheet, 8, 65, 577, 64, 64)

        self.standing_animation_north = Animation(self.spritesheet, 1, 0, 513, 64, 64)
        self.standing_animation_east = Animation(self.spritesheet, 1, 0, 705, 64, 64)
        self.standing_animation_south = Animation(self.spritesheet, 1, 0, 641, 64, 64)
        self.standing_animation_west = Animation(self.spritesheet, 1, 0, 577, 64, 64)

        self.current_animation = self.animation_south

    def move(self, dx, dy, collision_rects, screen_width, screen_height):
        temp_rect = self.collision_rect.copy()
        temp_rect.x += dx * self.speed
        temp_rect.y += dy * self.speed

        if not self.is_collision(temp_rect, collision_rects) and self.is_in_screen(
            temp_rect, screen_width, screen_height
        ):
            if dx > 0:
                self.current_animation = self.animation_east
            elif dx < 0:
                self.current_animation = self.animation_west
            elif dy > 0:
                self.current_animation = self.animation_south
            elif dy < 0:
                self.current_animation = self.animation_north

            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

            self.collision_rect.x += dx * self.speed
            self.collision_rect.y += dy * self.speed

            return True
        else:
            if self.current_animation == self.animation_east:
                self.current_animation = self.standing_animation_east
            elif self.current_animation == self.animation_west:
                self.current_animation = self.standing_animation_west
            elif self.current_animation == self.animation_south:
                self.current_animation = self.standing_animation_south
            elif self.current_animation == self.animation_north:
                self.current_animation = self.standing_animation_north
            return False

    def is_collision(self, rect, collision_rects):
        return rect.collidelist(collision_rects) != -1

    def is_in_screen(self, rect, screen_width, screen_height):
        return (
            0 <= rect.x < screen_width - rect.width
            and 0 <= rect.y < screen_height - rect.height
        )

    def take_damage(self):
        self.hp -= 1
        self.invincible = True
        self.hit_counter = 10
        self.tint = (255, 0, 0)

    def draw(self, map_surface):
        self.update_hit_counter()
        self.current_animation.draw(
            map_surface, self.rect.x, self.rect.y, self.size_x, self.size_y, self.tint
        )

    def update_hit_counter(self):
        if self.hit_counter > 0:
            self.hit_counter -= 1
        else:
            self.invincible = False
            self.tint = (255, 255, 255)

    def has_line_of_sight(self, target_x, target_y, collision_rects):
        x0, y0 = self.rect.center
        x1, y1 = target_x, target_y
        dx, dy = x1 - x0, y1 - y0
        distance = math.hypot(dx, dy)
        dx, dy = dx / distance, dy / distance
        arrow_rect = pygame.Rect(0, 0, 10, 10)
        for i in range(int(distance)):
            x, y = x0 + i * dx, y0 + i * dy
            arrow_rect.center = (x, y)
            for rect in collision_rects:
                if rect.colliderect(arrow_rect):
                    return False
        return True
