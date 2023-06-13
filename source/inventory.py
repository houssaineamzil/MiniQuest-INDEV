import pygame


class Inventory:
    def __init__(self):
        self.items = []
        self.inv_width = 200
        self.inv_height = 400
        self.inv_pos_x = 5
        self.inv_pos_y = 5
        self.inv_image = pygame.Surface((self.inv_width, self.inv_height))
        self.font = pygame.font.Font(None, 35)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def move_item(self, item, target_inventory):
        if item in self.items:
            self.remove_item(item)
            target_inventory.add_item(item)

    def get_item_rects(self):
        rects = []
        for i, item in enumerate(self.items):
            rect = pygame.Rect(
                10 + self.inv_pos_x,
                50 * (i + 1) + 10 + self.inv_pos_y,
                self.inv_width - 20,
                40,
            )
            rects.append(rect)
        return rects

    def draw_inventory(self, screen):
        pygame.draw.rect(
            self.inv_image, (123, 123, 123), (0, 0, self.inv_width, self.inv_height)
        )

        title_surface = self.font.render("Inventory", True, (255, 255, 255))
        self.inv_image.blit(
            title_surface, (self.inv_width // 2 - title_surface.get_width() // 2, 10)
        )

        for i, item in enumerate(self.items):
            text_surface = self.font.render(item.name, True, (255, 255, 255))
            self.inv_image.blit(text_surface, (10, 50 * (i + 1) + 10))

        screen.blit(self.inv_image, (self.inv_pos_x, self.inv_pos_y))
