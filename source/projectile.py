import random
import pygame
import pytmx
import math

from particle import Particle
from explosion import Explosion, SpellExplosion, ArrowExplosion


class Projectile:
    explosion = Explosion

    def __init__(
        self,
        target_x,
        target_y,
        life,
        speed,
        owner=None,
    ):
        self.owner = owner
        self.image = pygame.image.load("source/img/projectile.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.shoot_sound = pygame.mixer.Sound("source/sound/fireball.mp3")
        self.hit_sound = pygame.mixer.Sound("source/sound/explosion.mp3")

        start_x, start_y = self.owner.rect.center
        start_y = start_y + 10

        dx = target_x - start_x
        dy = target_y - start_y
        self.angle = math.atan2(dy, dx)

        spawn_radius = 10

        spawn_x = start_x + spawn_radius * math.cos(self.angle)
        spawn_y = start_y + spawn_radius * math.sin(self.angle)

        self.rect = pygame.FRect(
            spawn_x, spawn_y, self.image.get_width(), self.image.get_height()
        )
        self.rect.x = spawn_x - self.image.get_width() // 2
        self.rect.y = spawn_y - self.image.get_height() // 2
        self.speed = speed
        self.lifespan = life

        self.collided = False

    # update method
    def update(self, tiles, screenWidth, screenHeight):
        center_x = self.rect.x + self.image.get_width() // 2
        center_y = self.rect.y + self.image.get_height() // 2

        velocity_x = random.uniform(-1, 1)
        velocity_y = random.uniform(-1, 1)

        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)

        self.lifespan -= 1

        if (
            (
                self.rect.x < 0
                or self.rect.x > screenWidth
                or self.rect.y < 0
                or self.rect.y > screenHeight
            )
            or self.lifespan == 0
            or self.is_collision(self.rect, tiles)
        ):
            self.hit_sound.play()
            return True

        self.particle = Particle(
            center_x,
            center_y,
            velocity_x,
            velocity_y,
            (255, random.randint(0, 100), 0),
            random.randint(3, 7),
        )
        return False

    def is_collision(self, rect, tiles):
        return rect.collidelist(tiles) != -1


class Spell(Projectile):
    explosion = SpellExplosion

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load("source/img/spell.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.shoot_sound = pygame.mixer.Sound("source/sound/fireball.mp3")
        self.hit_sound = pygame.mixer.Sound("source/sound/explosion.mp3")
        self.shoot_sound.set_volume(0.4)
        self.hit_sound.set_volume(0.4)
        self.shoot_sound.play()


class Arrow(Projectile):
    explosion = ArrowExplosion

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load("source/img/arrow.png")
        self.image = pygame.transform.scale(self.image, (25, 10))
        self.image = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        self.shoot_sound = pygame.mixer.Sound("source/sound/arrowrelease.mp3")
        self.hit_sound = pygame.mixer.Sound("source/sound/arrowimpact.mp3")
        self.shoot_sound.set_volume(4)
        self.hit_sound.set_volume(0.4)
        self.shoot_sound.play()

    def update(self, tiles, screenWidth, screenHeight):
        center_x = self.rect.x + self.image.get_width() // 2
        center_y = self.rect.y + self.image.get_height() // 2

        velocity_x = random.uniform(-0.5, 0.5)
        velocity_y = random.uniform(-0.5, 0.5)

        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)

        self.lifespan -= 1

        if (
            self.rect.x < 0
            or self.rect.x > screenWidth
            or self.rect.y < 0
            or self.rect.y > screenHeight
        ) or self.lifespan == 0:
            self.hit_sound.play()
            return True

        if self.is_collision(self.rect, tiles):
            self.hit_sound.play()
            return True

        self.particle = Particle(
            center_x,
            center_y,
            velocity_x,
            velocity_y,
            (
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255),
            ),
            random.randint(2, 7),
        )
        return False
