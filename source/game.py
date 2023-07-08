import pygame
from sys import exit
from pygame.math import Vector2
import os
from resourcePath import resource_path
import sys
from map import Map
from player import Player
from enemy import Enemy
from npc import NPC
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
    HealingNecklace,
)
from spritesheet import Spritesheet
import random
from healthBar import HealthBar
from camera import Camera
import tempfile


class Game:
    def __init__(
        self,
        screen_width,
        screen_height,
        map_file,
        game_screen,
        screen_resolution,
        scale_factor_x_y,
        scale_factor,
    ):
        self.temp_dir = tempfile.TemporaryDirectory()
        print(self.temp_dir)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_file = map_file
        self.game_screen = game_screen
        self.last_shot = 0
        self.game_over = False
        self.screen_resolution = screen_resolution
        self.scale_factor_x_y = scale_factor_x_y
        self.scale_factor = scale_factor
        print(self.scale_factor_x_y, self.scale_factor)
        self.PLAYER_TELEPORT_ARTEFACT = pygame.USEREVENT + 1

    def run(self, player_x, player_y):
        self.init_game_loop(player_x, player_y)
        while self.game_running():
            if not self.player.dead:
                self.camera.target_pos = Vector2(*self.player.rect.center)
                self.camera.update()
                self.map.update_music()

                self.perform_game_operations()
                self.handle_game_events()
                self.draw_map()
                self.update_ui()
                self.update_game_screen()
            if self.player.dead:
                self.delete_save_files()
                self.handle_dead_player()

    def init_game_loop(self, player_x, player_y):
        self.clock_object = pygame.time.Clock()

        self.player = Player(player_x, player_y, "Adam")
        self.player.equip_item(LeatherPants())
        self.health_bar = HealthBar(self.player, 5, 5)

        self.map = Map(self.map_file, self.screen_width, self.temp_dir)
        self.map.entity_collision_rects.append(self.player.collision_rect)
        self.camera = Camera(
            Vector2(*self.player.rect.center),
            *self.screen_resolution,
            self.map.width,
            self.map.height,
        )

        self.cursor_img = pygame.image.load(resource_path("source/img/cursor.png"))

    def game_running(self):
        return not self.game_over

    def perform_game_operations(self):
        self.clock_object.tick(60)

        self.map.draw_layer("floor")
        self.map.draw_layer("ground")

        self.map.update(self.player, self.camera)
        self.update_dynamic_objects()

        self.map.update_particles(self.map.particles, self.player)
        self.map.draw_layer("above_ground")

        # for rect in self.map.collision_rects:  # COLLISION RECT DEBUG
        #    self.map.draw_rect(self.map.surface, rect)

    def update_dynamic_objects(self):
        entities_to_sort = self.map.enemies + self.map.npcs + [self.player]
        sorted_entities = sorted(entities_to_sort, key=lambda entity: entity.rect.y)
        for entity in sorted_entities:
            if isinstance(entity, Player):
                if not self.player.in_quest_ui:
                    if entity.movement(
                        self.map.collision_rects,
                        self.map.entity_collision_rects,
                        self.map.width,
                        self.map.height,
                    ):
                        if random.random() < 0.3:
                            walk_particle = walkParticle(entity)
                            self.map.add_ground_particle(walk_particle)
                entity.update()
                entity.draw(self.map.surface)
            elif isinstance(entity, Enemy):
                self.map.update_enemy(self.player, entity)
                entity.draw(self.map.surface)
            elif isinstance(entity, NPC):
                self.map.update_npc(self.player, entity)
                entity.draw(self.map.surface)

            # self.map.draw_rects(
            #    self.map.surface, entity
            # )  # DYNAMIC OBJECT COLLISION DEBUG (PLAYER, NPCS)

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

        for npc in self.map.npcs:
            if npc.current_quest_offer_ui is not None:
                npc.current_quest_offer_ui.draw(self.game_screen)
                self.player.in_quest_ui = True

                if npc.speech_box and npc.speech_box.active:
                    if not self.player.rect.colliderect(npc.rect):
                        npc.speech_box.stop()
                        self.player.in_dialogue = False
                    else:
                        npc.speech_box.draw(self.game_screen)
                        if npc.speech_box and npc.speech_box.active:
                            npc.speech_box.stop()
                            self.player.in_dialogue = False
            else:
                self.player.in_quest_ui = False

            if npc.speech_box and npc.speech_box.active:
                if not self.player.rect.colliderect(npc.rect):
                    npc.speech_box.stop()
                    self.player.in_dialogue = False
                else:
                    npc.speech_box.draw(self.game_screen)

    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.delete_save_files()
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_button_down_event(event)
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion_event()
            if event.type == self.PLAYER_TELEPORT_ARTEFACT:
                self.handle_teleport_artefact()

    def handle_mouse_motion_event(self):
        mouse_position = pygame.mouse.get_pos()
        for npc in self.map.npcs:
            if npc.speech_box and npc.speech_box.active:
                npc.speech_box.handle_mouse_movement(mouse_position)

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
        for file in os.listdir(self.temp_dir.name):
            if file.endswith(".pkl"):
                os.remove(os.path.join(self.temp_dir.name, file))

    def handle_mouse_button_down_event(self, event):
        if self.player.in_quest_ui:
            for npc in self.map.npcs:
                if npc.current_quest_offer_ui is not None:
                    action = npc.current_quest_offer_ui.check_button_press(event)
                    if action == "reject":
                        npc.current_quest_offer_ui = None
                        self.player.in_quest_ui = False

                    if action == "accept":
                        self.player.in_quest_ui = False
                        self.player.quest_log.add_quest(
                            npc.current_quest_offer_ui.get_quest()
                        )
                        npc.current_quest_offer_ui = None
                        npc.speech_box = None

            return
        if event.button not in [1, 3]:
            pass
        else:
            if not self.player.dead:
                if event.button == 1:
                    self.handle_player_attack(event)
                elif event.button == 3:
                    self.handle_artefact_activation(event)
            for npc in self.map.npcs:
                if npc.speech_box and npc.speech_box.active:
                    npc.speech_box.handle_click(event.pos)

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
            mouse_x += self.camera.rect.x
            mouse_y += self.camera.rect.y
            all_collision_rects = (
                self.map.collision_rects + self.map.entity_collision_rects
            )
            all_collision_rects = [
                rect
                for rect in all_collision_rects
                if rect != self.player.collision_rect
            ]
            self.player.worn_equipment["Artefact"].activate_effect(
                self.player, mouse_x, mouse_y, all_collision_rects, self.map
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
            and not self.player.in_dialogue
        ):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x += self.camera.rect.x
            mouse_y += self.camera.rect.y
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
                    # If there's an item already in the equipment slot
                    if self.player.worn_equipment[item.equipment_slot]:
                        # Swap the items
                        self.player.inventory.items.insert(
                            i, self.player.worn_equipment[item.equipment_slot]
                        )
                        self.player.unequip_item(item.equipment_slot)
                    # Equip the clicked item
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
        if self.player.in_quest_ui:
            return
        if event.key == pygame.K_TAB:
            self.player.toggle_inventory()
        elif event.key == pygame.K_e:
            self.handle_keydown_e()

    def handle_keydown_e(self):
        for chest in self.map.chests:
            if self.player.rect.colliderect(chest.rect):
                if self.player.current_chest is None:
                    self.player.open_chest(chest)
                else:
                    self.player.close_chest()

        for npc in self.map.npcs:
            if self.player.rect.colliderect(npc.rect):
                if npc.speech_box is None:
                    npc.interact(self.screen_width, self.screen_height, self.player)
                    self.player.in_dialogue = True
                elif npc.speech_box and not npc.speech_box.active:
                    npc.interact(self.screen_width, self.screen_height, self.player)
                    self.player.in_dialogue = True
                elif npc.speech_box and npc.speech_box.active:
                    npc.speech_box.stop()
                    self.player.in_dialogue = False

    def draw_map(self):
        self.game_screen.fill((48, 44, 45, 255))
        self.game_screen.blit(self.map.surface, (0, 0), self.camera.rect)

    def update_game_screen(self):
        self.update_mouse()
        pygame.display.flip()

    def update_mouse(self):
        mx, my = pygame.mouse.get_pos()
        self.game_screen.blit(self.cursor_img, (mx, my))

    def handle_dead_player(self):
        self.game_over = True
