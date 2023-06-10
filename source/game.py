# game.py
import pygame
import os
from map import Map
from player import Player
from projectile import Arrow, Spell
from equipment import Equipment, Armour, Weapon
from spritesheet import Spritesheet


class Game:
    def __init__(self, screen_width, screen_height, player_x, player_y, map_file):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_file = map_file
        self.last_shot = 0

        pygame.init()
        pygame.mixer.init()

        self.game_screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption("MiniQuest")
        self.clock_object = pygame.time.Clock()

        self.whiteshirt = Armour(Spritesheet("source/img/whiteshirt.png"), 1)
        self.blackpants = Armour(Spritesheet("source/img/blackpants.png"), 1)
        self.brownboots = Armour(Spritesheet("source/img/brownboots.png"), 1)

        self.shortbow = Weapon(Spritesheet("source/img/brownboots.png"), Arrow, 10, 30)
        self.firestaff = Weapon(Spritesheet("source/img/brownboots.png"), Spell, 30, 10)

        self.player = Player(player_x, player_y)

        self.player.equip_armour(self.whiteshirt)
        self.player.equip_armour(self.blackpants)
        self.player.equip_armour(self.brownboots)
        self.player.equip_weapon(self.firestaff)

        self.map = Map(self.map_file, self.screen_width, self.screen_height)
        self.map.collisionSetup()

        pygame.mixer.music.load("source/sound/music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)

    def run(self):
        run = True
        while run:
            self.clock_object.tick(60)
            self.map.drawFloorLayer(self.game_screen)
            self.map.drawGroundLayer(self.game_screen)

            self.map.update(self.game_screen, self.player)
            # self.map.drawRects(self.game_screen, self.player)  # debug player collision

            if self.player.movement(
                self.map.collision_tiles, self.screen_width, self.screen_height
            ):
                self.map.walk_particles(self.player)
                pass

            self.player.update()
            self.player.draw(self.game_screen)
            self.map.drawAboveGroundLayer(self.game_screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    for file in os.listdir("source/tile"):
                        if file.endswith(".pkl"):
                            os.remove(os.path.join("source/tile", file))
                        run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.player.dead:
                        current_time = pygame.time.get_ticks()
                        if current_time - self.last_shot >= 1000:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            self.map.add_projectile(
                                self.player.weapon.shoot(self.player, mouse_x, mouse_y)
                            )
                            self.last_shot = current_time

            pygame.display.update()

        pygame.quit()
