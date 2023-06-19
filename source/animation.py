import pygame


class Animation:
    def __init__(self, spritesheet, num_frames, x, y, width, height):
        self.frames = [
            spritesheet.get_image(x + i * width, y, width, height)
            for i in range(num_frames)
        ]
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100
        self.direction = "south"

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen, x, y, size_x, size_y, color=(255, 255, 255)):
        image = self.frames[self.current_frame].copy()  # Make a copy of the sprite
        image.fill(color, special_flags=pygame.BLEND_MULT)
        image_rect = image.get_rect()
        image_rect.midbottom = (x + size_x // 2, y + size_y)
        screen.blit(image, image_rect.topleft)

    def reset(self):
        self.current_frame = 0

    def get_current_image(self):
        return self.frames[self.current_frame].copy()
