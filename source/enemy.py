import random
import pygame
import pytmx
import math

from character import Character
from projectile import Projectile


class Enemy(Character):
    PROJECTILE_LIFE = 20
    PROJECTILE_SPEED = 20

    def __init__(self, x, y, hp):
        super().__init__(x, y, hp)
        self.move_counter = 0
        self.direction = 0
        self.last_shot = 0
        self.canshoot = True

    def ai_move(self, collision_tiles, screen_width, screen_height, *args):
        if self.move_counter > 0:
            self.move_counter -= 1
            speed = 2
            if self.direction == 0:
                self.move(0, -speed, collision_tiles, screen_width, screen_height)
            elif self.direction == 1:
                self.move(speed, 0, collision_tiles, screen_width, screen_height)
            elif self.direction == 2:
                self.move(0, speed, collision_tiles, screen_width, screen_height)
            elif self.direction == 3:
                self.move(-speed, 0, collision_tiles, screen_width, screen_height)
        else:
            self.move_counter = 60
            self.direction = random.randint(0, 3)

    def shoot(
        self,
        target_x,
        target_y,
    ):
        if self.canshoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot >= 1000:
                self.last_shot = current_time
                self.projectile = Projectile(
                    target_x,
                    target_y,
                    self.PROJECTILE_LIFE,
                    self.PROJECTILE_SPEED,
                    self,
                )
                return True
        return False
