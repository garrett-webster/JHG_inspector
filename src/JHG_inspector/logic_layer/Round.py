from functools import cached_property


class Round:
    def __init__(self, game: "Game", round_number: int):
        self.game = game
        self.round_number = round_number

    @cached_property
    def popularities(self) -> list[int]:
        return self.game.popularities[self.round_number]

    @cached_property
    def allocations(self) -> list[list[int]]:
        return self.game.allocations[self.round_number]
