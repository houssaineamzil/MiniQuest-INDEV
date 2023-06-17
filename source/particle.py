import random
import pygame
import pytmx
import math


class Particle:
    def __init__(self, start_x, start_y, velocity_x, velocity_y, color, size):
        self.image = pygame.Surface((size, size))
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
        alpha = max(255 - self.lifetime * 5, 0)
        self.image.set_alpha(alpha)

        if alpha <= 0:
            return True
        return False


class FireBallParticle(Particle):
    def __init__(self, start_x, start_y, velocity_x, velocity_y):
        color = (255, random.randint(0, 100), 0)
        size = random.randint(3, 7)
        super().__init__(start_x, start_y, velocity_x, velocity_y, color, size)


class ArrowParticle(Particle):
    def __init__(self, start_x, start_y, velocity_x, velocity_y):
        color = (
            random.randint(200, 255),
            random.randint(200, 255),
            random.randint(200, 255),
        )
        size = random.randint(2, 7)
        super().__init__(start_x, start_y, velocity_x, velocity_y, color, size)


class TeleportParticle(Particle):
    def __init__(self, start_x, start_y):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0, 1)
        velocity_x = speed * math.cos(angle)
        velocity_y = speed * math.sin(angle)

        color = (
            random.randint(50, 100),
            random.randint(50, 100),
            random.randint(50, 100),
        )
        size = random.randint(2, 5)

        super().__init__(start_x, start_y, velocity_x, velocity_y, color, size)

    def update(self):
        self.velocity_y -= 0.03

        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        self.lifetime += 0.5
        alpha = max(255 - self.lifetime * 10, 0)
        self.image.set_alpha(alpha)

        if alpha <= 0:
            return True
        return False
