import pygame


class Animation:
    def __init__(self, spritesheet, num_frames, x, y, width, height):
        self.frames = [
            spritesheet.get_image(x + i * width, y, width, height)
            for i in range(num_frames)
        ]
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 150
        self.direction = "south"

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen, x, y):
        image = self.frames[self.current_frame]
        screen.blit(image, (x, y))

    def reset(self):
        self.current_frame = 0
