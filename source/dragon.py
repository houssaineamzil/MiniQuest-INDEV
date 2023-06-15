import random
import pygame
import pytmx
import math

from enemy import Enemy
from projectile import Spell


class Dragon(Enemy):
    PROJECTILE_LIFE = 30
    PROJECTILE_SPEED = 20

    def __init__(self, x, y, hp):
        super().__init__(x, y, hp)
        self.size = 50
        self.hp = hp
        self.speed = 1
        self.original_image = pygame.image.load("source/img/dragon.png")
        self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect = pygame.FRect(x, y, self.size, self.size)
        self.hit = False
        self.hit_counter = 0
