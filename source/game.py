# game.py
import pygame
import pickle
from map import Map
from player import Player
from projectile import Arrow


class Game:
    def __init__(self, screen_width, screen_height, map_file):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = 20
        self.map_file = map_file
        self.last_shot = 0

        pygame.init()
        pygame.mixer.init()

        self.game_screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption("MiniQuest")
        self.clock_object = pygame.time.Clock()

        self.player = Player(400, 400, self.tile_size)
        self.map = Map(self.map_file, self.screen_width, self.screen_height)
        self.map.collisionSetup()

        pygame.mixer.music.load("source/sound/music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)

    def save_map(self, map_filename):
        with open(map_filename, "wb") as f:
            pickle.dump(self.map, f)

    def load_map(self, map_filename):
        with open(map_filename, "rb") as f:
            self.map = pickle.load(f)

    def run(self):
        run = True
        while run:
            self.clock_object.tick(60)
            self.map.drawFloorLayer(self.game_screen)
            self.map.drawGroundLayer(self.game_screen)

            self.map.update(self.game_screen, self.player)

            if self.player.movement(
                self.map.collision_tiles, self.screen_width, self.screen_height
            ):
                self.map.walk_particles(self.player)

            self.game_screen.blit(self.player.image, self.player.rect)
            self.map.drawAboveGroundLayer(self.game_screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 & self.player.canshoot:
                        current_time = pygame.time.get_ticks()
                        if current_time - self.last_shot >= 1000:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            new_projectile = Arrow(
                                mouse_x,
                                mouse_y,
                                20,
                                15,
                                self.player,
                            )
                            self.map.projectiles.append(new_projectile)
                            self.last_shot = current_time

            pygame.display.update()

        pygame.quit()
