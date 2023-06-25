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

    def update(self, *args):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        self.lifetime += 2
        alpha = max(255 - self.lifetime * 5, 0)
        self.image.set_alpha(alpha)

        if alpha <= 0:
            return True
        return False


class walkParticle(Particle):
    def __init__(self, entity):
        x, y = entity.collision_rect.midbottom

        velocity_x = random.uniform(-0.3, 0.3)
        velocity_y = random.uniform(-0.3, -0.3)
        color = (
            random.randint(100, 165),
            random.randint(50, 115),
            random.randint(10, 45),
        )
        super().__init__(x, y, velocity_x, velocity_y, color, random.randint(2, 4))


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

        intensity = random.randint(50, 200)
        color = (intensity, intensity, intensity)

        size = random.randint(2, 5)

        super().__init__(start_x, start_y, velocity_x, velocity_y, color, size)

    def update(self, *args):
        self.velocity_y -= 0.02

        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        self.lifetime += 0.5
        alpha = max(255 - self.lifetime * 10, 0)
        self.image.set_alpha(alpha)

        if alpha <= 0:
            return True
        return False


class HealingParticle(Particle):
    def __init__(self, player_rect):
        self.color = (
            random.randint(150, 200),
            random.randint(0, 25),
            random.randint(0, 25),
        )
        self.speed = random.randint(2, 4)
        self.relative_target_pos = pygame.Vector2(
            random.randint(0, player_rect.width), random.randint(0, player_rect.height)
        )
        self.target_pos = pygame.Vector2(player_rect.topleft) + self.relative_target_pos

        self.radius = random.randint(20, 60)
        self.angle = random.uniform(0, 2 * math.pi)
        self.position = self.target_pos + pygame.Vector2(
            self.radius * math.cos(self.angle), self.radius * math.sin(self.angle)
        )
        self.size = random.randint(3, 5)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.color)
        self.rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)

        self.swirl_angle = random.uniform(0, 2 * math.pi)
        self.swirl_speed = random.choice([-0.1, 0.1])

    def update(self, player_rect):
        self.target_pos = pygame.Vector2(player_rect.topleft) + self.relative_target_pos

        direction_vector = self.target_pos - self.position
        if direction_vector.length() != 0:
            direction_vector = direction_vector.normalize() * 2

        self.swirl_angle += self.swirl_speed
        swirl_vector = pygame.Vector2(
            math.cos(self.swirl_angle), math.sin(self.swirl_angle)
        )
        swirl_vector = pygame.Vector2(-swirl_vector.y, swirl_vector.x)

        direction_vector += swirl_vector
        direction_vector = direction_vector.normalize()

        self.position += direction_vector * self.speed
        self.rect.topleft = self.position

        distance = self.target_pos.distance_to(self.position)
        if distance <= self.speed:
            self.size = 0
            return True
        else:
            self.speed += 0.05

        return False
