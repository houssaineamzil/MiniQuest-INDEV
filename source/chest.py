import pygame
from equipment import Equipment

from equipment import (
    Shortbow,
    LeatherPants,
    BlackBoots,
    Chainmail,
    FireStaff,
    TeleportScroll,
    HealingNecklace,
)


class Chest:
    def __init__(self, x, y, width, height, items_string, screen_width):
        self.inv_width = 200
        self.inv_height = 400
        self.inv_pos_x = screen_width - self.inv_width - 5
        self.inv_pos_y = 5
        self.inv_image = pygame.Surface((self.inv_width, self.inv_height))
        self.font = pygame.font.Font(None, 25)
        self.rect = pygame.Rect(x, y, width, height)
        self.items = self.create_items_from_string(items_string)
        self.opened = False

    def open_chest(self):
        self.opened = True
        return self.items

    def close(self):
        self.opened = False

    def move_item(self, item, target_inventory):
        if item in self.items:
            self.remove_item(item)
            target_inventory.add_item(item)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def create_items_from_string(self, item_string):
        item_names = item_string.split(",")
        items = []
        for name in item_names:
            item_class = globals().get(name)
            if item_class is not None and issubclass(item_class, Equipment):
                items.append(item_class())
        return items

    def get_item_rects(self):
        rects = []
        for i, item in enumerate(self.items):
            text_surface = self.font.render(item.name, True, (255, 255, 255))
            width, height = text_surface.get_size()
            x = self.inv_pos_x + self.inv_width // 2 - width // 2
            y = 35 * (i + 1) + 10 + self.inv_pos_y
            rects.append(pygame.Rect(x, y, width, height))
        return rects

    def draw_inventory(self, screen):
        pygame.draw.rect(
            self.inv_image, (123, 123, 123), (0, 0, self.inv_width, self.inv_height)
        )
        title_surface = self.font.render("Chest", True, (255, 255, 255))
        self.inv_image.blit(
            title_surface, (self.inv_width // 2 - title_surface.get_width() // 2, 10)
        )

        mouse_pos = pygame.mouse.get_pos()

        for i, item in enumerate(self.items):
            text_surface = self.font.render(item.name, True, (255, 255, 255))
            width, height = text_surface.get_size()
            x = self.inv_pos_x + self.inv_width // 2 - width // 2
            y = 35 * (i + 1) + 10 + self.inv_pos_y

            rect = pygame.Rect(x, y, width, height)
            if rect.collidepoint(mouse_pos):
                text_surface = self.font.render(item.name, True, (255, 200, 200))

            self.inv_image.blit(text_surface, (x - self.inv_pos_x, y - self.inv_pos_y))

        screen.blit(self.inv_image, (self.inv_pos_x, self.inv_pos_y))
