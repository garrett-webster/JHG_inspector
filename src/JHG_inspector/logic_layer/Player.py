from functools import cached_property


class Player:
    def __init__(self, game: "Game", player_id: int, player_order_num: int):
        self.game = game
        self.player_id = player_id
        self.player_order_num = player_order_num

    @cached_property
    def round_popularity(self):
        popularity_list = []
        for round_popularity in self.game.popularities:
            popularity_list.append(round_popularity[self.player_order_num])

        return popularity_list

    @cached_property
    def round_allocations(self):
        allocation_list = []
        for round_allocation in self.game.allocations:
            allocation_list.append(round_allocation[self.player_order_num])

        return allocation_list

    @cached_property
    def gameName(self):
        return self.game.database_manager.DAOs["players"].select_one(["gameName"], ["id"], [self.player_id])[0]

    @cached_property
    def name(self):
        return self.game.database_manager.DAOs["players"].select_one(["name"], ["id"], [self.player_id])[0]

    @cached_property
    def experience(self):
        return self.game.database_manager.DAOs["players"].select_one(["experience"], ["id"], [self.player_id])[0]

    @cached_property
    def permission_level(self):
        return self.game.database_manager.DAOs["players"].select_one(["permissionLevel"], ["id"], [self.player_id])[0]

    @cached_property
    def color(self):
        return self.game.database_manager.DAOs["players"].select_one(["color"], ["id"], [self.player_id])[0]

    @cached_property
    def hue(self):
        return self.game.database_manager.DAOs["players"].select_one(["hue"], ["id"], [self.player_id])[0]

    @cached_property
    def avatar(self):
        return self.game.database_manager.DAOs["players"].select_one(["avatar"], ["id"], [self.player_id])[0]

    @cached_property
    def icon(self):
        return self.game.database_manager.DAOs["players"].select_one(["icon"], ["id"], [self.player_id])[0]