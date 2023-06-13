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

        start_x, start_y = self.owner.rect.center

        dx = target_x - start_x
        dy = target_y - start_y
        self.angle = math.atan2(dy, dx)

        spawn_radius = 10

        spawn_x = start_x + spawn_radius * math.cos(self.angle)
        spawn_y = start_y + spawn_radius * math.sin(self.angle)

        self.orig_rect = pygame.FRect(
            spawn_x, spawn_y, self.orig_image.get_width(), self.orig_image.get_height()
        )
        self.orig_rect.x = spawn_x - self.orig_image.get_width() // 2
        self.orig_rect.y = spawn_y - self.orig_image.get_height() // 2
        self.speed = speed
        self.lifespan = life

        self.collided = False

    def update(self, tiles, screenWidth, screenHeight):
        center_x = self.rect.x + self.orig_image.get_width() // 2
        center_y = self.rect.y + self.orig_image.get_height() // 2

        velocity_x = random.uniform(-1, 1)
        velocity_y = random.uniform(-1, 1)

        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)

        self.collision_rect.x += self.speed * math.cos(self.angle)
        self.collision_rect.y += self.speed * math.sin(self.angle)

        self.lifespan -= 1

        if (
            (
                self.orig_rect.x < 0
                or self.orig_rect.x > screenWidth
                or self.orig_rect.y < 0
                or self.orig_rect.y > screenHeight
            )
            or self.lifespan == 0
            or self.is_collision(self.collision_rect, tiles)
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
        self.orig_image = pygame.image.load("source/img/spell.png")
        self.orig_image = pygame.transform.scale(self.orig_image, (20, 20))
        super().__init__(*args, **kwargs)

        self.image = self.orig_image
        self.collision_rect = self.image.get_rect(center=self.orig_rect.center)
        self.rect = self.image.get_rect(center=self.orig_rect.center)

        self.shoot_sound = pygame.mixer.Sound("source/sound/fireball.mp3")
        self.hit_sound = pygame.mixer.Sound("source/sound/explosion.mp3")
        self.shoot_sound.set_volume(0.4)
        self.hit_sound.set_volume(0.4)
        self.shoot_sound.play()


class Arrow(Projectile):
    explosion = ArrowExplosion

    def __init__(self, *args, **kwargs):
        self.orig_image = pygame.image.load("source/img/arrow.png")
        self.orig_image = pygame.transform.scale(self.orig_image, (30, 30))
        super().__init__(*args, **kwargs)

        self.collision_radius = 10
        self.collision_rect = pygame.FRect(
            0, 0, self.collision_radius, self.collision_radius
        )

        self.collision_rect.centerx = (
            self.orig_rect.centerx + self.collision_radius * math.cos(self.angle)
        )
        self.collision_rect.centery = (
            self.orig_rect.centery + self.collision_radius * math.sin(self.angle)
        )

        self.image = pygame.transform.rotate(self.orig_image, -math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.orig_rect.center)

        self.shoot_sound = pygame.mixer.Sound("source/sound/arrowrelease.mp3")
        self.hit_sound = pygame.mixer.Sound("source/sound/arrowimpact.mp3")
        self.shoot_sound.set_volume(4)
        self.hit_sound.set_volume(0.4)
        self.shoot_sound.play()

    def update(self, tiles, screenWidth, screenHeight):
        center_x = self.orig_rect.x + self.orig_image.get_width() // 2
        center_y = self.orig_rect.y + self.orig_image.get_height() // 2

        velocity_x = random.uniform(-0.5, 0.5)
        velocity_y = random.uniform(-0.5, 0.5)

        self.orig_rect.x += self.speed * math.cos(self.angle)
        self.orig_rect.y += self.speed * math.sin(self.angle)

        self.rect = self.image.get_rect(center=self.orig_rect.center)

        self.collision_rect.centerx = (
            self.orig_rect.centerx + self.collision_radius * math.cos(self.angle)
        )
        self.collision_rect.centery = (
            self.orig_rect.centery + self.collision_radius * math.sin(self.angle)
        )

        self.lifespan -= 1

        if (
            self.orig_rect.x < 0
            or self.orig_rect.x > screenWidth
            or self.orig_rect.y < 0
            or self.orig_rect.y > screenHeight
        ) or self.lifespan == 0:
            self.hit_sound.play()
            return True

        if self.is_collision(self.collision_rect, tiles):
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
