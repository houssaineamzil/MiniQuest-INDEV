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
        self.speed = 4
        self.red_image = pygame.Surface(self.image.get_size()).convert_alpha()
        self.red_image.fill((255, 0, 0))
        self.collision_rect = pygame.FRect(  # collision smaller than the sprite
            0, 0, self.rect.width - 3, self.rect.height * 0.25
        )
        self.collision_rect.midbottom = (
            self.rect.midbottom
        )  # place it at the bottom center
        self.canshoot = True

    def is_collision(self, rect, tiles):  # check for collision function
        return rect.collidelist(tiles) != -1

    def hit_by_projectile(self):
        self.image.blit(self.red_image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    def drawRects(self, gameScreen):
        pygame.draw.rect(
            gameScreen, (255, 0, 0), self.rect, 2
        )  # draws player rectangle in red
        pygame.draw.rect(
            gameScreen, (0, 255, 0), self.collision_rect, 2
        )  # draws collision rectangle in green

    def movement(self, tiles, walk_particles, screen_width, screen_height):
        key = pygame.key.get_pressed()
        dx, dy = 0, 0  # Changes in x and y
        # Change 'elif' to 'if' for all directions
        if key[pygame.K_a]:
            dx -= 1
        if key[pygame.K_d]:
            dx += 1
        if key[pygame.K_w]:
            dy -= 1
        if key[pygame.K_s]:
            dy += 1

        # Normalize direction vector for consistent speed
        if dx != 0 or dy != 0:
            dist = math.hypot(dx, dy)
            dx, dy = dx / dist, dy / dist  # Normalize the speed
            dx *= self.speed
            dy *= self.speed
            if self.speed != 0:
                walk_particles(self)

        # Check for collisions before updating the player's position
        if dx != 0:  # If there is a change in x
            temp_rect = self.collision_rect.copy()
            temp_rect.x += dx
            # Check for screen bounds
            if (
                temp_rect.right <= screen_width
                and temp_rect.left >= 0
                and not self.is_collision(temp_rect, tiles)
            ):
                self.rect.x += dx
                self.collision_rect.x += dx  # Update collision box position

        if dy != 0:  # If there is a change in y
            temp_rect = self.collision_rect.copy()
            temp_rect.y += dy
            # Check for screen bounds
            if (
                temp_rect.bottom <= screen_height
                and temp_rect.top >= 0
                and not self.is_collision(temp_rect, tiles)
            ):
                self.rect.y += dy
                self.collision_rect.y += dy  # Update collision box position
