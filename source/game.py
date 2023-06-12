# game.py
import pygame
import os
from map import Map
from player import Player
from projectile import Arrow, Spell
from equipment import (
    Equipment,
    Armour,
    Weapon,
    Shortbow,
    LeatherPants,
    BlackBoots,
    Chainmail,
)
from spritesheet import Spritesheet
from chest import Chest


class Game:
    def __init__(self, screen_width, screen_height, player_x, player_y, map_file):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_file = map_file
        self.last_shot = 0
        self.game_over = False
        self.fade_in_time = 2000
        self.fade_in_start = None

        pygame.init()
        pygame.mixer.init()

        self.game_screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption("MiniQuest")
        self.clock_object = pygame.time.Clock()

        self.player = Player(player_x, player_y)

        self.chainmail = Chainmail(Spritesheet("source/img/chainmail.png"), 1)
        self.leatherpants = LeatherPants(Spritesheet("source/img/leatherpants.png"), 1)
        self.blackboots = BlackBoots(Spritesheet("source/img/blackboots.png"), 1)
        self.shortbow = Shortbow(Spritesheet("source/img/shortbow.png"), Arrow, 15, 20)

        self.player.equip_armour(self.leatherpants)
        self.player.equip_armour(self.blackboots)

        self.player.inventory.add_item(self.shortbow)
        self.player.inventory.add_item(self.chainmail)

        self.map = Map(self.map_file, self.screen_width, self.screen_height)
        self.map.collisionSetup()

        pygame.mixer.music.load("source/sound/music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)

    def run(self):
        run = True
        while run == True:
            if self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        for file in os.listdir("source/tile"):
                            if file.endswith(".pkl"):
                                os.remove(os.path.join("source/tile", file))
                            run = False
                continue

            self.clock_object.tick(60)

            self.map.drawFloorLayer(self.game_screen)
            self.map.drawGroundLayer(self.game_screen)

            self.map.update(self.game_screen, self.player)
            # self.map.drawRects(self.game_screen, self.player)  # debug player collision

            if self.player.movement(
                self.map.collision_tiles, self.screen_width, self.screen_height
            ):
                self.map.walk_particles(self.player)

            self.player.update()
            self.player.draw(self.game_screen)
            self.map.drawAboveGroundLayer(self.game_screen)

            if self.player.inventory_open:
                self.player.inventory.draw_inventory(self.game_screen, 5, 5)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    for file in os.listdir("source/tile"):
                        if file.endswith(".pkl"):
                            os.remove(os.path.join("source/tile", file))
                        run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.player.dead:
                        current_time = pygame.time.get_ticks()
                        if current_time - self.last_shot >= 1000 and self.player.weapon:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            self.map.add_projectile(
                                self.player.weapon.shoot(self.player, mouse_x, mouse_y)
                            )
                            self.last_shot = current_time
                        if self.player.inventory_open == True:
                            click_pos = event.pos
                            inv_pos_x, inv_pos_y = (0, 0)
                            for i, item_rect in enumerate(
                                self.player.inventory.get_item_rects()
                            ):
                                item_rect.move_ip(inv_pos_x, inv_pos_y)
                                if item_rect.collidepoint(click_pos):
                                    item = self.player.inventory.items[i]
                                    if isinstance(item, Weapon):
                                        self.player.equip_weapon(item)
                                        self.player.inventory.remove_item(item)
                                    elif isinstance(item, Armour):
                                        self.player.equip_armour(item)
                                        self.player.inventory.remove_item(item)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i:
                        self.player.inventory_open = not self.player.inventory_open

            if self.player.dead:
                game_over_font = pygame.font.Font(None, 50)
                game_over_text = game_over_font.render("You Died.", True, (150, 0, 0))
                text_surface = pygame.Surface(
                    game_over_text.get_size(), pygame.SRCALPHA
                )
                text_rect = text_surface.get_rect(
                    center=(self.screen_width / 2, self.screen_height / 2)
                )

                self.game_screen.fill((0, 0, 0))

                text_surface.blit(game_over_text, (0, 0))

                self.game_screen.blit(text_surface, text_rect)

                self.game_over = True

            pygame.display.flip()
