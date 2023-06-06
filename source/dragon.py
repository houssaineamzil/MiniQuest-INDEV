import random
import pygame
import pytmx
import math

from enemy import Enemy
from projectile import Spell


class Dragon(Enemy):
    PROJECTILE_LIFE = 50
    PROJECTILE_SPEED = 15

    def __init__(self, x, y, image_path, size, hp):
        super().__init__(x, y, image_path, size, hp)

    def shoot(
        self,
        target_x,
        target_y,
        projectiles,
        create_particle,
    ):
        if self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot >= 1000:
                self.last_shot = current_time

                # Create a new projectile
                new_projectile = Spell(
                    self.rect.centerx,  # start x
                    self.rect.centery,  # start y
                    target_x,  # target x
                    target_y,  # target y
                    self.PROJECTILE_LIFE,  # life time
                    self.PROJECTILE_SPEED,  # speed
                    self,  # owner
                    create_particle,  # create_particle function
                )

                # Add the new projectile to the list
                projectiles.append(new_projectile)
