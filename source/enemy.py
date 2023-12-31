import random
import pygame
import pytmx
import math
from character import Character

from projectile import FireBall, Arrow
from animation import Animation


class Enemy(Character):
    def __init__(self, hp, spritesheet):
        super().__init__(hp, spritesheet)

    def attack(self, player):
        raise NotImplementedError("Subclasses must implement attack method")

    def ai_move(self, collision_rects, screen_width, screen_height, *args):
        raise NotImplementedError("Subclasses must implement ai_move method")


class Dragon(Enemy):
    size_x = 50
    size_y = 50
    PROJECTILE_LIFE = 30
    PROJECTILE_SPEED = 25
    DAMAGE = 3

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

    def ai_move(
        self,
        collision_rects,
        entity_collision_rects,
        screen_width,
        screen_height,
        *args
    ):
        if self.move_counter > 0:
            self.move_counter -= 1
            speed = 2
            if self.direction == 0:
                self.move(0, -speed, collision_rects, screen_width, screen_height)
            elif self.direction == 1:
                self.move(speed, 0, collision_rects, screen_width, screen_height)
            elif self.direction == 2:
                self.move(0, speed, collision_rects, screen_width, screen_height)
            elif self.direction == 3:
                self.move(-speed, 0, collision_rects, screen_width, screen_height)
        else:
            self.move_counter = 50
            self.direction = random.randint(0, 3)

    def attack(self, player, collision_rects):
        if (
            self.canattack
            and player.targetable
            and self.has_line_of_sight(
                player.rect.centerx, player.rect.centery, collision_rects
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
                    self.DAMAGE,
                    self,
                )
                return True
        return False


class Archer(Enemy):
    size_x = 32
    size_y = 50
    PROJECTILE_LIFE = 25
    PROJECTILE_SPEED = 15
    DAMAGE = 2

    def __init__(self, x, y, hp):
        spritesheet = "source/img/archer.png"
        super().__init__(hp, spritesheet)
        self.speed = 1.5
        adjustment = 3
        self.rect = pygame.FRect(
            x, y - adjustment, self.size_x, self.size_y - adjustment
        )
        self.collision_rect = pygame.FRect(
            self.rect.x, self.rect.y, self.rect.width * 0.9, self.rect.height * 0.4
        )
        self.collision_rect.midbottom = self.rect.midbottom
        self.next_shot_time = self.get_next_shot_time()

    def get_next_shot_time(
        self,
    ):
        return pygame.time.get_ticks() + random.randint(500, 3000)

    def attack(self, player, collision_rects):
        current_time = pygame.time.get_ticks()
        if (
            current_time >= self.next_shot_time
            and player.targetable
            and self.canattack
            and self.has_line_of_sight(
                player.rect.centerx, player.rect.centery, collision_rects
            )
        ):
            self.projectile = Arrow(
                player.rect.centerx,
                player.rect.centery,
                self.PROJECTILE_LIFE,
                self.PROJECTILE_SPEED,
                self.DAMAGE,
                self,
            )
            self.next_shot_time = self.get_next_shot_time()
            return True
        return False

    def ai_move(
        self,
        collision_rects,
        entity_collision_rects,
        screen_width,
        screen_height,
        target_x,
        target_y,
    ):
        all_collision_rects = collision_rects + entity_collision_rects
        all_collision_rects = [
            rect for rect in all_collision_rects if rect != self.collision_rect
        ]
        self.current_animation.update()
        if self.move_counter > 0:
            self.move_counter -= 1
            if self.direction == 0:
                moved = self.move(
                    0, -self.speed, all_collision_rects, screen_width, screen_height
                )
            elif self.direction == 1:
                moved = self.move(
                    self.speed, 0, all_collision_rects, screen_width, screen_height
                )
            elif self.direction == 2:
                moved = self.move(
                    0, self.speed, all_collision_rects, screen_width, screen_height
                )
            elif self.direction == 3:
                moved = self.move(
                    -self.speed, 0, all_collision_rects, screen_width, screen_height
                )
            return moved
        else:
            self.move_counter = random.randint(25, 150)
            self.direction = self.get_direction(target_x, target_y, all_collision_rects)
            return False

    def get_direction(self, target_x, target_y, collision_rects):
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
                next_rect.colliderect(tile_rect) for tile_rect in collision_rects
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
