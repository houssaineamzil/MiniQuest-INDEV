import random
import pygame
import pytmx
import math


class Map:
    def __init__(self, file, screenWidth, screenHeight):
        self.map = pytmx.load_pygame(file, pixelalpha=True)
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.collision_tiles = []
        self.portals = {}  # Dictionary linking portals to map files

    def collisionSetup(self):
        collision = self.map.get_layer_by_name("collision")
        for x, y, gid in collision:
            if gid:  # Check if the tile exists
                self.collision_tiles.append(
                    pygame.Rect(
                        x * self.map.tilewidth,
                        y * self.map.tileheight,
                        self.map.tilewidth,
                        self.map.tileheight,
                    )
                )

        self.portals = []
        for layer in self.map.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "portal":
                    for obj in layer:
                        if obj.name is not None:  # check if name is not None
                            portal_rect = pygame.Rect(
                                obj.x, obj.y, obj.width, obj.height
                            )
                            portal_info = obj.name.split(
                                ","
                            )  # Split the portal name into parts
                            map_file = portal_info[0]
                            destination = tuple(
                                int(i) for i in portal_info[1:]
                            )  # convert to integers and pack in a tuple
                            self.portals.append(
                                Portal(portal_rect, map_file, destination)
                            )

    def drawGroundLayer(self, gameScreen):
        ground_layer = self.map.get_layer_by_name("ground")

        for x, y, gid in ground_layer:
            tile = self.map.get_tile_image_by_gid(gid)
            if tile:
                gameScreen.blit(tile, (x * self.map.tilewidth, y * self.map.tileheight))

    def drawGroundLayer2(self, gameScreen):
        ground_layer = self.map.get_layer_by_name("ground2")

        for x, y, gid in ground_layer:
            tile = self.map.get_tile_image_by_gid(gid)
            if tile:
                gameScreen.blit(tile, (x * self.map.tilewidth, y * self.map.tileheight))

    def drawAboveGroundLayer(self, gameScreen):
        above_ground_layer = self.map.get_layer_by_name("above_ground")

        for x, y, gid in above_ground_layer:
            tile = self.map.get_tile_image_by_gid(gid)
            if tile:
                gameScreen.blit(tile, (x * self.map.tilewidth, y * self.map.tileheight))


class Portal:
    def __init__(self, rect, map_file, destination):
        self.rect = rect
        self.map_file = map_file
        self.destination = destination
