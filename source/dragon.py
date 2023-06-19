import random
import pygame
import pytmx
import math

from projectile import FireBall
from character import Character
from animation import Animation


class Dragon(Character):
    size_x = 40
    size_y = 40
    PROJECTILE_LIFE = 30
    PROJECTILE_SPEED = 25

    def __init__(self, x, y, hp):
        spritesheet = "source/img/dragon.png"
        super().__init__(hp, spritesheet)
        self.animation_north = Animation(self.spritesheet, 1, 0, 513, 64, 64)
        self.animation_east = Animation(self.spritesheet, 1, 0, 513, 64, 64)
        self.animation_south = Animation(self.spritesheet, 1, 0, 513, 64, 64)
        self.animation_west = Animation(self.spritesheet, 1, 0, 513, 64, 64)

        self.standing_animation_north = Animation(self.spritesheet, 1, 0, 513, 64, 64)
        self.standing_animation_east = Animation(self.spritesheet, 1, 0, 513, 64, 64)
        self.standing_animation_south = Animation(self.spritesheet, 1, 0, 513, 64, 64)
        self.standing_animation_west = Animation(self.spritesheet, 1, 0, 513, 64, 64)

        self.current_animation = self.animation_south
        self.speed = 1.2
        self.rect = pygame.FRect(x, y, self.size_x, self.size_y)
        self.collision_rect = pygame.FRect(
            self.rect.x, self.rect.y, self.rect.width * 0.9, self.rect.height * 0.4
        )
        self.collision_rect.midbottom = self.rect.midbottom

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
