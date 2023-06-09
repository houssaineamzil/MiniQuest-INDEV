import random
import pygame
import math
from enemy import Enemy
from projectile import Arrow


class Archer(Enemy):
    PROJECTILE_LIFE = 20  # Lifetime of the arrow projectile
    PROJECTILE_SPEED = 20  # Speed of the arrow projectile

    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = 30
        self.hp = 1
        self.speed = 1.2
        self.original_image = pygame.image.load("source/img/archer.png")
        self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect = pygame.FRect(x, y, self.size, self.size)
        self.next_shot_time = (
            self.get_next_shot_time()  # Time when the next shot can be fired
        )

    def get_next_shot_time(
        self,
    ):  # Get the next shot time by adding a random number between 500 to 1000 to the current time
        return pygame.time.get_ticks() + random.randint(1000, 4000)

    def shoot(self, target_x, target_y):
        # Shoot a projectile if the current time is larger than the next shot time
        current_time = pygame.time.get_ticks()
        if current_time >= self.next_shot_time and self.canshoot:
            # Create a new projectile and append it to the projectiles list
            self.projectile = Arrow(
                target_x,
                target_y,
                self.PROJECTILE_LIFE,
                self.PROJECTILE_SPEED,
                self,
            )
            self.next_shot_time = self.get_next_shot_time()
            return True
        return False

    def ai_move(self, collision_tiles, screen_width, screen_height, target_x, target_y):
        # AI movement logic for the archer
        if self.move_counter > 0:
            # If move counter is greater than 0, decrement it and move in the current direction
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
            # If move counter is 0, choose a new direction towards the target
            self.move_counter = 60
            self.direction = self.get_direction(target_x, target_y, collision_tiles)

    def get_direction(self, target_x, target_y, collision_tiles):
        # Get the direction of the target based on Euclidean distance and checking if the path is blocked
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
        # Get the next position in the provided direction
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
