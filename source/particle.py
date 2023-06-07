import random
import pygame
import pytmx
import math


class Particle:
    def __init__(self, start_x, start_y, velocity_x, velocity_y, color, size):
        self.image = pygame.Surface((size, size))  # adjust to your desired size
        self.image.fill(color)
        self.rect = pygame.FRect(start_x, start_y, size, size)
        self.rect.center = (start_x, start_y)
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = 0

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        self.lifetime += 2
        alpha = max(255 - self.lifetime * 5, 0)  # decrease by 5 each frame
        self.image.set_alpha(alpha)

        if alpha <= 0:
            return True
        return False
