import pygame


class Camera:
    def __init__(self, player_rect_centre, width, height, map_width, map_height):
        self.target_pos = player_rect_centre
        self.rect = pygame.FRect(
            self.target_pos[0] - width // 2,
            self.target_pos[1] - height // 2,
            width,
            height,
        )

        self.map_width = map_width
        self.map_height = map_height
        self.lerp_speed = 0.15

    def update(self):
        lerp_x = self.lerp(self.rect.centerx, self.target_pos[0], self.lerp_speed)
        lerp_y = self.lerp(self.rect.centery, self.target_pos[1], self.lerp_speed)
        self.rect.centerx = max(
            self.rect.width // 2, min(self.map_width - self.rect.width // 2, lerp_x)
        )
        self.rect.centery = max(
            self.rect.height // 2, min(self.map_height - self.rect.height // 2, lerp_y)
        )

    def teleport_to_player(self, player_rect_centre):
        self.target_pos = player_rect_centre
        self.rect.center = self.target_pos

    def change_map(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height

    @staticmethod
    def lerp(v0, v1, t):
        return (1 - t) * v0 + t * v1
