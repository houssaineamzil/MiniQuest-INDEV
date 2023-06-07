import random
import pygame
import pytmx
import math

from particle import Particle


class Projectile:
    def __init__(
        self,
        target_x,
        target_y,
        life,
        speed,
        owner=None,
        create_particle=None,
    ):
        self.create_particle = create_particle
        self.owner = owner
        self.image = pygame.image.load(
            "source/img/projectile.png"
        )  # load projectile image
        self.image = pygame.transform.scale(self.image, (20, 20))  # adjust size

        # Calculate the start position from the owner's midbottom position
        start_x, start_y = self.owner.rect.center

        # calculate the angle from the start to the target position
        dx = target_x - start_x
        dy = target_y - start_y
        self.angle = math.atan2(dy, dx)

        # define a radius for the spawn circle of projectile
        spawn_radius = 20  # adjust

        # calculate the offset position on the spawn circle
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

        new_particle = Particle(
            center_x,
            center_y,
            velocity_x,
            velocity_y,
            (255, random.randint(0, 100), 0),
            random.randint(3, 7),
        )
        self.create_particle(new_particle)

        # update the position
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)

        # decrease lifespan
        self.lifespan -= 1

        # remove if it leaves the screen or if lifespan is over
        if (
            self.rect.x < 0
            or self.rect.x > screenWidth
            or self.rect.y < 0
            or self.rect.y > screenHeight
        ) or self.lifespan == 0:
            self.hit_sound.play()
            return True

        # remove if it collides with something
        if self.is_collision(self.rect, tiles):
            self.hit_sound.play()
            return True
        return False

    def is_collision(self, rect, tiles):  # check for collision function
        return rect.collidelist(tiles) != -1


class Spell(Projectile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load("source/img/spell.png")  # load spell image
        self.image = pygame.transform.scale(self.image, (20, 20))  # scale image
        self.shoot_sound = pygame.mixer.Sound("source/sound/fireball.mp3")
        self.hit_sound = pygame.mixer.Sound("source/sound/explosion.mp3")
        self.shoot_sound.set_volume(0.4)
        self.hit_sound.set_volume(0.4)
        self.shoot_sound.play()

    # override or add new methods unique to the spell here


class Arrow(Projectile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load("source/img/arrow.png")  # load arrow image
        self.image = pygame.transform.scale(self.image, (25, 10))  # scale image
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

        new_particle = Particle(
            center_x,
            center_y,
            velocity_x,
            velocity_y,
            (
                random.randint(200, 255),
                random.randint(200, 255),  # white/silver color
                random.randint(200, 255),
            ),
            random.randint(2, 7),
        )

        self.create_particle(new_particle)

        # update the position
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)

        # decrease lifespan
        self.lifespan -= 1

        # remove if it leaves the screen or if lifespan is over
        if (
            self.rect.x < 0
            or self.rect.x > screenWidth
            or self.rect.y < 0
            or self.rect.y > screenHeight
        ) or self.lifespan == 0:
            self.hit_sound.play()
            return True

        # remove if it collides with something
        if self.is_collision(self.rect, tiles):
            self.hit_sound.play()
            return True
        return False
