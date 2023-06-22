from character import Character


class NPC(Character):
    def __init__(self, hp, spritesheet):
        super().__init__(hp, spritesheet)

    def interact(self, player):
        raise NotImplementedError("Subclasses must implement interact method")

    def ai_move(self, collision_tiles, screen_width, screen_height, *args):
        raise NotImplementedError("Subclasses must implement ai_move method")

    def talk():
        raise NotImplementedError("Subclasses must implement talk method")
