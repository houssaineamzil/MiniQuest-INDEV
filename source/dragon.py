import random
import pygame
import pytmx
import math

from enemy import Enemy
from projectile import Spell


class Dragon(Enemy):
    PROJECTILE_LIFE = 30
    PROJECTILE_SPEED = 20

    def __init__(self, x, y, image_path, size, hp):
        super().__init__(x, y, image_path, size, hp)

    def shoot(
        self,
        target_x,
        target_y,
        create_particle,
        projectile_life,
        projectile_speed,
    ):
        if self.canshoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot >= 1000:
                self.last_shot = current_time
                self.projectile = Spell(
                    self.rect.centerx,  # start x
                    self.rect.centery,  # start y
                    target_x,  # target x
                    target_y,  # target y
                    projectile_life,  # speed
                    projectile_speed,  # damage
                    self,  # owner
                    create_particle,  # create_particle function
                )
                return True
        return False
