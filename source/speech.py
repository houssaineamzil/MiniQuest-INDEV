import pygame


class DialogueOption:
    def __init__(self, text, response, next_options):
        self.text = text
        self.response = response
        self.next_options = next_options
        self.action = None

    def set_action(self, action):
        self.action = action

    def select(self):
        if self.action:
            self.action()
        return self


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
        self.speech_surface = pygame.Surface(self.box_size)

        self.options_surface = pygame.Surface(self.box_size)
        self.options = dialogue_option.next_options
        self.active = False
        self.npc_name = npc_name
        self.hovered_option_index = None
        self.box_hover_color = (170, 140, 100)

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
        self.speech_surface.fill(self.box_color)

        name_surface = self.name_font.render(self.npc_name, True, self.text_color)
        name_rect = name_surface.get_rect(center=(self.box_size[0] // 2, 20))
        self.speech_surface.blit(name_surface, name_rect)

        lines = self.wrap_text(
            self.dialogue_option.response, self.font, self.box_size[0]
        )
        for i, line in enumerate(lines):
            line_surface = self.font.render(line, True, self.text_color)
            line_rect = line_surface.get_rect(
                center=(self.box_size[0] // 2, 50 + 20 * i)
            )
            self.speech_surface.blit(line_surface, line_rect)

        options_height = len(self.options) * 30
        options_padding = 10

        self.options_surface = pygame.Surface((self.box_size[0], options_height))
        self.options_surface.fill(self.box_color)

        for i, option in enumerate(self.options):
            color = (
                self.box_hover_color
                if i == self.hovered_option_index
                else self.box_color
            )

            box_rect = pygame.Rect(0, 30 * i + options_padding, self.box_size[0], 30)

            if i == self.hovered_option_index:
                box_rect.y -= options_padding
            self.options_surface.fill(color, box_rect)

            lines = self.wrap_text(option.text, self.font, self.box_size[0])
            text_height = len(lines) * self.font.get_height()
            text_offset = (30 - text_height) // 2

            for j, line in enumerate(lines):
                line_surface = self.font.render(line, True, self.text_color)
                line_rect = line_surface.get_rect(
                    center=(
                        self.box_size[0] // 2,
                        30 * i
                        + options_padding
                        + text_offset
                        + self.font.get_height() * j,
                    )
                )
                self.options_surface.blit(line_surface, line_rect)

    def draw(self, screen):
        screen.blit(self.speech_surface, self.box_position)

        if self.options:
            options_position = (
                self.box_position[0],
                self.box_position[1] + self.box_size[1] + 10,
            )
            screen.blit(self.options_surface, options_position)

    def handle_click(self, mouse_position):
        option_index = (
            mouse_position[1] - self.box_position[1] - self.box_size[1] - 10
        ) // 30
        if 0 <= option_index < len(self.options):
            selected_option = self.options[option_index].select()
            self.dialogue_option = selected_option
            self.options = selected_option.next_options
            self.update()

    def start(self):
        self.active = True
        self.update()

    def stop(self):
        self.active = False

    def handle_mouse_movement(self, mouse_position):
        new_option_index = (
            mouse_position[1] - self.box_position[1] - self.box_size[1] - 10
        ) // 30
        if 0 <= new_option_index < len(self.options):
            self.hovered_option_index = new_option_index
        else:
            self.hovered_option_index = None
        self.update()
