import pygame


class DialogueOption:
    def __init__(self, text, response, next_options):
        self.text = text
        self.response = response
        self.next_options = next_options


class SpeechBox:
    def __init__(self, npc_name, dialogue_option, screen_width, screen_height):
        self.dialogue_option = dialogue_option
        self.font = pygame.font.Font(None, 22)
        self.name_font = pygame.font.Font(None, 24)
        self.text_color = (0, 0, 0)
        self.box_color = (210, 180, 140)
        self.box_size = (220, 120)
        self.box_position = (
            screen_width // 2 - self.box_size[0] // 2,
            int(screen_height * 0.6),
        )
        self.box_surface = pygame.Surface(self.box_size)
        self.options_surface = pygame.Surface(self.box_size)
        self.options_font = pygame.font.Font(None, 18)
        self.options = dialogue_option.next_options
        self.active = False
        self.npc_name = npc_name

    def wrap_text(self, text, font, max_width):
        lines = []
        words = text.split(" ")
        while words:
            line_words = []
            while (
                words and font.size(" ".join(line_words + [words[0]]))[0] <= max_width
            ):
                line_words.append(words.pop(0))
            lines.append(" ".join(line_words))
        return lines

    def update(self):
        self.box_surface.fill(self.box_color)

        name_surface = self.name_font.render(self.npc_name, True, self.text_color)
        name_rect = name_surface.get_rect(center=(self.box_size[0] // 2, 20))
        self.box_surface.blit(name_surface, name_rect)

        lines = self.wrap_text(
            self.dialogue_option.response, self.font, self.box_size[0]
        )
        for i, line in enumerate(lines):
            line_surface = self.font.render(line, True, self.text_color)
            line_rect = line_surface.get_rect(
                center=(self.box_size[0] // 2, 50 + 20 * i)
            )
            self.box_surface.blit(line_surface, line_rect)

        self.options_surface.fill(self.box_color)
        for i, option in enumerate(self.options):
            lines = self.wrap_text(option.text, self.options_font, self.box_size[0])
            for j, line in enumerate(lines):
                line_surface = self.options_font.render(line, True, self.text_color)
                line_rect = line_surface.get_rect(
                    center=(self.box_size[0] // 2, 30 * i + 10 + 20 * j)
                )
                self.options_surface.blit(line_surface, line_rect)

    def draw(self, screen):
        screen.blit(self.box_surface, self.box_position)
        options_position = (
            self.box_position[0],
            self.box_position[1] + self.box_size[1] + 10,
        )
        screen.blit(self.options_surface, options_position)

    def add_dialogue_option(self, text, response, next_options):
        self.dialogue_options.append(DialogueOption(text, response, next_options))

    def handle_click(self, mouse_position):
        option_index = (
            mouse_position[1] - self.box_position[1] - self.box_size[1] - 10
        ) // 30
        if 0 <= option_index < len(self.options):
            self.dialogue_option = self.options[option_index]
            self.options = self.dialogue_option.next_options
            self.update()

    def start(self):
        self.active = True
        self.update()

    def stop(self):
        self.active = False
