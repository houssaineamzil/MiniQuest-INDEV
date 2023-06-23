import random
import math
from character import Character
import pygame


class NPC(Character):
    def __init__(self, hp, spritesheet):
        super().__init__(hp, spritesheet)

    def interact(self, player):
        raise NotImplementedError("Subclasses must implement interact method")

    def ai_move(self, collision_rects, screen_width, screen_height):
        raise NotImplementedError("Subclasses must implement ai_move method")

    def talk():
        raise NotImplementedError("Subclasses must implement talk method")


class Townsfolk(NPC):
    size_x = 32
    size_y = 50

    def __init__(self, x, y, hp):
        spritesheet = "source/img/townsfolk.png"
        super().__init__(hp, spritesheet)
        self.speed = 1.3
        adjustment = 3
        self.rect = pygame.FRect(
            x, y - adjustment, self.size_x, self.size_y - adjustment
        )
        self.collision_rect = pygame.FRect(
            self.rect.x, self.rect.y, self.rect.width * 0.9, self.rect.height * 0.4
        )
        self.collision_rect.midbottom = self.rect.midbottom
        self.respawn_time = 20000
        self.dead = False
        self.dead_counter = 0
        self.wait_counter = 0
        self.direction = 2
        self.next_direction = 2

    def interact(self, player):
        self.talk()

    def ai_move(
        self, collision_rects, entity_collision_rects, screen_width, screen_height
    ):
        self.current_animation.update()
        moved = False

        all_collision_rects = collision_rects + entity_collision_rects
        all_collision_rects = [
            rect for rect in all_collision_rects if rect != self.collision_rect
        ]

        if self.wait_counter > 0:
            self.wait_counter -= 1
            if self.direction == 0:
                self.current_animation = self.standing_animation_north
            elif self.direction == 1:
                self.current_animation = self.standing_animation_east
            elif self.direction == 2:
                self.current_animation = self.standing_animation_south
            elif self.direction == 3:
                self.current_animation = self.standing_animation_west
            return False

        if self.move_counter > 0:
            self.move_counter -= 1
            self.direction = self.next_direction
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
        else:
            self.move_counter = random.randint(20, 70)
            self.next_direction = random.randint(0, 3)
            self.wait_counter = random.randint(50, 500)
        return moved

    def talk(self):
        # Create a list of potential phrases the NPC could say
        phrases = [
            "Hello!",
            "Nice weather we're having.",
            "Good day to you.",
            "I hope you're enjoying your time here.",
        ]
        # Pick a random phrase
        phrase = random.choice(phrases)
        print(phrase)

    def take_damage(self):
        super().take_damage()
        if self.hp <= 0:
            self.dead = True
            self.dead_counter = self.respawn_time

    def update(self, collision_rects, screen_width, screen_height):
        if self.dead:
            self.dead_counter -= 1
            if self.dead_counter <= 0:
                self.dead = False
                self.hp = self.max_hp
                self.rect = self.spawn_point.copy()
        else:
            self.ai_move(collision_rects, screen_width, screen_height)
