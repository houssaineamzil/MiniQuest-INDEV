import pygame
from spritesheet import Spritesheet


class HealthBar:
    def __init__(self, player, x, y):
        self.x = x
        self.y = y
        self.player = player
        self.sprite_sheet = Spritesheet("source/img/hearts.png")
        self.heart_full = pygame.transform.scale(
            self.sprite_sheet.get_image(0, 0, 17, 17), (34, 34)
        )
        self.heart_half = pygame.transform.scale(
            self.sprite_sheet.get_image(17, 0, 17, 17), (34, 34)
        )
        self.heart_empty = pygame.transform.scale(
            self.sprite_sheet.get_image(34, 0, 17, 17), (34, 34)
        )

    def draw(self, screen):
        for i in range(self.player.hp // 2):
            screen.blit(self.heart_full, (self.x + i * 40, self.y))
        if self.player.hp % 2:
            screen.blit(self.heart_half, (self.x + (self.player.hp // 2) * 40, self.y))
        for i in range(
            self.player.hp // 2 + self.player.hp % 2, self.player.max_hp // 2
        ):
            screen.blit(self.heart_empty, (self.x + i * 40, self.y))
