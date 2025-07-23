from src.JHG_inspector.data_layer.game_file_loaders.GameFileLoader import GameFileLoader, load_data


class GameFileLoader_JsonV1(GameFileLoader):
    """Game file loader for the first version of the json"""

    @load_data("games")
    def _load_games_data(self, data, values, table_name):
        if data["transactions"]:
            num_transactions = len(data["transactions"])
        else:
            num_transactions = 0
        values.append((
            data["lobby"]["code"],
            data["lobby"]["numPlayers"],
            data["lobby"]["numObservers"],
            num_transactions,
            data["status"],
            data["startDateTime"],
            data["gameParams"]["lengthOfRound"],
            data["gameParams"]["nameSet"],
            data["gameParams"]["chatType"],
            data["gameParams"]["messageType"],
            data["gameParams"]["advancedGameSetup"],
            data["gameParams"]["gameEndCriteria"]["low"],
            data["gameParams"]["gameEndCriteria"]["high"],
            data["gameParams"]["gameEndCriteria"]["runtimeType"],
            data["gameParams"]["popularityFunctionParams"]["alpha"],
            data["gameParams"]["popularityFunctionParams"]["beta"],
            data["gameParams"]["popularityFunctionParams"]["cGive"],
            data["gameParams"]["popularityFunctionParams"]["cKeep"],
            data["gameParams"]["popularityFunctionParams"]["cSteal"],
            data["gameParams"]["popularityFunctionParams"]["povertyLine"],
            data["gameParams"]["governmentParams"]["initialPopularity"],
            data["gameParams"]["governmentParams"]["initialPopularityType"],

            data["gameParams"]["popularityParams"]["randomPopularities"],
            data["gameParams"]["popularityParams"]["randomPopHigh"],
            data["gameParams"]["popularityParams"]["randomPopLow"],

            data["gameParams"]["governmentParams"]["sendVotesImmediately"],
            data["gameParams"]["labels"]["enabled"],
            data["endCondition"]["duration"],
            data["endCondition"]["runtimeType"],
        ))

    @load_data("searchTags")
    def _load_searchTags_data(self, data, values, table_name):
        for tag, value in data["gameParams"]["show"].items():
            values.append((self.game.id, "show_" + tag, value))

        for tag, value in data["gameParams"]["allowEdit"].items():
            values.append((self.game.id, "allowEdit_" + tag, value))

    @load_data("players")
    def _load_player_data(self, data, values, table_name):
        for entry in data[table_name]:
            values.append(
                (self.game.id, entry["gameName"], entry["name"], entry["experience"], entry["permissionLevel"],
                 entry["color"], entry["hue"], entry["avatar"], entry["icon"]))

    @load_data("admins")
    def _load_admins_data(self, data, values, table_name):
        for game_name in data["lobby"]["admins"]:
            admin_id = self.game.name_to_id[game_name]
            values.append((self.game.id, game_name, admin_id))

    @load_data("playersThatWillBeGovernment")
    def _load_playersThatWillBeGovernment_data(self, data, values, table_name):
        if data["gameParams"]["governmentParams"]["playersThatWillBeGovernment"] is not None:
            for name in data["gameParams"]["governmentParams"]["playersThatWillBeGovernment"]:
                player_id = self.database_manager.DAOs["players"].select_one(["id"], ["name", "gameId"], [name, self.game.id])
                values.append((self.game.id, player_id[0]))

        self.game.set_id_to_name_dicts()

    @load_data("colorGroups")
    def _load_colorGroups_data(self, data, values, table_name):
        if data.get("colorGroups") is not None:
            for color_group in data["colorGroups"]:
                values.append((self.game.id, color_group["percentOfPlayers"], color_group["color"]))

    @load_data("transactions")
    def _load_transactions_data(self, data, values, table_name):
        if data[table_name]:
            for round_num, (round_name, round_transactions) in enumerate(data[table_name].items()):
                for player_from, transactions in round_transactions.items():
                    player_from_id = self.game.name_to_id[player_from]
                    for player_to, allocation in transactions.items():
                        player_to_id = self.game.name_to_id[player_to]
                        values.append((self.game.id, round_num + 1, player_from_id, player_to_id, allocation))

    @load_data("popularities")
    def _load_popularities_data(self, data, values, table_name):
        for round_num, (round_name, round_data) in enumerate(data[table_name].items()):
            for player, popularity in round_data.items():
                player_id = self.game.name_to_id[player]
                values.append((self.game.id, round_num + 1, player_id, popularity))

    @load_data("groups")
    def _load_groups_data(self, data, values, table_name):
        for round_num, (round_name, round_data) in enumerate(data[table_name].items()):
            values.append((self.game.id, round_num + 1, round_name))

    @load_data("influences")
    def _load_influences_data(self, data, values, table_name):
        for round_num, (round_name, round_transactions) in enumerate(data[table_name].items()):
            for player_from, influences in round_transactions.items():
                player_from_id = self.game.name_to_id[player_from]
                for player_to, influence in influences.items():
                    if player_to != "__intrinsic__":
                        player_to_id = self.game.name_to_id[player_to]
                        values.append((self.game.id, round_num + 1, player_from_id, player_to_id, influence))

    @load_data("chatInfo")
    def _load_chatInfo_data(self, data, values, table_name):
        for in_game_id, chat_info in data[table_name].items():
            values.append((self.game.id, in_game_id, chat_info["name"]))

    @load_data("chatParticipants")
    def _load_chatParticipants_data(self, data, values, table_name):
        game_id = self.game.id
        for chat_name, chat_info in data["chatInfo"].items():
            chat_id = self.database_manager.DAOs["chatInfo"].select_id(["inGameId", "gameId"], [chat_name, game_id])

            if chat_name == "global":
                for player_id in self.game.id_to_name.keys():
                    values.append((chat_id, player_id))
            else:
                for participant in chat_info["participants"]:
                    participant_id = self.game.name_to_id[participant]
                    values.append((chat_id, participant_id))

    @load_data("messages")
    def _load_messages_data(self, data, values, table_name):
        game_id = self.game.id
        for chat_name, chat_info in data["chatInfo"].items():
            chat_id = self.database_manager.DAOs["chatInfo"].select_id(["inGameId", "gameId"], [chat_name, game_id])

            for in_game_id, message in chat_info["messages"].items():
                if "from" not in message: message["from"] = None
                values.append(
                    (chat_id, in_game_id, message["from"], message["body"], message["time"], message["runtimeType"]))