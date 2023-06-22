import pygame
import random
from animation import Animation
from projectile import Arrow, FireBall
from spritesheet import Spritesheet
from particle import TeleportParticle


class Equipment:
    def __init__(self, spritesheet):
        self.walk_animation_north = Animation(spritesheet, 8, 65, 513, 64, 64)
        self.walk_animation_east = Animation(spritesheet, 8, 65, 705, 64, 64)
        self.walk_animation_south = Animation(spritesheet, 8, 65, 641, 64, 64)
        self.walk_animation_west = Animation(spritesheet, 8, 65, 577, 64, 64)

        self.stand_animation_north = Animation(spritesheet, 1, 0, 513, 64, 64)
        self.stand_animation_east = Animation(spritesheet, 1, 0, 705, 64, 64)
        self.stand_animation_south = Animation(spritesheet, 1, 0, 641, 64, 64)
        self.stand_animation_west = Animation(spritesheet, 1, 0, 577, 64, 64)

        self.directions = {
            "north": (self.walk_animation_north, self.stand_animation_north),
            "south": (self.walk_animation_south, self.stand_animation_south),
            "west": (self.walk_animation_west, self.stand_animation_west),
            "east": (self.walk_animation_east, self.stand_animation_east),
        }

        self.current_direction = "south"
        self.name = "Undefined"

    def update(self, direction, is_moving):
        self.current_direction = direction
        for dir, (animation, standing_animation) in self.directions.items():
            if dir == self.current_direction:
                if is_moving:
                    animation.update()
                else:
                    standing_animation.update()

    def draw(self, screen, x, y, size_x, size_y, moved, tint):
        if moved:
            self.directions[self.current_direction][0].draw(
                screen, x, y, size_x, size_y, tint
            )
        else:
            self.directions[self.current_direction][1].draw(
                screen, x, y, size_x, size_y, tint
            )


class Weapon(Equipment):
    def __init__(self, spritesheet, projectile_type, life, speed, cooldown):
        super().__init__(spritesheet)
        self.name = "Undefined Weapon"
        self.life = life
        self.speed = speed
        self.projectile_type = projectile_type
        self.cooldown = cooldown

    def attack(self, player, mouse_x, mouse_y):
        projectile = self.projectile_type(
            mouse_x, mouse_y, self.life, self.speed, player
        )
        return projectile


class Armour(Equipment):
    def __init__(self, spritesheet, hp_buff):
        super().__init__(spritesheet)
        self.name = "Undefined Armour"
        self.hp_buff = hp_buff

    def apply_buff(self, character):
        pass  # replace with actual implementation


class Artefact(Equipment):
    def __init__(self, spritesheet):
        super().__init__(spritesheet)
        self.name = "Undefined Artefact"

    def activate_effect(self, player, mouse_x, mouse_y, tiles):
        pass  # replace with actual implementation


class Shortbow(Weapon):
    def __init__(self):
        super().__init__(Spritesheet("source/img/shortbow.png"), Arrow, 18, 15, 1400)
        self.class_name = self.__class__.__name__
        self.name = "Shortbow"
        self.equipment_slot = "Weapon"


class FireStaff(Weapon):
    def __init__(self):
        super().__init__(Spritesheet("source/img/firestaff.png"), FireBall, 22, 10, 800)
        self.class_name = self.__class__.__name__
        self.name = "Fire Staff"
        self.equipment_slot = "Weapon"


class LeatherPants(Armour):
    def __init__(self):
        super().__init__(Spritesheet("source/img/leatherpants.png"), 1)
        self.class_name = self.__class__.__name__
        self.name = "Leather Pants"
        self.equipment_slot = "Legs"


class BlackBoots(Armour):
    def __init__(self):
        super().__init__(Spritesheet("source/img/blackboots.png"), 1)
        self.class_name = self.__class__.__name__
        self.name = "Black Boots"
        self.equipment_slot = "Feet"


class Chainmail(Armour):
    def __init__(self):
        super().__init__(Spritesheet("source/img/chainmail.png"), 1)
        self.class_name = self.__class__.__name__
        self.name = "Chainmail"
        self.equipment_slot = "Torso"


class TeleportScroll(Artefact):
    COOLDOWN = 1500
    TELEPORT_DELAY = 200

    def __init__(self):
        super().__init__(Spritesheet("source/img/chainmail.png"))
        self.class_name = self.__class__.__name__
        self.name = "Teleport Scroll"
        self.equipment_slot = "Artefact"
        self.teleport_radius = 300
        self.last_activation = 0

    def activate_effect(self, player, mouse_x, mouse_y, tiles, map):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_activation < self.COOLDOWN:
            return False

        if not self.is_in_radius(player.rect.center, (mouse_x, mouse_y)):
            return False

        potential_rect = pygame.Rect(
            0, 0, player.collision_rect.width, player.collision_rect.height
        )
        potential_rect.midbottom = (mouse_x, mouse_y)

        if potential_rect.top < 0:
            return False

        if self.is_collision(potential_rect, tiles):
            return False

        self.add_smoke_effect(player.rect, map)

        player.teleport(mouse_x, mouse_y)

        player.targetable = False
        player.teleporting = True
        player.canmove = False
        player.canattack = False
        self.last_activation = current_time

        pygame.time.set_timer(pygame.USEREVENT + 1, self.TELEPORT_DELAY)
        return True

    def add_smoke_effect(self, rect, map):
        for _ in range(50):
            x = random.uniform(rect.left, rect.right)
            y = random.uniform(rect.top, rect.bottom)
            map.add_particle(TeleportParticle(int(x), int(y)))

    def is_in_radius(self, center, point):
        dx = center[0] - point[0]
        dy = center[1] - point[1]
        distance = (dx**2 + dy**2) ** 0.5
        return distance <= self.teleport_radius

    def is_collision(self, rect, tiles):
        return rect.collidelist(tiles) != -1
