import pygame

from game import Game


class ScreenManager:
    def __init__(self, screen_width, screen_height, map_file):
        self.cursor_img = pygame.image.load("source/img/cursor.png")
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_file = map_file
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("MiniQuest")
        pygame.font.init()
        pygame.mouse.set_visible(False)
        self.game_screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )

        self.game = None
        self.screen = "main_menu"

    def run(self):
        while True:
            if self.screen == "game":
                if not self.game:
                    self.game = Game(
                        self.screen_width,
                        self.screen_height,
                        self.map_file,
                        self.game_screen,
                    )
                    self.game.run(375, 420)
                else:
                    if self.game.game_over:
                        self.screen = "death"
                        self.game = None
            elif self.screen == "main_menu":
                self.main_menu()
            elif self.screen == "death":
                self.death_screen()

    def main_menu(self):
        running = True
        clock = pygame.time.Clock()

        button_width = 200
        button_height = 50
        button_start_x = self.screen_width / 2 - button_width / 2
        button_gap = 20

        buttons = [
            pygame.Rect(
                button_start_x,
                self.screen_height / 2 - 1.5 * button_height - button_gap,
                button_width,
                button_height,
            ),
            pygame.Rect(
                button_start_x,
                self.screen_height / 2 - 0.5 * button_height,
                button_width,
                button_height,
            ),
            pygame.Rect(
                button_start_x,
                self.screen_height / 2 + 0.5 * button_height + button_gap,
                button_width,
                button_height,
            ),
        ]
        button_texts = ["Start Game", "Credits", "Exit"]

        while running:
            self.game_screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for i, button in enumerate(buttons):
                        if button.collidepoint(mouse_pos):
                            if button_texts[i] == "Start Game":
                                self.screen = "game"
                                running = False
                            elif button_texts[i] == "Credits":
                                # TODO: Show the credits screen
                                pass
                            elif button_texts[i] == "Exit":
                                pygame.quit()
                                quit()

            for i, button in enumerate(buttons):
                pygame.draw.rect(self.game_screen, (255, 255, 255), button)
                button_font = pygame.font.Font(None, 30)
                button_text = button_font.render(button_texts[i], True, (0, 0, 0))
                button_text_rect = button_text.get_rect(center=button.center)
                self.game_screen.blit(button_text, button_text_rect)

            self.update_screen()
            clock.tick(60)

    def death_screen(self):
        game_over_font = pygame.font.Font(None, 50)
        game_over_text = game_over_font.render("You Died.", True, (150, 0, 0))
        text_surface = pygame.Surface(game_over_text.get_size(), pygame.SRCALPHA)
        text_rect = text_surface.get_rect(
            center=(self.screen_width / 2, self.screen_height / 2)
        )
        self.game_screen.fill((0, 0, 0))
        text_surface.blit(game_over_text, (0, 0))
        self.game_screen.blit(text_surface, text_rect)

        respawn_font = pygame.font.Font(None, 30)
        respawn_text = respawn_font.render("Main Menu", True, (150, 0, 0))
        respawn_surface = pygame.Surface(respawn_text.get_size(), pygame.SRCALPHA)
        respawn_rect = respawn_surface.get_rect(
            center=(self.screen_width / 2, self.screen_height / 2 + 100)
        )
        respawn_surface.blit(respawn_text, (0, 0))
        self.game_screen.blit(respawn_surface, respawn_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.handle_quit_event()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if respawn_rect.collidepoint((mx, my)):
                    self.screen = "main_menu"

        self.update_screen()

    def update_screen(self):
        self.update_mouse()
        pygame.display.flip()

    def handle_quit_event(self):
        pygame.quit()
        quit()

    def update_mouse(self):
        mx, my = pygame.mouse.get_pos()
        self.game_screen.blit(self.cursor_img, (mx, my))
