SIMPLE_JSON_STRUCTURE = {
    # "miscData": {
    #     "status": "TEXT",
    #     "creatorId": "TEXT",
    # },
    "lobby": {
        "code": "TEXT",
        "numPlayers": "INTEGER",
        "numObservers": "INTEGER",
        "creatorName": "TEXT",
        # "admins": [],
        # "playerNames": [],
        "gameStarted": "BOOLEAN"
    },
    "gameParams": {
        "lengthOfRound": "INTEGER",
        "nameSet": "TEXT",
        "chatType": "TEXT",
        "messageType": "TEXT",

        "gameEndCriteria": {
            "low": "INTEGER",
            "high": "INTEGER",
            "runtimeType": "TEXT"
        },

        "popularityFunctionParams": {
            "alpha": "REAL",
            "beta": "REAL",
            "cGive": "REAL",
            "cKeep": "REAL",
            "cSteal": "REAL",
            "povertyLine": "REAL",
            "shouldUseNewUpdate": "BOOLEAN"
        },

        "governmentParams": {
            "initialPopularity": "REAL",
            "initialPopularityType": "TEXT",
            "randomPopularities": "BOOLEAN",
            "randomPopHigh": "REAL",
            "randomPopLow": "REAL",
            "playersThatWillBeGovernment": "TEXT",
            "sendVotesImmediately": "BOOLEAN"
        },

        # "colorGroups": [],
        # "customParams": {},
        "labels": {
            "enabled": "BOOLEAN",
            # "labelPools": []
        },

        "show": {
            "roundLength": "BOOLEAN",
            "gameLength": "BOOLEAN",
            "chatType": "BOOLEAN",
            "messageType": "BOOLEAN",
            "nameSet": "BOOLEAN",
            "initialSetup": "BOOLEAN",
            "grouping": "BOOLEAN",
            "labels": "BOOLEAN",
            "advancedParams": "BOOLEAN",
            "government": "BOOLEAN",
            "visibilities": "BOOLEAN",
            "colorGrouping": "BOOLEAN",
            "pregame": "BOOLEAN",
            "agents": "BOOLEAN"
        },

        "allowEdit": {
            "roundLength": "BOOLEAN",
            "gameLength": "BOOLEAN",
            "chatType": "BOOLEAN",
            "messageType": "BOOLEAN",
            "nameSet": "BOOLEAN",
            "initialSetup": "BOOLEAN",
            "grouping": "BOOLEAN",
            "labels": "BOOLEAN",
            "advancedParams": "BOOLEAN",
            "government": "BOOLEAN",
            "visibilities": "BOOLEAN",
            "colorGrouping": "BOOLEAN",
            "pregame": "BOOLEAN",
            "agents": "BOOLEAN"
        }
    },
    "endCondition": {
        "duration": "INTEGER",
        "runtimeType": "TEXT"
    }
}