import random
import pygame
import pytmx
import math


class Game:
    def __init__(self):
        self.maps = {}
        self.current_map = None

    def load_map(self, map_name):
        self.current_map = self.maps[map_name]
        self.current_map.load()

    def save_map(self, map_name):
        self.maps[map_name].save()

    def change_map(self, new_map_name):
        self.save_map(self.current_map)
        self.load_map(new_map_name)

    def update(self):
        pass
        # update current map

    def draw(self, screen):
        pass
        # draw current map to screen
