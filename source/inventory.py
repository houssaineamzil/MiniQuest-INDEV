import pygame


class Inventory:
    def __init__(self):
        self.items = []
        self.inv_width = 200
        self.inv_height = 400
        self.inv_image = pygame.Surface((self.inv_width, self.inv_height))
        self.font = pygame.font.Font(None, 35)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def get_item_rects(self):
        rects = []
        for i, item in enumerate(self.items):
            rect = pygame.Rect(10, 50 * i + 10, self.inv_width - 20, 40)
            rects.append(rect)
        return rects

    def draw_inventory(self, screen, inv_pos_x, inv_pos_y):
        pygame.draw.rect(
            self.inv_image, (123, 123, 123), (0, 0, self.inv_width, self.inv_height)
        )

        for i, item in enumerate(self.items):
            text_surface = self.font.render(item.name, True, (255, 255, 255))
            self.inv_image.blit(text_surface, (10, 50 * i + 10))

        screen.blit(self.inv_image, (inv_pos_x, inv_pos_y))
