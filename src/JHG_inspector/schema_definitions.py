GAME_SCHEMA_QUERIES = {
    "lobby": """
        CREATE TABLE IF NOT EXISTS lobby (
            code TEXT NOT NULL,
            numPlayers INTEGER NOT NULL,
            numObservers INTEGER NOT NULL,
            creatorName TEXT,
            gameStarted INTEGER NOT NULL
        )
    """,
    "miscData": """
        CREATE TABLE IF NOT EXISTS miscData (
            status TEXT,
            nameSet TEXT,
            chatType TEXT,
            messageType TEXT,
            creatorId TEXT
        )
    """,
    "gameParams": """
        CREATE TABLE IF NOT EXISTS gameParams (
            lengthOfRound INTEGER,
            nameSet TEXT,
            chatType TEXT,
            messageType TEXT,
            gameEndCriteria_low INTEGER,
            gameEndCriteria_high INTEGER,
            gameEndCriteria_runtimeType TEXT,

            popularityFunctionParams_alpha REAL,
            popularityFunctionParams_beta REAL,
            popularityFunctionParams_cGive REAL,
            popularityFunctionParams_cKeep REAL,
            popularityFunctionParams_cSteal REAL,
            popularityFunctionParams_povertyLine REAL,
            popularityFunctionParams_shouldUseNewUpdate BOOLEAN,

            governmentParams_initialPopularity REAL,
            governmentParams_initialPopularityType TEXT,
            governmentParams_randomPopularities BOOLEAN,
            governmentParams_randomPopHigh REAL,
            governmentParams_randomPopLow REAL,
            governmentParams_playersThatWillBeGovernment TEXT,
            governmentParams_sendVotesImmediately BOOLEAN,

            labels_enabled BOOLEAN,

            show_roundLength BOOLEAN,
            show_gameLength BOOLEAN,
            show_chatType BOOLEAN,
            show_messageType BOOLEAN,
            show_nameSet BOOLEAN,
            show_initialSetup BOOLEAN,
            show_grouping BOOLEAN,
            show_labels BOOLEAN,
            show_advancedParams BOOLEAN,
            show_government BOOLEAN,
            show_visibilities BOOLEAN,
            show_colorGrouping BOOLEAN,
            show_pregame BOOLEAN,
            show_agents BOOLEAN,

            allowEdit_roundLength BOOLEAN,
            allowEdit_gameLength BOOLEAN,
            allowEdit_chatType BOOLEAN,
            allowEdit_messageType BOOLEAN,
            allowEdit_nameSet BOOLEAN,
            allowEdit_initialSetup BOOLEAN,
            allowEdit_grouping BOOLEAN,
            allowEdit_labels BOOLEAN,
            allowEdit_advancedParams BOOLEAN,
            allowEdit_government BOOLEAN,
            allowEdit_visibilities BOOLEAN,
            allowEdit_colorGrouping BOOLEAN,
            allowEdit_pregame BOOLEAN,
            allowEdit_agents BOOLEAN
        )
    """,
    "endCondition": """
        CREATE TABLE IF NOT EXISTS endCondition (
            duration INTEGER,
            runtimeType TEXT
        )
    """,
    "rounds": """
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY
        )
    """,
    "players": """
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT,
            experience TEXT,
            permissionLevel TEXT,
            color TEXT,
            hue TEXT,
            avatar TEXT,
            icon TEXT
        )
    """,
    "transactions": """
        CREATE TABLE IF NOT EXISTS transactions (
            round_id INTEGER,
            player_from_id INTEGER,
            player_to_id INTEGER,
            FOREIGN KEY(player_from_id) REFERENCES players(id),
            FOREIGN KEY(player_to_id) REFERENCES players(id),
            FOREIGN KEY(round_id) REFERENCES rounds(id)
        )
    """,
    "playerRoundInfo": """
        CREATE TABLE IF NOT EXISTS playerRoundInfo (
            player_id INTEGER,
            round_id INTEGER,
            numTokens INTEGER,
            group_name TEXT,
            FOREIGN KEY(player_id) REFERENCES players(id),
            FOREIGN KEY(round_id) REFERENCES rounds(id)
        )
    """,
    "popularities": """
        CREATE TABLE IF NOT EXISTS popularities (
            player_id INTEGER,
            round_id INTEGER,
            popularity REAL,
            FOREIGN KEY(player_id) REFERENCES players(id),
            FOREIGN KEY(round_id) REFERENCES rounds(id)
        )
    """,
    "influences": """
        CREATE TABLE IF NOT EXISTS influences (
            player_from_id INTEGER,
            player_to_id INTEGER,
            round_id INTEGER,
            influence REAL,
            FOREIGN KEY(player_from_id) REFERENCES players(id),
            FOREIGN KEY(player_to_id) REFERENCES players(id),
            FOREIGN KEY(round_id) REFERENCES rounds(id)
        )
    """
}