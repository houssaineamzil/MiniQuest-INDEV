import random
import pygame
import pytmx
import math

from projectile import FireBall
from character import Character


class Dragon(Character):
    PROJECTILE_LIFE = 30
    PROJECTILE_SPEED = 20

    def __init__(self, x, y, hp):
        super().__init__(hp)
        self.size = 50
        self.speed = 1.2
        self.original_image = pygame.image.load("source/img/dragon.png")
        self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect = pygame.FRect(x, y, self.size, self.size)

    def ai_move(self, collision_tiles, screen_width, screen_height, *args):
        if self.move_counter > 0:
            self.move_counter -= 1
            speed = 2
            if self.direction == 0:
                self.move(0, -speed, collision_tiles, screen_width, screen_height)
            elif self.direction == 1:
                self.move(speed, 0, collision_tiles, screen_width, screen_height)
            elif self.direction == 2:
                self.move(0, speed, collision_tiles, screen_width, screen_height)
            elif self.direction == 3:
                self.move(-speed, 0, collision_tiles, screen_width, screen_height)
        else:
            self.move_counter = 50
            self.direction = random.randint(0, 3)

    def shoot(self, player, collision_tiles):
        if (
            self.canshoot
            and player.targetable
            and self.has_line_of_sight(
                player.rect.centerx, player.rect.centery, collision_tiles
            )
        ):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot >= 1000:
                self.last_shot = current_time
                self.projectile = FireBall(
                    player.rect.centerx,
                    player.rect.centery,
                    self.PROJECTILE_LIFE,
                    self.PROJECTILE_SPEED,
                    self,
                )
                return True
        return False
