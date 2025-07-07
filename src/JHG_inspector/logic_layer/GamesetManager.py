from src.JHG_inspector.logic_layer.Gameset import Gameset


class GamesetManager:
    """Used by the DatabaseManager to handle operations dealing with the gamesets.

       The DatabaseManager has a reference to the GamesetManager. Anytime that a change needs to be made to the gamesets
       (loading, creation, deletion, etc), the request will be routed through the GamesetManager, which then will access
       the Data Access Objects (DOAs) from the DatabaseManager to perform the database operations.
       """

    def __init__(self, database: "DatabaseManager", tools_manager: "ToolsManager"):
        self.database = database
        self.tools_manager = tools_manager
        self.gamesets = {}

        self.load_gamesets()

    def __getitem__(self, gameset_id):
        return self.gamesets[gameset_id]

    @property
    def all(self):
        """The preferred way to access self.gamesets"""
        return self.gamesets

    def load_gamesets(self):
        """Loads the gamesets from the database into memory."""
        self.gamesets = {}
        gameset_ids = self.database.DAOs["gamesets"].select_all(["id"])

        for gameset_id in gameset_ids:
            from src.JHG_inspector.logic_layer.Gameset import Gameset
            new_gameset = Gameset(gameset_id[0], self.database, self.update_signal)
            new_gameset.load_games()
            self.gamesets[new_gameset.id] = new_gameset

            self.tools_manager.new_gameset(new_gameset)

    def create_gameset(self, name: str):
        """Creates a new gameset and adds it to the database."""
        new_gameset_id = self.database.DAOs["gamesets"].insert_one((name,))
        new_gameset = Gameset(new_gameset_id, self.database, self.update_signal)
        self.gamesets[new_gameset.id] = new_gameset

        self.tools_manager.new_gameset(new_gameset)
        return new_gameset

    def delete_gameset(self, gameset: "Gameset"):
        """Deletes a gameset from the database, as well as all related gameset to game relationships."""
        self.database.DAOs["gameset_games"].delete_one(["gamesetId"], (gameset.id,))
        self.database.DAOs["gamesets"].delete_one(["id"], [gameset.id])
        self.database.connection.commit()

    def update_signal(self, gameset_id: int):
        """Not implemented yet. Will be used to trigger updates in the tools once they are implemented"""
        self.tools_manager.update_tools(gameset_id)
        pass
