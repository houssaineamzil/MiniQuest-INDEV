import random
import pygame
import pytmx
import math

from enemy import Enemy


class Dragon(Enemy):
    PROJECTILE_LIFE = 50
    PROJECTILE_SPEED = 15

    def __init__(self, x, y, image_path, size, hp):
        super().__init__(x, y, image_path, size, hp)

    def shoot(self, target_x, target_y, projectiles, create_particle):
        super().shoot(
            target_x,
            target_y,
            projectiles,
            create_particle,
            self.PROJECTILE_LIFE,
            self.PROJECTILE_SPEED,
        )
