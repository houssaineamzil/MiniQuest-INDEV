import random
import pygame
import math
from projectile import Arrow
from character import Character


class Archer(Character):
    size_x = 32
    size_y = 50
    PROJECTILE_LIFE = 25
    PROJECTILE_SPEED = 15

    def __init__(self, x, y, hp):
        spritesheet = "source/img/archer.png"
        super().__init__(hp, spritesheet)
        self.speed = 1.3
        self.rect = pygame.FRect(x, y, self.size_x, self.size_y)
        self.collision_rect = pygame.FRect(
            self.rect.x, self.rect.y, self.rect.width * 0.9, self.rect.height * 0.4
        )
        self.collision_rect.midbottom = self.rect.midbottom
        self.next_shot_time = self.get_next_shot_time()

    def get_next_shot_time(
        self,
    ):
        return pygame.time.get_ticks() + random.randint(500, 3000)

    def shoot(self, player, collision_tiles):
        current_time = pygame.time.get_ticks()
        if (
            current_time >= self.next_shot_time
            and player.targetable
            and self.canshoot
            and self.has_line_of_sight(
                player.rect.centerx, player.rect.centery, collision_tiles
            )
        ):
            self.projectile = Arrow(
                player.rect.centerx,
                player.rect.centery,
                self.PROJECTILE_LIFE,
                self.PROJECTILE_SPEED,
                self,
            )
            self.next_shot_time = self.get_next_shot_time()
            return True
        return False

    def ai_move(self, collision_tiles, screen_width, screen_height, target_x, target_y):
        self.current_animation.update()
        if self.move_counter > 0:
            self.move_counter -= 1
            speed = 2
            if self.direction == 0:
                moved = self.move(
                    0, -speed, collision_tiles, screen_width, screen_height
                )
            elif self.direction == 1:
                moved = self.move(
                    speed, 0, collision_tiles, screen_width, screen_height
                )
            elif self.direction == 2:
                moved = self.move(
                    0, speed, collision_tiles, screen_width, screen_height
                )
            elif self.direction == 3:
                moved = self.move(
                    -speed, 0, collision_tiles, screen_width, screen_height
                )
            return moved
        else:
            self.move_counter = 50
            self.direction = self.get_direction(target_x, target_y, collision_tiles)
            return False

    def get_direction(self, target_x, target_y, collision_tiles):
        directions = [0, 1, 2, 3]
        distances = []

        for direction in directions:
            next_x, next_y = self.get_next_position(direction)
            dx = target_x - next_x
            dy = target_y - next_y
            distances.append(math.sqrt(dx**2 + dy**2))

        directions = [x for _, x in sorted(zip(distances, directions))]

        for direction in directions:
            next_x, next_y = self.get_next_position(direction)
            next_rect = pygame.Rect(next_x, next_y, self.rect.width, self.rect.height)
            if not any(
                next_rect.colliderect(tile_rect) for tile_rect in collision_tiles
            ):
                return direction

        return random.choice(directions)

    def get_next_position(self, direction_index):
        next_x = self.rect.x
        next_y = self.rect.y
        if direction_index == 0:
            next_y -= self.rect.height
        elif direction_index == 1:
            next_x += self.rect.width
        elif direction_index == 2:
            next_y += self.rect.height
        elif direction_index == 3:
            next_x -= self.rect.width
        return next_x, next_y
