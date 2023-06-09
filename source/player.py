import random
import pygame
import pytmx
import math


class Player:
    def __init__(self, x, y, tileSize):
        playerIMG = pygame.image.load("source/img/player.png")
        self.image = pygame.transform.scale(playerIMG, (tileSize + 12, tileSize * 2))
        self.rect = pygame.FRect(x, y, tileSize + 12, tileSize * 2)
        self.rect.x = x
        self.rect.y = y
        self.speed = 3
        self.red_image = pygame.Surface(self.image.get_size()).convert_alpha()
        self.red_image.fill((255, 0, 0))
        self.collision_rect = pygame.FRect(
            0, 0, self.rect.width - 3, self.rect.height * 0.25
        )
        self.collision_rect.midbottom = self.rect.midbottom
        self.canshoot = True

    def is_collision(self, rect, tiles):
        return rect.collidelist(tiles) != -1

    def hit_by_projectile(self):
        self.image.blit(self.red_image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        self.speed = 0
        self.canshoot = False
        self.image = pygame.transform.rotate(self.image, -90)

    def teleport(self, x, y):
        self.rect.midbottom = (x, y)
        self.collision_rect.midbottom = (x, y)

    def drawRects(self, gameScreen):
        pygame.draw.rect(gameScreen, (255, 0, 0), self.rect, 2)
        pygame.draw.rect(gameScreen, (0, 255, 0), self.collision_rect, 2)

    def movement(self, tiles, screen_width, screen_height):
        self.moved = False
        key = pygame.key.get_pressed()
        dx, dy = 0, 0
        if key[pygame.K_a]:
            dx -= 1
        if key[pygame.K_d]:
            dx += 1
        if key[pygame.K_w]:
            dy -= 1
        if key[pygame.K_s]:
            dy += 1

        if dx != 0 or dy != 0:
            dist = math.hypot(dx, dy)
            dx, dy = dx / dist, dy / dist
            dx *= self.speed
            dy *= self.speed

        if dx != 0:
            temp_rect = self.collision_rect.copy()
            temp_rect.x += dx
            if (
                temp_rect.right <= screen_width
                and temp_rect.left >= 0
                and not self.is_collision(temp_rect, tiles)
            ):
                self.rect.x += dx
                self.collision_rect.x += dx
                self.moved = True

        if dy != 0:
            temp_rect = self.collision_rect.copy()
            temp_rect.y += dy
            if (
                temp_rect.bottom <= screen_height
                and temp_rect.top >= 0
                and not self.is_collision(temp_rect, tiles)
            ):
                self.rect.y += dy
                self.collision_rect.y += dy
                self.moved = True
        return self.moved
