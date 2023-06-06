import random
import pygame
import math
from enemy import Enemy
from projectile import Arrow


class Archer(Enemy):
    PROJECTILE_LIFE = 20
    PROJECTILE_SPEED = 20

    def __init__(self, x, y, image_path, size, hp):
        super().__init__(x, y, image_path, size, hp)
        self.next_shot_time = self.get_next_shot_time()
        self.speed = 1.5

    def get_next_shot_time(self):
        # Generate a random interval between 1 and 3 seconds (1000 to 3000 milliseconds)
        return pygame.time.get_ticks() + random.randint(1000, 2000)

    def shoot(self, target_x, target_y, projectiles, create_particle):
        current_time = pygame.time.get_ticks()
        if current_time >= self.next_shot_time:
            new_projectile = Arrow(
                self.rect.centerx,
                self.rect.centery,
                target_x,
                target_y,
                self.PROJECTILE_LIFE,
                self.PROJECTILE_SPEED,
                self,
                create_particle,
            )
            projectiles.append(new_projectile)
            self.next_shot_time = self.get_next_shot_time()

    def ai_move(self, collision_tiles, screen_width, screen_height, target_x, target_y):
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
            self.move_counter = 60
            self.direction = self.get_direction(target_x, target_y, collision_tiles)

    def get_direction(self, target_x, target_y, collision_tiles):
        directions = [0, 1, 2, 3]  # Possible directions
        distances = []  # Distances to the target for each direction

        # Calculate distances for all directions
        for direction in directions:
            next_x, next_y = self.get_next_position(direction)
            dx = target_x - next_x
            dy = target_y - next_y
            distances.append(math.sqrt(dx**2 + dy**2))

        # Sort directions based on the distance
        directions = [x for _, x in sorted(zip(distances, directions))]

        # Select the closest non-obstructed direction
        for direction in directions:
            next_x, next_y = self.get_next_position(direction)
            next_rect = pygame.Rect(next_x, next_y, self.rect.width, self.rect.height)
            if not any(
                next_rect.colliderect(tile_rect) for tile_rect in collision_tiles
            ):
                return direction

        return random.choice(
            directions
        )  # If all directions are obstructed, choose randomly

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