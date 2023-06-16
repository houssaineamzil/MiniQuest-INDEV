import pygame
import os
from map import Map
from player import Player
from projectile import Arrow, FireBall
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


class Game:
    def __init__(self, screen_width, screen_height, map_file):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_file = map_file
        self.last_shot = 0
        self.game_over = False

    def run(self, player_x, player_y):
        self.init_game_loop(player_x, player_y)
        while self.game_running():
            self.perform_game_operations()
            self.handle_game_events()
            self.update_game_screen()
            self.update_ui()

    def init_game_loop(self, player_x, player_y):
        pygame.init()
        pygame.mixer.init()

        self.game_screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption("MiniQuest")
        self.clock_object = pygame.time.Clock()

        self.player = Player(player_x, player_y)
        self.player.equip_item(LeatherPants())

        self.map = Map(self.map_file, self.screen_width, self.screen_height)
        self.map.object_setup()

        pygame.mixer.music.load("source/sound/music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)

        pygame.mouse.set_visible(False)
        self.cursor_img = pygame.image.load("source/img/cursor.png")

    def game_running(self):
        return not self.game_over

    def perform_game_operations(self):
        self.clock_object.tick(60)

        self.map.draw_floor_layer(self.game_screen)
        self.map.draw_ground_layer(self.game_screen)

        self.map.update(self.game_screen, self.player)

        if self.player.movement(
            self.map.collision_tiles, self.screen_width, self.screen_height
        ):
            self.map.walk_particles(self.player)

        self.player.update()
        self.player.draw(self.game_screen)
        # self.map.draw_rects(self.game_screen, self.player)  # PLAYER COLLISION DEBUG

        self.map.draw_above_ground_layer(self.game_screen)

    def update_ui(self):
        if self.player.inventory_open:
            self.player.inventory.draw_inventory(self.game_screen)
            self.player.inventory.draw_equipment(self.game_screen, self.player)

        for chest in self.map.chests:
            if (
                self.player.current_chest == chest
                and self.player.collision_rect.colliderect(chest.rect)
            ):
                chest.draw_inventory(self.game_screen)
            else:
                if self.player.current_chest == chest:
                    self.player.current_chest = None

    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.handle_quit_event()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_button_down_event(event)
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown_event(event)

    def handle_quit_event(self):
        for file in os.listdir("source/tile"):
            if file.endswith(".pkl"):
                os.remove(os.path.join("source/tile", file))
        self.game_over = True

    def handle_mouse_button_down_event(self, event):
        if event.button == 1 and not self.player.dead:
            current_time = pygame.time.get_ticks()
            if (
                current_time - self.last_shot >= 1000
                and self.player.worn_equipment["Weapon"] is not None
                and self.player.inventory_open == False
                and self.player.current_chest == None
            ):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.map.add_projectile(
                    self.player.worn_equipment["Weapon"].shoot(
                        self.player, mouse_x, mouse_y
                    )
                )
                self.last_shot = current_time
            click_pos = event.pos
            inv_pos_x, inv_pos_y = (0, 0)

            for i, item_rect in enumerate(self.player.inventory.get_inventory_rects()):
                item_rect.move_ip(inv_pos_x, inv_pos_y)
                if item_rect.collidepoint(click_pos):
                    item = self.player.inventory.items[i]
                    if self.player.current_chest:
                        self.player.inventory.remove_item(item)
                        self.player.current_chest.add_item(item)
                    else:
                        if isinstance(item, (Weapon, Armour)):
                            if self.player.worn_equipment[item.equipment_slot] is None:
                                self.player.equip_item(item)
                                self.player.inventory.remove_item(item)

            for i, item_rect in enumerate(
                self.player.inventory.get_equipment_rects(self.player)
            ):
                if item_rect.collidepoint(click_pos):
                    slot, item = list(self.player.worn_equipment.items())[i]
                    if item:
                        self.player.unequip_item(slot)
                        self.player.inventory.add_item(item)

            if self.player.current_chest:
                for i, item_rect in enumerate(
                    self.player.current_chest.get_item_rects()
                ):
                    if item_rect.collidepoint(click_pos):
                        item = self.player.current_chest.items[i]
                        self.player.current_chest.remove_item(item)
                        self.player.inventory.add_item(item)

    def handle_keydown_event(self, event):
        if event.key == pygame.K_TAB:
            self.player.toggle_inventory()
        elif event.key == pygame.K_e:
            self.handle_keydown_e()

    def handle_keydown_e(self):
        for chest in self.map.chests:
            if self.player.collision_rect.colliderect(chest.rect):
                if self.player.current_chest is None:
                    self.player.open_chest(chest)
                else:
                    self.player.close_chest()

    def update_game_screen(self):
        mx, my = pygame.mouse.get_pos()
        self.game_screen.blit(self.cursor_img, (mx, my))
        self.handle_dead_player()
        pygame.display.flip()

    def handle_dead_player(self):
        if self.player.dead:
            game_over_font = pygame.font.Font(None, 50)
            game_over_text = game_over_font.render("You Died.", True, (150, 0, 0))
            text_surface = pygame.Surface(game_over_text.get_size(), pygame.SRCALPHA)
            text_rect = text_surface.get_rect(
                center=(self.screen_width / 2, self.screen_height / 2)
            )

            self.game_screen.fill((0, 0, 0))

            text_surface.blit(game_over_text, (0, 0))

            self.game_screen.blit(text_surface, text_rect)

            self.game_over = True

            self.handle_quit_event()
