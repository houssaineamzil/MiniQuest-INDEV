import random
import pygame
import pytmx
import math

from enemy import Enemy
from projectile import Spell


class Dragon(Enemy):
    PROJECTILE_LIFE = 30
    PROJECTILE_SPEED = 20

    def __init__(self, x, y):
        super().__init__(x, y)

        self.size = 50
        self.hp = 1
        self.speed = 1

        self.original_image = pygame.image.load("source/img/dragon.png")
        self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect = pygame.FRect(x, y, self.size, self.size)
        self.hit = False
        self.hit_counter = 0

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
