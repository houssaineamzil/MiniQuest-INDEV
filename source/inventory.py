import pygame


class Inventory:
    def __init__(self):
        self.items = []
        self.inv_width = 200
        self.inv_height = 400
        self.inv_pos_x = 5
        self.inv_pos_y = 5
        self.equip_inv_height = 300
        self.equip_inv_width = 200
        self.equip_inv_pos_y = self.inv_pos_y + self.inv_height + 5
        self.inv_image = pygame.Surface((self.inv_width, self.inv_height))
        self.equip_inv_image = pygame.Surface(
            (self.equip_inv_width, self.equip_inv_height)
        )
        self.font = pygame.font.Font(None, 25)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def move_item(self, item, target_inventory):
        if item in self.items:
            self.remove_item(item)
            target_inventory.add_item(item)

    def draw_inventory(self, screen):
        pygame.draw.rect(
            self.inv_image, (123, 123, 123), (0, 0, self.inv_width, self.inv_height)
        )
        title_surface = self.font.render("Inventory", True, (255, 255, 255))
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

    def draw_equipment(self, screen, player):
        pygame.draw.rect(
            self.equip_inv_image,
            (123, 123, 123),
            (0, 0, self.equip_inv_width, self.equip_inv_height),
        )
        equip_title_surface = self.font.render("Equipment", True, (255, 255, 255))
        self.equip_inv_image.blit(
            equip_title_surface,
            (self.equip_inv_width // 2 - equip_title_surface.get_width() // 2, 10),
        )

        mouse_pos = pygame.mouse.get_pos()

        for i, (slot, item) in enumerate(player.worn_equipment.items()):
            item_text = item.name if item else f"No {slot}"
            text_color = (192, 192, 192) if item is None else (255, 255, 255)
            text_surface = self.font.render(item_text, True, text_color)
            width, height = text_surface.get_size()
            x = self.inv_pos_x + self.equip_inv_width // 2 - width // 2
            y = 35 * (i + 1) + 10 + self.equip_inv_pos_y

            rect = pygame.Rect(x, y, width, height)
            if rect.collidepoint(mouse_pos) and item is not None:
                text_surface = self.font.render(item_text, True, (255, 200, 200))

            self.equip_inv_image.blit(
                text_surface, (x - self.inv_pos_x, y - self.equip_inv_pos_y)
            )

        screen.blit(self.equip_inv_image, (self.inv_pos_x, self.equip_inv_pos_y))

        screen.blit(self.equip_inv_image, (self.inv_pos_x, self.equip_inv_pos_y))

    def get_inventory_rects(self):
        rects = []
        for i, item in enumerate(self.items):
            text_surface = self.font.render(item.name, True, (255, 255, 255))
            width, height = text_surface.get_size()
            x = self.inv_pos_x + self.inv_width // 2 - width // 2
            y = 35 * (i + 1) + 10 + self.inv_pos_y
            rects.append(pygame.Rect(x, y, width, height))
        return rects

    def get_equipment_rects(self, player):
        rects = []
        for i, (slot, item) in enumerate(player.worn_equipment.items()):
            item_text = item.name if item else f"No {slot}"
            text_surface = self.font.render(item_text, True, (255, 255, 255))
            width, height = text_surface.get_size()
            x = self.inv_pos_x + self.equip_inv_width // 2 - width // 2
            y = 35 * (i + 1) + 10 + self.equip_inv_pos_y
            rects.append(pygame.Rect(x, y, width, height))
        return rects

    def handle_equipment_click(self, pos, player):
        for i, rect in enumerate(self.get_equipment_rects()):
            if rect.collidepoint(pos):
                slot = list(player.worn_equipment.keys())[i]
                item = player.worn_equipment[slot]
                if item:
                    player.worn_equipment[slot] = None
                    self.add_item(item)
