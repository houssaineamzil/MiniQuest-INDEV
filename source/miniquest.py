import pygame
from screenManager import ScreenManager
from resourcePath import resource_path

if __name__ == "__main__":
    manager = ScreenManager(1280, 720, "inn.tmx")
    icon = pygame.image.load(resource_path("source/img/mq.ico"))
    pygame.display.set_icon(icon)
    manager.run()
