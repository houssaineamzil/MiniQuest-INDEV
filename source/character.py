import random
import pygame
import pytmx
import math


class Character:
    def __init__(self, x, y):
        self.size = 20
        self.hp = 1
        self.speed = 1

        self.original_image = pygame.image.load("source/img/skeleton.png")
        self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect = pygame.FRect(x, y, self.size, self.size)
        self.hit = False
        self.hit_counter = 0

    def move(self, dx, dy, collision_tiles, screen_width, screen_height):
        temp_rect = self.rect.copy()
        temp_rect.x += dx * self.speed  # multiply delta x by speed
        temp_rect.y += dy * self.speed  # multiply delta y by speed
        if not self.is_collision(temp_rect, collision_tiles) and self.is_in_screen(
            temp_rect, screen_width, screen_height
        ):
            self.rect.x += dx * self.speed  # multiply delta x by speed
            self.rect.y += dy * self.speed  # multiply delta y by speed

    def is_collision(self, rect, collision_tiles):
        return rect.collidelist(collision_tiles) != -1

    def is_in_screen(self, rect, screen_width, screen_height):
        return (
            0 <= rect.x < screen_width - rect.width
            and 0 <= rect.y < screen_height - rect.height
        )

    def take_damage(self):
        self.hp -= 1
        self.hit = True
        self.hit_counter = 10

    def draw(self, game_screen):
        if self.hit_counter > 0:
            red_image = pygame.Surface(self.image.get_size()).convert_alpha()
            red_image.fill((255, 128, 128))
            self.image.blit(red_image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            self.hit_counter -= 1

        game_screen.blit(self.image, self.rect)

        if self.hit_counter <= 0:
            self.image = pygame.transform.scale(
                self.original_image, (self.rect.width, self.rect.height)
            )
            self.hit = False
