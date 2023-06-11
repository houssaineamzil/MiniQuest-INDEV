import pygame


class Chest:
    def __init__(self):
        self.open = False
        self.items = ["hello", "world"]

    def draw(self, screen):
        x, y = 50, 50
        font = pygame.font.Font(None, 24)
        for item in self.items:
            text = font.render(item, True, (255, 255, 255))
            screen.blit(text, (x, y))
            y += text.get_height()
