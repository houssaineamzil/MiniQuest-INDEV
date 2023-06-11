from animation import Animation
from projectile import Arrow, Spell


class Equipment:
    def __init__(self, spritesheet):
        self.animation_north = Animation(spritesheet, 8, 65, 513, 64, 64)
        self.animation_east = Animation(spritesheet, 8, 65, 705, 64, 64)
        self.animation_south = Animation(spritesheet, 8, 65, 641, 64, 64)
        self.animation_west = Animation(spritesheet, 8, 65, 577, 64, 64)

        self.standing_animation_north = Animation(spritesheet, 1, 0, 513, 64, 64)
        self.standing_animation_east = Animation(spritesheet, 1, 0, 705, 64, 64)
        self.standing_animation_south = Animation(spritesheet, 1, 0, 641, 64, 64)
        self.standing_animation_west = Animation(spritesheet, 1, 0, 577, 64, 64)

        self.directions = {
            "north": (self.animation_north, self.standing_animation_north),
            "south": (self.animation_south, self.standing_animation_south),
            "west": (self.animation_west, self.standing_animation_west),
            "east": (self.animation_east, self.standing_animation_east),
        }

        self.current_direction = "south"

    def update(self, direction, is_moving):
        self.current_direction = direction
        for dir, (animation, standing_animation) in self.directions.items():
            if dir == self.current_direction:
                if is_moving:
                    animation.update()
                else:
                    standing_animation.update()

    def draw(self, screen, x, y, size_x, size_y, is_moving):
        if is_moving:
            self.directions[self.current_direction][0].draw(
                screen, x, y, size_x, size_y
            )
        else:
            self.directions[self.current_direction][1].draw(
                screen, x, y, size_x, size_y
            )


class Weapon(Equipment):
    def __init__(self, spritesheet, projectile_type, life, speed):
        super().__init__(spritesheet)
        self.life = life
        self.speed = speed
        self.projectile_type = projectile_type

    def shoot(self, player, mouse_x, mouse_y):
        projectile = self.projectile_type(
            mouse_x, mouse_y, self.life, self.speed, player
        )
        return projectile


class Armour(Equipment):
    def __init__(self, spritesheet, hp_buff):
        super().__init__(spritesheet)
        self.hp_buff = hp_buff

    def apply_buff(self, character):
        pass  # replace with actual implementation
