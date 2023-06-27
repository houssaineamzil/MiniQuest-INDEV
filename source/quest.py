import pygame


class Objective:
    def __init__(self, description, complete=False):
        self.description = description
        self.complete = complete

    def is_complete(self):
        return self.complete


class Quest:
    def __init__(
        self, name, description, reward, difficulty, length, offered_by, objectives
    ):
        self.name = name
        self.description = description
        self.reward = reward
        self.difficulty = difficulty
        self.length = length
        self.offered_by = offered_by
        self.objectives = objectives

    def is_complete(self):
        return all([obj.is_complete() for obj in self.objectives])

    def get_incomplete_objectives(self):
        return [obj for obj in self.objectives if not obj.is_complete()]


class QuestLog:
    def __init__(self):
        self.quests = []
        self.completed_quests = []

    def add_quest(self, quest):
        self.quests.append(quest)

    def remove_quest(self, quest):
        self.quests.remove(quest)

    def complete_quest(self, quest):
        self.quests.remove(quest)
        self.completed_quests.append(quest)


class QuestOfferUI:
    def __init__(self, screen_width, screen_height, quest):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.accept_button = Button(0, 0, 100, 50, "Accept")
        self.reject_button = Button(0, 0, 100, 50, "Reject")
        self.quest = quest

    def get_quest(self):
        return self.quest

    def draw(self, game_screen):
        scroll = pygame.Surface((self.screen_width // 2, self.screen_height // 2))
        scroll.fill((210, 180, 140))

        font = pygame.font.Font(None, 24)
        font_bold = pygame.font.Font(None, 36)

        name_text = font_bold.render(self.quest.name, True, (0, 0, 0))

        description_text = self.quest.description
        reward_text = self.quest.reward
        difficulty_text = self.quest.difficulty
        length_text = self.quest.length
        offered_by_text = self.quest.offered_by

        text_y = 40

        name_rect = name_text.get_rect(center=(self.screen_width // 4, text_y))
        scroll.blit(name_text, name_rect)
        text_y += name_rect.height + 20

        words = description_text.split(" ")
        lines = [words[0]]
        for word in words[1:]:
            test_line = lines[-1] + " " + word
            test_text = font.render(test_line, True, (0, 0, 0))
            if test_text.get_rect().width > self.screen_width // 2 - 20:
                lines.append(word)
            else:
                lines[-1] = test_line
        for line in lines:
            line_text = font.render(line, True, (0, 0, 0))
            scroll.blit(line_text, (10, text_y))
            text_y += line_text.get_rect().height + 5
        text_y += 20

        for text_str in [reward_text, difficulty_text, length_text, offered_by_text]:
            line_text = font.render(text_str, True, (0, 0, 0))
            scroll.blit(line_text, (10, text_y))
            text_y += line_text.get_rect().height + 10

        game_screen.blit(scroll, (self.screen_width // 4, self.screen_height // 4))

        total_button_width = self.accept_button.width + self.reject_button.width
        space_between_buttons = self.screen_width // 10

        total_width = total_button_width + space_between_buttons
        starting_x = (self.screen_width - total_width) // 2

        self.accept_button.x = starting_x
        self.accept_button.y = (
            (self.screen_height * 3 // 4) - self.accept_button.height // 2 - 40
        )

        self.reject_button.x = (
            self.accept_button.x + self.accept_button.width + space_between_buttons
        )
        self.reject_button.y = self.accept_button.y

        self.accept_button.draw(game_screen)
        self.reject_button.draw(game_screen)

    def check_button_press(self, event):
        mouse_pos = event.pos
        if (
            self.reject_button.rect.collidepoint(mouse_pos)
            and pygame.mouse.get_pressed()[0]
        ):
            return "reject"
        elif (
            self.accept_button.rect.collidepoint(mouse_pos)
            and pygame.mouse.get_pressed()[0]
        ):
            return "accept"
        else:
            return None


class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        color=(210, 180, 140),
        text_color=(0, 0, 0),
        border_thickness=2,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.text_color = text_color
        self.border_thickness = border_thickness
        self.is_hovered = False

    def draw(self, screen):
        button_color = self.color

        if self.is_hovered:
            button_color = (
                button_color[0] - 30,
                button_color[1] - 30,
                button_color[2] - 30,
            )

        pygame.draw.rect(
            screen, button_color, (self.x, self.y, self.width, self.height)
        )
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (self.x, self.y, self.width, self.height),
            self.border_thickness,
        )

        # Draw the button text
        font = pygame.font.Font(None, 24)
        text = font.render(self.text, True, self.text_color)
        screen.blit(
            text,
            (
                self.x + (self.width - text.get_width()) // 2,
                self.y + (self.height - text.get_height()) // 2,
            ),
        )
