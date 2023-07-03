import pygame


class Camera:
    def __init__(self, target_pos, width, height, map_width, map_height):
        self.target_pos = target_pos
        self.rect = pygame.FRect(
            target_pos.x - width // 2, target_pos.y - height // 2, width, height
        )

        self.map_width = map_width
        self.map_height = map_height
        self.lerp_speed = 0.15

    def update(self):
        lerp_x = self.lerp(self.rect.centerx, self.target_pos.x, self.lerp_speed)
        lerp_y = self.lerp(self.rect.centery, self.target_pos.y, self.lerp_speed)
        self.rect.centerx = max(
            self.rect.width // 2, min(self.map_width - self.rect.width // 2, lerp_x)
        )
        self.rect.centery = max(
            self.rect.height // 2, min(self.map_height - self.rect.height // 2, lerp_y)
        )

    @staticmethod
    def lerp(v0, v1, t):
        return (1 - t) * v0 + t * v1
