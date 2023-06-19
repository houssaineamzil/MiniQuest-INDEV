import random
import pygame
import pytmx
import math

from particle import Particle


class particleEffect:
    def update(self):
        for particle in list(self.particles):
            if particle.update():
                self.particles.remove(particle)

        return len(self.particles) == 0


class ArrowExplosion(particleEffect):
    def __init__(self, x, y):
        self.particles = [
            Particle(
                x,
                y,
                (random.uniform(-3, 3)),
                (random.uniform(-3, 3)),
                (
                    random.randint(100, 150),
                    random.randint(100, 150),
                    random.randint(100, 150),
                ),
                random.randint(2, 4),
            )
            for _ in range(20)
        ]


class FireBallExplosion(particleEffect):
    def __init__(self, x, y):
        self.particles = [
            Particle(
                x,
                y,
                (random.uniform(-5, 5)),
                (random.uniform(-5, 5)),
                (
                    random.randint(200, 255),
                    random.randint(50, 100),
                    0,
                ),
                random.randint(3, 6),
            )
            for _ in range(20)
        ]
