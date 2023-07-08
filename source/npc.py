import random
import math
from character import Character
import pygame
from speech import SpeechBox, DialogueOption
from quest import QuestOfferUI, Quest, Objective


class NPC(Character):
    def __init__(self, hp, spritesheet):
        super().__init__(hp, spritesheet)

    def interact(self, player):
        raise NotImplementedError("Subclasses must implement interact method")

    def ai_move(self, collision_rects, screen_width, screen_height):
        raise NotImplementedError("Subclasses must implement ai_move method")


class Townsfolk(NPC):
    size_x = 32
    size_y = 50

    def __init__(self, x, y, hp):
        spritesheet = "source/img/townsfolk.png"
        super().__init__(hp, spritesheet)
        self.speed = 1
        adjustment = 3
        self.rect = pygame.FRect(
            x, y - adjustment, self.size_x, self.size_y - adjustment
        )
        self.collision_rect = pygame.FRect(
            self.rect.x, self.rect.y, self.rect.width * 0.9, self.rect.height * 0.4
        )
        self.collision_rect.midbottom = self.rect.midbottom
        self.respawn_time = 20000
        self.dead = False
        self.dead_counter = 0
        self.wait_counter = 0
        self.direction = random.randint(0, 3)
        self.next_direction = random.randint(0, 3)
        self.initial_dialogue_option = None
        self.speech_box = None
        self.current_quest_offer_ui = None

        self.quests = {
            "pest_control": Quest(
                name="Pest Control",
                description="Bob, the local innkeeper, is grappling with a rat infestation in his cellar. He seeks a brave soul to eliminate these pests and safeguard his storeroom.",
                reward="Reward: You will get a free room in the inn",
                difficulty="Difficulty: Easy",
                length="Length: Short",
                offered_by="Offered by: Bob",
                objectives=[
                    Objective(
                        description="Kill 1 Archer",
                        target="Archer",
                        target_amount=1,
                    ),
                ],
            )
        }

    def interact(self, screen_width, screen_height, player):
        self.talk(screen_width, screen_height, player)

    def talk(self, screen_width, screen_height, player):
        if self.speech_box is None:
            continue_option = DialogueOption("Continue...", "", [])
            continue_option.set_action(
                lambda: setattr(
                    self,
                    "current_quest_offer_ui",
                    QuestOfferUI(
                        screen_width, screen_height, self.quests["pest_control"]
                    ),
                )
            )

            rat_quest_option_1 = DialogueOption(
                "Ok, I'll do it",
                "Great! I knew I could count on you.",
                [continue_option],
            )

            rat_quest_option_2 = DialogueOption(
                "No, I hate rats",
                "Well, I can't force you. If you change your mind, you know where to find me.",
                [],
            )

            has_pest_quest = any(
                quest.name == "Pest Control" for quest in player.quest_log.quests
            )

            whats_in_it_for_me_option = DialogueOption(
                "What's in it for me?",
                "I'll let you stay in my inn, free of charge!",
                [rat_quest_option_1, rat_quest_option_2] if not has_pest_quest else [],
            )

            rumour_text = (
                "No, I don't have any rumours."
                if has_pest_quest
                else "Yes, actually I need someone to go into the basement and clear out some rats."
            )

            rumour_option = DialogueOption(
                "Do you have any rumours?",
                rumour_text,
                [whats_in_it_for_me_option] if not has_pest_quest else [],
            )

            cant_afford_option = DialogueOption(
                "I can't afford that", "Well, I'm sorry to hear that.", []
            )

            stay_at_in_text = (
                "Sure, it's 1,000 gold per night."
                if not has_pest_quest
                else "Sure, it's 1,000 gold per night. But I'll let you stay for free if you take care of those rats."
            )

            what_was_i_supposed_to_do_option = DialogueOption(
                "What was I supposed to do again?",
                "You were supposed to clear out the rats in my cellar and make sure they dont come back.",
                [],
            )

            about_those_rats_option = DialogueOption(
                "About those rats...",
                "Yes?",
                [what_was_i_supposed_to_do_option],
            )

            stay_at_inn = DialogueOption(
                "Can I stay at your inn?",
                stay_at_in_text,
                [cant_afford_option]
                if not has_pest_quest
                else [about_those_rats_option],
            )
            cant_afford_option = DialogueOption(
                "I can't afford that", "Well, I'm sorry to hear that.", []
            )
            ask_something = DialogueOption(
                "I have something to ask you",
                "What is it?",
                [rumour_option, stay_at_inn],
            )
            just_kidding_option = DialogueOption(
                "Just kidding", "That's not funny!", []
            )
            no_really_option = DialogueOption("No, really", "Please, no!", [])

            prepare_to_die_option = DialogueOption(
                "Prepare to die!",
                "Wait, what?!",
                [
                    just_kidding_option,
                    no_really_option,
                ],
            )

            have_to_go_option = DialogueOption("I have to go now", "Goodbye", [])

            hello_option = DialogueOption(
                "Hello",
                "How can I help you?",
                [
                    ask_something,
                    have_to_go_option,
                ],
            )

            initial_options = [
                hello_option,
                prepare_to_die_option
                if not has_pest_quest
                else about_those_rats_option,
            ]

            initial_text = "Hello, welcome to my inn!"
            self.initial_dialogue_option = DialogueOption(
                initial_text, initial_text, initial_options
            )
            self.speech_box = SpeechBox(
                "Bob", self.initial_dialogue_option, screen_width, screen_height
            )

        if not self.speech_box.active:
            self.speech_box.dialogue_option = self.initial_dialogue_option
            self.speech_box.options = self.speech_box.dialogue_option.next_options
            self.speech_box.start()

    def ai_move(
        self, collision_rects, entity_collision_rects, screen_width, screen_height
    ):
        if self.speech_box and self.speech_box.active:
            return False

        self.current_animation.update()
        moved = False

        all_collision_rects = collision_rects + entity_collision_rects
        all_collision_rects = [
            rect for rect in all_collision_rects if rect != self.collision_rect
        ]

        if self.wait_counter > 0:
            self.wait_counter -= 1
            if self.direction == 0:
                self.current_animation = self.standing_animation_north
            elif self.direction == 1:
                self.current_animation = self.standing_animation_east
            elif self.direction == 2:
                self.current_animation = self.standing_animation_south
            elif self.direction == 3:
                self.current_animation = self.standing_animation_west
            return False

        if self.move_counter > 0:
            self.move_counter -= 1
            self.direction = self.next_direction
            if self.direction == 0:
                moved = self.move(
                    0, -self.speed, all_collision_rects, screen_width, screen_height
                )
            elif self.direction == 1:
                moved = self.move(
                    self.speed, 0, all_collision_rects, screen_width, screen_height
                )
            elif self.direction == 2:
                moved = self.move(
                    0, self.speed, all_collision_rects, screen_width, screen_height
                )
            elif self.direction == 3:
                moved = self.move(
                    -self.speed, 0, all_collision_rects, screen_width, screen_height
                )
        else:
            self.move_counter = random.randint(20, 70)
            self.next_direction = random.randint(0, 3)
            self.wait_counter = random.randint(20, 500)
        return moved

    def take_damage(self):
        super().take_damage()
        if self.hp <= 0:
            self.dead = True
            self.dead_counter = self.respawn_time

    def update(self, collision_rects, screen_width, screen_height):
        if self.dead:
            self.dead_counter -= 1
            if self.dead_counter <= 0:
                self.dead = False
                self.hp = self.max_hp
                self.rect = self.spawn_point.copy()
        else:
            self.ai_move(collision_rects, screen_width, screen_height)
