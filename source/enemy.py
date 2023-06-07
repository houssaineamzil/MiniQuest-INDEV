import random
import pygame
import pytmx
import math

from character import Character
from projectile import Projectile


class Enemy(Character):
    def __init__(self, x, y, image_path, size, hp):
        super().__init__(x, y, image_path, size, hp)
        self.move_counter = 0
        self.direction = 0
        self.last_shot = 0
        self.canshoot = True

    def ai_move(self, collision_tiles, screen_width, screen_height):
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
        projectiles,
        create_particle,
        projectile_life,
        projectile_speed,
    ):
        if self.canshoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot >= 1000:
                self.last_shot = current_time

                # Create a new projectile
                new_projectile = Projectile(
                    self.rect.centerx,  # start x
                    self.rect.centery,  # start y
                    target_x,  # target x
                    target_y,  # target y
                    projectile_life,  # speed
                    projectile_speed,  # damage
                    self,  # owner
                    create_particle,  # create_particle function
                )

                # Add the new projectile to the list
                projectiles.append(new_projectile)
