import pygame
import os
from map import Map
from player import Player
from enemy import Enemy
from projectile import Arrow, FireBall
from particle import walkParticle
from equipment import (
    Equipment,
    Armour,
    Weapon,
    Shortbow,
    LeatherPants,
    BlackBoots,
    Chainmail,
    TeleportScroll,
)
from spritesheet import Spritesheet
import random
from healthBar import HealthBar


class Game:
    def __init__(self, screen_width, screen_height, map_file, game_screen):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_file = map_file
        self.game_screen = game_screen
        self.last_shot = 0
        self.game_over = False
        self.PLAYER_TELEPORT_ARTEFACT = pygame.USEREVENT + 1

    def run(self, player_x, player_y):
        self.init_game_loop(player_x, player_y)
        while self.game_running():
            if not self.player.dead:
                self.perform_game_operations()
                self.handle_game_events()
                self.update_ui()
                self.update_game_screen()
            if self.player.dead:
                self.delete_save_files()
                self.handle_dead_player()

    def init_game_loop(self, player_x, player_y):
        self.clock_object = pygame.time.Clock()

        self.player = Player(player_x, player_y)
        self.player.equip_item(LeatherPants())
        self.health_bar = HealthBar(self.player, 5, 5)

        self.map = Map(self.map_file, self.screen_width, self.screen_height)
        self.map.object_setup()

        pygame.mixer.music.load("source/sound/music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0)

        self.cursor_img = pygame.image.load("source/img/cursor.png")

    def game_running(self):
        return not self.game_over

    def perform_game_operations(self):
        self.clock_object.tick(60)

        self.map.draw_layer(self.game_screen, "floor")
        self.map.draw_layer(self.game_screen, "ground")

        self.map.update(self.game_screen, self.player)

        entities_to_sort = self.map.enemies + [self.player]
        sorted_entities = sorted(entities_to_sort, key=lambda entity: entity.rect.y)
        for entity in sorted_entities:
            if isinstance(entity, Player):
                if entity.movement(
                    self.map.collision_tiles, self.screen_width, self.screen_height
                ):
                    if random.random() < 0.3:
                        walk_particle = walkParticle(entity)
                        self.map.add_ground_particle(walk_particle)
                entity.update()
                entity.draw(self.game_screen)
            elif isinstance(entity, Enemy):
                self.map.update_enemy(self.player, entity)
                entity.draw(self.game_screen)

            # self.map.draw_rects(
            # self.game_screen, entity
            # )  # PLAYER AND ENEMY COLLISION DEBUG

        self.map.update_particles(self.game_screen, self.map.particles)
        self.map.draw_layer(self.game_screen, "above_ground")

        # for rect in self.map.collision_tiles:  # COLLISION RECT DEBUG
        # self.map.draw_rect(self.game_screen, rect)

    def update_ui(self):
        if self.player.inventory_open:
            self.player.inventory.draw_inventory(self.game_screen)
            self.player.inventory.draw_equipment(self.game_screen, self.player)
        else:
            self.health_bar.draw(self.game_screen)

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
                self.delete_save_files()
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_button_down_event(event)
            if event.type == self.PLAYER_TELEPORT_ARTEFACT:
                self.handle_teleport_artefact()

    def handle_teleport_artefact(self):
        if self.player.teleporting:
            self.player.canattack = True
            self.player.canmove = True
            self.player.teleporting = False
            self.player.targetable = True
            self.player.worn_equipment["Artefact"].add_smoke_effect(
                self.player.rect, self.map
            )

    def delete_save_files(self):
        for file in os.listdir("source/tile"):
            if file.endswith(".pkl"):
                os.remove(os.path.join("source/tile", file))

    def handle_mouse_button_down_event(self, event):
        if event.button not in [1, 3]:
            pass
        else:
            if not self.player.dead:
                if event.button == 1:
                    self.handle_player_attack(event)
                elif event.button == 3:
                    self.handle_artefact_activation(event)

            self.handle_inventory_click(event)
            self.handle_equipment_click(event)
            self.handle_chest_click(event)

    def handle_artefact_activation(self, event):
        if (
            self.player.worn_equipment["Artefact"] is not None
            and self.player.inventory_open == False
            and self.player.current_chest == None
        ):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.player.worn_equipment["Artefact"].activate_effect(
                self.player, mouse_x, mouse_y, self.map.collision_tiles, self.map
            )

    def handle_player_attack(self, event):
        current_time = pygame.time.get_ticks()
        if (
            self.player.worn_equipment["Weapon"] is not None
            and current_time - self.last_shot
            >= self.player.worn_equipment["Weapon"].cooldown
            and self.player.inventory_open == False
            and self.player.current_chest == None
            and self.player.canattack
        ):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.map.add_projectile(
                self.player.worn_equipment["Weapon"].attack(
                    self.player, mouse_x, mouse_y
                )
            )
            self.last_shot = current_time

    def handle_inventory_click(self, event):
        if not self.player.inventory_open:
            return

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
                    if self.player.worn_equipment[item.equipment_slot] is None:
                        self.player.equip_item(item)
                        self.player.inventory.remove_item(item)

    def handle_equipment_click(self, event):
        if not self.player.inventory_open:
            return

        click_pos = event.pos

        for i, item_rect in enumerate(
            self.player.inventory.get_equipment_rects(self.player)
        ):
            if item_rect.collidepoint(click_pos):
                slot, item = list(self.player.worn_equipment.items())[i]
                if item:
                    self.player.unequip_item(slot)
                    self.player.inventory.add_item(item)

    def handle_chest_click(self, event):
        click_pos = event.pos

        if self.player.current_chest:
            for i, item_rect in enumerate(self.player.current_chest.get_item_rects()):
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
        self.update_mouse()
        pygame.display.flip()

    def update_mouse(self):
        mx, my = pygame.mouse.get_pos()
        self.game_screen.blit(self.cursor_img, (mx, my))

    def handle_dead_player(self):
        self.game_over = True
