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
    ):
        if self.canshoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot >= 1000:
                self.last_shot = current_time
                self.projectile = Spell(
                    target_x,  # target x
                    target_y,  # target y
                    self.PROJECTILE_LIFE,  # speed
                    self.PROJECTILE_SPEED,  # damage
                    self,  # owner
                )
                return True
        return False
